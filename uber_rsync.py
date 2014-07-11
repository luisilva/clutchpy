#!/usr/bin/env python

import os
import sys
import glob
import shlex
import argparse
import logging
import collections
import subprocess
from shutil import copytree

LOG_FORMAT = "[%(asctime)s][%(levelname)s] - %(name)s - %(message)s"
logger = logging.getLogger('uber.rsync')

def walk_source_dir(source_dir):
  tree_list = []
  count = 0
  for dirpath, dirnames, filenames in os.walk(source_dir,topdown=False):
    if len(dirnames) == 0 :
      tree_list.append(dirpath)
    count +=1
    if count == 1000:
      return tree_list
      
def find_deepest_branch(relative_path_list):
  branch_depth = []
  for dirpath in relative_path_list:
    branch_depth.append(dirpath.count("/"))
  return max(branch_depth)
  
def check_path_exists(path):
  if not os.path.exists(path):
    logger.critical("Path does not exists => %s" % path)
    sys.exit(1)
  else:
    logger.debug("Path exists => %s" % path)
  return 
  
def order_paths_by_depth(path_list, max_depth):
  ordered_dict = {}
  for num in range(1,max_depth):
    order_dict = {num:[]}
  for dirpath in path_list:
    depth = dirpath.count("/")
    ordered_dict[depth].value().append(dirpath)
    #print depth, dirpath
  for k,v in ordered_dict.iteritems():
    print k,v
  return ordered_dict
  
def main():
  #Setting up parsing options for inputting data
  parser = argparse.ArgumentParser(description="Runs multiple rsyncs between source and destination in attempt to speed up mirror copy")
  parser.add_argument("-s", "--source-dir", required=True, help="source directory") 
  parser.add_argument("-d", "--dest-dir", required=True, help="destination directory") 
  parser.add_argument("-a", "--arguments", required=False, help="addition rsync arguments eg. A = extemded attrinutes or --log-file=FILE")  
  parser.add_argument("-b", "--debug", action='store_true',required=False, default=False,help="verbose output directory")
  parser.add_argument("-m", "--max-load", required=False, default=100, help="maxiumum acceptable load limit default value is 100")

  args = parser.parse_args()
  
  # Basic displaying of logging when debug flag is on
  debug = args.debug
  log_level = logging.INFO
  if debug == True:
    log_level = logging.DEBUG
  logging.basicConfig(level=log_level, format=LOG_FORMAT)

  logger.debug(" ".join(sys.argv))

  #print args => Namespace(arguments='Ava', debug=False, dest_dir='/test/directory', max_load='200', source_dir='/net/server_8/microchem/share_root/)'
  
  # grab args
  source_dir = args.source_dir
  dest_dir = args.dest_dir
  arguments = args.arguments
  max_load = args.max_load
  # check source and destination directory exists
  check_path_exists(source_dir)
  check_path_exists(dest_dir)
  #Call walk tree and get the deepest paths           
  tree_list = walk_source_dir(source_dir)
  #sort that list 
  tree_list_sorted = sorted(tree_list)
  #define empty list for all the relative paths
  relative_path_list =[]
  #itterate over sorted path list and strip out the root of the directory path 
  for dirpath in tree_list_sorted:
    relative_path = dirpath.strip('%s' % source_dir)  
    #print relative_path
    relative_path_list.append(relative_path)
    
  max_depth = find_deepest_branch(relative_path_list)  
  ordered_list = order_paths_by_depth(relative_path_list, max_depth)    
  for lines in ordered_list:
    print lines

if __name__ == "__main__":
    main()
