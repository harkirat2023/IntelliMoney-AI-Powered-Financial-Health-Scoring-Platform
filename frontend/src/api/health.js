import { api } from "./client";

export const healthApi = {
  calculate: () => api.post("/health/calculate"),
  recalculate: () => api.post("/health/recalculate"),
  getCurrent: () => api.get("/health/current"),
  getHistory: (limit) => api.get("/health/history", { params: { limit } }),
  getTrends: (months) => api.get("/health/trends", { params: { months } }),
  getBreakdown: () => api.get("/health/breakdown"),
  getRecommendations: () => api.get("/health/recommendations"),
  getRisk: () => api.get("/health/risk"),
};
