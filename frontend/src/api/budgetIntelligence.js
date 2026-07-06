import { api } from "./client";

export const budgetIntelligenceApi = {
  generate: () => api.post("/budget-intelligence/generate"),
  recalculate: () => api.post("/budget-intelligence/recalculate"),
  getCurrent: () => api.get("/budget-intelligence/current"),
  getRecommendations: () => api.get("/budget-intelligence/recommendations"),
  getOptimization: () => api.get("/budget-intelligence/optimization"),
  getTrends: () => api.get("/budget-intelligence/trends"),
  getRisk: () => api.get("/budget-intelligence/risk"),
  getOpportunities: () => api.get("/budget-intelligence/opportunities"),
};
