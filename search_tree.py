#Search Tree
#Want to perform a depth-first type search
import Queue
import copy
SUCCESS = 1
NO_SUCCESS = 0

			
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
	
def cmp_same(mat_a,mat_b):
	for i in range(9):
		for j in range(9):
			val1 = mat_a[i][j].value
			val2 = mat_b[i][j].value
			if val1 != val2:
				return False
	return True
class Node:
	def __init__(self,parent,state,action):
		self.state = state
		self.parent = parent
		self.expanded = False
		self.children = Queue.Queue()
		self.action = action #Action is the (rect,val) that produced this state
	
class SearchTree:
	def __init__(self, start_state, goal_state, solver):
		self.solver = solver #just call solver functions from here
		self.state = start_state
		self.root = Node(None,start_state,None)
		self.current_node = self.root
		self.goal_state = goal_state
		self.action_list = [] #list of all states passed, 
		
	#make sure to check if node has been visited or not before calling this!!!
	def expand_node(self,current_node):
		(cell,sset) = self.solver.find_next_cell(current_node.state)
		if sset == None:
			return None #?
		possibles = set(range(1,10)) - sset
		for i in possibles:
			new_state = copy.deepcopy(current_node.state)
			new_cell = new_state[cell.i][cell.j]
			new_cell.set_value(None,i)
			if not self.solver.is_valid_move(new_cell,new_state):
				new_cell.set_value(None,0)
			else:
				node = Node(current_node,new_state,(self.solver.board_matrix[cell.i][cell.j],i))
				node.action = (self.solver.board_matrix[cell.i][cell.j],i)
				current_node.children.put(node)
		current_node.expanded = True
	def do_search(self):
		return self.search(self.root,self.state)
		
	def search(self,node,state):
		self.solver.moves+=1
		self.current_node = node
		self.action_list.append(node)
		if self.solver.is_done(state):	
			return True
		if not node.expanded:
			self.expand_node(node)
			node.expanded = True
		while not node.children.empty():
			next_node = node.children.get()
			
			res = self.search(next_node,next_node.state)
			mat = board_to_matrix(state)
			
			if res == False:
				if len(self.action_list) > 0:
					self.action_list.pop()
			else:
				return True
			
		#if children is empty
		#Only need this if we're not comparing to the solution board...
		
		return False
		#Could return false here and then pop() inside loop
def main():
	pass
if __name__ == "__main__":
	main()