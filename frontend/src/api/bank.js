import { api } from "./client";

export const bankApi = {
  connect: (provider) => api.post("/bank/connect", { provider }),
  submitConsent: (payload) => api.post("/bank/consent", payload),
  getAccounts: () => api.get("/bank/accounts"),
  getStatus: () => api.get("/bank/status"),
  disconnect: (accountId) => api.delete(`/bank/disconnect/${accountId}`),
};
