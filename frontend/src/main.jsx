import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, useNavigate } from "react-router-dom";
import { ClerkProvider } from "@clerk/clerk-react";

import App from "./App";
import { AuthProvider } from "./auth/AuthContext";
import { CLERK_PUBLISHABLE_KEY } from "./config";
import "./styles.css";
import "./landing/index.css";
import "./styles/cyber-theme.css";

const toPath = (to) => {
  if (typeof to === "string" && /^https?:\/\//.test(to)) {
    try {
      const url = new URL(to);
      return url.pathname + url.search + url.hash;
    } catch {
      return to;
    }
  }
  return to;
};

function ClerkProviderWithRouter({ children }) {
  const navigate = useNavigate();
  return (
    <ClerkProvider
      publishableKey={CLERK_PUBLISHABLE_KEY}
      routerPush={(to) => navigate(toPath(to))}
      routerReplace={(to) => navigate(toPath(to), { replace: true })}
    >
      {children}
    </ClerkProvider>
  );
}

function Root() {
  if (!CLERK_PUBLISHABLE_KEY) {
    return (
      <AuthProvider>
        <App />
      </AuthProvider>
    );
  }
  return (
    <ClerkProviderWithRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </ClerkProviderWithRouter>
  );
}

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Root />
    </BrowserRouter>
  </React.StrictMode>
);