#Solver
#This will be the official solver program that 
#Uses whatever algorithm to solve the problem
#Next step: Remove solution matrix, so that the algorithm has less help
#Check neighbors to make sure move is legal instead of checking against solution matrix
from Tkinter import *
import random
import Queue
import copy
from search_tree import *
import time

#This first implementation will be to just be to create a sudoku board
BOARD_WIDTH = 800
BOARD_HEIGHT = 800
FONT = ("Courier New Bold", 26)

#Simple instance of to check if object is instance of class
def instanceOf(obj,cls):
	#takes an object and class
	c_name = getattr(cls,"__name__")
	if hasattr(obj,"__class__"):
		c = getattr(obj,"__class__")
		cn = getattr(c,"__name__")
		if cn == c_name:
			return True
		else:
			return False
	else:
		return False

			
def board_to_matrix(mat):
	#Takes a board_matrix of Rect object and convets to matrix of number values
	mat2 = []
	for i in range(9):
		row = []
		for j in range(9):
			row.append(mat[i][j].value)
		mat2.append(row)
		row = []
	return mat2
def print_matrix(mat):
	for i in mat:
		print i
def cmp_correct(mat_a,mat_b):
	for i in range(9):
		for j in range(9):
			val1 = mat_a[i][j].value
			val2 = mat_b[i][j].value
			if val1 != val2:
				if val1 == 0 or val2 == 0:
					continue
				else:
					return False
	return True
	
def cmp_same(mat_a,mat_b):
	for i in range(9):
		for j in range(9):
			val1 = mat_a[i][j].value
			val2 = mat_b[i][j].value
			if val1 != val2:
				return False
	return True
		
class Results:
	def __init__(self, init_squares_filled):
		self.moves = 0
		self.init_squares = init_squares_filled
		self.unfilled = 81 - self.init_squares
		self.filled_active = 0 #Number filled by solver
		self.is_correct = False
		self.current_matrix = None
		self.solution_matrix = None
		self.difference_matrix = None #Matrix of 1's and 0's 1 if the answer is correct, 0 if not
		self.time_started = time.clock()
		self.time_finished = 0
		self.time_elapsed = 0
	def fill_square(self):
		self.moves += 1
		self.filled_active +=1
		self.unfilled -=1 
	def find_difference_matrix(self):
		self.difference_matrix = []
		for i in range(9):
			row = []
			for j in range(9):
				if self.current_matrix[i][j] == self.solution_matrix[i][j]:
					row.append(1)
				else:
					row.append(0)
			self.difference_matrix.append(row)
			row = []
			
	def print_report(self):
		if self.is_correct:
			print "Correct Solution was found!"
			print "It took %d moves and %d squares were filled correctly" %(self.moves,self.filled_active)
			print_matrix(self.current_matrix)
		else:
			if self.difference_matrix == None:
				self.find_difference_matrix()
			print "The correct solution was NOT found"
			print "Solution board:\n"
			print_matrix(self.solution_matrix)
			print "\n"
			print "This board\n"
			print_matrix(self.current_matrix)
			print "\nDifference (1 is corect, 0 is incorrect)\n"
			print_matrix(self.difference_matrix)
			print "\n\nMoves: %d, Squares filled: %d" %(self.moves,self.filled_active)
			print "Missing squares: %d" %(self.unfilled)
		print "Took %.04f seconds to complete" %self.time_elapsed
		
		
