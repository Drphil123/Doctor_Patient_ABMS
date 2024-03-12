import mesa

# Data visualization tools.
import seaborn

# Has multi-dimensional arrays and matrices. Has a large collection of
# mathematical functions to operate on these arrays.
import numpy

# Data manipulation and analysis.
import pandas

import random

import heapq

# Constants
ALIVE = 1
DEAD = 0
DOCTOR = 2
PATIENT = 3
WIDTH = 15
HEIGHT = 15

def calculate_doctor_efficiency(model):
	num_deaths = 0
	num_saved = 0

	for agent in model.schedule.agents:
		if agent.type == PATIENT:
			if agent.state == DEAD:
				num_deaths += 1
				#agent.remove() # remove the dead patient from the environment
			elif agent.TTL == 100:
				num_saved += 1

	if num_deaths > 0:
		return num_saved / (num_deaths + num_saved)
	else:
		return 1 

class PatientAgent(mesa.Agent):
	def __init__(self, unique_id, model, init_state = ALIVE):
		super().__init__(unique_id, model)
		self.injury_level = random.randint(1, 10) # set injury level of patient
		self.TTL = int(99 / self.injury_level) # how long the patient has to live (depends on how injured they are)
		self.state = init_state
		self.type = PATIENT

	def step(self):
		print(f"patient ID = {str(self.unique_id)}, injury level = {str(self.injury_level)}, TTL = {str(self.TTL)}")
		
		# if the patient's Time To Live is 0, we need to "kill" it
		# otherwise, we take an amount off of TTL proportinal to the level of injury
		if self.TTL <= 0:
			self.injury_level = 0
			self.state = DEAD
		else:
			self.TTL = self.TTL -  int(self.injury_level / 2) # change this function if needed to speed up/slow down the death rate of patients

	def get_injury_lvl(self, agent):
		return	agent.injury_level

class DoctorAgent(mesa.Agent):
	def __init__(self, unique_id, model):
		super().__init__(unique_id, model)
		self.speed = 5
		self.type = DOCTOR

	def step(self):
		#print(f"Hi, I am a doctor agent, you can call me {str(self.unique_id)}.")
		self.move()
		self.treat_patient()

	def move(self):
		# pos = agent tuple vairable that hold the x and y coodinates of the agent
		# moore = look at all 8 surrounding squares (false means only up/down/left/right)
		# include_center = include the center tile as a neighboring tile
		#possible_steps = self.model.grid.get_neighborhood(self.pos, moore = True, include_center = False)
		#new_position = self.random.choice(possible_steps)
		#self.model.grid.move_agent(self, new_position)
		#patient_location = self.locate_patient()
		path_to_patient = self.locate_patient()
		#self.model.grid.move_agent(self, patient_location)
		print(f"**moving doctor to {path_to_patient[1]}**")
		self.model.grid.move_agent(self, path_to_patient[1])

	def locate_patient(self):
		#all_patients = []
		all_cells = self.model.grid.get_neighborhood(self.pos, moore = True, include_center = False, radius = 15) # get a list of all cells within a 15 cell radius of the doctor agent
		all_agents = self.model.grid.get_cell_list_contents(all_cells) # get a list of all agents in list of all cells
		
		for agent in all_agents:
			if agent.type == DOCTOR or agent.state == DEAD: # only keep agents that are patients and alive in the list
				all_agents.remove(agent)

		# sort the list of patients by their injury level in decending order
		all_agents.sort(reverse = True, key = agent.get_injury_lvl)

		# return the x and y coordinates of the patient with the highest injury value
		#return all_agents[0].pos

		# use A* informed search algorithm to find best path to patient who needs treatment
		# create start and end nodes, add start node (the doctor's position) to the open list
		start = Node(None, self.pos)
		start.g = 0
		start.h = 0
		start.f = 0

		end = Node(None, all_agents[0].pos)
		end.g = 0
		end.h = 0
		end.f = 0

		open_list = [] # list of nodes for A* that we have not searched yet
		closed_list = [] # list of nodes for A* that we have searched
		
		# use heap to heapify the list of open nodes (should hopefully speed up algorithm)
		heapq.heapify(open_list)
		heapq.heappush(open_list, start)
	
		# loop until we find the goal node (the patient)
		while len(open_list) > 0:
			#print(f"open_list length = {str(len(open_list))}")
			c_node = heapq.heappop(open_list) # get current node from heap
			print(f"current node = {c_node.position}")
			closed_list.append(c_node)

			# if we found the goal node, back track all the way back to start node and store path in a list
			if c_node.position == end.position:
				print("found patient!!!!")
				path = []
				current = c_node

				while current is not None:
					path.append(current.position)
					current = current.parent

				return path[::-1]

			# generate all "child" nodes
			child_nodes = []
			neighbouring_squares = ((0, -1), (0, 1), (-1, 0), (1, 0),)

			# check all the neighbouring nodes around the current node to see which one has the lowest cost
			for position_new in neighbouring_squares:
				n_position = (c_node.position[0] + position_new[0], c_node.position[1] + position_new[1])

				# make sure that the doctor can actually move to this cell
				# doctor can only move to same cell as patient when he is treating them, otherwise he must walk around them
				# therefore, we will not generate a child node for the path if there is a patient in that cell
				for agents in all_agents:
					if agent.pos == n_position:
						continue

				# create a new child node and append it to the list of children nodes
				new_node = Node(c_node,n_position)
				child_nodes.append(new_node)

			# iterate through all child nodes and only add them to open list if they have the lowest g cost
			for child in child_nodes:

				# if child is already on the closed list, simply continue to next child
				if len([child_closed for child_closed in closed_list if child_closed == child]) > 0:
					continue

				# calculate f, g and h values using Pythagorean Theorem (since doctor can move diagonaly as well)
				child.g = c_node.g + 1
				child.h = ((child.position[0] - end.position[0]) ** 2) + ((child.position[1] - end.position[1]) ** 2)
				child.f = child.g + child.h

				# do not add child to list of open nodes to explore if its g cost is greater than the g cost of nodes already on the list
				if len([all_open_nodes for all_open_nodes in open_list if child.position == all_open_nodes.position and child.g > all_open_nodes.g]) > 0:
					continue

				#open_list.append(child)
				heapq.heappush(open_list, child)

		#return full_path.reverse()


	def treat_patient(self):
		cell_mates = self.model.grid.get_cell_list_contents([self.pos])
		cell_mates.pop(cell_mates.index(self)) # make sure that doctor does not randomly choose to treat himself

		if len(cell_mates) >= 1:
			other = self.random.choice(cell_mates)
			other.injury_level = 0
			other.TTL = int(100)

