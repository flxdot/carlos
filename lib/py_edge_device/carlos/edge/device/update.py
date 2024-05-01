"""This module contains code that allows the device to update itself."""

__all__ = ["update_device"]

import os
import shutil
import subprocess
from pathlib import Path

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
            + process.stderr.decode("utf-8").strip()
        )
    else:
        logger.debug(process.stdout.decode("utf-8").strip())

    # Update the dependencies
    update_dependencies()

    # Restart the running process
    logger.info("Restarting the running process...")
    os.execv(sys.executable, [sys.executable] + sys.argv)


def update_dependencies():
    """Removes all known carlos dependencies and installs the latest ones."""

    logger.debug("Removing the current carlos dependencies...")
    venv_path = Path(__file__).parent.parent.parent.parent / ".venv"
    site_packages = venv_path / "lib" / "python3.11" / "site-packages"
    for dep in site_packages.glob("carlos*"):
        logger.debug(f"Removing {dep}...")
        if dep.is_dir():
            shutil.rmtree(dep)
        else:
            dep.unlink()

    logger.debug("Installing the latest dependencies...")
    process = subprocess.run(["poetry", "install"], capture_output=True)
    if process.returncode != 0:  # pragma: no cover
        raise RuntimeError(
            "Failed to install the latest dependencies: "
            + process.stderr.decode("utf-8").strip()
        )
    else:
        logger.debug(process.stdout.decode("utf-8").strip())


if __name__ == "__main__":
    # Little test script to see if the update_device function works
    for i in reversed(range(1, 6)):
        print(f"updating device in {i} seconds...")
        time.sleep(1)

    update_device()
