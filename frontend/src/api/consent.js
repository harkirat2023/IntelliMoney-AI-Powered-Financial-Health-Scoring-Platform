import { api } from "./client";

export const consentApi = {
  grant: (payload) => api.post("/consent/grant", payload),
  revoke: (payload) => api.post("/consent/revoke", payload),
  status: (bankAccountId) => api.get("/consent/status", { params: { bank_account_id: bankAccountId } }),
};
