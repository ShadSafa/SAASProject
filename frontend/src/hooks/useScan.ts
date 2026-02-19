import { useEffect, useRef, useCallback } from 'react';
import { useScanStore } from '../store/scanStore';
import { triggerScan, analyzeUrl, getScanStatus } from '../api/scans';
import type { TimeRange } from '../types/scan';

const POLL_INTERVAL_MS = 2000;  // Poll every 2 seconds
const POLL_TIMEOUT_MS = 5 * 60 * 1000;  // Stop polling after 5 minutes

export function useScan() {
  const {
    currentScanId,
    currentStatus,
    scanResults,
    isScanning,
    error,
    lastScan,
    setScanId,
    setStatus,
    setScanResults,
    setIsScanning,
    setError,
    setLastScan,
    clearScan,
  } = useScanStore();

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const pollStartTimeRef = useRef<number | null>(null);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    pollStartTimeRef.current = null;
  }, []);

  const startPolling = useCallback((scanId: number) => {
    stopPolling();
    pollStartTimeRef.current = Date.now();

    intervalRef.current = setInterval(async () => {
      // Timeout guard
      if (pollStartTimeRef.current && Date.now() - pollStartTimeRef.current > POLL_TIMEOUT_MS) {
        stopPolling();
        setStatus('failed');
        setError('Scan timed out after 5 minutes. Please try again.');
        setIsScanning(false);
        return;
      }

      try {
        const data = await getScanStatus(scanId);
        setStatus(data.status);
        setLastScan(data);

        if (data.status === 'completed') {
          setScanResults(data.results);
          setIsScanning(false);
          stopPolling();
        } else if (data.status === 'failed') {
          setError(data.error_message || 'Scan failed. Please try again.');
          setIsScanning(false);
          stopPolling();
        }
      } catch (err) {
        // Network error during polling — don't stop, retry next interval
        console.warn('Polling error (will retry):', err);
      }
    }, POLL_INTERVAL_MS);
  }, [stopPolling, setStatus, setScanResults, setIsScanning, setError, setLastScan]);

  // Cleanup on unmount
  useEffect(() => {
    return () => stopPolling();
  }, [stopPolling]);

  const startScan = useCallback(async (timeRange: TimeRange) => {
    clearScan();
    setIsScanning(true);
    setError(null);

    try {
      const response = await triggerScan(timeRange);
      setScanId(response.scan_id);
      setStatus(response.status as 'pending');
      startPolling(response.scan_id);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Failed to start scan. Please try again.';
      setError(message);
      setIsScanning(false);
    }
  }, [clearScan, setIsScanning, setError, setScanId, setStatus, startPolling]);

  const startUrlScan = useCallback(async (instagramUrl: string) => {
    clearScan();
    setIsScanning(true);
    setError(null);

    try {
      const response = await analyzeUrl(instagramUrl);
      setScanId(response.scan_id);
      setStatus(response.status as 'pending');
      startPolling(response.scan_id);
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Failed to analyze URL. Please check the URL and try again.';
      setError(message);
      setIsScanning(false);
    }
  }, [clearScan, setIsScanning, setError, setScanId, setStatus, startPolling]);

  return {
    // State
    scanId: currentScanId,
    status: currentStatus,
    scanResults,
    isScanning,
    error,
    lastScan,

    // Actions
    startScan,
    startUrlScan,
    clearResults: clearScan,
  };
}