class DoctorPatientModel(mesa.Model):
	def __init__(self, D, P, width, height):

		self.num_patient_agents = P # set the number of patient agents
		self.num_doctor_agents = D # set the number of doctor agents

		# set width and height of the graph
		width = WIDTH
		height = HEIGHT
		
		# need these two attributes to avoid AttributeException (they do absolutely nothing in this code)
		self._steps = 0
		self._time = 0
		
		# create scheduler and assign it to the model
		self.schedule = mesa.time.RandomActivation(self)
		
		# create a grid to place agents onto it
		# true makes the grid toroidal (wrap around the edges)
		# MultiGrid is a grid where multiple agents can be on the same cell
		self.grid = mesa.space.MultiGrid(width, height, True)

		# create patient agents
		for i in range(self.num_patient_agents):
			agent = PatientAgent(i, self)
			
			# add agent to the scheduler
			self.schedule.add(agent)

			# add agent to a random grid cell
			x = self.random.randrange(self.grid.width)
			y = self.random.randrange(self.grid.height)
			self.grid.place_agent(agent, (x, y))


		for i in range(self.num_patient_agents + 1, self.num_patient_agents + self.num_doctor_agents):
			agent = DoctorAgent(i, self)
			self.schedule.add(agent)

			# add agent to a random grid cell
			x = self.random.randrange(self.grid.width)
			y = self.random.randrange(self.grid.height)
			self.grid.place_agent(agent, (x, y))

		# create the data collector to save data
		self.datacollector = mesa.DataCollector(model_reporters={"Doctor Efficiency": calculate_doctor_efficiency}, agent_reporters={"Time To Live": "TTL"})

	def step(self):
		self.datacollector.collect(self) # start the data collector
		self.schedule.step() # randomly call step function of each agent once per model step

# need this extra class for A* to store values of g, h and f for A* calculations
class Node():
	def __init__(self, parent = None, position = None):
		self.parent = parent # link to parent node in the grid
		self.position = position # tuple of x and y coordinates of cell position in grid
		self.g = 0 # g = cost from current node to start node
		self.h = 0 # h = cost from current node to goal node
		self.f = 0 # f = sum of g and h

	# need to define this for the heap queue to work
	def __lt__(self, other):
		return self.f < other.f

	# need to define this for the heap queue to work
	def __gt__(self, other):
		return self.f > other.f


















