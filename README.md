# Support to use Raspberry Pi as Console Server-Like
This tool will help you add a USB serial cable to your Raspberry Pi.

## Like a Console Server 
* Use some USB serial cables and Raspberry Pi or something else.
  - only FT232R USB UART is available
* Use minicom

## Howto
Install minicom and git clone

```bash
python -m pip install -r requirements.txt

python src/add_usb_serial.py
```

plug in USB serial cable and make symlink and reload udev

