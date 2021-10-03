import subprocess
import sqlite3

con = sqlite3.connect('devices_mac.db')
cursor = con.cursor()

try:
    cursor.execute("CREATE TABLE mac_addresses (mac_address text)")
    con.commit()
except sqlite3.OperationalError:
    pass


process = subprocess.run(["nmap", "-sP", "192.168.0.0/24"], stdout=subprocess.PIPE)
str_process = str(process.stdout.decode("utf-8"))

hosts = str_process.split('\n')[1:-2] #exclude the first and last line
num_hosts = len(hosts)

ip_addresses = [hosts[x].split(' ')[4] for x in range(0,num_hosts,2)][1:] #extract only the ip addresses in the evenly numbered elements. Also, ignore the first ip address.

#ping the ip addresses
for ip_address in ip_addresses:
    subprocess.run(["ping", "-c", "5", ip_address], stdout=subprocess.PIPE)

arp_scanner = subprocess.run(['arp', '-a'], stdout=subprocess.PIPE).stdout.decode('utf-8').split('\n')

def find_mac_address(ip_address):
    for mac_address in arp_scanner:
        if ip_address in mac_address:
            return (ip_address, mac_address.split(' ')[3])


output = list(map(find_mac_address, ip_addresses))


for ip_address, mac_address in output:
    
    row = []
    for row in cursor.execute(f'SELECT * FROM mac_addresses WHERE mac_address="{mac_address}"'):
        print("Known device detected!")

    if len(row) == 0:
        print(f"There's an unknown device connected to your network! Device Mac Address: {mac_address}, Device IP address: {ip_address}. Do you want to add this device into the known list?")
        user_val = int(input("Please enter 1 for yes and 0 for no: "))
        if user_val == 1:
            cursor.execute(f"INSERT INTO mac_addresses VALUES ('{mac_address}')")
            con.commit()

