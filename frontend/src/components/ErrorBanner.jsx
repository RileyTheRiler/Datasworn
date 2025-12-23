import React from 'react';

/**
 * ErrorBanner - Display errors with retry and dismiss options
 *
 * @param {Object} error - Error object with message, details, and retryable flag
 * @param {Function} onRetry - Callback when user clicks retry
 * @param {Function} onDismiss - Callback when user dismisses error
 */
export function ErrorBanner({ error, onRetry, onDismiss }) {
  if (!error) return null;

  return (
    <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 max-w-2xl w-full px-4">
      <div className="bg-red-900 border border-red-700 rounded-lg p-4 shadow-lg">
        <div className="flex items-start">
          {/* Error Icon */}
          <div className="flex-shrink-0">
            <svg
              className="h-6 w-6 text-red-400"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
          </div>

          {/* Error Content */}
          <div className="ml-3 flex-1">
            <h3 className="text-sm font-medium text-red-200">
              {error.message || "An error occurred"}
            </h3>

            {error.details && (
              <p className="mt-2 text-sm text-red-300">
                {error.details}
              </p>
            )}

            {/* Action Buttons */}
            <div className="mt-4 flex space-x-3">
              {error.retryable && onRetry && (
                <button
                  onClick={onRetry}
                  className="inline-flex items-center px-3 py-1.5 border border-red-600 text-sm font-medium rounded text-red-200 bg-red-800 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition"
                >
                  <svg className="mr-1.5 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Try Again
                </button>
              )}

              {onDismiss && (
                <button
                  onClick={onDismiss}
                  className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded text-red-300 hover:text-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition"
                >
                  Dismiss
                </button>
              )}
            </div>
          </div>

          {/* Close Button */}
          {onDismiss && (
            <div className="ml-4 flex-shrink-0">
              <button
                onClick={onDismiss}
                className="inline-flex text-red-400 hover:text-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 rounded"
              >
                <span className="sr-only">Close</span>
                <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ErrorBanner;
