__all__ = [
    "CarlosDeviceDriver",
    "CarlosDeviceDriverCreate",
    "CarlosDeviceDriverUpdate",
    "CarlosDeviceSignal",
    "CarlosDeviceSignalCreate",
    "CarlosDeviceSignalUpdate",
    "create_device_driver",
    "create_device_signals",
    "delete_device_driver",
    "delete_device_signal",
    "get_device_drivers",
    "get_device_signals",
    "update_device_driver",
    "update_device_signal",
]

from uuid import UUID

from carlos.edge.interface import DeviceId
from carlos.edge.interface.device.driver_config import (
    DRIVER_IDENTIFIER_LENGTH,
    DriverDirection,
)
from carlos.edge.interface.units import UnitOfMeasurement
from pydantic import Field
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import NoResultFound

from carlos.database.context import RequestContext
from carlos.database.exceptions import NotFound
from carlos.database.orm import (
    CarlosDeviceDriverOrm,
    CarlosDeviceOrm,
    CarlosDeviceSignalOrm,
)
from carlos.database.schema import CarlosSchema
from carlos.database.utils import does_exist


class _DriverMixin(CarlosSchema):
    display_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="The name of the driver that is displayed in the UI.",
    )

    is_visible_on_dashboard: bool = Field(
        ...,
        description="Whether the driver is visible on the dashboard.",
    )


class CarlosDeviceDriverCreate(_DriverMixin):
    """The properties required to create a device driver."""

    driver_identifier: str = Field(
        ...,
        min_length=1,
        max_length=DRIVER_IDENTIFIER_LENGTH,
        description="The unique identifier of the driver in the context of the device.",
    )
    direction: DriverDirection = Field(..., description="The direction of the IO.")

    driver_module: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="The module that implements the IO driver.",
    )


class CarlosDeviceDriverUpdate(_DriverMixin):
    """The properties required to update a device."""

    pass


class CarlosDeviceDriver(CarlosDeviceDriverCreate):

    device_id: UUID = Field(..., description="The device the driver belongs to.")


class _SignalMixin(CarlosSchema):

    display_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="The name of the signal that is displayed in the UI.",
    )

    unit_of_measurement: UnitOfMeasurement = Field(
        ...,
        description="The unit of measurement of the signal.",
    )

    is_visible_on_dashboard: bool = Field(
        ...,
        description="Whether the signal is visible on the dashboard.",
    )


class CarlosDeviceSignalCreate(_SignalMixin):
    """The properties required to create or update a device signal."""

    signal_identifier: str = Field(
        ...,
        min_length=1,
        max_length=DRIVER_IDENTIFIER_LENGTH,
        description="The unique identifier of the signal in the context of the driver.",
    )


class CarlosDeviceSignalUpdate(_SignalMixin):
    """The properties required to update a device signal."""


class CarlosDeviceSignal(_SignalMixin):
    """The properties of a device signal."""

    timeseries_id: int = Field(..., description="The unique identifier of the signal.")
    device_id: UUID = Field(..., description="The device the driver belongs to.")
    driver_identifier: str = Field(
        ...,
        min_length=1,
        max_length=DRIVER_IDENTIFIER_LENGTH,
        description="The unique identifier of the driver in the context of the device.",
    )


async def get_device_drivers(
    context: RequestContext,
    device_id: DeviceId,
) -> list[CarlosDeviceDriver]:
    """Returns all drivers registered for a given device.

    :param context: The request context.
    :param device_id: The unique identifier of the device.
    :return: A list of drivers registered for the device.
    :raises NotFound: If the device does not exist.
    """

    query = select(CarlosDeviceDriverOrm).where(
        CarlosDeviceDriverOrm.device_id == device_id
    )

    drivers = (await context.connection.execute(query)).all()

    if not drivers and await does_exist(
        context, [CarlosDeviceOrm.device_id == device_id]
    ):
        raise NotFound(f"Device {device_id} does not exist.")

    return [CarlosDeviceDriver.model_validate(driver) for driver in drivers]


async def create_device_driver(
    context: RequestContext,
    driver: CarlosDeviceDriverCreate,
) -> CarlosDeviceDriver:
    """Creates a new driver for a given device.

    :param context: The request context.
    :param driver: The properties of the driver to create.
    :return: The properties of the created driver.
    :raises NotFound: If the device does not exist.
    """

    stmt = (
        insert(CarlosDeviceDriverOrm)
        .values(
            **driver.model_dump(),
        )
        .returning(CarlosDeviceDriverOrm)
    )

    driver = (await context.connection.execute(stmt)).one()
    await context.connection.commit()

    return CarlosDeviceDriver.model_validate(driver)


