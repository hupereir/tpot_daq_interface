#!/opt/venvs/sphenix-pytpc/bin/python
import sys
import signal
from pathlib import Path
import time
import datetime
import argparse
import os
import subprocess
import sphenix_pytpc.damserv_grpc_client as client
from sphenix_pytpc import fee

def monitor(ip_addr):
    d = client.Dam(0, ip_addr)

    # store FEE objects
    sfee = []
    for i in range(0, 26):
        sfee.append(fee(i, backend='grpc', ip_addr=ip_addr))

    # store fee status    
    s = d.fee_status()

    # look for errors
    errfee = []
    for i in range(0,len(s.rx_ready)):
        if(s.rx_ready[i]==1):
            fee_id = sfee[i].fee_addr
            # print( "processing ", ip_addr, fee_id )
            if(s.rx_sob[i] > s.rx_eob[i]):
                errfee.append(fee_id)
                sfee[i].reg_write(0x213,0)
                print("found error: ", ip_addr,fee_id,s.rx_sob[i],s.rx_eob[i],s.rx_sob[i]-s.rx_eob[i])

    return errfee

def Check_err():
    
    ip_addr ='ebdc39:50051'
    print( 'tpot_fee_mask - checking error in ',ip_addr )
    errfee=monitor(ip_addr)

    # do nothing if no error found
    if not errfee:
         return
    
    command = '/home/phnxrc/operations/TPOT/tpot_lv_interface/tpot_lv_off.py'
    for fee in errfee:

        # update command
        command = command + ' ' + str(fee)

        # mark error
        ppath="ROCerr/ebdc39_"+str(fee)+".err"
        Path(ppath).touch()

    # process command and print output
    print( 'command: ', command )
    result = subprocess.run( ['ssh', 'daq02', '-x', command], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf8');
    print( output )

if __name__ == '__main__':
    # infinite loop. This is intended to run in the background
    while True:
        Check_err()
        time.sleep(30)
