import { create } from 'zustand';
import type { ScanResponse, ViralPost, ScanStatus } from '../types/scan';

interface ScanState {
  currentScanId: number | null;
  currentStatus: ScanStatus | 'idle';
  scanResults: ViralPost[];
  isScanning: boolean;
  error: string | null;
  lastScan: ScanResponse | null;

  // Actions
  setScanId: (id: number) => void;
  setStatus: (status: ScanStatus) => void;
  setScanResults: (results: ViralPost[]) => void;
  setIsScanning: (scanning: boolean) => void;
  setError: (error: string | null) => void;
  setLastScan: (scan: ScanResponse) => void;
  clearScan: () => void;
}

export const useScanStore = create<ScanState>((set) => ({
  currentScanId: null,
  currentStatus: 'idle',
  scanResults: [],
  isScanning: false,
  error: null,
  lastScan: null,

  setScanId: (id) => set({ currentScanId: id }),
  setStatus: (status) => set({ currentStatus: status }),
  setScanResults: (results) => set({ scanResults: results }),
  setIsScanning: (scanning) => set({ isScanning: scanning }),
  setError: (error) => set({ error }),
  setLastScan: (scan) => set({ lastScan: scan }),
  clearScan: () =>
    set({
      currentScanId: null,
      currentStatus: 'idle',
      scanResults: [],
      isScanning: false,
      error: null,
      lastScan: null,
    }),
}));
