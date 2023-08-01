#!/opt/venvs/sphenix-pytpc/bin/python

import subprocess
import re
import argparse

def main():
    fee_init_base_command = '/opt/venvs/sphenix-pytpc/bin/fee_init sampa --pre-samples 103 --samples 50 --shape-gain 6'

    # first run full command on all TPOT FEEs
    fee_init_command = fee_init_base_command + ' --region TPOT'
    print( 'fee_init_command: ', fee_init_command )
    
    result = subprocess.run( ['ssh', 'ebdc39', '-x', fee_init_command], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf8');
    # print( output )

    # now run over all FEEs independantly, up to five times or untill there is no error message
    # these are TPOT links
    fee_list = [0, 1, 5, 6, 7, 8, 9, 11, 12, 14, 15, 18, 19, 23, 24, 25]
    for channel in  fee_list:
        fee_init_command = fee_init_base_command + ' --fee ' + str(channel) + ' --no-stream-enable'
        print( 'fee_init_command: ', fee_init_command )
        
        # try at most 5 times
        for i in range(0,10):
            result = subprocess.run( ['ssh', 'ebdc39', '-x', fee_init_command], stdout=subprocess.PIPE)
            output = result.stdout.decode('utf8');
            # print( output )
    
            # parse output for errors and break if none found
            error = (
                re.match( 'SAMPA \d: Can\'t set time window', output ) or
                re.match( 'SAMPA \d: Can\'t set pre trigger', output ) or
                re.match( 'SAMPA \d: WARNING: Unexpected pre trigger length', output ) or
                re.match( 'SAMPA \d: WARNING: Unexpected time window length', output )
            )
            if not error:
                print( 'success' )
                break     

if __name__ == '__main__':
  main()
