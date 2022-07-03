import os, re, datetime, shutil, textwrap
import pyudev
from rich import pretty, print
from rich.console import Console

console = Console()
pretty.install()

class UsbSerialInstallSupport():
    def __init__(self):
        # minicom config dir
        self.minirc_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../conf'))

        # minicom config files
        self.minirc_files = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../conf/minirc.*'))

        # udev rule file
        self.rule_file = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../conf/50-usb-serial.rules'))
        with open(self.rule_file, 'a') as f:
            pass

    # installed device list
    def gen_installed_list(self):
        installed_dev_list = []
        pattern = re.compile(r'ATTRS{serial}=="(\w+)", SYMLINK\+="ttyUSB-com(\d+)", GROUP="dialout"')
        with open(self.rule_file, 'r') as f:
            for line in f:
                let = pattern.findall(line)
                installed_dev_list.append({
                        'serial': let[0][0],
                        'num': int(let[0][1]),
                    })
        return installed_dev_list

    # check installed
    def check_installed(self,  serial):
        console.print(f'fond {serial}')
        for i in self.installed_dev_list:
            if serial == i['serial']:
                console.print(f"serial:{i['serial']} is already installed com{i['num']}")
                return True
        return False

    # assing num
    def assign_new_num(self, installed_dev_list):
        nums = [i['num'] for i in installed_dev_list]
        new_num = None
        for i in range(1, 99):
            if not i in nums:
                new_num = i
                break
        return new_num

    # add new rule
    def add_new_rule(self, device, serial, new_num):
        new_rule = f'SUBSYSTEM=="tty", ATTRS{{idVendor}}=="0403", ATTRS{{idProduct}}=="6001", ATTRS{{serial}}=="{device.get("ID_SERIAL_SHORT")}", SYMLINK+="ttyUSB-com{new_num}", GROUP="dialout"'
        # udev rule backup
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        shutil.copy2(self.rule_file, (self.rule_file + f'.{timestamp}'))
        
        # udev rule append
        with open(self.rule_file, 'a') as f:
            f.write(new_rule + '\n')

        console.print(f'new rule add')
        console.print(f'{new_rule}')

        # minicomrc add
        self.new_minicomrc_file = os.path.join(self.minirc_path, f'minirc.ttyUSB-com{new_num}')
        with open(self.new_minicomrc_file, 'w') as f:
            f.write(f'pu port             /dev/ttyUSB-com{new_num}\n')
            f.write('pu baudrate         9600\n')
            f.write('pu bits             8\n')
            f.write('pu parity           N\n')
            f.write('pu stopbits         1\n')


        with open(self.new_minicomrc_file, 'r') as f:
            self.new_minicomrc = f.read()

        console.print('new minicomrc add')
        console.print(self.new_minicomrc_file)
        console.print(self.new_minicomrc)

        return self.new_minicomrc_file

    def run(self):
        # show installed serial
        console.print(f'installed usb serials')
        console.print(f'{self.gen_installed_list()}')
        console.print(f'++++++++++++++++++++++++')
        console.print(f'Stop Ctrl + C')
        console.print(f'++++++++++++++++++++++++')

        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='usb')
        #self.observer = pyudev.MonitorObserver(self.monitor, self.usbDeviceEventHandler)
        self.observer = pyudev.MonitorObserver(self.monitor, self.usb_event_handler)
        self.observer.start()
        try:
            loop = True
            while loop == True:
                pass
        except KeyboardInterrupt:
                console.print('\n')
                console.print('Stop monitor -----')
        finally:
            loop = False
            self.observer.stop()


    def usb_event_handler(self, action, device):
        if device.action == 'bind' and device.get('ID_MODEL') == 'FT232R_USB_UART':
            self.installed_dev_list = self.gen_installed_list()
            message = f"""
            =================================================
            {device.action}
            BUSNUM: {device.get('BUSNUM')}
            DEVNUM: {device.get('DEVNUM')}
            ID_MODEL_ID: {device.get('ID_MODEL_ID')}
            ID_VENDOR_ID: {device.get('ID_VENDOR_ID')}
            ID_SERIAL: {device.get('ID_SERIAL')}
            ID_SERIAL_SHORT: {device.get('ID_SERIAL_SHORT')}
            =================================================
            """
            console.print(textwrap.dedent(message)[1:-1])
    
            if self.check_installed(device.get('ID_SERIAL_SHORT')):
                pass
            else:
                new_num = self.assign_new_num(self.installed_dev_list)
                self.new_minicomrc_file = self.add_new_rule(device, device.get('ID_SERIAL_SHORT'), new_num)
                udev_reload_notice = f"""
                Plz make minicom simlink then execute udev reload or system reboot.
                ```bash
                sudo ln -fs self.rule_file /etc/udev/rules.d/.
                sudo ln -fs {self.new_minicomrc_file} /etc/minicom/.
                sudo udevadm control --reload-rules && sudo udevadm trigger
                ```
                """
                console.print(textwrap.dedent(udev_reload_notice)[1:-1], style='bold white on blue')
                    

if __name__ == '__main__':
    usis = UsbSerialInstallSupport()
    usis.run()