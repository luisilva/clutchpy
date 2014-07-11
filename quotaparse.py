# Script to pull out xfs quota data in to a spreadsheet
# Writen by Luis Silva 03-14-2012
#
import os
import xlwt
#
wb = xlwt.Workbook() #open workbook
ws = wb.add_sheet('raw_data') # add sheet
a=[] # start an empty array
rptout = os.popen('xfs_quota -x -c "report -pN"') # run os command and collect out put to rptout
for lines in rptout.readlines(): # loop through output strip out new line character and break it up by spaces
	lines = lines.strip("\n")
	cdata = lines.split(" ")
	for column in cdata: # get rid of empty spaces and put it all into and array
		if len(column) > 0 :
			a.append(column)
col=0 
row = 1
headings = ["Project ID","Actual Use", "Soft Quota","Hard Quota","Warn/Grace"]
x=0
for things in headings: # Write out headings
	ws.write(0,x, things)
	x=x+1
for items in a: # Loop through the array of items and write 5 times accross then go to the next row.
	if col==5:
		col=0
		row = row + 1
	else:
		ws.write(row,col,items)
		print items
		col=col+1
wb.save('nssdeep.xls')

				
			
				
			
	
