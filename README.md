# KEBA_Monitor
KEBA charger monitor through ModbusTCP and UDP. These Python scripts are meant to run continuosly and provide data from KEBA charger to other systems in JSON format. Simple http user interface is also provided to monitor values.

# Installation
- Copy .py and .html files to same directory.
- Modify your KEBA charging station IP address in .py file.
- Run .py file. It will start ModbusTCP or UDP communication and http server and will run until stopped e.g. with ctrl-C.

# Web interface
Opening address http://yourIP:8082/ with a browser shows simple user interface with current charger status. "yourIP" is the IP for location where .py file is run.

# JSON API
From address http://yourIP:8082/status a JSON formatted data is returned. The keys are Modbus register addresses or UDP fields, see details in KEBA manuals. Exception is key 0 which tells communication status (true=ok, false=error).

# Links
KEBA ModbusTCP manual: https://www.keba.com/download/x/dea7ae6b84/kecontactp30modbustcp_pgen.pdf

KEBA UDP manual: https://www.keba.com/download/x/4a925c4c61/kecontactp30udp_pgen.pdf
