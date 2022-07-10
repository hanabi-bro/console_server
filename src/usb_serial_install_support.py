import os, re, datetime, shutil, textwrap
import pyudev
from rich import pretty, print
from rich.console import Console

console = Console()
pretty.install()

# minicom config dir
minirc_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '../conf'))

# minicom config files
minirc_files = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '../conf/minirc.*'))

# udev rule file
rule_file = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '../conf/50-usb-serial.rules'))

# installed device list
def gen_installed_list():
    installed_dev_list = []
    pattern = re.compile(r'ATTRS{serial}=="(\w+)", SYMLINK\+="ttyUSB-com(\d+)", GROUP="dialout"')
    with open(rule_file, 'w+') as f:
        pass

    with open(rule_file, 'r') as f:
        for line in f:
            print(line)
            let = pattern.findall(line)
            print(let)
            if len(let) == 0: continue 
            installed_dev_list.append({
                    'serial': let[0][0],
                    'num': int(let[0][1]),
                })
    return installed_dev_list

# check installed
def check_installed(serial):
    console.print(f'fond {serial}')
    for i in installed_dev_list:
        if serial == i['serial']:
            console.print(f"serial:{i['serial']} is already installed com{i['num']}")
            return True
    return False

# assing num
def assign_new_num(installed_dev_list):
    nums = [i['num'] for i in installed_dev_list]
    new_num = None
    for i in range(1, 99):
        if not i in nums:
            new_num = i
            break
    return new_num

# add new rule
def add_new_rule(serial, num):
    new_rule = f'SUBSYSTEM=="tty", ATTRS{{idVendor}}=="0403", ATTRS{{idProduct}}=="6001", ATTRS{{serial}}=="{device.get("ID_SERIAL_SHORT")}", SYMLINK+="ttyUSB-com{new_num}", GROUP="dialout"'
    # udev rule backup
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    shutil.copy2(rule_file, (rule_file + f'.{timestamp}'))
    
    # udev rule append
    with open(rule_file, 'a') as f:
        f.write(new_rule + '\n')

    console.print(f'new rule add')
    console.print(f'{new_rule}')

    # minicomrc add
    new_minicomrc_file = os.path.join(minirc_path, f'minirc.ttyUSB-com{num}')
    with open(new_minicomrc_file, 'w') as f:
        f.write(f'pu port             /dev/ttyUSB-com{num}\n')
        f.write('pu baudrate         9600\n')
        f.write('pu bits             8\n')
        f.write('pu parity           N\n')
        f.write('pu stopbits         1\n')


    with open(new_minicomrc_file, 'r') as f:
        new_minicomrc = f.read()

    console.print('new minicomrc add')
    console.print(new_minicomrc_file)
    console.print(new_minicomrc)

    return new_minicomrc_file

# show installed serial
console.print(f'installed usb serials')
console.print(f'{gen_installed_list()}')
console.print(f'++++++++++++++++++++++++')
console.print(f'Stop Ctrl + C')
console.print(f'++++++++++++++++++++++++')

    
# monitor usb plugin
try:
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem='usb')
    monitor.start()
    
    for device in iter(monitor.poll, None):
        if device.action == 'bind' and device.get('ID_MODEL') == 'FT232R_USB_UART':
            installed_dev_list = gen_installed_list()
            new_num = assign_new_num(installed_dev_list)
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
    
            if check_installed(device.get('ID_SERIAL_SHORT')):
                pass
            else:
                new_minicomrc_file = add_new_rule(device.get('ID_SERIAL_SHORT'), new_num)
                udev_reload_notice = f"""
                Plz make minicom simlink then execute udev reload or system reboot.
                ```bash
                sudo ln -fs {new_minicomrc_file} /etc/minicom/.
                sudo udevadm control --reload-rules && sudo udevadm trigger
                ```
                """
                console.print(textwrap.dedent(udev_reload_notice)[1:-1], style='bold white on blue')
               
except KeyboardInterrupt:
    monitor.stop()

except Exception as e:
    console.log(e, log_locals=True)
