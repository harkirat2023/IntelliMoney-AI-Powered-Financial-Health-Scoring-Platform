import { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";

import { api } from "../api/client";

const TOKEN_KEY = "intellimoney_token";
const REFRESH_KEY = "intellimoney_refresh";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const refreshingRef = useRef(false);

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get("/auth/me")
      .then((response) => setUser(response.data))
      .catch(() => { clearAuth(); })
      .finally(() => setLoading(false));
  }, []);

  function clearAuth() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    setUser(null);
  }

  function storeAuth(accessToken, refreshToken, userData) {
    localStorage.setItem(TOKEN_KEY, accessToken);
    if (refreshToken) localStorage.setItem(REFRESH_KEY, refreshToken);
    setUser(userData);
  }

  async function refreshToken() {
    const storedRefresh = localStorage.getItem(REFRESH_KEY);
    if (!storedRefresh) {
      clearAuth();
      return null;
    }
    try {
      const res = await api.post("/auth/refresh", { refresh_token: storedRefresh });
      const { access_token, refresh_token, user: userData } = res.data;
      localStorage.setItem(TOKEN_KEY, access_token);
      if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token);
      setUser(userData);
      return access_token;
    } catch {
      clearAuth();
      return null;
    }
  }

  async function login(email, password) {
    const response = await api.post("/auth/login", { email, password });
    storeAuth(response.data.access_token, response.data.refresh_token, response.data.user);
  }

  async function register(payload) {
    const response = await api.post("/auth/register", payload);
    storeAuth(response.data.access_token, response.data.refresh_token, response.data.user);
  }

  function logout() {
    clearAuth();
  }

  const value = useMemo(
    () => ({ user, loading, login, register, logout, refreshToken, refreshingRef }),
    [user, loading, refreshToken],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
