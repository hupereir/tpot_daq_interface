#!/bin/bash
#
# Init and clock sync the TPOT FEE/SAMPA after power on
# This is different than TPC, we run in local mode
#
# J. Kuczewski 31-MAR-2025

export GTMHOST=gtm0
vGTM=( 12 ) 
TPC_SAMPA_INIT_SCH=/home/phnxrc/operations/TPC/schedulers/tpc_sampa_init.sch
TPC_SYNC_CLK_RST_SAMPA_SCH=/home/phnxrc/operations/TPC/schedulers/tpc_sync_clk_rst_sampa.sch

function gtm_setup_mode {
    # This should setup in local mode and disables lvl1 accepts
    for i in "${vGTM[@]}"
    do
        /home/repo/Debian/bin/gl1_gtm_client gtm_enable $i
        /home/repo/Debian/bin/gl1_gtm_client gtm_set_mode $i 0
        /home/repo/Debian/bin/gl1_gtm_client gtm_set_accept_l1 $i 0
    done
}

function gtm_exec {
    /home/repo/Debian/bin/gl1_gtm_client gtm_startrun ${vGTM[0]}
    sleep 1
    /home/repo/Debian/bin/gl1_gtm_client gtm_stop ${vGTM[0]}
}

function gtm_load_sch {
    for i in "${vGTM[@]}"
    do
        /home/repo/Debian/bin/gl1_gtm_client gtm_load_modebits $i $1
    done
}

function gtm_set_fee_decoder {
    for i in "${vGTM[@]}"
    do
       /home/repo/Debian/bin/gl1_gtm_client gtm_set_register $i 0x8 $1
    done
}

# Set only vGTM in list to local
gtm_setup_mode

# Set FEE GTM decoder to alternate function 1
gtm_set_fee_decoder 0x01

# Send the SAMPA init command
gtm_load_sch $TPC_SAMPA_INIT_SCH
gtm_exec

# FIXME: Check for SAMPA PoR flags
sleep 60

# Send the BX/ADC Clock sync and reset SAMPA
gtm_load_sch $TPC_SYNC_CLK_RST_SAMPA_SCH
gtm_exec

# Normal GTM decoder
gtm_set_fee_decoder 0x00

