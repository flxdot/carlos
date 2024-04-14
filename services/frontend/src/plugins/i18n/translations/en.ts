import {
  ERouteName,
} from '@/router/route-name.ts';

const authentication = {
  login: 'Login',
  logout: 'Logout',
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
  pages,
  error,
  navbar,
};
