import * as Sentry from '@sentry/vue';
import config from '@/config';
import packageInfo from '@/../package.json';

export function useSentry(app) {
  const tracePropagationTargets = [
    'localhost',
  ];
  if (config.VITE_APP_API_URL !== undefined) {
    tracePropagationTargets.push(config.VITE_APP_API_URL);
  }

  Sentry.init({
    app,
    dsn: config.VITE_SENTRY_DSN,
    environment: config.VITE_SENTRY_ENVIRONMENT,
    release: `Carlos Frontend@${packageInfo.version}`,
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration(),
    ],
    // Performance Monitoring
    tracesSampleRate: 0.1,
    // Set 'tracePropagationTargets' to control for which URLs distributed tracing should be enabled
    tracePropagationTargets,
    // Session Replay
    replaysSessionSampleRate: 0.0,
    replaysOnErrorSampleRate: 1.0,
  });
}
