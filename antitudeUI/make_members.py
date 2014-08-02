#!/usr/bin/env python

import sys
import random

template = '''    {
      "name": "powermule",
      "addr": "10.99.176.%d:7946",
      "port": 7946,
      "tags": {
        "role": "%s"
      },
      "status": "alive",
      "protocol": {
        "max": 4,
        "min": 2,
        "version": 4
      }
    }%s
'''

print('''{
  "members": [''')
nlines = int(sys.argv[1])
roles = ['ui', 'database', 'loadbalancer']
for i in range(nlines):
	print(template % (i, random.choice(roles), '' if i == nlines - 1 else ','))
print(''']
}''')