class Solver:
	#init_board and solution_board are 2-dim matrices
		def __init__(self,init_board = None,solution_board = None):
			self.board_matrix = self.build_board(init_board)
			if solution_board != None:
				self.solution = self.build_board(solution_board)
			self.canvas = None #If the gui is provided, it will modify and add the correct canvas
			self.num_filled = self.find_num_filled()
			self.results = Results(self.num_filled)
			self.solution_list = [] #action sequence or precept, list of the form (Rect,val)
			self.moves = 0
			self.search_tree = SearchTree(self.board_matrix,self.solution,self)
		def find_num_filled(self):
			filled = 0
			for i in range(9):
				for j in range(9):
					if self.board_matrix[i][j].value != 0:
						filled += 1
			return filled 
		
		def is_complete(self,matrix):
			for i in range(9):
				for j in range(9):
					if matrix[i][j].value == 0:
						return False
			return True
		def is_done(self,matrix):
			return self.is_complete(matrix) and self.is_board_valid(matrix)
		def build_board(self,matrix):
			id = 1
			board = []
			for i in range(9):
				row = []
				for j in range(9):
					row.append(Rect(id,-1,-1,i,j,number_value = matrix[i][j]))
					id += 1
				board.append(row)
				row = []
			return board
		def print_matrix_info(self,mat):
			m = board_to_matrix(mat)
			m_n_count = []
			for i in range(9):
				row = []
				for j in range(9):
					row.append(len(self.build_set(mat[i][j],mat)))
				m_n_count.append(row)
				row = []
			print "MATRIX\n"
			for i in m:
				print i
			print "\nNeighbors"
			for i in m_n_count:
				print i
			print "\n"
			
		def get_set(self,square, matrix):
		#Gets the actual Rect objects as a set
			if square.value != 0:
				return []
			if not instanceOf(square,Rect):
				raise Exception
			row_set = [i for i in matrix[square.i] if i != 0]
			
			column_set = [matrix[k][square.j] for k in range(9)]
			square_set = []
			#Indices are 0-2, 3-5, 6-8 
			#Squares 1-3, then 4-6, then 7-9 left to right, top to bottom
			if square.i <= 2 and square.j <= 2:
				square_set = matrix[0][0:3] + matrix[1][0:3] + matrix[2][0:3]
				
			elif square.i <=2 and square.j >= 3 and square.j <= 5:
				square_set = matrix[0][3:6] + matrix[1][3:6] + matrix[2][3:6]
			elif square.i <= 2 and square.j >= 6:
				square_set = matrix[0][6:9] + matrix[1][6:9] + matrix[2][6:9]
			elif square.i >= 3 and square.i <= 5 and square.j <= 2:
				square_set = matrix[3][0:3] + matrix[4][0:3] + matrix[5][0:3]
			elif square.i >=3 and square.i <=5 and square.j >= 3 and square.j <= 5:
				square_set = matrix[3][3:6] + matrix[4][3:6] + matrix[5][3:6]
			elif square.i >=3 and square.i <= 5 and square.j >= 6:
				square_set = matrix[3][6:9] + matrix[4][6:9] + matrix[5][6:9]
			elif square.i >= 6 and square.j <= 2:
				square_set = matrix[6][0:3] + matrix[7][0:3] + matrix[8][0:3]
			elif square.i >=6 and square.j >= 3 and square.j <= 5:
				square_set = matrix[6][3:6] + matrix[7][3:6] + matrix[8][3:6]
			elif square.i >=6 and square.j >= 6:
				square_set = matrix[6][6:9] + matrix[7][6:9] + matrix[8][6:9]
			
			#Note, may want to use Rect ojects and may want to use just the values
			final_list = row_set + column_set + square_set
			return final_list
			
		def is_valid_move(self,square,matrix):
			if self.is_valid_row(square,matrix) and self.is_valid_column(square,matrix) and self.is_valid_square(square,matrix):
				return True
			else:
				return False
		
		def is_board_valid(self,matrix):
			for i in range(9):
				if not (self.is_valid_move(matrix[i][i],matrix)):
					return False
			return True
			
		def is_valid_row(self,square,matrix):
			row = [t.value for t in matrix[square.i]]
			for i in range(row.count(0)):
				row.remove(0)
			if len(set(row)) == len(row):
				return True
			else:
				return False
		def is_valid_column(self,square,matrix):
			col = [matrix[k][square.j].value for k in range(9)]
			for i in range(col.count(0)):
				col.remove(0)
			if len(set(col)) == len(col):
				return True
			else:
				return False
		def is_valid_square(self,square,matrix):
			square_set = []
			#Indices are 0-2, 3-5, 6-8 
			#Squares 1-3, then 4-6, then 7-9 left to right, top to bottom
			if square.i <= 2 and square.j <= 2:
				square_set = matrix[0][0:3] + matrix[1][0:3] + matrix[2][0:3]
				
			elif square.i <=2 and square.j >= 3 and square.j <= 5:
				square_set = matrix[0][3:6] + matrix[1][3:6] + matrix[2][3:6]
			elif square.i <= 2 and square.j >= 6:
				square_set = matrix[0][6:9] + matrix[1][6:9] + matrix[2][6:9]
			elif square.i >= 3 and square.i <= 5 and square.j <= 2:
				square_set = matrix[3][0:3] + matrix[4][0:3] + matrix[5][0:3]
			elif square.i >=3 and square.i <=5 and square.j >= 3 and square.j <= 5:
				square_set = matrix[3][3:6] + matrix[4][3:6] + matrix[5][3:6]
			elif square.i >=3 and square.i <= 5 and square.j >= 6:
				square_set = matrix[3][6:9] + matrix[4][6:9] + matrix[5][6:9]
			elif square.i >= 6 and square.j <= 2:
				square_set = matrix[6][0:3] + matrix[7][0:3] + matrix[8][0:3]
			elif square.i >=6 and square.j >= 3 and square.j <= 5:
				square_set = matrix[6][3:6] + matrix[7][3:6] + matrix[8][3:6]
			elif square.i >=6 and square.j >= 6:
				square_set = matrix[6][6:9] + matrix[7][6:9] + matrix[8][6:9]
			
			square_set = [i.value for i in square_set]
			
			for i in range(square_set.count(0)):
				square_set.remove(0)
			if len(set(square_set)) == len(square_set):
				return True
			else:
				return False
			
		def build_set(self,square,matrix):
			#square is a Rectangle object
			final_list = self.get_set(square,matrix)
			if len(final_list) > 0:
				
				final_set = set([i.value for i in final_list])
				if 0 in final_set:
					final_set.remove(0)
				return final_set
			else:
				return set([])
		
		def check_solution(self):
			for t in self.solution_list:	
				action = t.action
				if action != None:
					i = action[0].i
					j = action[0].j
					val = action[1]
					cell = self.board_matrix[i][j]
					cell.set_value(self.canvas,val,color="red")
					self.num_filled += 1
			self.num_filled = self.find_num_filled() #should be up to date, but double checking
			self.results.filled_active = self.num_filled - self.results.init_squares
			self.results.unfilled = 81 - self.num_filled
			self.results.is_correct = self.is_done(self.board_matrix)
			self.results.current_matrix = board_to_matrix(self.board_matrix)
			self.results.solution_matrix = board_to_matrix(self.solution)
			self.results.moves = self.moves
			self.results.time_finished = time.clock()
			self.results.time_elapsed = self.results.time_finished - self.results.time_started
			return self.results
		
			
		def solve(self):
			KILL_COUNT = 0 #Set to terminate if over X number of iterations
			#algorithm 1
			full_set = set(range(1,10))
			queue = Queue.Queue()
			#Add all empty cells to queue
			for i in range(9):
				for j in range(9):
					if self.board_matrix[i][j].value == 0:
						queue.put(self.board_matrix[i][j])
			
			
			while (not self.is_complete(self.board_matrix)) and queue.qsize() > 0:
				#Algorithm to fill in squares
				box = queue.get()
				
				sset = self.build_set(box,self.board_matrix)
				print sset
				
				if len(sset) < 8:
					ret = self.search_tree.do_search()
					if ret == True:
						self.solution_list = self.search_tree.action_list
						print "Got a solution!!!"
						#for i in self.solution_list:
						#	print i
						#	r = self.board_matrix[i[0].i,i[0].j]
						#	v = i[1]
						#	r.set_value(self.canvas,v,color='red')
						break
				elif len(sset) == 8:
					val = (full_set - sset).pop()
					box.set_value(self.canvas,val,color="red")
					self.results.fill_square()
					self.num_filled += 1
					self.moves += 1
				else:
					queue.put(box)
				KILL_COUNT += 1
				if KILL_COUNT >= 800:
					break
					
			return self.check_solution()
		
		def find_next_cell(self,state):
			#Finds the next suitable cell at the current state
			#The cell with the lowest possible number of options
			max_cell = None
			max_val = -1
			max_sset = None
			for i in range(9):
				for j in range(9):
					cell = state[i][j]
					if cell.value != 0:
						continue
					sset = self.build_set(cell,state)
					size = len(sset)
					if size > max_val and size <= 8 and cell.value == 0:
						max_val = size #not needed
						max_cell = cell
						max_sset = sset
			
			return max_cell,max_sset
			#Note this returns the cell and the state associated with the cell
			
		#state will just be the inital board, then we'll pass copies rather than 
		def first_search(self, state):
			
			cell,sset = self.find_next_cell(state)
			if sset == None:
				return True #Need to work on that
			new_state = copy.deepcopy(state)
			
			possible_vals = list(set(range(1,10)) - sset)
			
			for val in possible_vals:
				
				new_state[cell.i][cell.j].set_value(None,val)
				
				if cmp_same(new_state,self.solution): #we'll still use this to check correctness
					self.moves += 1
					self.solution_list.append((cell,val))
					return True #End program, found solution!
				#elif self.solution[cell.i][cell.j].value != val: #chaning this
				#	self.moves += 1
				#	new_state[cell.i][cell.j].set_value(None,0) #Go back
				#	continue
				elif not (self.is_board_valid(new_state)):
					self.moves +=1
					new_state[cell.i][cell.j].set_value(None,0)
					continue
				else:
					
					self.moves += 1
					self.solution_list.append((cell,val))
					return self.first_search(new_state)
		
			#See if this works
			new_state[cell.i][cell.j].set_value(None,0)
			
