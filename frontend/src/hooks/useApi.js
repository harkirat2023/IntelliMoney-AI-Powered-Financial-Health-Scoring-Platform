import { useCallback, useEffect, useState } from "react";

export function useApi(fetcher, immediate = true) {
  const [state, setState] = useState({
    data: null,
    loading: immediate,
    error: null,
  });

  const execute = useCallback(async () => {
    setState({ data: null, loading: true, error: null });
    try {
      const result = await fetcher();
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (err) {
      const message = err?.response?.data?.detail || err?.message || "Request failed";
      setState({ data: null, loading: false, error: message });
      throw err;
    }
  }, [fetcher]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return { ...state, refetch: execute };
}
