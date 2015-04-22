#!/usr/bin/python

from boto.glacier.layer1 import Layer1
from boto.glacier.concurrent import ConcurrentUploader
import argparse,logging,os,csv,sys

class glacier_freeze:
  def __init__(self):
      self.argparser = self.argparser()
      self.parsecreds = self.parsecreds()
      self.freeze = self.freeze()
      #self.validatedata = self.validatedata()
      
  def argparser(self):
      #Setting up parsing options for inputting data
      parser = argparse.ArgumentParser(description="Uploads file to glacier")
      parser.add_argument("-a", "--archive-dir", required=True, help="file to be archived") 
      parser.add_argument("-c", "--creds", required=True, help="Path to Credential .csv file from amazon") 
      parser.add_argument("-n", "--vault-name", required=True, help="Name of the vault to upload to")
      parser.add_argument("-d", "--description", required=False, help="Optional descrition for the archive")
      parser.add_argument("-v", "--verbose", action='store_true',required=False, default=False,help="verbose output directory")
      parser.add_argument("-b", "--block-size", required=False, default=33554432, help="block size to write. Amazon default it 33554432")
      parser.add_argument("-p", "--proxy", required=False, default="rcsocks.rc.fas.harvard.edu:8888", help="override proxy settings default odyssey proxy setting are => rcproxy.rc.fas.harvard.edu:8888")

      args = parser.parse_args()
    
      self.archive_dir = args.archive_dir
      self.creds = args.creds
      self.verbose = args.verbose
      self.block_size=args.block_size
      self.vault_name = args.vault_name
      self.proxy_address = args.proxy.split(':')[0]
      self.proxy_port = args.proxy.split(':')[1]
      self.description = args.description
      #if there's no description we should just make it they name as the file name for the archve. 
      if self.description == None:
          self.description = self.archive_dir
      
      debug = args.verbose
      log_level = logging.INFO
      if debug == True:
        log_level = logging.DEBUG
      logging.basicConfig(filename="glacier.log", level=log_level, format=LOG_FORMAT)

      logger.debug(" ".join(sys.argv))
        
  def parsecreds(self): # getting credentials from CSV file assigning them to variables
      if not os.path.exists(self.creds):
          logger.critical("credential file does not exists => %s" % self.creds)
          sys.exit()
      else:
          with open(self.creds) as csvfile:
              reader = csv.DictReader(csvfile)
              for row in reader:
                  self.glacier_users = row['User Name']
                  self.glacier_key_id = row['Access Key Id']
                  self.glacier_secret_key = row['Secret Access Key']

  def freeze(self):
      if not os.path.exists(self.archive_dir):
          logger.critical("archive file does not exists => %s" % self.archive_dir)
          sys.exit()
      else:
          self.glacier_layer1 = Layer1(aws_access_key_id=self.glacier_key_id, aws_secret_access_key=self.glacier_secret_key)
          self.glacier_upload = ConcurrentUploader(self.glacier_layer1, self.vault_name, self.block_size)
          logger.info("pushing data to glacier... => %s" % self.glacier_upload)
          self.archive_id = self.glacier_upload.upload(self.archive_dir,self.description)
          logger.info("Sucess! archive id is => %s" % self.archive_id)
          print "Sucess! archive id is => %s \nPlease allow up to 4 hrs before checking archive" % self.archive_id

if __name__ == '__main__':
    # set log formatting
    LOG_FORMAT = "[%(asctime)s][%(levelname)s] - %(name)s - %(message)s"
    logger = logging.getLogger('glacier.log')
    glacier_freeze()
    