class Board(Frame):
	def __init__(self,size=9,master=None, solver=None):
		self.size = size
		self.solver = solver
		self.filled = 0 #Used to keep track of how many spaces are filled, having to modify each time we make a call to set_value
		self.board_matrix = solver.board_matrix
		self.solution_matrix = solver.solution
		Frame.__init__(self,master,{"width":BOARD_WIDTH,"height":BOARD_HEIGHT})
		self.canvas = Canvas(master=self, width=BOARD_WIDTH,height=BOARD_HEIGHT,bg="white")
		self.draw_board()
		self.canvas.pack()
		self.solver.canvas = self.canvas
	def isFilled(self):
		if self.filled == 81:
			return True
		return False
	
	
	def draw_board(self):
		row = []
		x1 = 0
		y1 = 0
		RECT_WIDTH = BOARD_WIDTH / 9.0
		RECT_HEIGHT = BOARD_HEIGHT / 9.0
		x2 = x1 + RECT_WIDTH
		y2 = y1 + RECT_HEIGHT
		
		for i in range(9): #Row
			for j in range(9): #Column
				if (j == 2 or j == 5):
					self.canvas.create_line(x2,0,x2,BOARD_HEIGHT, width=6)
				if (i == 2 or i == 5):
					self.canvas.create_line(0,y2,BOARD_WIDTH,y2,width = 6)
				rect = self.canvas.create_rectangle(x1,y1,x2,y2)
				centerx = (x2+x1)/2
				centery = (y2+y1)/2
				rect = self.board_matrix[i][j]
				rect.x = centerx
				rect.y = centery
								
				x1 = x2
				x2 += RECT_WIDTH

			y1 = y2
			y2 = y2 + RECT_HEIGHT
			x1 = 0
			x2 = x1 + RECT_WIDTH
			row = []
	def print_game_matrix(self):
		game_matrix = board_to_matrix(self.board_matrix)
		for i in game_matrix:
			print i
	def update_board(self):
		for i in range(9):
			for j in range(9):
				self.board_matrix[i][j].set_value(self.canvas,self.board_matrix[i][j].value)
	#Takes a 2 dim array that represent the board 9x9 and fills in the game board
	def set_board(self,b_mat):
		for i in range(9):
			for j in range(9):
				self.board_matrix[i][j].set_value(self.canvas,b_mat[i][j])
				if b_mat[i][j] != 0:
					self.filled += 1
		self.canvas.update()
		
	def solve(self):
		res = self.solver.solve()
		self.board_matrix = self.solver.board_matrix
		#self.update_board()
		return res
		
	
	
