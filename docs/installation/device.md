# Carlos Device (Raspberry Pi)

Operating System: Raspberry Pi OS Lite (64-bit) - Headless

`raspi-config`:
- 1 System Options
  - S1 Wireless LAN
  - S5 Boot / Auto Login
    - Select `B1 Console Autologin`
- 3 Interface Options
  - I4 I2C: Activate
- 5 Localisation Options
  - L2 Timezone
  - L4 WLAN Country

    
```shell
sudo apt update
sudo apt upgrade
sudo apt install git python3 python-rpi.gpio
```

Check python version

```shell
python3 --version
```

Install [poetry](https://python-poetry.org/docs/#installation):

```shell
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Check poetry version

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