
import axios from "axios";

const API_BASE_URL = process.env.API_BASE_URL || "http://localhost:8080/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("intellimoney_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
