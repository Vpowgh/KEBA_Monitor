'''
keba_UDP.py
KEBA Monitor - Simple web monitor for KEBA charger through UDP
Developed by Vpow 2025-
'''
import socket
import select
import json
from bottle import Bottle, run, static_file
from threading import Timer

#KEBA charger ip address, for example "192.168.100.158"
KEBA_IP = "insert_KEBA_IP_here"

#Polling interval for reading reports. KEBA manual states this should be >100ms
pollDT = 2.0

#Reports to read.
fastdata = ['report 2', 'report 3']
slowdata = ['report 1', 'report 100']

#dictionaries for translating numbers to strings
state_dict = {0:"Start-up", 1:"Not ready", 2:"Ready", 3:"Charging", 4:"Error", 5:"Suspended"}
cablestate_dict = {0:"No cable", 1:"Cable in charger", 3:"Cable in charger, locked", 5:"Cable in charger and car", 7:"Cable in charger and car, locked"}

#Place to keep read values
kebadata = {}

#Special key for communication status. Register values use register numbers as keys.
COMMSTATUS = 0

#helper variables
fastindex = 0
slowindex = 0
timer_i = 0

#polling task
def task():
    global fastindex, slowindex
    global timer_i
    global kebadata
    
    #poll data
    if timer_i < 5:
        timer_i = timer_i + 1
        sock.send(bytes(fastdata[fastindex], "utf-8"))
        fastindex = (fastindex+1)%len(fastdata)
    else:
        timer_i = 0
        sock.send(bytes(slowdata[slowindex], "utf-8"))
        slowindex = (slowindex+1)%len(slowdata)
    
    ready = select.select([sock], [], [], 2)
    if ready[0]:
        #KEBA manual states max 512 bytes transmission
        data, addr = sock.recvfrom(512)
        
        #check that received data is from right source
        if addr[0] == KEBA_IP and addr[1] == 7090:
            data_string = json.loads(data.decode("utf-8"))

            for id, val in data_string.items():
                #format value if needed
                if id == 'State':
                    if val in state_dict:
                        regval = state_dict[val]
                elif id == 'Plug':
                    if val in cablestate_dict:
                        regval = cablestate_dict[val]
                elif id in ['I1', 'I2', 'I3', 'Max curr', 'Curr HW']:
                    regval = '{0:.1f}'.format(val/1000.0)
                elif id == 'P':
                    regval = '{0:.1f}'.format(val/1000000.0)
                elif id == 'PF':
                    regval = '{0:.2f}'.format(val/1000.0)
                elif id in ['E pres', 'E total']:
                    regval = '{0:.2f}'.format(val/10000.0)                
                elif id in ['U1', 'U2', 'U3', 'Product', 'Serial', 'Firmware', 'Error1', 'Error2', 'RFID tag']:
                    regval = val
                else: #if value is not in above formatters, skip
                    continue

                kebadata[id] = regval
                
            #combine error datas to one
            if 'Error1' in kebadata and 'Error2' in kebadata:
                kebadata['Error'] = str(kebadata['Error1']) + ' ' + str(kebadata['Error2'])
                
            kebadata[COMMSTATUS] = True
    else:
        kebadata[COMMSTATUS] = False
    
    #retrigger timer
    Timer(pollDT, task).start()


#setup Bottle http server to serve json and UI html
app = Bottle()

@app.route('/status')
def status():
    return kebadata

@app.route('/')
def server_index():
    return static_file('kebaUI_UDP.html', root = './')


if __name__ == '__main__':
    #UDP mode socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(0)
    #listen KEBA port 7090 to receive
    sock.bind(("", 7090))
    #connect to KEBA IP to send, port 7090
    sock.connect((KEBA_IP, 7090))    
    
    #initial trigger for timer
    Timer(pollDT, task).start()
    
    #run bottle http server, this will run forever
    run(app, host='0.0.0.0', port=8082, quiet=True)
