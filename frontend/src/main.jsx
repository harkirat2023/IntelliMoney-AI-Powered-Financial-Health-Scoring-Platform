import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { ClerkProvider } from "@clerk/clerk-react";

import App from "./App";
import { AuthProvider } from "./auth/AuthContext";
import { CLERK_PUBLISHABLE_KEY } from "./config";
import "./styles.css";
import "./landing/index.css";
import "./styles/cyber-theme.css";

function Root() {
  if (!CLERK_PUBLISHABLE_KEY) {
    return (
      <AuthProvider>
        <App />
      </AuthProvider>
    );
  }
  return (
    <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </ClerkProvider>
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Root />
    </BrowserRouter>
  </React.StrictMode>
);