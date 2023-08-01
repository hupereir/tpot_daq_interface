#!/usr/bin/env python3
import argparse
import os.path
import subprocess
import re

def parse_runs( input_runlist ):
  output_runlist = []
  for input in input_runlist:
    if re.fullmatch( '\d+',input ):
      output_runlist.append( int(input) )
      continue

    result = re.fullmatch( '(\d+)\.\.(\d+)',input ) 
    if result:
      begin = int(result.group(1))
      end = int(result.group(2))
      for run in range( begin, end+1 ):
        output_runlist.append(run)
      continue

    print( f'invalid run {input}' )
    
  return output_runlist

def main():
  parser = argparse.ArgumentParser(
    prog = 'copy_runs',
    description = 'copy runs from bufferboxes to sdcc',
    epilog = '')
		
  parser.add_argument(
    'run_numbers', 
    nargs='+',
    help='the list of run numbers')
  
  parser.add_argument('-t', '--type', default='junk', help='run type')
  args = parser.parse_args()
  
  runlist = parse_runs( args.run_numbers )
  type = args.type
  print( runlist )	

  for run in runlist:
	  
    source = f'/bbox/commissioning/TPOT/{type}/TPOT_ebdc39_{type}-{run:08d}-0000.evt'
    destination  = f'/sdcc/sphnxpro/commissioning/TPOT/{type}/TPOT_ebdc39_{type}-{run:08d}-0000.evt'
	  
    if not os.path.isfile(source):
      print( f'file {source} not found' )
      continue
	
    print( f'{source} -> {destination}' )
    command = f'rsync -P {source} {destination}';
    subprocess.call(['rsync', '-P', source, destination] )

if __name__ == '__main__':
  main()
