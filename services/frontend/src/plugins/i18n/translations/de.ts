import {
  ERouteName,
} from '@/router/route-name.ts';

const authentication = {
  login: 'Anmelden',
  logout: 'Abmelden',
};

const chart = {
  boolean: {
    high: 'An',
    low: 'Aus',
  },
};

const data = {
  labelWithUnit: '{label} in {unit}',
};

const device = {
  status: {
    online: 'Online',
    offline: 'Offline',
    offlineSince: 'Offline set {time}',
    disconnected: 'Getrennt',
  },
  warning: {
    dummyData: 'Die gezeigten Daten sind nur für Präsentationszwecke. Die echten Daten sind noch nicht verbunden.',
  },
};

const error = {
  oops: 'Hoppla!',
  errorMessageTemplate: 'Fehler {code} - {message}',
  notFound: {
    title: 'Seite nicht gefunden',
    message: 'Die angeforderte Seite konnte nicht gefunden werden.',
  },
  goBack: 'Zurück',
};

const navbar = {
  devices: 'Geräte',
};

const pages = {
  [ERouteName.DEVICES_OVERVIEW]: 'Geräte Übersicht',
};

export default {
  authentication,
  chart,
  data,
  device,
  error,
  navbar,
  pages,
};
