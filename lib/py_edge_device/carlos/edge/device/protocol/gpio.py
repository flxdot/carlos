__all__ = ["GPIO"]

import traceback
import warnings

try:
    from RPi import GPIO  # type: ignore
except ImportError:
    warnings.warn(
        "RPi.GPIO not available. Fallback tom mocked GPIO instead. "
        f"{traceback.format_exc()}"
    )
    from ._gpio_mock import GPIO  # type: ignore

# Choose the GPIO mode globally
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
