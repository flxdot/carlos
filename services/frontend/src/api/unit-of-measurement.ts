import {
  components,
} from '@/api/openapi.ts';

export enum EUnitOfMeasurement {
    UNIT_LESS = 0,
    PERCENTAGE = 100,
    CELSIUS = 200,
    FAHRENHEIT = 201,
    HUMIDITY_PERCENTAGE = 300,
    LUX = 400,
}

/*
 * This map exists to formally couple the EUnitOfMeasurement and the UnitOfMeasurement
 * from the API.
 */
export const UnitOfMeasurementMap: Record<components['schemas']['UnitOfMeasurement'], keyof typeof EUnitOfMeasurement> = {
  0: 'UNIT_LESS',
  100: 'PERCENTAGE',
  200: 'CELSIUS',
  201: 'FAHRENHEIT',
  300: 'HUMIDITY_PERCENTAGE',
  400: 'LUX',
};

export const UnitOfMeasurementSymbol: Record<EUnitOfMeasurement, string> = {
  [EUnitOfMeasurement.UNIT_LESS]: '',
  [EUnitOfMeasurement.PERCENTAGE]: '%',
  [EUnitOfMeasurement.CELSIUS]: '°C',
  [EUnitOfMeasurement.FAHRENHEIT]: '°F',
  [EUnitOfMeasurement.HUMIDITY_PERCENTAGE]: '%',
  [EUnitOfMeasurement.LUX]: 'lx',
};

export enum EPhysicalDimension {
    IDENTITY= 0,
    TEMPERATURE =1,
    HUMIDITY = 2,
    ILLUMINANCE = 3,
    RATIO = 4,
}

/*
 * This map exists to formally couple the EPhysicalDimension and the PhysicalQuantity
 * from the API.
 */
export const PhysicalQuantityMap: Record<components['schemas']['PhysicalQuantity'], keyof typeof EPhysicalDimension> = {
  0: 'IDENTITY',
  1: 'TEMPERATURE',
  2: 'HUMIDITY',
  3: 'ILLUMINANCE',
  4: 'RATIO',
};
