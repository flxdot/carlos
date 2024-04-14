import {
  ERouteName,
} from '@/router/route-name.ts';

const authentication = {
  login: 'Anmelden',
  logout: 'Abmelden',
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
  pages,
  error,
  navbar,
};
