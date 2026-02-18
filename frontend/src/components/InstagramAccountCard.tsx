import type { InstagramAccount } from '../types/instagram';

interface Props {
  account: InstagramAccount;
  onReconnect: (account: InstagramAccount) => void;
  onDisconnect: (account: InstagramAccount) => void;
}

const statusConfig = {
  active: {
    label: 'Connected',
    className: 'bg-green-100 text-green-800 border border-green-200',
  },
  expired: {
    label: 'Token Expired',
    className: 'bg-yellow-100 text-yellow-800 border border-yellow-200',
  },
  revoked: {
    label: 'Permission Revoked',
    className: 'bg-red-100 text-red-800 border border-red-200',
  },
};

export default function InstagramAccountCard({ account, onReconnect, onDisconnect }: Props) {
  const status = statusConfig[account.status];

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6 flex items-center gap-4">
      {/* Profile picture */}
      {account.profile_picture ? (
        <img
          src={account.profile_picture}
          alt={account.username}
          className="w-14 h-14 rounded-full object-cover flex-shrink-0 border border-gray-100"
        />
      ) : (
        <div className="w-14 h-14 rounded-full bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center flex-shrink-0 text-white font-bold text-xl">
          {account.username[0]?.toUpperCase() ?? '?'}
        </div>
      )}

      {/* Account info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <h3 className="font-semibold text-gray-900 truncate">@{account.username}</h3>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium status-badge ${status.className}`}>
            {status.label}
          </span>
        </div>
        <div className="flex items-center gap-3 mt-1 text-sm text-gray-500">
          {account.account_type && (
            <span>{account.account_type}</span>
          )}
          {account.follower_count !== null && account.follower_count !== undefined && (
            <span>{account.follower_count.toLocaleString()} followers</span>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 flex-shrink-0">
        {account.status === 'expired' && (
          <button
            onClick={() => onReconnect(account)}
            className="px-3 py-1.5 text-sm font-medium text-yellow-700 bg-yellow-50 border border-yellow-200 rounded-lg hover:bg-yellow-100 transition-colors"
          >
            Reconnect
          </button>
        )}
        <button
          onClick={() => onDisconnect(account)}
          className="px-3 py-1.5 text-sm font-medium text-red-600 bg-white border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
        >
          Disconnect
        </button>
      </div>
    </div>
  );
}
