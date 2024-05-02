import {
  ERouteName,
} from '@/router/route-name.ts';
import {
  EPhysicalDimension, EUnitOfMeasurement,
} from '@/api/unit-of-measurement.ts';

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

const unitOfMeasurement: Record<EUnitOfMeasurement, string> = {
  [EUnitOfMeasurement.UNIT_LESS]: '',
  [EUnitOfMeasurement.PERCENTAGE]: 'Percent',
  [EUnitOfMeasurement.CELSIUS]: 'Degrees Celsius',
  [EUnitOfMeasurement.FAHRENHEIT]: 'Degrees Fahrenheit',
  [EUnitOfMeasurement.HUMIDITY_PERCENTAGE]: 'Percent',
  [EUnitOfMeasurement.LUX]: 'Lux',
};

const physicalDimension: Record<EPhysicalDimension, string> = {
  [EPhysicalDimension.IDENTITY]: 'Identity',
  [EPhysicalDimension.TEMPERATURE]: 'Temperature',
  [EPhysicalDimension.HUMIDITY]: 'Humidity',
  [EPhysicalDimension.ILLUMINANCE]: 'Illuminance',
  [EPhysicalDimension.RATIO]: 'Ratio',
};

export default {
  authentication,
  chart,
  data,
  device,
  error,
  navbar,
  pages,
  unitOfMeasurement,
  physicalDimension,
};
