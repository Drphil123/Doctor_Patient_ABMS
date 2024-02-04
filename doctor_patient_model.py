import mesa

# Data visualization tools.
import seaborn

# Has multi-dimensional arrays and matrices. Has a large collection of
# mathematical functions to operate on these arrays.
import numpy

# Data manipulation and analysis.
import pandas

import random

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
		self.TTL = int(100 / self.injury_level) # how long the patient has to live (depends on how injured they are)
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
			self.TTL = self.TTL -  self.injury_level

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
		# pos = agent vairable that hold the x and y coodinates of the agent
		# moore = look at all 8 surrounding squares (false means only up/down/left/right)
		# include_center = include the center tile as a neighboring tile
		#possible_steps = self.model.grid.get_neighborhood(self.pos, moore = True, include_center = False)
		#new_position = self.random.choice(possible_steps)
		#self.model.grid.move_agent(self, new_position)
		patient_location = self.locate_patient()
		self.model.grid.move_agent(self, patient_location)

	def locate_patient(self):
		#all_patients = []
		all_cells = self.model.grid.get_neighborhood(self.pos, moore = True, include_center = False, radius = 15) # get a list of all cells within a 10 cell radius of the doctor agent
		all_agents = self.model.grid.get_cell_list_contents(all_cells) # get a list of all agents in list of all cells
		
		for agent in all_agents:
			if agent.type == DOCTOR or agent.state == DEAD: # only keep agents that are patients and alive in the list
				all_agents.remove(agent)

		# sort the list of patients by their injury level in decending order
		all_agents.sort(reverse = True, key = agent.get_injury_lvl)

		# return the x and y coordinates of the patient with the highest injury value
		return all_agents[0].pos

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


















