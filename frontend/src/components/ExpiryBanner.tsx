import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { InstagramAccount } from '../types/instagram';

interface Props {
  expiredAccounts: InstagramAccount[];
}

export default function ExpiryBanner({ expiredAccounts }: Props) {
  const [dismissed, setDismissed] = useState(false);
  const navigate = useNavigate();

  if (dismissed || expiredAccounts.length === 0) return null;

  const firstAccount = expiredAccounts[0];
  const isRevoked = firstAccount.status === 'revoked';
  const otherCount = expiredAccounts.length - 1;

  return (
    <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-3">
      {/* Warning icon */}
      <div className="flex-shrink-0 mt-0.5">
        <svg className="w-5 h-5 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>

      {/* Message */}
      <div className="flex-1 min-w-0">
        <p className="text-sm text-yellow-800">
          {isRevoked ? (
            <>Your Instagram account <strong>@{firstAccount.username}</strong> permission was revoked.</>
          ) : (
            <>Your Instagram account <strong>@{firstAccount.username}</strong> connection has expired.</>
          )}
          {otherCount > 0 && (
            <> And {otherCount} other {otherCount === 1 ? 'account' : 'accounts'}.</>
          )}
          {' '}
          <button
            onClick={() => navigate('/settings/integrations')}
            className="font-semibold underline text-yellow-900 hover:text-yellow-700 transition-colors"
          >
            Fix now
          </button>
        </p>
      </div>

      {/* Dismiss */}
      <button
        onClick={() => setDismissed(true)}
        className="flex-shrink-0 text-yellow-600 hover:text-yellow-800 transition-colors"
        aria-label="Dismiss"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}
