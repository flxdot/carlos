# Carlos Device (Raspberry Pi)

This guide will explain how to setup a fresh Raspberry Pi. I'm using a 
Raspberry Pi 3 Model B but you are free to use any other model, that supports
your requirements.

Well choose the [Raspberry Pi OS Lite (64-bit)](https://www.raspberrypi.com/software/operating-systems/) - Headless version, because we won't
be needing the overhead of a desktop environment.

Once you have flashed the image to your SD card, you can boot up the Raspberry Pi and 
start the setup by running the following commands:

```shell
sudo raspi-config
```

Well configure the following settings:

**1 System Options**

  - S1 Wireless LAN: Configure Wifi to your needs.
  - S5 Boot / Auto Login
      - Select `B1 Console Autologin` - Otherwise it will be impossible to run the carlos device without a monitor and keyboard.

**3 Interface Options**

  - I4 I2C: Activate - We will use I2C to communicate with the sensors.

**5 Localisation Options**

  - L2 Timezone

Once the basic setup is done, we can start installing the required tools and dependencies:
    
```shell
sudo apt update # (1)
sudo apt upgrade # (2)
sudo apt install git # (3)
```

1. This command will update the local package repository.
2. This command will install all available updates.
3. This command will install the `git` tool, which we will use to clone the carlos repository.

Check python version.

```shell
python3 --version
```

If your Python version is <3.11 you'll need to upgrade it.

This repository uses [Poetry](https://python-poetry.org/docs/#installation) as dependency manager, thus we'll install it here as well:

```shell
curl -sSL https://install.python-poetry.org | python3 - # (1)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc # (2)
source ~/.bashrc # (3)
```

1.  This command will download and execute the official installation script.
2.  This command will add the poetry binary to the PATH.
3.  This command will reload the shell to make the changes take effect.


To ensure that poetry is installed correctly, run the following command:

```shell
poetry --version
```

Clone the carlos repository to the root of the device:

```bash
git clone https://github.com/flxdot/carlos.git ~/carlos
```

Install the virtual environment and dependencies:

```shell
cd ~/carlos/services/device
poetry install --without dev
```

We are now done with the installation of the device.

Configure the device by invoking the following command:

```shell
make config
```

Register the device as a service:

```shell
sh install-service.sh
```