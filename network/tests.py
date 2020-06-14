from django.test import TestCase
import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "x_network.settings")
django.setup()
# Create your tests here.

import re

x = '18   09                        any                                    1234554321                    l2tp-server                  172.162.254.9'

l = re.compile(r"\d*[.]\d*[.]\d*[.]\d*")
print(l.findall(x))
