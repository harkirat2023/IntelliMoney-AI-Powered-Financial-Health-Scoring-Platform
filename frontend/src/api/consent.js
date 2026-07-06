import { api } from "./client";

export const consentApi = {
  grant: (payload) => api.post("/api/v1/consent/grant", payload),
  revoke: (payload) => api.post("/api/v1/consent/revoke", payload),
  status: (bankAccountId) => api.get("/api/v1/consent/status", { params: { bank_account_id: bankAccountId } }),
};
