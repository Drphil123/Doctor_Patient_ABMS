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
        path_to_patient = self.locate_patient()
        if path_to_patient:
            # Assuming path_to_patient is a list of grid positions leading to the patient
            # Move the doctor to the next position in the path
            # Note: You might need to adjust this logic depending on how you handle agent movements
            next_position = path_to_patient[0]
            self.model.grid.move_agent(self, next_position)
            print(f"Doctor {self.unique_id} moving to {next_position} towards patient")
        self.treat_patient()

    def locate_patient(self):
        all_cells = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=15)
        all_agents = self.model.grid.get_cell_list_contents(all_cells)
        alive_patients = [agent for agent in all_agents if isinstance(agent, PatientAgent) and agent.state == ALIVE]

        # Sort alive patients by TTL to prioritize urgent care
        sorted_patients_by_ttl = sorted(alive_patients, key=lambda patient: patient.TTL)

        for patient in sorted_patients_by_ttl:
            start_node = Node(None, self.pos)
            goal_node = Node(None, patient.pos)
            path = self.a_star_search(start_node, goal_node)
            if path:
                return path
        return None

    def a_star_search(self, start, end):
        open_list = [start]
        closed_list = []

        while len(open_list) > 0:
            current_node = min(open_list, key=lambda node: node.f)
            open_list.remove(current_node)
            closed_list.append(current_node)

            if current_node.position == end.position:
                path = []
                while current_node is not None:
                    path.append(current_node.position)
                    current_node = current_node.parent
                return path[::-1]  # Path found

            children = []
            for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

                if not (0 <= node_position[0] < WIDTH) or not (0 <= node_position[1] < HEIGHT):
                    continue

                if self.model.grid.is_cell_occupied(node_position) and node_position != end.position:
                    continue

                new_node = Node(current_node, node_position)
                children.append(new_node)

            for child in children:
                if any(child.position == closed_node.position for closed_node in closed_list):
                    continue

                child.g = current_node.g + 1
                child.h = abs(child.position[0] - end.position[0]) + abs(child.position[1] - end.position[1])
                child.f = child.g + child.h

                if any(open_node.position == child.position and child.g > open_node.g for open_node in open_list):
                    continue

                open_list.append(child)
        return None


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