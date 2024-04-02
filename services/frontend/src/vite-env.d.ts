/// <reference types="vite/client" />

import {
  appConfig,
} from '@/config.ts';

declare global {
  interface Window { config: appConfig; }
}
