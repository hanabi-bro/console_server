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
1. Start this tool
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
sudo apt install -y python3 python3-pip python3-venv minicom git &&
sudo useradd -s /bin/bash -m -G dialout,ssh,plugdev $NewUser &&
echo $NewUser:$NewUserPass | sudo chpasswd &&
sudo -iu $NewUser mkdir -p /home/$NewUser/.ssh &&
cat <<EOF | sudo -iu $NewUser tee /home/$NewUser/.ssh/config > /dev/null &&
StrictHostKeyChecking no
UserKnownHostsFile=/dev/null
EOF
sudo chmod 700 /home/$NewUser/.ssh &&
sudo chmod 600 /home/$NewUser/.ssh/config &&
# cat <<'EOF' | sudo -iu $NewUser tee -a /home/$NewUser/.myrc > /dev/null &&
cat <<'EOF' | sudo tee -a /etc/profile.d/myenv.sh > /dev/null &&
## minicom settings
export PATH=$PATH:~/.local/bin
function minicom() {
    /usr/bin/minicom -C /home/console/console_server/log/$1_`date +%y%m%d_%H%M%S`.log $@
}
EOF
# cat <<'EOF' | sudo -iu $NewUser tee -a /home/$NewUser/.bashrc > /dev/null &&
# source ~/.myrc
# EOF
cat <<EOF | sudo tee /etc/sudoers.d/050_console > /dev/null &&
%console    ALL=NOPASSWD: /usr/bin/ln, /usr/bin/udevadm control --reload-rules, /usr/bin/udevadm trigger
%console    ALL=/usr/sbin/shutdown, /usr/sbin/reboot
EOF
sudo -iu $NewUser git clone https://github.com/hanabi-bro/console_server.git /home/$NewUser/console_server &&
sudo ln -fs /home/$NewUser/console_server/conf/50-usb-serial.rules /etc/udev/rules.d/. &&
sudo chmod 775 /home/$NewUser/console_server/log
```

### extra user use console
```bash
sudo gpasswd -a $USER console
```


## 補足 conserver 同居させてみたもののいくつかの理由で使わないことにした
* ログに1行ごとにタイムスタンプつけられるのは良い。が、セッションごとのファイル作成ができない
* 新しいUSB追加時に、restartが必要。既存セッションがDropされる
  - reload試したところ、実行後にconserver-serverにアクセスできなくなる。（バグ？）
* シリアル接続コマンド`console`で接続対象がtab保管されない。minicomは出来る。
* conserverとminicomを同居するとminicomが途中で固まったり不安定になる。気がする。

minicomは、1行ごとのタイムスタンプをログに残せないけど、後はだいたい使える気がする、

### conserver Install
```bash
sudo apt-get install -y conserver-server conserver-client
sudo chmod 755 /var/log/conserver
sudo ln -s /var/log/conserver/ /home/console/console_server/log/.
sudo ln -fs /home/console/console_server/conf/conserver/conserver.cf /etc/conserver/.
```

### conserver.cf Sample Default conf
```cf
config * {
}
default full {
        rw *;
}
default * {
        logfile /var/log/conserver/&.log;
        timestamp 1h1lab;
        include full;
}
access * {
        trusted 127.0.0.1;
        allowed 127.0.0.1;
}
console ttyUSB0 {
        master localhost;
        type device;
        device /dev/ttyUSB0;
        baud 9600;
        parity none;
}
```


