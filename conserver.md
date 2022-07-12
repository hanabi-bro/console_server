## Install
```bash
sudo apt-get install -y conserver-server conserver-client
```

sudo chmod 755 /var/log/conserver
sudo ln -s /var/log/conserver/ /home/console/console_server/log/.

### Default conf
```cf
default full {
	rw root,plathome;
	ro watch; 
} 
default * {
	logfile /home/console/console_server/&;
	logfilemax 1m;
	timestamp 1hab;
	include full;
	master localhost; 
}
access * {
	trusted 127.0.0.1;
	allowed 127.0.0.1;
}
console ttyUSB-kmcom3 {
	master localhost;
	type device;
	device /dev/ttyUSB-kmcom3;
	baud 9600;
	!cstopb;
	!crtscts;
	parity none;
}
```

echo '*any*:*' | sudo tee /etc/conserver/conserver.passwd > /dev/null


