__all__ = ["GPIO"]

try:
    from RPi import GPIO
except ImportError:
    from RPiSim.GPIO import GPIO
