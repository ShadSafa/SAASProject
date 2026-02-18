import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../hooks/useAuth';
import { useAuthStore } from '../store/authStore';

const emailUpdateSchema = z.object({
  email: z.string().email('Invalid email address'),
});

const passwordUpdateSchema = z.object({
  currentPassword: z.string().min(1, 'Current password required'),
  newPassword: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain uppercase letter')
    .regex(/[0-9]/, 'Must contain number'),
  confirmPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
});

type EmailUpdateData = z.infer<typeof emailUpdateSchema>;
type PasswordUpdateData = z.infer<typeof passwordUpdateSchema>;

export default function ProfilePage() {
  const { user, updateProfile, deleteAccount } = useAuth();
  const { isLoading, error } = useAuthStore();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [updateSuccess, setUpdateSuccess] = useState<string | null>(null);

  const emailForm = useForm<EmailUpdateData>({
    resolver: zodResolver(emailUpdateSchema),
    defaultValues: { email: user?.email ?? '' },
  });

  const passwordForm = useForm<PasswordUpdateData>({
    resolver: zodResolver(passwordUpdateSchema),
  });

  const onEmailUpdate = async (data: EmailUpdateData) => {
    setUpdateSuccess(null);
    const success = await updateProfile({ email: data.email });
    if (success) {
      setUpdateSuccess('Email updated. Please verify your new email address.');
    }
  };

  const onPasswordUpdate = async (data: PasswordUpdateData) => {
    setUpdateSuccess(null);
    const success = await updateProfile({
      currentPassword: data.currentPassword,
      newPassword: data.newPassword,
    });
    if (success) {
      setUpdateSuccess('Password updated successfully.');
      passwordForm.reset();
    }
  };

  const handleDeleteAccount = async () => {
    await deleteAccount();
    // deleteAccount redirects to /login on success
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
      </div>

      <div className="max-w-4xl space-y-6">
        {/* Global success message */}
        {updateSuccess && (
          <div className="rounded-md bg-green-50 p-4">
            <p className="text-sm text-green-800">{updateSuccess}</p>
          </div>
        )}

        {/* Global error message */}
        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Account Info */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-2">Account Information</h2>
          <p className="text-sm text-gray-600">
            Member since:{' '}
            {user?.created_at
              ? new Date(user.created_at).toLocaleDateString()
              : '—'}
          </p>
          <p className="text-sm text-gray-600 mt-1">
            Email verified:{' '}
            <span
              className={
                user?.email_verified ? 'text-green-600 font-medium' : 'text-yellow-600 font-medium'
              }
            >
              {user?.email_verified ? 'Yes' : 'No'}
            </span>
          </p>
        </div>

        {/* Email Update Section */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Email Address</h2>
          <form onSubmit={emailForm.handleSubmit(onEmailUpdate)} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                {...emailForm.register('email')}
                id="email"
                type="email"
                autoComplete="email"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              {emailForm.formState.errors.email && (
                <p className="mt-1 text-sm text-red-600">
                  {emailForm.formState.errors.email.message}
                </p>
              )}
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Updating...' : 'Update Email'}
            </button>
          </form>
        </div>

        {/* Password Update Section */}
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Change Password</h2>
          <form onSubmit={passwordForm.handleSubmit(onPasswordUpdate)} className="space-y-4">
            <div>
              <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-700">
                Current Password
              </label>
              <input
                {...passwordForm.register('currentPassword')}
                id="currentPassword"
                type="password"
                autoComplete="current-password"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              {passwordForm.formState.errors.currentPassword && (
                <p className="mt-1 text-sm text-red-600">
                  {passwordForm.formState.errors.currentPassword.message}
                </p>
              )}
            </div>

            <div>
              <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700">
                New Password
              </label>
              <input
                {...passwordForm.register('newPassword')}
                id="newPassword"
                type="password"
                autoComplete="new-password"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              {passwordForm.formState.errors.newPassword && (
                <p className="mt-1 text-sm text-red-600">
                  {passwordForm.formState.errors.newPassword.message}
                </p>
              )}
              <p className="mt-1 text-xs text-gray-500">
                Min 8 characters, 1 uppercase letter, 1 number
              </p>
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                Confirm New Password
              </label>
              <input
                {...passwordForm.register('confirmPassword')}
                id="confirmPassword"
                type="password"
                autoComplete="new-password"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              {passwordForm.formState.errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">
                  {passwordForm.formState.errors.confirmPassword.message}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Updating...' : 'Update Password'}
            </button>
          </form>
        </div>

        {/* Account Deletion Section */}
        <div className="bg-white shadow rounded-lg p-6 border-2 border-red-200">
          <h2 className="text-xl font-semibold text-red-600 mb-4">Danger Zone</h2>
          <p className="text-sm text-gray-600 mb-4">
            Once you delete your account, there is no going back. All your data including
            scans, analyses, and settings will be permanently deleted.
          </p>

          {!showDeleteConfirm ? (
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
            >
              Delete Account
            </button>
          ) : (
            <div className="space-y-4">
              <p className="text-sm font-medium text-red-800">
                Are you absolutely sure? This action cannot be undone.
              </p>
              <div className="flex space-x-3">
                <button
                  onClick={handleDeleteAccount}
                  disabled={isLoading}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {isLoading ? 'Deleting...' : 'Yes, delete my account'}
                </button>
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
