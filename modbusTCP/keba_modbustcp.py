'''
keba_modbustcp.py
KEBA Monitor - Simple web monitor for KEBA charger through ModbusTCP
Developed by Vpow 2025-
'''

from pyModbusTCP.client import ModbusClient
from bottle import Bottle, run, static_file
from threading import Timer

#KEBA charger ip address, for example "192.168.100.158"
KEBA_IP = "insert_KEBA_IP_here"

#Polling interval for reading registers. KEBA manual states this should be >0.5s.
pollDT = 1.0

#Registers to read. Fast registers are read as fast polling allows, slow registers slower.
fastdata = [1000, 1004, 1006, 1008, 1010, 1012, 1020, 1040, 1042, 1044, 1046, 1502]
slowdata = [1014, 1016, 1018, 1036, 1100, 1110, 1500]

#dictionaries for translating numbers to strings
state_dict = {0:"Start-up", 1:"Not ready", 2:"Ready",3:"Charging", 4:"Error", 5:"Suspended"}
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
        
    #mostly read fast values, every now and then slow value
    if timer_i < 5:
        timer_i = timer_i + 1
        register_id = fastdata[fastindex]
        fastindex = (fastindex+1)%len(fastdata)
    else:
        timer_i = 0
        register_id = slowdata[slowindex]
        slowindex = (slowindex+1)%len(slowdata)
        
    #Read 2x16bit registers. KEBA manual states reading only 2 words allowed at a time.
    try:
        regval = c.read_holding_registers(register_id, 2)
    except:
        regval = None
    
    if regval != None:
        #convert to single 32bit value
        regval = 65536*regval[0]+regval[1]
        
        #format value if needed
        if register_id == 1000:
            if regval in state_dict:
                regval = state_dict[regval]
        elif register_id == 1004:
            if regval in cablestate_dict:
                regval = cablestate_dict[regval]
        elif register_id == 1006:
            regval = format(regval, 'x')
        #elif register_id == 1008 or register_id == 1010 or register_id == 1012 or register_id == 1100 or register_id == 1110:
        elif register_id in [1008, 1010, 1012, 1100, 1110]:
            regval = '{0:.1f}'.format(regval/1000.0)
        elif register_id == 1020:
            regval = '{0:.1f}'.format(regval/1000000.0)
        elif register_id == 1046:
            regval = '{0:.2f}'.format(regval/1000.0)
        elif register_id == 1036 or register_id == 1502:
            regval = '{0:.2f}'.format(regval/10000.0)
        elif register_id == 1018:
            regval = str((regval>>24)&0xff) + '.' + str((regval>>16)&0xff) + '.' + str((regval>>8)&0xff)
        elif register_id == 1500: #convert to hex without 0x prefix
            regval = format(regval, 'x')
                
        kebadata[register_id] = regval
        kebadata[COMMSTATUS] = True
    else:
        kebadata[COMMSTATUS] = False

    #retrigger timer
    Timer(pollDT, task).start()


#setup Bottle http server to serve json and UI html
app = Bottle()

@app.route('/status')
def status():
    #bottle kindly converts content and content type to json
    return kebadata

@app.route('/')
def server_index():
    return static_file('kebaUI_modbustcp.html', root = './')


if __name__ == '__main__':
    #open connection to KEBA
    c = ModbusClient(host=KEBA_IP, port=502, unit_id=255, auto_open=True, timeout=1)
    
    #initial trigger for timer
    Timer(pollDT, task).start()
    
    #run bottle http server, this will run forever
    run(app, host='0.0.0.0', port=8082, quiet=True)
