#!/opt/venvs/sphenix-pytpc/bin/python
import sys, os
import time
import argparse
import concurrent.futures

from sphenix_pytpc import fee
import sphenix_pytpc.damserv_grpc_client as client

backend = 'grpc'

class Retry(object):
    def __init__(self, retrys=100, inforce_retry=2):
        self.retry = retrys
        self.inforce_retry = inforce_retry
        self.retry_count = 0
        self.total_retry = 0
        self.run_count = 0

    def read(self, run_f, r_args=None, r_kwargs=None):
        self.retry_count = 0
        self.run_count += 1
        run_args = r_args if r_args else []
        run_kwargs = r_kwargs if r_kwargs else {}
        for i in range(0, self.retry):
            try:
                ret = run_f(*run_args, **run_kwargs)
                if (i > self.inforce_retry):
                    return ret
            except RuntimeError:
                self.retry_count += 1
                self.total_retry += 1
            except RuntimeWarning:
                self.retry_count += 1
                self.total_retry += 1

    def check(self, run_f, check_f, expected_val, r_args=None, r_kwargs=None, c_args=None, c_kwargs=None):
        self.retry_count = 0
        self.run_count += 1
        run_args = r_args if r_args else []
        run_kwargs = r_kwargs if r_kwargs else {}
        chk_args = c_args if c_args else []
        chk_kwargs = c_kwargs if c_kwargs else {}
        for i in range(0, self.retry):
            try:
                run_f(*run_args, **run_kwargs)
                if (check_f(*chk_args, **chk_kwargs) == expected_val):
                    if (i > self.inforce_retry):
                        break
                else:
                    self.retry_count += 1
                    self.total_retry += 1
            except RuntimeError:
                self.retry_count += 1
                self.total_retry += 1
            except RuntimeWarning:
                self.retry_count += 1
                self.total_retry += 1

    def only(self, run_f,  r_args=None, r_kwargs=None):
        self.retry_count = 0
        self.run_count += 1
        run_args = r_args if r_args else []
        run_kwargs = r_kwargs if r_kwargs else {}
        for i in range(0, self.retry):
            try:
                run_f(*run_args, **run_kwargs)
                if (i > self.inforce_retry):
                    break
            except RuntimeError:
                self.retry_count += 1
                self.total_retry += 1
            except RuntimeWarning:
                self.retry_count += 1
                self.total_retry += 1

    def is_successful(self):
        return self.retry_count < self.retry

    def is_totally_successful(self):
        return self.total_retry < (self.retry*self.run_count)

class FeeInit(object):
    def __init__(self, hostname, fee_list):
        self.d = client.Dam(0, "%s:50051" % (hostname))
        self.hostname = hostname
        self.fee_list = fee_list
        self.fee = []
        for i in self.fee_list:
            self.fee.append(fee(i, backend=backend, ip_addr="%s:50051" % (hostname)))

    def disable_elinks(self, ff):

        # keep track of unconfigured sampas and elinks
        skip_sampa = []
        lower_elinks = 0
        upper_elinks = 0

        # check which sampa is properly configure by trying to read pre_trigger value
        retry = Retry(inforce_retry=1)
        for s in ff.sampa:
            pre_trigger = retry.read(s.get_pre_trigger)
            if not retry.is_successful():
                print("Can't get pre trigger for ",s)
                skip_sampa.append(s)
                if (ss >= 0 and ss <= 3):
                    lower_elinks |= (0b1111 << ss)
                elif (ss >= 4 and ss <= 7):
                    upper_elinks |= (0b1111 << ss)

        # Disable trigger
        ff.reg_write(0x213, 0x0)

        # Disable elink
        ff.reg_write(0x200, 0x0)
        ff.reg_write(0x201, 0x0)

        # Hold elinks in reset
        ff.reg_write(0x210, 0xffff)
        ff.reg_write(0x211, 0xffff)

        # Enable elinks (lower the reset)
        ff.reg_write(0x210, lower_elinks)
        ff.reg_write(0x211, upper_elinks)

        return 0

   def enable_elinks(self, ff):

        # Enable the Elinks which have established lock
        ff.reg_write(0x200, ff.reg_read(0x302))
        ff.reg_write(0x201, ff.reg_read(0x303))

        # Enable trigger
        ff.reg_write(0x213, 0x1)

        return 0

    def do_fee_config(self, args):

        skipped = []
        for i, f in enumerate(self.fee):
            if ((self.d.reg.fee_reply[f.fee_addr].rx_ready != 1) or (f.board_sn() == 0)):
                skipped.append(f.fee_addr)
                continue
            print(" %s - FEE: %02i - disabling" % (self.hostname, f.fee_addr))#, end='\r')
            self.disable_elinks(f);

        time.sleep(1)
        for i, f in enumerate(self.fee):
            if ((self.d.reg.fee_reply[f.fee_addr].rx_ready != 1) or (f.board_sn() == 0)):
              continue;
            print(" %s - FEE: %02i - re-enabling" % (self.hostname, f.fee_addr))#, end='\r')
            self.enable_elinks(f);

        return skipped

def fee_init_exec(host, fee_list, args):
    fee_init = FeeInit(host, fee_list)
    skipped = fee_init.do_fee_config(args)

    if (len(skipped) > 0):
      print("FEEs skipped:", skipped)

    return 0

if __name__ == "__main__":

    print( "running fee_reset_elinks.py" )

    rlookup = {'R2': [0, 1, 11, 12, 14, 15, 18, 19],
               'R1': [2, 3, 4, 13, 16, 17],
               'R3': [5, 6, 7, 8, 9, 10, 20, 21, 22, 23, 24, 25],
               'TPOT' : [0, 1, 5, 6, 7, 8, 9, 12, 14, 15, 18, 19, 21, 23, 24, 25]}
#               'TPOT' : [0, 1, 5, 6, 7, 8, 9, 11, 12, 14, 15, 18, 19, 23, 24, 25]}

    argp = argparse.ArgumentParser()
    argp.add_argument("-f", "--fee", nargs='*', type=int, default=range(0, 26))
    argp.add_argument("-r", "--region", type=str, choices=["R1", "R2", "R3", "TPOT"])
    argp.add_argument("-c", "--connect", type=str, nargs='*', default="localhost")
    argp.add_argument("--connect-tpc", action='store_true', default=False)
    argp.add_argument("--connect-tpot", action='store_true', default=False)
    argp.add_argument("--reset-sampa", action='store_true', default=False)

    args = argp.parse_args()

    if args.region:
        fee_list = rlookup[args.region]
    else:
        fee_list = args.fee

    hostlist = args.connect
    if args.connect == 'localhost':
        hostlist = [args.connect]

    if args.connect_tpc:
        hostlist = []
        for i in range(0, 24):
            hostlist.append("ebdc%02i.sphenix.bnl.gov" % i)
    if args.connect_tpot:
        hostlist = []
        hostlist.append("ebdc39.sphenix.bnl.gov")

    print( "fee_list: ",fee_list )

    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
        future_to_fee = {executor.submit(fee_init_exec, host, fee_list, args): host for host in hostlist}
        for future in concurrent.futures.as_completed(future_to_fee):
            ret = future_to_fee[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (ret, exc))