class Rect:
	def __init__(self,id,x_coord,y_coord,matrix_pos_i,matrix_pos_j,number_value=0):
		self.id = id #Canvas id to Tkinter
		self.value = number_value
		#i and j are the indices into the game matrix where this rectangle is located
		self.i = matrix_pos_i
		self.j = matrix_pos_j
		#Gives the center x and y coordinates on the canvas (location of rectangle)
		self.x = x_coord
		self.y = y_coord
		self.text_object = None
	def get_value(self):
		return self.value
	def get_id(self):
		return self.id
	def print_value(self):
		print self.value
	def print_id(self):
		print self.id
	def get_location(self):
		return (x,y)
	def set_value(self,canvas,value,color="black"):
		#Value must be an int
		#WARNING: Takes outside reference of canvas
		#Note: right now you are just adding text, not setting or erasing previously typed text
		#Need to fix that
		if canvas != None:
			if self.text_object == None:
				if value != 0:
					
					#Credit for finding how to color text: http://effbot.org/tkinterbook/canvas.htm
					self.text_object = canvas.create_text(self.x,self.y,text=str(value),font=FONT,fill=color)
			else:
				if value !=0:
					canvas.itemconfigure(self.text_object,font=FONT,fill=color,text=str(value))
			self.value = value
			canvas.update()
		else:
			self.value = value
	

	

	
