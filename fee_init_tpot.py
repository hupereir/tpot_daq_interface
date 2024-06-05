#!/usr/bin/env python3

import subprocess
import re
import argparse

def main():
    # first run full command on all TPOT FEEs
    fee_init_command = '/home/phnxrc/operations/TPOT/tpot_daq_interface/fee_init_local triggered --connect-tpot --pre-samples 86 --samples 25 --shape-gain 6'
    
    print( 'fee_init_command: ', fee_init_command )
    
    result = subprocess.run( ['ssh', 'ebdc39', '-x', fee_init_command], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf8');
    print( output )

if __name__ == '__main__':
  main()
