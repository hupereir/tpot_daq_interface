#!/opt/venvs/sphenix-pytpc/bin/python

import time
from sphenix_pytpc import fee
import sphenix_pytpc.damserv_grpc_client as client

d = client.Dam(0, 'localhost:50051')

# FIFO reset
d.reset()

d.reg.gtm_recovered_clock = 0
d.reg.si5345_pll.program = 1
while d.reg.si5345_pll.nLOL != 1:
    time.sleep(0.1) # wait for GTM lock
    
d.reg.phy_reset = 1
d.reg.phy_reset = 0

print ("LMK PLL check:")
print (d.reg.lmk_locked)
