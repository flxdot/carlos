import {
  ERouteName,
} from '@/router/route-name.ts';

const authentication = {
  login: 'Login',
  logout: 'Logout',
};

const chart = {
  boolean: {
    high: 'On',
    low: 'Off',
  },
};

const data = {
  labelWithUnit: '{label} in {unit}',
};

const device = {
  status: {
    online: 'Online',
    offline: 'Offline',
    offlineSince: 'Offline since {time}',
    disconnected: 'Disconnected',
  },
  warning: {
    dummyData: 'The shown data is for presentation purposes only. The real data is not yet connected.',
  },
};

const error = {
  oops: 'Oops!',
  errorMessageTemplate: 'Error {code} - {message}',
  notFound: {
    title: 'Not Found',
    message: 'The requested page could not be found.',
  },
  goBack: 'Go back',
};

const navbar = {
  devices: 'Devices',
};

const pages = {
  [ERouteName.DEVICES_OVERVIEW]: 'Devices Overview',
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
