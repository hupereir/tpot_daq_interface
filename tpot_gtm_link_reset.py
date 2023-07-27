#!/opt/venvs/sphenix-pytpc/bin/python

from sphenix_pytpc import fee
import sphenix_pytpc.damserv_grpc_client as client
d = client.Dam(0, 'localhost:50051')

# gtm link reset
d.reg.si5345_pll.program = 1
