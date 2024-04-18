__all__ = ["GPIO"]

from loguru import logger


class GpioMock:  # pragma: no cover

    LOW = 0
    HIGH = 1

    IN = 0
    OUT = 1

    PUD_OFF = 0
    PUD_DOWN = 1
    PUD_UP = 2

    BOARD = 10
    BCM = 11

    def __init__(self):
        self._pins: list[int] = []

    def setwarnings(self, state: bool):
        pass

    def setmode(self, mode: int):
        pass

    def setup(self, pin: int | list[int], mode: int):
        if isinstance(pin, list):
            for p in pin:
                self.setup(p, mode)
            return

        if pin not in self._pins:
            self._pins.append(pin)
            logger.debug(f"Setup pin {pin} in mode {mode}")

    def output(self, pin: int, state: bool):
        if pin in self._pins:
            logger.debug(f"Set pin {pin} to {'HIGH' if state else 'LOW'}")
        else:
            raise ValueError(f"Pin {pin} not set up")

    def input(self, pin: int) -> bool:
        if pin in self._pins:
            logger.debug(f"Reading input from pin {pin}")
            return False  # Dummy value, always returning False for simplicity
        else:
            raise ValueError(f"Pin {pin} not set up")

    def cleanup(self):
        self._pins.clear()
        logger.debug("Cleaned up GPIO pins")


GPIO = GpioMock()
