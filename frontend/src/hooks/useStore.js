import { useEffect, useSyncExternalStore } from "react";

export function useStore(store) {
  const state = useSyncExternalStore(store.subscribe, store.getState);
  return state;
}

export function createStoreHook(store, fetchFn) {
  return function useStoreWithFetch() {
    const state = useStore(store);
    useEffect(() => {
      if (fetchFn && !state.loading && !state.error) {
        const needsFetch = !state.summary && !store.getState().loading;
        if (needsFetch) {
          fetchFn();
        }
      }
    }, []);
    return state;
  };
}
