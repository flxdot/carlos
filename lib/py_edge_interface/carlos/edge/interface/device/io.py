__all__ = ["peripheral_registry"]

from collections import namedtuple
from typing import Callable, TypedDict, TypeVar

from .config import PeripheralConfig
from .peripheral import CarlosIO

C = TypeVar("C", bound=PeripheralConfig)

RegistryItem = namedtuple("RegistryItem", ["config", "factory"])


class ConfigDict(TypedDict):
    ptype: str


class PeripheralRegistry:
    def __init__(self):
        self._peripherals: dict[str, RegistryItem] = {}

    def register(self, ptype: str, config: type[C], factory: Callable[[C], CarlosIO]):
        """Registers a peripheral with the peripheral registry.

        :param ptype: The peripheral type.
        :param config: The peripheral configuration model.
        :param factory: The peripheral factory function.
        """

        if ptype in self._peripherals:
            raise ValueError(f"The peripheral {ptype} is already registered.")

        self._peripherals[ptype] = RegistryItem(config, factory)

    def build(self, config: ConfigDict) -> CarlosIO:
        """Builds a peripheral from the peripheral registry."""

        ptype = config["ptype"]

        if type not in self._peripherals:
            raise ValueError(f"The peripheral {ptype} is not registered.")

        entry = self._peripherals[ptype]

        return entry.factory(entry.config.model_validate(config))


peripheral_registry = PeripheralRegistry()
