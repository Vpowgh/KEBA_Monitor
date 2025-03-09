# KEBA_Monitor
KEBA charger monitor through ModbusTCP.

# Installation
- Copy .py and .html files to same directory. Modify your KEBA charging station IP address in .py file.

# Web interface
Opening address http://yourIP:8082/ with a browser shows simple user interface with current charger status.

# JSON API
From address http://yourIP:8082/status a JSON formatted data is returned. The keys are directly Modbus register addresses, except key 0 tells communication status (true=ok, false=error).

# Links
KEBA ModbusTCP manual:

https://www.keba.com/download/x/dea7ae6b84/kecontactp30modbustcp_pgen.pdf
