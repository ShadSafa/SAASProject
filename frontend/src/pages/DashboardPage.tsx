import { useAuthStore } from '../store/authStore';
import { useAccountsStore } from '../store/accountsStore';
import ExpiryBanner from '../components/ExpiryBanner';
import ScanHistory from '../components/ScanHistory';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const accounts = useAccountsStore((state) => state.accounts);
  const expiredAccounts = accounts.filter(
    (a) => a.status === 'expired' || a.status === 'revoked'
  );

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Welcome back, {user?.email}</p>
      </div>

      <ExpiryBanner expiredAccounts={expiredAccounts} />

      {/* Show scan history regardless of account connection (dev mode allows scanning without accounts) */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <ScanHistory />
      </div>

      {accounts.length === 0 && (
        /* Empty state: no accounts connected */
        <div className="border-2 border-dashed border-gray-200 rounded-xl p-12 text-center">
          <div className="max-w-sm mx-auto">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">No Instagram account connected</h2>
            <p className="text-gray-500 text-sm mb-6">Connect your Instagram account to start discovering viral content patterns.</p>
            <a
              href="/settings/integrations"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Connect Instagram Account
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
