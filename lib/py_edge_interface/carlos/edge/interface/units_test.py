import pytest

from .units import PhysicalQuantity, UnitOfMeasurement


@pytest.mark.parametrize("unit", list(UnitOfMeasurement))
def test_unit_of_measurement(unit):
    """This test ensures that each unit of measurement can be converted into
    a physical quantity. This test does not ensure that the conversion is
    correct. This can't be done automatically. Since this is already quite declarative,
    we don't need to test the conversion here."""
    assert isinstance(unit.physical_quantity, PhysicalQuantity)
