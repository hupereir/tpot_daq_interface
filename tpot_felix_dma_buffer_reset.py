#!/opt/venvs/sphenix-pytpc/bin/python

from sphenix_pytpc import fee
import sphenix_pytpc.damserv_grpc_client as client

# FIFO reset
d = client.Dam(0, 'localhost:50051')
d.reset()
