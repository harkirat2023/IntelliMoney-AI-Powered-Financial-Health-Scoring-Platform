import { api } from "./client";

export const copilotApi = {
  chat: (data) => api.post("/copilot/chat", data),
  getSessions: () => api.get("/copilot/sessions"),
  getSessionHistory: (sessionId) => api.get(`/copilot/sessions/${sessionId}`),
  deleteAllSessions: () => api.delete("/copilot/sessions"),
  submitFeedback: (data) => api.post("/copilot/feedback", data),
  getSuggestions: () => api.get("/copilot/suggestions"),
  getSettings: () => api.get("/copilot/settings"),
};
