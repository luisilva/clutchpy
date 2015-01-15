#!/usr/bin/python

# Author Luis Silva 01-14-2015

## used for gathering contact information for the multiple shares on the isilon

# This should be run on sa01 as it has access to both isilon systems


import os,sys,string,sh
from datetime import datetime
import time

def get_share_names():
    rootifs=["/net/rcstore/ifs/rc_labs", "/net/rcstore02/ifs/rc_labs"]
    rc_lab_dirs =[]
    for isi in rootifs:
        #rc_lab_dirs.append(sh.ls(isi))
        for dir in sh.ls(isi).split():
            rc_lab_dirs.append(dir)
    return rc_lab_dirs
    
def crawl_share_groups(share_names):
    for share in share_names:
        print share
    
#def get_share_location():
    
#def get_

if __name__=='__main__':
    ## asumptions all things are under /net/rcstore[|02]/ifs/[rc_admin|rc_labs]
    share_names = get_share_names()
    crawl_share_groups(share_names)