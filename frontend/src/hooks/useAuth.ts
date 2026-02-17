import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/auth';
import { useAuthStore } from '../store/authStore';
import type { LoginCredentials, SignupCredentials } from '../types/auth';

export const useAuth = () => {
  const navigate = useNavigate();
  const { user, setUser, setLoading, setError, clearAuth } = useAuthStore();

  const signup = useCallback(async (credentials: SignupCredentials) => {
    setLoading(true);
    setError(null);
    try {
      await authApi.signup(credentials);
      // Don't log in yet - redirect to verification pending page
      navigate('/verify-email-pending', { state: { email: credentials.email } });
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Signup failed';
      setError(message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [navigate, setLoading, setError]);

  const login = useCallback(async (credentials: LoginCredentials) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authApi.login(credentials);
      setUser(response.user);
      navigate('/dashboard');
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed';
      setError(message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [navigate, setLoading, setError, setUser]);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
      clearAuth();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
      // Clear local state anyway
      clearAuth();
      navigate('/login');
    }
  }, [clearAuth, navigate]);

  const verifyEmail = useCallback(async (token: string) => {
    setLoading(true);
    setError(null);
    try {
      await authApi.verifyEmail(token);
      return true;
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Verification failed';
      setError(message);
      return false;
    } finally {
      setLoading(false);
    }
  }, [setLoading, setError]);

  const requestPasswordReset = useCallback(async (email: string) => {
    setLoading(true);
    setError(null);
    try {
      await authApi.requestPasswordReset(email);
      return true;
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Request failed';
      setError(message);
      return false;
    } finally {
      setLoading(false);
    }
  }, [setLoading, setError]);

  const resetPassword = useCallback(async (token: string, newPassword: string) => {
    setLoading(true);
    setError(null);
    try {
      await authApi.resetPassword(token, newPassword);
      return true;
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Password reset failed';
      setError(message);
      return false;
    } finally {
      setLoading(false);
    }
  }, [setLoading, setError]);

  return {
    user,
    signup,
    login,
    logout,
    verifyEmail,
    requestPasswordReset,
    resetPassword,
  };
};
