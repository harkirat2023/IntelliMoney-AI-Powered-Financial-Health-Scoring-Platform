import { api } from "./client";

export const receiptsApi = {
  upload: (file) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/receipts/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  process: (receiptId) => api.post(`/receipts/${receiptId}/process`),
  confirm: (receiptId) => api.post(`/receipts/${receiptId}/confirm`),
  getAll: (status) => api.get("/receipts", { params: { status } }),
  getById: (receiptId) => api.get(`/receipts/${receiptId}`),
  update: (receiptId, data) => api.patch(`/receipts/${receiptId}`, data),
  delete: (receiptId) => api.delete(`/receipts/${receiptId}`),
  getImageUrl: (receiptId) => `/api/v1/receipts/${receiptId}/image`,
};
