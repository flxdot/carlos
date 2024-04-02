import {
  normalizeUrl,
} from '@/utils/url.ts';

export type appConfig = {
  VITE_APP_API_URL: string,
  VITE_SENTRY_DSN?: string,
  VITE_SENTRY_ENVIRONMENT?: string,
};

// The following object will be taken the config values from the public/config.js file
// when the app is running in the container. If running via Vite, the config values will
// be taken from the environment variables.
export default {
  VITE_APP_API_URL: normalizeUrl(window.config.VITE_APP_API_URL || import.meta.env.VITE_APP_API_URL),
  VITE_SENTRY_DSN: window.config.VITE_SENTRY_DSN || import.meta.env.VITE_SENTRY_DSN,
  VITE_SENTRY_ENVIRONMENT: window.config.VITE_SENTRY_ENVIRONMENT || import.meta.env.VITE_SENTRY_ENVIRONMENT || 'development',
};
