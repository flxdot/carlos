__all__ = ["GPIO"]

try:
    from RPi import GPIO  # type: ignore
except ImportError:
    from RPiSim.GPIO import GPIO  # type: ignore

# Choose the GPIO mode globally
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
