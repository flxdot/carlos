__all__ = ["GPIO"]

try:
    from RPi import GPIO
except ImportError:
    from RPiSim.GPIO import GPIO

# Choose the GPIO mode globally
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
