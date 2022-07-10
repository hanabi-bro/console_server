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

disconnect session
```bash
Ctrl + c-x
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

### Server Setup Sample
```bash
NewUser='console' &&
NewUserPass='P@ssw0rd' &&
ConsoleGroup='console' &&

sudo apt install -y python3 python3-pip python3-venv minicom task-japanese locales-all
sudo groupadd $ConsoleGroup &&
sudo useradd -s /bin/bash -m -g $ConsoleGroup dialout plugdev -G ssh $NewUser &&
echo $NewUser:$NewUserPass | sudo chpasswd &&
sudo -iu $NewUser mkdir -p /home/$NewUser/.ssh &&
cat <<EOF | sudo -iu $NewUser tee /home/$NewUser/.ssh/config > /dev/null &&
StrictHostKeyChecking no
UserKnownHostsFile=/dev/null
EOF
sudo chmod 700 /home/$NewUser/.ssh &&
sudo chmod 600 /home/$NewUser/.ssh/config &&

cat <<'EOF' | sudo -iu $NewUser tee -a /home/$NewUser/.bashrc > /dev/null &&

alias minicom="~/.minicom.sh"
EOF

cat <<'EOF' | sudo -iu $NewUser tee -a /home/$NewUser/.minicom.sh > /dev/null &&
#!/bin/bash
minicom -C ~/console_server/log/$(date +%y%m%d_%H%M%S).log $*
EOF


cat <<EOF | sudo tee /etc/sudoers.d/050_console > /dev/null &&
%console    ALL=NOPASSWD: /usr/bin/ln, /usr/bin/udevadm control --reload-rules, /usr/bin/udevadm trigger
%console    ALL=/usr/sbin/shutdown, /usr/sbin/reboot
EOF

sudo -iu $NewUser git clone https://github.com/hanabi-bro/console_server.git /home/$NewUser/console_server
sudo ln -fs /home/$NewUser/console_server/conf/50-usb-serial.rules /etc/udev/rules.d/.
```

