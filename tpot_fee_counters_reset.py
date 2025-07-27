#!/opt/venvs/sphenix-pytpc/bin/python

import time
from sphenix_pytpc import fee
import sphenix_pytpc.damserv_grpc_client as client

d = client.Dam(0, 'localhost:50051')

d.reg.phy_reset = 1
d.reg.phy_reset = 0

print ("LMK PLL check:")
print (d.reg.lmk_locked)
