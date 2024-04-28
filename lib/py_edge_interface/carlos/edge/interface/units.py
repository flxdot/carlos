__all__ = [
    "PhysicalQuantity",
    "UnitOfMeasurement",
]
from enum import IntEnum

from carlos.edge.interface.utils import add_enum_members_to_docstr


class PhysicalQuantity(IntEnum):
    """An enumeration of supported physical quantities"""

    IDENTITY = 0
    TEMPERATURE = 1
    HUMIDITY = 2
    ILLUMINANCE = 3
    RATIO = 4


add_enum_members_to_docstr(PhysicalQuantity)


class UnitOfMeasurement(IntEnum):
    """An enumeration of supported units of measurement.

    The values of this enumeration are based on the PhysicalQuantity enumeration.
    """

    # 0 - 99: IDENTITY
    UNIT_LESS = 0

    # 100 - 199: RATIO
    PERCENTAGE = 100

    # 200 - 299: TEMPERATURE
    CELSIUS = 200
    FAHRENHEIT = 201

    # 300 - 399: HUMIDITY
    HUMIDITY_PERCENTAGE = 300

    # 400 - 499: ILLUMINANCE
    LUX = 400

    @property
    def physical_quantity(self) -> PhysicalQuantity:
        """Returns the physical quantity of this unit of measurement."""
        return PhysicalQuantity(self.value // 100)


add_enum_members_to_docstr(UnitOfMeasurement)
