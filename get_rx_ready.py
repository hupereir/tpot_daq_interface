#!/opt/venvs/sphenix-pytpc/bin/python
import sys
import signal
import time
import argparse
import os
import sphenix_pytpc.damserv_grpc_client as client

parser = argparse.ArgumentParser(
                    prog = 'status',
                    description = 'Print FEE/DAM link status',
                    epilog = '')
parser.add_argument('-d', '--damid', default=0)
parser.add_argument('-c', '--connect', default="localhost:50051")
args = parser.parse_args()

d = client.Dam(args.damid, args.connect)
s = d.fee_status()
print( s.rx_ready )
d.channel.close()

