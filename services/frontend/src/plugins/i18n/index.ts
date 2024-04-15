import {
  createI18n,
} from 'vue-i18n';

import en from './translations/en';
import de from './translations/de';

// Type-define "en" as the master schema for the resource
// "master" schema means it will be used for keys resolving
type MessageSchema = typeof en;

const messages = {
  en,
  'en-US': en,
  'en-GB': en,
  de,
  'de-DE': de,
  'de-CH': de,
  'de-AT': de,
};

const definedLocales = Object.keys(messages) as Array<keyof typeof messages>;

const i18n = createI18n<[MessageSchema], typeof definedLocales[number]>({
  locale: navigator.language,
  fallbackLocale: 'en',
  messages,
});

export default i18n;
