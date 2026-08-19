import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useAuth as useClerkAuth, useUser as useClerkUser } from "@clerk/clerk-react";

import { CLERK_PUBLISHABLE_KEY } from "../config";
import { api } from "../api/client";

const AuthContext = createContext(null);

function UnconfiguredProvider({ children }) {
  const value = useMemo(
    () => ({
      user: null,
      loading: false,
      clerkLoaded: false,
      isSignedIn: false,
      clerkConfigured: false,
      authError: null,
      logout: async () => {},
      refreshUser: async () => null,
      getToken: async () => null,
    }),
    [],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

function ClerkAuthProvider({ children }) {
  const { isLoaded: clerkLoaded, isSignedIn, getToken, signOut } = useClerkAuth();
  const { user: clerkUser } = useClerkUser();
  const [user, setUser] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [authError, setAuthError] = useState(null);

  const clerkUserId = clerkUser?.id;
  const clerkName = clerkUser?.fullName || clerkUser?.firstName || "";
  const clerkEmail = clerkUser?.primaryEmailAddress?.emailAddress || "";
  const clerkIncome = clerkUser?.unsafeMetadata?.monthly_income || null;

  const syncUser = useCallback(async () => {
    if (!isSignedIn || !clerkUserId) {
      setUser(null);
      return null;
    }
    try {
      const res = await api.post("/auth/clerk-sync", {
        name: clerkName,
        email: clerkEmail,
        monthly_income: clerkIncome,
      });
      setAuthError(null);
      setUser(res.data);
      return res.data;
    } catch (err) {
      setAuthError(err?.response?.data?.detail || "Account sync failed. Please try again.");
      setUser(null);
      return null;
    }
  }, [isSignedIn, clerkUserId, clerkName, clerkEmail, clerkIncome]);

  useEffect(() => {
    if (!clerkLoaded) return;
    if (isSignedIn) {
      setSyncing(true);
      syncUser().finally(() => setSyncing(false));
    } else {
      setUser(null);
      setAuthError(null);
      setSyncing(false);
    }
  }, [clerkLoaded, isSignedIn, syncUser]);

  const refreshUser = useCallback(() => syncUser(), [syncUser]);

  const logout = useCallback(() => signOut(), [signOut]);

  const loading = !clerkLoaded || syncing;

  const value = useMemo(
    () => ({
      user,
      loading,
      clerkLoaded,
      isSignedIn,
      clerkConfigured: true,
      authError,
      logout,
      refreshUser,
      getToken,
    }),
    [user, loading, clerkLoaded, isSignedIn, authError, logout, refreshUser, getToken],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function AuthProvider({ children }) {
  if (!CLERK_PUBLISHABLE_KEY) {
    return <UnconfiguredProvider>{children}</UnconfiguredProvider>;
  }
  return <ClerkAuthProvider>{children}</ClerkAuthProvider>;
}

export function useAuth() {
  return useContext(AuthContext);
}