import { NavLink, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useAuth } from '../hooks/useAuth';

interface AppLayoutProps {
  children: React.ReactNode;
  accountCount?: number;
}

export default function AppLayout({ children, accountCount = 0 }: AppLayoutProps) {
  const { user } = useAuthStore();
  const { logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Left: Brand */}
            <div className="flex items-center">
              <Link to="/dashboard" className="text-xl font-bold text-gray-900 hover:text-gray-700">
                Instagram Viral Analyzer
              </Link>
            </div>

            {/* Center: Navigation links */}
            <div className="flex items-center space-x-8">
              <NavLink
                to="/dashboard"
                className={({ isActive }) =>
                  `text-sm font-medium transition-colors ${
                    isActive ? 'text-blue-600 border-b-2 border-blue-600 pb-0.5' : 'text-gray-600 hover:text-gray-900'
                  }`
                }
              >
                Dashboard
              </NavLink>
              <NavLink
                to="/settings/integrations"
                className={({ isActive }) =>
                  `text-sm font-medium transition-colors ${
                    isActive ? 'text-blue-600 border-b-2 border-blue-600 pb-0.5' : 'text-gray-600 hover:text-gray-900'
                  }`
                }
              >
                Settings
              </NavLink>
            </div>

            {/* Right: User info + account count */}
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user?.email}</p>
                <p className="text-xs text-gray-500">
                  {accountCount} {accountCount === 1 ? 'account' : 'accounts'}
                </p>
              </div>
              <button
                onClick={() => logout()}
                className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
