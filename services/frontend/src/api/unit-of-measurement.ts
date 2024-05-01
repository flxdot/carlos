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
 * Ensures that each available UnitOfMeasurement is present in the EUnitOfMeasurement
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
