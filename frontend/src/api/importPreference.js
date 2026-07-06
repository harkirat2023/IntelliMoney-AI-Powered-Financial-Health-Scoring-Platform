import { api } from "./client";

export const importPreferenceApi = {
  save: (payload) => api.post("/api/v1/import-preference/", payload),
  get: (bankAccountId) => api.get("/api/v1/import-preference/", { params: { bank_account_id: bankAccountId } }),
};
