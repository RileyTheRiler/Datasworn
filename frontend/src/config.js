/**
 * Application Configuration
 *
 * Centralized configuration for API URLs, feature flags, and app settings
 */

// Determine environment
const isDevelopment = import.meta.env.MODE === 'development';
const isProduction = import.meta.env.MODE === 'production';

// API Configuration
export const API_CONFIG = {
    // Base URL for API - can be overridden by environment variable
    baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',

    // Request timeout in milliseconds
    timeout: 30000,

    // Retry configuration
    maxRetries: 3,
    retryDelay: 1000,
};

// Feature Flags
export const FEATURES = {
    // Voice features
    voiceEnabled: true,
    speechRecognitionEnabled: true,

    // Visual effects
    ambientParticles: true,
    tensionVignette: true,
    crtEffects: true,

    // Advanced features
    psycheDashboard: true,
    tacticalBlueprint: true,
    starMap: true,

    // Accessibility
    reducedMotionSupport: true,
    highContrastMode: true,
    screenReaderSupport: true,
};

// UI Configuration
export const UI_CONFIG = {
    // Typewriter effect
    typewriterBaseSpeed: 25, // ms per character

    // Auto-save interval
    autoSaveInterval: 30000, // 30 seconds

    // Session timer
    sessionTimerEnabled: true,
    breakReminderInterval: 3600000, // 1 hour

    // Loading messages rotation
    loadingMessageInterval: 3000,
};

// Audio Configuration
export const AUDIO_CONFIG = {
    // Default volumes (0-1)
    defaultSoundEffectsVolume: 0.5,
    defaultMusicVolume: 0.3,
    defaultVoiceVolume: 1.0,

    // Enable audio by default
    soundEffectsEnabled: true,
    musicEnabled: true,
};

// Development Tools
export const DEV_CONFIG = {
    // Enable debug logging
    debugMode: isDevelopment,

    // Show performance metrics
    showPerformanceMetrics: isDevelopment,

    // Enable React DevTools
    reactDevTools: isDevelopment,
};

// Session Configuration
export const SESSION_CONFIG = {
    // Default session ID (for development)
    defaultSessionId: 'default',

    // Auto-load last session
    autoLoadLastSession: true,
};

// Export environment helpers
export const ENV = {
    isDevelopment,
    isProduction,
};

// Export all config as a single object (optional)
export default {
    api: API_CONFIG,
    features: FEATURES,
    ui: UI_CONFIG,
    audio: AUDIO_CONFIG,
    dev: DEV_CONFIG,
    session: SESSION_CONFIG,
    env: ENV,
};
