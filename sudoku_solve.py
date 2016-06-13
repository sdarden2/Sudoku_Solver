#File reader
#fin is the open file
import sys
from solver import *

alnum = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
zero_mat = [[0 for i in range(9)] for i in range(9)]
def read_next_matrix(fin):
	mat = []
	for i in range(9):
		line = fin.readline().strip()
		l = line.split(',')
		if len(l) != 9:
			return None
		for i in range(len(l)):
			if l[i] == '':
				l[i] = 0
			else:
				l[i] = int(l[i])
		mat.append(l)
		
	return mat
def main():
	if len(sys.argv) < 2:
		print "Usage %s <file containing matrices> to solve" %(sys.argv[0])
		return 0
	if sys.argv[1][0] in alnum:
		f = file(sys.argv[1],'r')
	else:
		print "Invalid filename"
		return 0
	ma = 0
	while True:
		ma = read_next_matrix(f)
		if ma == None:
			return
		solver = Solver(ma,zero_mat)
		res = solver.solve()
		res.print_report()
	f.close()
	
	
if __name__ == "__main__":
	main()