def main():
	root = Tk()
	
	#m = random_mat()
	#Easy example to get it running
	#http://www.puzzles.ca/sudoku_puzzles/sudoku_easy_219.html problem 219
	"""
	m = [[0,0,0,2,0,0,0,0,5],
		 [8,0,0,0,0,9,0,0,4],
		 [0,0,0,1,8,0,0,2,0],
		 [3,0,0,0,0,0,5,0,9],
		 [5,0,0,0,0,0,0,7,0],
		 [0,6,0,0,0,0,0,4,0],
		 [0,0,0,0,0,0,0,0,6],
		 [0,0,1,0,3,4,9,8,0],
		 [9,2,0,6,5,0,0,0,3]
			]
	m_soln = [[1,3,6,2,4,7,8,9,5],
	 [8,7,2,5,6,9,1,3,4],
	 [4,9,5,1,8,3,6,2,7],
     [3,1,8,4,7,2,5,6,9],
	 [5,4,9,3,1,6,2,7,8],
	 [2,6,7,8,9,5,3,4,1],
	 [7,8,3,9,2,1,4,5,6],
	 [6,5,1,7,3,4,9,8,2],
	 [9,2,4,6,5,8,7,1,3]]
	"""	
	#Medium example		
	#http://www.puzzles.ca/sudoku_puzzles/sudoku_medium_217.html
	"""
	m = [[0,0,6,0,3,5,0,0,0],
		[0,7,8,0,0,0,0,0,9],
		[0,0,0,0,0,2,0,0,7],
		[4,0,0,0,0,0,6,0,0],
		[0,0,0,5,8,0,0,1,0],
		[1,8,0,0,6,0,0,2,0],
		[0,0,0,6,0,0,0,0,0],
		[5,0,4,0,0,7,0,0,0],
		[0,0,0,0,0,0,0,5,2]]
			
	m_soln = [[9,1,6,7,3,5,2,4,8],
			[2,7,8,4,1,6,5,3,9],
			[3,4,5,8,9,2,1,6,7],
			[4,5,9,2,7,1,6,8,3],
			[6,2,3,5,8,9,7,1,4],
			[1,8,7,3,6,4,9,2,5],
			[8,9,2,6,5,3,4,7,1],
			[5,3,4,1,2,7,8,9,6],
			[7,6,1,9,4,8,3,5,2]]
	
	"""
	#Medium Example
	#http://www.puzzles.ca/sudoku_puzzles/sudoku_medium_163.html
	"""
	m = [[0,0,0,4,0,0,0,6,0],
	[0,0,0,0,0,7,0,0,0],
	[5,8,0,0,0,9,3,0,0],
	[0,4,3,0,0,0,0,0,0],
	[7,0,0,8,0,0,0,0,0],
	[2,0,0,0,1,0,0,7,0],
	[0,6,0,5,0,0,2,0,4],
	[0,0,4,0,0,2,0,0,3],
	[0,0,0,0,0,3,0,0,5]]
	
	m_soln = [[9,3,7,4,5,8,1,6,2],
		[4,2,6,1,3,7,9,5,8],
		[5,8,1,2,6,9,3,4,7],
		[6,4,3,7,9,5,8,2,1],
		[7,1,5,8,2,6,4,3,9],
		[2,9,8,3,1,4,5,7,6],
		[3,6,9,5,7,1,2,8,4],
		[1,5,4,6,8,2,7,9,3],
		[8,7,2,9,4,3,6,1,5]]	
	"""
	"""
	#Another easy example with new algorithm (search tree)
	m = [[0,0,9,0,8,0,0,0,0],
	[0,3,0,5,0,0,0,0,0],
	[0,0,0,1,2,0,0,0,0],
	[3,0,4,0,0,0,0,0,0],
	[7,2,0,0,0,0,0,4,8],
	[0,0,0,6,4,7,0,5,0],
	[4,6,2,0,0,0,0,0,7],
	[1,0,0,0,0,0,0,8,6],
	[0,9,8,0,0,0,0,0,3]]
	
	m_soln =  [[6,1,9,7,8,4,2,3,5],
		[2,3,7,5,6,9,8,1,4],
		[8,4,5,1,2,3,6,7,9],
		[3,5,4,2,9,8,7,6,1],
		[7,2,6,3,1,5,9,4,8],
		[9,8,1,6,4,7,3,5,2],
		[4,6,2,8,3,1,5,9,7],
		[1,7,3,9,5,2,4,8,6],
		[5,9,8,4,7,6,1,2,3]]
		
	"""
	"""
	#Medium 3
	#Number #179 http://www.puzzles.ca/sudoku_puzzles/sudoku_medium_179.html
	
	m = [[6,0,0,9,0,0,0,0,0],
	[7,0,0,0,0,0,0,1,3],
	[0,0,0,0,0,4,2,0,0],
	[0,4,0,0,0,6,0,0,0],
	[0,6,2,0,8,3,0,0,0],
	[0,0,0,0,0,1,5,0,0],
	[4,0,0,0,0,0,1,0,2],
	[9,0,1,0,0,0,7,0,0],
	[0,0,0,5,0,0,0,0,0]]
	
	m_soln = [[6,1,3,9,2,7,8,5,4],
	[7,2,4,8,6,5,9,1,3],
	[8,9,5,1,3,4,2,6,7],
	[1,4,9,2,5,6,3,7,8],
	[5,6,2,7,8,3,4,9,1],
	[3,7,8,4,9,1,5,2,6],
	[4,5,6,3,7,9,1,8,2],
	[9,8,1,6,4,2,7,3,5],
	[2,3,7,5,1,8,6,4,9]]
	"""
	"""
	#Hard #215 http://www.puzzles.ca/sudoku_puzzles/sudoku_hard_215.html
	m = [[0,0,7,0,1,0,0,0,0],
	[0,0,0,0,6,0,7,9,0],
	[0,0,0,9,0,0,2,3,0],
	[0,6,0,0,0,0,0,0,8],
	[0,0,0,0,3,0,0,0,0],
	[5,0,4,0,9,0,0,0,0],
	[9,0,0,5,0,0,1,0,0],
	[0,8,0,0,0,2,0,0,0],
	[0,4,3,0,0,0,0,8,0]]
	"""
	"""
	#Hard Sudoku puzzle #216 http://www.puzzles.ca/sudoku_puzzles/sudoku_hard_215.html
	m = [[6,3,0,0,1,0,0,0,0],
	[0,0,0,0,2,0,0,0,0],
	[2,0,0,0,0,0,4,5,0],
	[0,0,0,0,0,0,0,6,0],
	[0,0,0,0,3,8,0,0,0],
	[0,1,0,0,0,0,0,0,3],
	[0,8,7,0,0,3,0,0,0],
	[0,6,0,9,5,0,0,3,0],
	[5,0,0,0,0,6,0,9,2]]
	"""
	"""
	#Hard puzzle #101 http://www.puzzles.ca/sudoku_puzzles/sudoku_hard_101.html
	m = [[7,0,0,0,0,9,0,2,0],
	[4,9,0,0,2,0,7,0,3],
	[0,0,0,0,0,8,5,0,0],
	[0,4,1,0,0,2,0,0,0],
	[0,0,0,9,0,0,1,3,6],
	[0,0,0,6,0,5,0,4,0],
	[8,3,0,0,0,0,0,1,5],
	[0,0,4,0,0,0,0,0,0],
	[2,0,0,0,0,7,0,9,0]]
	"""
	"""
	#Medium #121 http://www.puzzles.ca/sudoku_puzzles/sudoku_medium_121.html
	m = [[2,4,0,0,5,7,3,6,0],
		[0,0,0,0,0,8,0,0,9],
		[3,7,8,0,0,0,2,0,0],
		[0,6,0,0,4,1,7,0,2],
		[0,8,0,0,0,0,0,0,5],
		[0,0,0,0,0,5,0,1,0],
		[1,3,0,0,0,0,0,0,0],
		[0,5,0,0,0,3,0,2,6],
		[0,0,0,8,1,2,0,0,0]]
	"""
	"""
	#Apparently very difficult puzzle solved in 5 minutes by website: http://www.math.cornell.edu/~mec/Summer2009/meerkamp/Site/Solving_any_Sudoku_I.html
	
	m = [[0,0,6,0,0,8,5,0,0],
	[0,0,0,0,7,0,6,1,3],
	[0,0,0,0,0,0,0,0,9],
	[0,0,0,0,9,0,0,0,1],
	[0,0,1,0,0,0,8,0,0],
	[4,0,0,5,3,0,0,0,0],
	[1,0,7,0,5,3,0,0,0],
	[0,5,0,0,6,4,0,0,0],
	[3,0,0,1,0,0,0,6,0]]
	#Finished in .2 seconds, not bad
	"""
	
	#Trying very difficult one here: http://www.7sudoku.com/view-puzzle?date=20150830
	
	m = [[1,0,2,0,0,0,3,0,0],
	[0,0,0,3,4,0,1,0,0],
	[0,0,0,0,7,0,2,5,0],
	[0,0,9,0,2,0,0,0,4],
	[8,0,0,0,0,0,0,0,5],
	[5,0,0,0,3,0,7,0,0],
	[0,8,3,0,5,0,0,0,0],
	[0,0,1,0,8,7,0,0,0],
	[0,0,7,0,0,0,6,0,2]]
	
	#got it in .7
	m_soln = [[0 for i in range(9)] for i in range(9)]
	#b.set_board(m)
	solver = Solver(m,m_soln)
	b = Board(master=root,solver=solver)
	b.pack()
	b.update_board()
	b.print_game_matrix()
	res = b.solve()
	print "After finishing..."
	res.print_report()
	#print solver.solution_list
	root.mainloop()
if __name__ == "__main__":
	main()