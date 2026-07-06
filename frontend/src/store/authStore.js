import { api } from "../api/client";

let storeSubscribers = [];
let state = {
  user: null,
  loading: true,
};

export const authStore = {
  subscribe(fn) {
    storeSubscribers.push(fn);
    fn(state);
    return () => {
      storeSubscribers = storeSubscribers.filter((s) => s !== fn);
    };
  },
  getState() {
    return state;
  },
  setLoading(loading) {
    state = { ...state, loading };
    storeSubscribers.forEach((fn) => fn(state));
  },
  setUser(user) {
    state = { ...state, user, loading: false };
    storeSubscribers.forEach((fn) => fn(state));
  },
  async login(email, password) {
    const response = await api.post("/auth/login", { email, password });
    localStorage.setItem("intellimoney_token", response.data.access_token);
    this.setUser(response.data.user);
  },
  async register(payload) {
    const response = await api.post("/auth/register", payload);
    localStorage.setItem("intellimoney_token", response.data.access_token);
    this.setUser(response.data.user);
  },
  logout() {
    localStorage.removeItem("intellimoney_token");
    this.setUser(null);
  },
  async validateToken() {
    const token = localStorage.getItem("intellimoney_token");
    if (!token) {
      this.setLoading(false);
      return;
    }
    try {
      const response = await api.get("/auth/me");
      this.setUser(response.data);
    } catch {
      localStorage.removeItem("intellimoney_token");
      this.setLoading(false);
    }
  },
};
