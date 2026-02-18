import { api } from '../utils/api';
import type { InstagramAccount } from '../types/instagram';

export async function getInstagramAccounts(): Promise<InstagramAccount[]> {
  const response = await api.get<InstagramAccount[]>('/integrations/instagram/accounts');
  return response.data;
}

export async function deleteInstagramAccount(accountId: number): Promise<void> {
  await api.delete(`/integrations/instagram/accounts/${accountId}`);
}

export function getInstagramAuthorizeUrl(): string {
  // Full-page redirect to backend OAuth endpoint (per CONTEXT.md decision)
  const baseUrl = import.meta.env.VITE_API_URL || '';
  return `${baseUrl}/integrations/instagram/authorize`;
}
