#!/opt/venvs/sphenix-pytpc/bin/python
import sys
import signal
import time
import argparse
import os
import sphenix_pytpc.damserv_grpc_client as client

def cleanup(sig, frame):
    clear()
    d.channel.close()
    sys.exit(0)

def clear():
    print("\033[2J")
    print("\033[H",end="")
    sys.stdout.flush()

def print_status(s, fee_list=[]):
    size = os.get_terminal_size()

    link_up = ["Up" if s else "DOWN" for s in s.rx_ready]
    count_link_up = 0
    count_errors = [0, 0, 0]
    for l in link_up:
        if l == "Up":
            count_link_up += 1

    for i, row in enumerate(zip(s.rx_sob, s.rx_eob, s.stream_crc_errors, s.control_crc_errors, s.rx_fifo_full)):
        if not i in fee_list:
            continue
        for i in range(2, 5):
            if row[i] > 0:
                count_errors[i-2] += 1

    print(" FEE Link Monitor - \033[01m%2i\033[0m links up, \033[01m%2i\033[0m total" % (count_link_up, len(s.rx_ready)))
    print("                    Errors: \033[01m%4i\033[0m stream, \033[01m%4i\033[0m ctrl, \033[01m%4i\033[0m fifo" % (count_errors[0], count_errors[1], count_errors[2])) 

    title = ""
    for r in ["Status", "Rx SOF", "Rx EOF", "Stream CRC", "Control CRC", "FIFO Full"]:
        title += " %10s " % (r)
    title += " "*int(size.columns-len(title))
    print("\033[07m%s" % (title), end="\033[0m")
    print("")

    for i, row in enumerate(zip(s.rx_sob, s.rx_eob, s.stream_crc_errors, s.control_crc_errors, s.rx_fifo_full)):
        if not i in fee_list:
            continue
        print("%2i %-7s " % (i, link_up[i]), end=" ")
        for r in row:
            print("%11i" % (r), end=" ")
        print("")

rlookup = {'R2': [0, 1, 11, 12, 14, 15, 18, 19],
           'R1': [2, 3, 4, 13, 16, 17],
           'R3': [5, 6, 7, 8, 9, 10, 20, 21, 22, 23, 24, 25],
           'TPOT' : [0, 1, 5, 6, 7, 8, 9, 11, 12, 14, 15, 18, 19, 23, 24, 25]}
twiddle = [".", "o", "O", "o"]
parser = argparse.ArgumentParser(
                    prog = 'status',
                    description = 'Print FEE/DAM link status',
                    epilog = '')
parser.add_argument('-d', '--damid', default=0)
parser.add_argument('-c', '--connect', default="localhost:50051")
parser.add_argument('-u', '--update', default=1)
parser.add_argument('-m', '--monitor', action='store_true')
parser.add_argument("--region", type=str, choices=["R1", "R2", "R3", "TPOT"])
parser.add_argument("--fee", nargs='*', type=int, default=range(0, 26))
args = parser.parse_args()

signal.signal(signal.SIGINT, cleanup)
d = client.Dam(args.damid, args.connect)

if args.region:
    fee_list = rlookup[args.region]
else:
    fee_list = args.fee

s = d.fee_status()
print_status(s, fee_list)

if (args.monitor):
    idx = 0
    while True:
        s = d.fee_status()
        clear()
        print_status(s, fee_list)
        print(twiddle[idx])
        idx = (idx + 1) % len(twiddle)
        time.sleep(float(args.update))

