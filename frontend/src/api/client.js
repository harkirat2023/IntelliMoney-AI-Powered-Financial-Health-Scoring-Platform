import axios from "axios";

const API_BASE_URL = process.env.API_BASE_URL || "/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

const TOKEN_KEY = "intellimoney_token";
const REFRESH_KEY = "intellimoney_refresh";

let _refreshing = false;
let _pendingQueue = [];

function _onRefreshed(token) {
  _pendingQueue.forEach((cb) => cb(token));
  _pendingQueue = [];
}

function _onRefreshFailed() {
  _pendingQueue.forEach((cb) => cb(null));
  _pendingQueue = [];
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }
    if (originalRequest.url === "/auth/refresh") {
      return Promise.reject(error);
    }
    if (_refreshing) {
      return new Promise((resolve) => {
        _pendingQueue.push((newToken) => {
          if (newToken) {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            resolve(api(originalRequest));
          } else {
            resolve(Promise.reject(error));
          }
        });
      });
    }
    originalRequest._retry = true;
    _refreshing = true;
    const refreshToken = localStorage.getItem(REFRESH_KEY);
    if (!refreshToken) {
      _refreshing = false;
      _onRefreshFailed();
      return Promise.reject(error);
    }
    try {
      const res = await api.post("/auth/refresh", { refresh_token: refreshToken });
      const { access_token, refresh_token } = res.data;
      localStorage.setItem(TOKEN_KEY, access_token);
      if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token);
      _refreshing = false;
      _onRefreshed(access_token);
      originalRequest.headers.Authorization = `Bearer ${access_token}`;
      return api(originalRequest);
    } catch {
      _refreshing = false;
      _onRefreshFailed();
      return Promise.reject(error);
    }
  },
);
