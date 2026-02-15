import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, AuthState, AuthActions } from '../types/auth';

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      // Initial state
      user: null,
      isLoading: false,
      error: null,
      isAuthenticated: false,

      // Actions
      setUser: (user) => set({
        user,
        isAuthenticated: !!user,
        error: null
      }),

      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error, isLoading: false }),

      clearAuth: () => set({
        user: null,
        isAuthenticated: false,
        error: null
      }),
    }),
    {
      name: 'auth-storage',  // localStorage key
      partialize: (state) => ({
        user: state.user,  // Only persist user, not loading/error states
        isAuthenticated: state.isAuthenticated
      }),
    }
  )
);

// Selectors for common use cases
export const selectUser = (state: AuthStore) => state.user;
export const selectIsAuthenticated = (state: AuthStore) => state.isAuthenticated;
export const selectIsLoading = (state: AuthStore) => state.isLoading;
export const selectError = (state: AuthStore) => state.error;
