from django.test import TestCase
import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "x_network.settings")
django.setup()
# Create your tests here.

import socket
def getIP(domain):
    myaddr = socket.getaddrinfo(domain, 'http')
    print(type(myaddr[0][4][0]))

getIP('115.238.')
