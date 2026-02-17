import { api } from '../utils/api';
import type { User, LoginCredentials, SignupCredentials } from '../types/auth';

export const authApi = {
  signup: async (credentials: SignupCredentials) => {
    const response = await api.post('/auth/signup', credentials);
    return response.data;
  },

  login: async (credentials: LoginCredentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },

  verifyEmail: async (token: string) => {
    const response = await api.post('/auth/verify-email', { token });
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  resendVerification: async (email: string) => {
    const response = await api.post('/auth/resend-verification', { email });
    return response.data;
  },

  requestPasswordReset: async (email: string) => {
    const response = await api.post('/auth/request-password-reset', { email });
    return response.data;
  },

  resetPassword: async (token: string, newPassword: string) => {
    const response = await api.post('/auth/reset-password', {
      token,
      new_password: newPassword,
    });
    return response.data;
  },

  getProfile: async (): Promise<User> => {
    const response = await api.get('/profile');
    return response.data;
  },

  updateProfile: async (data: { email?: string; currentPassword?: string; newPassword?: string }): Promise<User> => {
    const response = await api.put('/profile', {
      email: data.email,
      current_password: data.currentPassword,
      new_password: data.newPassword,
    });
    return response.data;
  },

  deleteAccount: async () => {
    const response = await api.delete('/profile/account');
    return response.data;
  },
};
