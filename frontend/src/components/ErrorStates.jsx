import React from 'react';

/**
 * ErrorMessage - Display error messages with retry option
 */
export const ErrorMessage = ({
    title = 'Error',
    message = 'Something went wrong',
    onRetry,
    className = ''
}) => {
    return (
        <div className={`bg-disco-red/10 border-2 border-disco-red/50 rounded-lg p-4 ${className}`}>
            <div className="flex items-start gap-3">
                {/* Icon */}
                <div className="text-disco-red text-2xl flex-shrink-0">⚠</div>

                {/* Content */}
                <div className="flex-1">
                    <h3 className="text-disco-red font-mono font-bold text-sm mb-1">
                        {title}
                    </h3>
                    <p className="text-disco-paper/80 font-serif text-sm">
                        {message}
                    </p>

                    {/* Retry button */}
                    {onRetry && (
                        <button
                            onClick={onRetry}
                            className="mt-3 px-3 py-1 bg-disco-red/20 hover:bg-disco-red/30 border border-disco-red text-disco-red font-mono text-xs rounded transition-colors"
                        >
                            Retry
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

/**
 * ErrorBoundary - Catch React errors and display fallback UI
 */
export class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error('ErrorBoundary caught an error:', error, errorInfo);
        this.setState({ error, errorInfo });

        // Log to error reporting service if configured
        if (this.props.onError) {
            this.props.onError(error, errorInfo);
        }
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
        if (this.props.onReset) {
            this.props.onReset();
        }
    };

    render() {
        if (this.state.hasError) {
            // Custom fallback UI
            if (this.props.fallback) {
                return this.props.fallback(this.state.error, this.handleReset);
            }

            // Default fallback UI
            return (
                <div className="min-h-screen bg-disco-bg flex items-center justify-center p-4">
                    <div className="max-w-md w-full bg-disco-bg border-2 border-disco-red/50 rounded-lg p-6">
                        <div className="text-center mb-4">
                            <div className="text-disco-red text-5xl mb-2">⚠</div>
                            <h2 className="text-disco-red font-mono text-xl mb-2">
                                System Error
                            </h2>
                            <p className="text-disco-paper/80 font-serif text-sm mb-4">
                                The application encountered an unexpected error.
                            </p>
                        </div>

                        {/* Error details (dev mode) */}
                        {import.meta.env.DEV && this.state.error && (
                            <details className="mb-4 bg-black/30 rounded p-3">
                                <summary className="text-disco-muted font-mono text-xs cursor-pointer mb-2">
                                    Error Details
                                </summary>
                                <pre className="text-disco-red text-xs overflow-auto max-h-40">
                                    {this.state.error.toString()}
                                    {this.state.errorInfo?.componentStack}
                                </pre>
                            </details>
                        )}

                        {/* Actions */}
                        <div className="flex gap-2">
                            <button
                                onClick={this.handleReset}
                                className="flex-1 px-4 py-2 bg-disco-cyan/20 hover:bg-disco-cyan/30 border border-disco-cyan text-disco-cyan font-mono text-sm rounded transition-colors"
                            >
                                Try Again
                            </button>
                            <button
                                onClick={() => window.location.reload()}
                                className="flex-1 px-4 py-2 bg-disco-red/20 hover:bg-disco-red/30 border border-disco-red text-disco-red font-mono text-sm rounded transition-colors"
                            >
                                Reload Page
                            </button>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

/**
 * OfflineMessage - Display when offline
 */
export const OfflineMessage = ({ onRetry, className = '' }) => {
    return (
        <div className={`bg-yellow-900/20 border-2 border-yellow-500/50 rounded-lg p-4 ${className}`}>
            <div className="flex items-start gap-3">
                <div className="text-yellow-500 text-2xl flex-shrink-0">📡</div>
                <div className="flex-1">
                    <h3 className="text-yellow-500 font-mono font-bold text-sm mb-1">
                        Connection Lost
                    </h3>
                    <p className="text-disco-paper/80 font-serif text-sm mb-3">
                        You're currently offline. Your actions will be queued and sent when the connection is restored.
                    </p>
                    {onRetry && (
                        <button
                            onClick={onRetry}
                            className="px-3 py-1 bg-yellow-500/20 hover:bg-yellow-500/30 border border-yellow-500 text-yellow-500 font-mono text-xs rounded transition-colors"
                        >
                            Retry Connection
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

/**
 * NotFoundMessage - Display when resource not found
 */
export const NotFoundMessage = ({ title = 'Not Found', message, onGoBack, className = '' }) => {
    return (
        <div className={`text-center ${className}`}>
            <div className="text-disco-muted text-6xl mb-4">404</div>
            <h2 className="text-disco-paper font-serif text-2xl mb-2">{title}</h2>
            {message && (
                <p className="text-disco-muted font-mono text-sm mb-4">{message}</p>
            )}
            {onGoBack && (
                <button
                    onClick={onGoBack}
                    className="px-4 py-2 bg-disco-cyan/20 hover:bg-disco-cyan/30 border border-disco-cyan text-disco-cyan font-mono text-sm rounded transition-colors"
                >
                    Go Back
                </button>
            )}
        </div>
    );
};

/**
 * EmptyState - Display when no data available
 */
export const EmptyState = ({ icon = '📭', title, message, action, className = '' }) => {
    return (
        <div className={`text-center py-8 ${className}`}>
            <div className="text-5xl mb-3">{icon}</div>
            <h3 className="text-disco-paper font-serif text-lg mb-2">{title}</h3>
            {message && (
                <p className="text-disco-muted font-mono text-sm mb-4 max-w-md mx-auto">
                    {message}
                </p>
            )}
            {action}
        </div>
    );
};

export default ErrorMessage;
