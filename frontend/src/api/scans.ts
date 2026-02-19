import { api } from '../utils/api';
import type {
  ScanTriggerResponse,
  ScanResponse,
  ScanHistoryItem,
  TimeRange,
} from '../types/scan';

export async function triggerScan(timeRange: TimeRange): Promise<ScanTriggerResponse> {
  const response = await api.post<ScanTriggerResponse>('/scans/trigger', {
    time_range: timeRange,
  });
  return response.data;
}

export async function analyzeUrl(instagramUrl: string): Promise<ScanTriggerResponse> {
  const response = await api.post<ScanTriggerResponse>('/scans/analyze-url', {
    instagram_url: instagramUrl,
  });
  return response.data;
}

export async function getScanStatus(scanId: number): Promise<ScanResponse> {
  const response = await api.get<ScanResponse>(`/scans/status/${scanId}`);
  return response.data;
}

export async function getScanHistory(): Promise<ScanHistoryItem[]> {
  const response = await api.get<ScanHistoryItem[]>('/scans/history');
  return response.data;
}
