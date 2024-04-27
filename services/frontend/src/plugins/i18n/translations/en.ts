import {
  ERouteName,
} from '@/router/route-name.ts';

const authentication = {
  login: 'Login',
  logout: 'Logout',
};

const device = {
  status: {
    online: 'Online',
    offline: 'Offline',
    offlineSince: 'Offline since {time}',
    disconnected: 'Disconnected',
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
  device,
  error,
  navbar,
  pages,
};
