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
      isSignedIn: false,
      clerkConfigured: false,
      logout: async () => {},
      completeOnboarding: async () => null,
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

  const syncUser = useCallback(async () => {
    if (!isSignedIn || !clerkUser) {
      setUser(null);
      return null;
    }
    try {
      const res = await api.post("/auth/clerk-sync", {
        name: clerkUser.fullName || clerkUser.firstName || "",
        email: clerkUser.primaryEmailAddress?.emailAddress || "",
        monthly_income: clerkUser.unsafeMetadata?.monthly_income || null,
      });
      setUser(res.data);
      return res.data;
    } catch (err) {
      setUser(null);
      return null;
    }
  }, [isSignedIn, clerkUser]);

  useEffect(() => {
    if (!clerkLoaded) return;
    if (isSignedIn) {
      setSyncing(true);
      syncUser().finally(() => setSyncing(false));
    } else {
      setUser(null);
      setSyncing(false);
    }
  }, [clerkLoaded, isSignedIn, syncUser]);

  const completeOnboarding = useCallback(async () => {
    const res = await api.post("/auth/onboarding/complete");
    setUser(res.data);
    return res.data;
  }, []);

  const refreshUser = useCallback(() => syncUser(), [syncUser]);

  const logout = useCallback(() => signOut(), [signOut]);

  const loading = !clerkLoaded || syncing;

  const value = useMemo(
    () => ({
      user,
      loading,
      isSignedIn,
      clerkConfigured: true,
      logout,
      completeOnboarding,
      refreshUser,
      getToken,
    }),
    [user, loading, isSignedIn, logout, completeOnboarding, refreshUser, getToken],
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