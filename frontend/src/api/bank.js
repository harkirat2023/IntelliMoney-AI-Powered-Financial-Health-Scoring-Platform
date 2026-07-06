import { api } from "./client";

export const bankApi = {
  connect: (provider) => api.post("/api/v1/bank/connect", { provider }),
  submitConsent: (payload) => api.post("/api/v1/bank/consent", payload),
  getAccounts: () => api.get("/api/v1/bank/accounts"),
  getStatus: () => api.get("/api/v1/bank/status"),
  disconnect: (accountId) => api.delete(`/api/v1/bank/disconnect/${accountId}`),
};
