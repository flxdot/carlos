"""This module contains code that allows the device to update itself."""

__all__ = ["update_device"]

import os
import subprocess
import sys
import time

from loguru import logger


def update_device():  # pragma: no cover
    """Update the device to the latest version.

    The code of the device is updated via git with a subsequent restart of the
    running process.
    """

    logger.info("Updating the device to the latest version...")

    logger.debug("Pulling the latest changes from the git repository...")
    process = subprocess.run(["git", "pull"], capture_output=True)
    if process.returncode != 0:  # pragma: no cover
        raise RuntimeError(
            "Failed to pull the latest changes from the git repository: "
            + process.stderr.decode("utf-8")
        )
    else:
        logger.debug(process.stdout.decode("utf-8").strip())

    # Restart the running process
    logger.debug("Restarting the running process...")
    os.execv(sys.executable, [sys.executable] + sys.argv)


if __name__ == "__main__":
    # Little test script to see if the update_device function works
    for i in reversed(range(1, 6)):
        print(f"updating device in {i} seconds...")
        time.sleep(1)

    update_device()
