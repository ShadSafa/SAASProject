import { useEffect, useCallback } from 'react';
import { useAccountsStore } from '../store/accountsStore';
import { getInstagramAccounts, deleteInstagramAccount } from '../api/instagram';

export function useInstagramAccounts() {
  const { accounts, isLoading, error, setAccounts, removeAccount, setLoading, setError } =
    useAccountsStore();

  const fetchAccounts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getInstagramAccounts();
      setAccounts(data);
    } catch (err) {
      setError('Failed to load Instagram accounts');
    } finally {
      setLoading(false);
    }
  }, [setAccounts, setError, setLoading]);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  const disconnect = useCallback(async (accountId: number) => {
    try {
      await deleteInstagramAccount(accountId);
      removeAccount(accountId);
      return true;
    } catch {
      setError('Failed to disconnect account');
      return false;
    }
  }, [removeAccount, setError]);

  return { accounts, isLoading, error, fetchAccounts, disconnect };
}
