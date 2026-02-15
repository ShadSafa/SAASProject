import { useLocation, Link } from 'react-router-dom';

export default function VerifyEmailPendingPage() {
  const location = useLocation();
  const email = location.state?.email;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full space-y-8 text-center">
        <div>
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
            <svg
              className="h-6 w-6 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-gray-900">Check your email</h2>
          <p className="mt-4 text-gray-600">
            We've sent a verification link to:
          </p>
          {email && (
            <p className="mt-2 text-lg font-medium text-gray-900">{email}</p>
          )}
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <p className="text-sm text-blue-800">
            Click the link in the email to verify your account and complete signup.
          </p>
        </div>

        <div className="space-y-2">
          <p className="text-sm text-gray-600">
            Didn't receive the email? Check your spam folder.
          </p>
          <div className="flex justify-center space-x-4 text-sm">
            <button className="text-blue-600 hover:text-blue-500">
              Resend email
            </button>
            <span className="text-gray-300">|</span>
            <Link to="/login" className="text-blue-600 hover:text-blue-500">
              Back to login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
