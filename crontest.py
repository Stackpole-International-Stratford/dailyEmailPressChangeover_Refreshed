#!/usr/bin/env python
import datetime
import socket

print(f'Cron job has run at {datetime.datetime.now()}')

address = socket.gethostbyname('mesg06.stackpole.ca')
print(address)
