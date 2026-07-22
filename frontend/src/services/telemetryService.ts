import axios, { AxiosError } from 'axios';

// API URL from Vite environment variables, fallback to window.location.origin
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
});

/**
 * Utility to retry a promise-returning function.
 */
const withRetry = async <T>(fn: () => Promise<T>, retries = 3, delay = 1000): Promise<T> => {
  try {
    return await fn();
  } catch (error) {
    if (retries === 0) throw error;
    // Delay before retrying
    await new Promise((res) => setTimeout(res, delay));
    return withRetry(fn, retries - 1, delay * 2); // Exponential backoff
  }
};

export interface TelemetryPoint {
  device_id: string;
  timestamp: string | number; // Some APIs return epoch, others ISO string
  heart_rate: number | null;
  stress_score: number | null;
  latitude: number | null;
  longitude: number | null;
  fall_detected: boolean | null;
  sound_alert: boolean | null;
}

export const telemetryService = {
  getLatestTelemetry: async (deviceId: string): Promise<TelemetryPoint | null> => {
    try {
      const response = await withRetry(() => apiClient.get(`/api/v1/telemetry/latest/${deviceId}`));
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        if (error.response?.status === 404) {
          console.warn(`No telemetry found for device ${deviceId}`);
          return null;
        }
        console.error(`Network error fetching latest telemetry: ${error.message}`);
      } else {
        console.error(`Unexpected error: ${error}`);
      }
      throw error;
    }
  },

  getTelemetryHistory: async (deviceId: string): Promise<TelemetryPoint[]> => {
    try {
      const response = await withRetry(() => apiClient.get(`/api/v1/telemetry/history/${deviceId}`));
      return response.data;
    } catch (error) {
      if (error instanceof AxiosError) {
        console.error(`Network error fetching telemetry history: ${error.message}`);
      } else {
        console.error(`Unexpected error: ${error}`);
      }
      throw error;
    }
  },
};
