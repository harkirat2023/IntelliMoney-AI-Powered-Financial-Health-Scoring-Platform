import { api } from "./client";

export const aaApi = {
  status: () => api.get("/aa/status"),
  createConsent: (provider = "setu") => api.post("/aa/consents", { provider }),
  listConsents: () => api.get("/aa/consents"),
  getConsent: (consentId) => api.get(`/aa/consents/${consentId}`),
  approve: (consentId) => api.post(`/aa/consents/${consentId}/approve`),
  reject: (consentId) => api.post(`/aa/consents/${consentId}/reject`),
  createDataSession: (consentId) => api.post("/aa/data-sessions", { consent_id: consentId }),
  listDataSessions: () => api.get("/aa/data-sessions"),
  fetchDataSession: (sessionId) => api.post(`/aa/data-sessions/${sessionId}/fetch`),
};