#!/usr/bin/env python

import random
import math

fout = open('nodes.txt', 'w')
empty = True

fout.write('''        {
            "nodes": [''')

counts = {"ui": 20, "loadbalancer": 3, "database": 6}
for typ in counts.keys():
    for i in range(counts[typ]):
        memory = 20 + math.floor(random.random() * 5)
        if empty:
            empty = False
        else:
            fout.write(',')
        fout.write('\n                {"role": "%s", "memory": %d}' % (typ, memory))

fout.write('''\n            ],
            "animation": [''')

istart = 0
empty = True
for typ in counts.keys():
    nodes = list(range(istart, istart + counts[typ]))
    istart += counts[typ]
    if empty:
        empty = False
    else:
        fout.write(',')
    fout.write('\n                {"type": "blow", "nodes": %s, "from": 20, "to": 40}' % str(nodes))

fout.write('''\n            ],
            "timeout": 2000
        }''')

fout.close()


# {"role": "ui", "memory": 30, "parent": 0},
# {"role": "ui", "memory": 30, "parent": 0},
# {"role": "ui", "memory": 30, "parent": 0},
# {"role": "ui", "memory": 30, "parent": 7},
# {"role": "database", "memory": 30},