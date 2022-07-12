## conserver
* ログに1行ごとにタイムスタンプつけられるのは良い。が、セッションごとのファイル作成ができない
* 新しいUSB追加時に、restartが必要。既存セッションがDropされる
  - reloadを実行後、conserver-serverにアクセスできなくなる。（バグ？）
  

## Install
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


