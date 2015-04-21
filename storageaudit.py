#!/usr/bin/python

import os,csv,pandas

class StorageData:
    def __init__(self):
	#self.raw_data = self.loadcsvdata()
	#self.rows = [list(r) for r in self.raw_data]
	#self.cols = [list(c) for c in cols
	self.cols = self.loadcsvpandastyle()
	#self.total
	#self.free
	#self.server

    def loadcsvdata(self):
	f = open('vgsrawsorted.csv')
	csv_f = csv.reader(f)
	allrows = []
	for row in csv_f:
  	  allrows.append(row)
	return allrows
	
    def loadcsvpandastyle(self):
	colnames = ['VG','PV','LV','SN','Attr','VSize','VFree']
	columns = pandas.read_csv('vgsrawsorted.csv', names=colnames)
	return columns

if __name__ == '__main__':
	sd = StorageData()
	print sd.cols

