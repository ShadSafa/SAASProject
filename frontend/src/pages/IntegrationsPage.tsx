import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useInstagramAccounts } from '../hooks/useInstagramAccounts';
import { getInstagramAuthorizeUrl } from '../api/instagram';
import InstagramAccountCard from '../components/InstagramAccountCard';
import DisconnectConfirmDialog from '../components/DisconnectConfirmDialog';
import type { InstagramAccount } from '../types/instagram';

export default function IntegrationsPage() {
  const [searchParams] = useSearchParams();
  const { accounts, isLoading, error, disconnect } = useInstagramAccounts();
  const [accountToDisconnect, setAccountToDisconnect] = useState<InstagramAccount | null>(null);
  const [disconnecting, setDisconnecting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Handle post-OAuth redirect messages
  useEffect(() => {
    const connected = searchParams.get('connected');
    const oauthError = searchParams.get('error');

    if (connected === 'true') {
      setSuccessMessage('Instagram account connected successfully!');
    } else if (oauthError) {
      const errorMessages: Record<string, string> = {
        denied: 'Instagram authorization was cancelled.',
        invalid_state: 'Authorization failed. Please try again.',
        token_exchange: 'Failed to complete authorization. Please try again.',
        profile_fetch: 'Failed to fetch Instagram profile. Please try again.',
        already_connected: 'This Instagram account is already connected to another user.',
        account_limit: 'You have reached the maximum number of connected accounts for your plan.',
      };
      setErrorMessage(errorMessages[oauthError] ?? 'Authorization failed. Please try again.');
    }
  }, [searchParams]);

  const handleConnect = () => {
    window.location.href = getInstagramAuthorizeUrl();
  };

  const handleReconnect = (_account: InstagramAccount) => {
    // Reconnect uses same OAuth flow (per CONTEXT.md decision)
    window.location.href = getInstagramAuthorizeUrl();
  };

  const handleDisconnectConfirm = async () => {
    if (!accountToDisconnect) return;
    setDisconnecting(true);
    const success = await disconnect(accountToDisconnect.id);
    setDisconnecting(false);
    if (success) {
      setAccountToDisconnect(null);
      setSuccessMessage(`@${accountToDisconnect.username} has been disconnected.`);
    }
  };

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Connected Accounts</h1>
          <p className="text-gray-600 mt-1">Manage your Instagram account connections</p>
        </div>
      </div>

      {/* Success/error alerts */}
      {successMessage && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center justify-between">
          <p className="text-green-800 text-sm">{successMessage}</p>
          <button onClick={() => setSuccessMessage(null)} className="text-green-600 hover:text-green-800 ml-4">&#x2715;</button>
        </div>
      )}
      {(errorMessage || error) && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between">
          <p className="text-red-800 text-sm">{errorMessage ?? error}</p>
          <button onClick={() => { setErrorMessage(null); }} className="text-red-600 hover:text-red-800 ml-4">&#x2715;</button>
        </div>
      )}

      {/* Account list or empty state */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : accounts.length === 0 ? (
        /* Empty state (CONTEXT.md: illustration + prominent CTA) */
        <div className="border-2 border-dashed border-gray-200 rounded-xl p-12 text-center">
          <div className="max-w-sm mx-auto">
            <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-purple-400 via-pink-500 to-orange-400 rounded-2xl flex items-center justify-center">
              <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No accounts connected</h2>
            <p className="text-gray-500 text-sm mb-8">Connect your Instagram account to start analyzing viral content and discovering what makes posts perform.</p>
            <button
              onClick={handleConnect}
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-lg shadow-sm text-white bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-all"
            >
              Connect Instagram Account
            </button>
          </div>
        </div>
      ) : (
        /* Account list (card layout) */
        <div>
          <div className="space-y-3">
            {accounts.map((account) => (
              <InstagramAccountCard
                key={account.id}
                account={account}
                onReconnect={handleReconnect}
                onDisconnect={setAccountToDisconnect}
              />
            ))}
          </div>
          {/* "Add another account" at bottom */}
          <div className="mt-6">
            <button
              onClick={handleConnect}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
            >
              + Add Another Account
            </button>
          </div>
        </div>
      )}

      {/* Disconnect confirmation dialog */}
      <DisconnectConfirmDialog
        account={accountToDisconnect}
        isOpen={!!accountToDisconnect}
        isLoading={disconnecting}
        onConfirm={handleDisconnectConfirm}
        onCancel={() => setAccountToDisconnect(null)}
      />
    </div>
  );
}
