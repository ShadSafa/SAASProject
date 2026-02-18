import { create } from 'zustand';
import type { InstagramAccount } from '../types/instagram';

interface AccountsState {
  accounts: InstagramAccount[];
  isLoading: boolean;
  error: string | null;
  setAccounts: (accounts: InstagramAccount[]) => void;
  removeAccount: (accountId: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAccountsStore = create<AccountsState>((set) => ({
  accounts: [],
  isLoading: false,
  error: null,
  setAccounts: (accounts) => set({ accounts, error: null }),
  removeAccount: (accountId) => set((state) => ({
    accounts: state.accounts.filter((a) => a.id !== accountId),
  })),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error, isLoading: false }),
}));
