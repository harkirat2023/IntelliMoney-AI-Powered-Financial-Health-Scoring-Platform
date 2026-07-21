import { api } from "./client";

export const importPreferenceApi = {
  save: (payload) => api.post("/import-preference/", payload),
  get: (bankAccountId) => api.get("/import-preference/", { params: { bank_account_id: bankAccountId } }),
};
