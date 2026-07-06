import { api } from "./client";

export const goalsApi = {
  create: (data) => api.post("/goals", data),
  update: (goalId, data) => api.put(`/goals/${goalId}`, data),
  delete: (goalId) => api.delete(`/goals/${goalId}`),
  getAll: (status) => api.get("/goals", { params: { status } }),
  getById: (goalId) => api.get(`/goals/${goalId}`),
  analyze: (data) => api.post("/goals/analyze", data),
  recalculate: () => api.post("/goals/recalculate"),
  getRecommendations: () => api.get("/goals/recommendations"),
  getProgress: () => api.get("/goals/progress"),
};
