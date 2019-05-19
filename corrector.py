# -*- coding:utf-8 -*-
import os
import re
root = '.'
for fn in os.listdir(root):
	bn, ext = os.path.splitext(fn)
	if ext=='.txt':
		correct = 0
		tot = 0
		ss = 0
		with open(fn) as fd:
			for row in fd.readlines():
				row = re.split(r'[\s]+', row.strip())
				if len(row):
					if len(row)==1 or len(row)==2 and row[1][0:2]=='-s':
						correct += 1
						if len(row)==2 and row[1][0:2]=='-s':
							ss += 1
					tot += 1
		if tot:
			print('%s: %.2f%% %d out of %d are correct (-s %d)'%(bn, correct*100./tot, correct, tot, ss))
