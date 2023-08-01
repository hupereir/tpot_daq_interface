#!/usr/bin/env python3
import argparse
import os.path
import subprocess

parser = argparse.ArgumentParser(
	  prog = 'copy_runs',
	  description = 'copy runs from bufferboxes to sdcc',
	  epilog = '')
	
parser.add_argument(
  'run_numbers', 
  nargs='+',
  type=int,
  help='the list of run numbers')
	
parser.add_argument('-t', '--type', default='junk', help='run type')
args = parser.parse_args()
	
runlist = args.run_numbers
type = args.type

for run in runlist:
  
  source = f'/bbox/commissioning/TPOT/{type}/TPOT_ebdc39_{type}-{run:08d}-0000.evt'
  destination  = f'/sdcc/sphnxpro/commissioning/TPOT/{type}/TPOT_ebdc39_{type}-{run:08d}-0000.evt'
  
  if not os.path.isfile(source):
    print( f'file {source} not found' )
    #continue

  print( f'{source} -> {destination}' )
  command = f'rsync -P {source} {destination}';
  subprocess.call(['rsync', '-P', source, destination] )
