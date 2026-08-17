import axios from "axios";

import { API_BASE_URL } from "../config";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

async function getClerkToken() {
  try {
    const clerk = window.Clerk;
    if (clerk?.session) {
      return await clerk.session.getToken();
    }
  } catch (err) {
    // Clerk not configured or session unavailable; requests will be unauthenticated.
  }
  return null;
}

api.interceptors.request.use(async (config) => {
  const token = await getClerkToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && window.Clerk?.session) {
      window.Clerk.session.touch().catch(() => {});
    }
    return Promise.reject(error);
  },
);