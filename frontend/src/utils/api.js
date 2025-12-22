/**
 * API Utility - Centralized API client with retry logic and offline handling
 *
 * Features:
 * - Exponential backoff for failed requests
 * - Request timeout handling
 * - Offline detection and queuing
 * - Loading state management
 */

import { API_CONFIG } from '../config';

const API_BASE_URL = API_CONFIG.baseUrl;
const DEFAULT_TIMEOUT = API_CONFIG.timeout;
const MAX_RETRIES = API_CONFIG.maxRetries;
const INITIAL_RETRY_DELAY = API_CONFIG.retryDelay;

class APIClient {
    constructor() {
        this.isOnline = navigator.onLine;
        this.requestQueue = [];

        // Listen for online/offline events
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.processQueue();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
        });
    }

    /**
     * Make an API request with retry logic
     * @param {string} endpoint - API endpoint (e.g., '/chat')
     * @param {object} options - Fetch options
     * @param {number} retryCount - Current retry attempt
     * @returns {Promise} Response data
     */
    async request(endpoint, options = {}, retryCount = 0) {
        const url = `${API_BASE_URL}${endpoint}`;

        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };

        // Add timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT);
        config.signal = controller.signal;

        try {
            const response = await fetch(url, config);
            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);

            // Handle abort (timeout)
            if (error.name === 'AbortError') {
                console.warn(`Request timeout for ${endpoint}`);
            }

            // Retry logic
            if (retryCount < MAX_RETRIES) {
                const delay = INITIAL_RETRY_DELAY * Math.pow(2, retryCount);
                console.log(`Retrying ${endpoint} in ${delay}ms (attempt ${retryCount + 1}/${MAX_RETRIES})`);

                await new Promise(resolve => setTimeout(resolve, delay));
                return this.request(endpoint, options, retryCount + 1);
            }

            // If offline, queue the request
            if (!this.isOnline) {
                console.log(`Offline: queuing request to ${endpoint}`);
                return new Promise((resolve, reject) => {
                    this.requestQueue.push({ endpoint, options, resolve, reject });
                });
            }

            throw error;
        }
    }

    /**
     * Process queued requests when back online
     */
    async processQueue() {
        console.log(`Processing ${this.requestQueue.length} queued requests`);

        while (this.requestQueue.length > 0) {
            const { endpoint, options, resolve, reject } = this.requestQueue.shift();

            try {
                const result = await this.request(endpoint, options);
                resolve(result);
            } catch (error) {
                reject(error);
            }
        }
    }

    /**
     * GET request
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    /**
     * POST request
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    /**
     * Check if online
     */
    getOnlineStatus() {
        return this.isOnline;
    }

    /**
     * Get queue length
     */
    getQueueLength() {
        return this.requestQueue.length;
    }
}

// Export singleton instance
const api = new APIClient();
export default api;