async def update_device_driver(
    context: RequestContext,
    device_id: DeviceId,
    driver_identifier: str,
    driver: CarlosDeviceDriverUpdate,
) -> CarlosDeviceDriver:
    """Updates a driver for a given device.

    :param context: The request context.
    :param device_id: The unique identifier of the device.
    :param driver_identifier: The unique identifier of the driver.
    :param driver: The properties of the driver to update.
    :return: The properties of the updated driver.
    :raises NotFound: If the device or driver does not exist.
    """

    stmt = (
        update(CarlosDeviceDriverOrm)
        .where(
            CarlosDeviceDriverOrm.device_id == device_id,
            CarlosDeviceDriverOrm.driver_identifier == driver_identifier,
        )
        .values(
            **driver.model_dump(),
        )
        .returning(CarlosDeviceDriverOrm)
    )

    try:
        driver = (await context.connection.execute(stmt)).one()
        await context.connection.commit()
    except NoResultFound:
        raise NotFound(
            f"Driver {driver_identifier=} does not exist for device {device_id=}."
        )

    return CarlosDeviceDriver.model_validate(driver)


async def delete_device_driver(
    context: RequestContext,
    device_id: DeviceId,
    driver_identifier: str,
):
    """Deletes a driver for a given device.

    :param context: The request context.
    :param device_id: The unique identifier of the device.
    :param driver_identifier: The unique identifier of the driver.
    """

    stmt = delete(CarlosDeviceDriverOrm).where(
        CarlosDeviceDriverOrm.device_id == device_id,
        CarlosDeviceDriverOrm.driver_identifier == driver_identifier,
    )

    await context.connection.execute(stmt)
    await context.connection.commit()


async def get_device_signals(
    context: RequestContext,
    device_id: DeviceId,
    driver_identifier: str,
) -> list[CarlosDeviceSignal]:
    """Returns all signals registered for a given driver.

    :param context: The request context.
    :param device_id: The unique identifier of the device.
    :param driver_identifier: The unique identifier of the driver.
    :return: A list of signals registered for the driver.
    :raises NotFound: If the device or driver does not exist.
    """

    query = select(CarlosDeviceSignalOrm).where(
        CarlosDeviceSignalOrm.device_id == device_id,
        CarlosDeviceSignalOrm.driver_identifier == driver_identifier,
    )

    signals = (await context.connection.execute(query)).all()

    if not signals and await does_exist(
        context,
        [
            CarlosDeviceDriverOrm.device_id == device_id,
            CarlosDeviceDriverOrm.driver_identifier == driver_identifier,
        ],
    ):
        raise NotFound(
            f"Driver {driver_identifier=} does not exist for device {device_id=}."
        )

    return [CarlosDeviceSignal.model_validate(signal) for signal in signals]


async def create_device_signals(
    context: RequestContext,
    device_id: DeviceId,
    driver_identifier: str,
    signals: list[CarlosDeviceSignalCreate],
) -> list[CarlosDeviceSignal]:
    """Creates new signals for a given driver.

    :param context: The request context.
    :param device_id: The unique identifier of the device.
    :param driver_identifier: The unique identifier of the driver.
    :param signals: The properties of the signals to create.
    :return: The properties of the created signals.
    :raises NotFound: If the device or driver does not exist.
    """

    stmt = (
        insert(CarlosDeviceSignalOrm)
        .values(
            [
                signal.model_dump()
                | {"device_id": device_id, "driver_identifier": driver_identifier}
                for signal in signals
            ]
        )
        .returning(CarlosDeviceSignalOrm)
    )

    signals = (await context.connection.execute(stmt)).all()
    await context.connection.commit()

    return [CarlosDeviceSignal.model_validate(signal) for signal in signals]


async def update_device_signal(
    context: RequestContext,
    timeseries_id: int,
    signal: CarlosDeviceSignalUpdate,
) -> CarlosDeviceSignal:
    """Updates a signal for a given driver.

    :param context: The request context.
    :param timeseries_id: The unique identifier of the signal.
    :param signal: The properties of the signal to update.
    :return: The properties of the updated signal.
    :raises NotFound: If the device, driver, or signal does not exist.
    """

    stmt = (
        update(CarlosDeviceSignalOrm)
        .where(CarlosDeviceSignalOrm.timeseries_id == timeseries_id)
        .values(
            **signal.model_dump(),
        )
        .returning(CarlosDeviceSignalOrm)
    )

    try:
        signal = (await context.connection.execute(stmt)).one()
        await context.connection.commit()
    except NoResultFound:
        raise NotFound(f"Signal {timeseries_id=} does not exist.")

    return CarlosDeviceSignal.model_validate(signal)


async def delete_device_signal(
    context: RequestContext,
    time_series_id: int,
):
    """Deletes a signal for a given driver.

    :param context: The request context.
    :param time_series_id: The unique identifier of the signal.
    """

    stmt = delete(CarlosDeviceSignalOrm).where(
        CarlosDeviceSignalOrm.timeseries_id == time_series_id
    )

    await context.connection.execute(stmt)
    await context.connection.commit()
