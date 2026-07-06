import { api } from "./client";

export const syncApi = {
  start: (bankAccountId) => api.post("/sync/start", { bank_account_id: bankAccountId }),
  manual: () => api.post("/sync/manual"),
  status: (bankAccountId) =>
    api.get("/sync/status", {
      params: bankAccountId ? { bank_account_id: bankAccountId } : {},
    }),
  history: (params) => api.get("/sync/history", { params }),
  retry: (syncLogId) => api.post("/sync/retry", { sync_log_id: syncLogId }),
};
