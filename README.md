# Support to use Raspberry Pi as Console Server-Like
This tool will help you add a USB serial cable to your Raspberry Pi.

When a new USB Serial Cable is plugged in, automatically detect then make udev rule file and minicom config file.
It need to make symlink and reload udev by root privileges with manualy. 

## Like a Console Server 
* Raspberry Pi 3 or 4 B.
* Use some USB serial cables and Raspberry Pi or something else.
  - only FT232R USB UART is available.
* Use minicom

## Install
```bash
sudo apt install -y python3 minicom task-japanese locales-all
git clone https://github.com/hanabi-bro/console_server.git
cd console_server
sudo python -m pip install -r requirements.txt
python src/add_usb_serial.py
```

## Howto
1. Starti this tool
```bash
python /src/usb_serial_install_support.py
```

2. plug in USB serial cable and make symlink and reload udev

3. Stop with Ctr + C

4. make symlink and  reload udev to use displayed command

## use minicom
Note:
The prefix, this tool creates is ttyUSB-com{num}.

```bash
minicom ttyUSB-com{num}.
```

### serial config
If you need to change baurate or other, plz edit minrc file by your self. 
minrc config file is in ./conf/minirc.tty-USB-com{num}.

default config
```text
pu port             /dev/ttyUSB-com1
pu baudrate         9600
pu bits             8
pu parity           N
pu stopbits         1
```
