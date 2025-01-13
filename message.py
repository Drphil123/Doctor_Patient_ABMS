import mesa
import seaborn
import numpy
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
			elif agent.TTL == 100:
				num_saved += 1
	return num_saved / (num_deaths + num_saved) if num_deaths > 0 else 1

class PatientAgent(mesa.Agent):
	def __init__(self, unique_id, model, init_state=ALIVE):
		super().__init__(unique_id, model)
		self.injury_level = random.randint(2, 10)
		self.TTL = int(99 / self.injury_level)
		self.state = init_state
		self.type = PATIENT

	def step(self):
		if self.TTL <= 0:
			self.injury_level = 0
			self.state = DEAD
		else:
			self.TTL = self.TTL - int(self.injury_level / 2)
	
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
			print(f"**moving doctor to {path_to_patient[1]}**")
			self.model.grid.move_agent(self, path_to_patient[1])
			self.treat_patient()
		else:
			print("no path found!")
	
	def locate_patient(self):
		all_cells = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False, radius=15)
		all_agents = self.model.grid.get_cell_list_contents(all_cells)
		alive_patients = [agent for agent in all_agents if agent.type == PATIENT and agent.state == ALIVE and agent.injury_level > 0]
		sorted_patients_by_ttl = sorted(alive_patients, key=lambda x: x.TTL)

		for patient in sorted_patients_by_ttl:
			start = Node(None, self.pos)
			goal = Node(None, patient.pos)
			open_list = []
			closed_list = []
			heapq.heapify(open_list)
			heapq.heappush(open_list, start)

			while open_list:
				current_node = heapq.heappop(open_list)
				closed_list.append(current_node)

				if current_node.position == goal.position:
					path = self.reconstruct_path(current_node)
					survival_prediction = self.estimate_survivability(patient, path)
					print(f"Surival prediction for patient {str(patient.unique_id)}: {survival_prediction}, Location: {str(patient.pos)}, Injury level: {str(patient.injury_level)}, TTL: {str(patient.TTL)}")
					if survival_prediction >= 0:
						print(f"Doctor chose patient {str(patient.unique_id)}")
						return path
					else:
						print("Moving to next patient")
						break  # Check next patient if this one can't be reached in time.

				children = self.generate_children(current_node, closed_list)
				for child in children:
					if not any(child.position == open_node.position and child.g >= open_node.g for open_node in open_list):
						heapq.heappush(open_list, child)

		return None

	def generate_children(self, current_node, closed_list):
		children = []
		for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # Adjacent squares
			node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

			if node_position[0] >= WIDTH or node_position[0] < 0 or node_position[1] >= HEIGHT or node_position[1] < 0:
				continue

			if any(closed_node.position == node_position for closed_node in closed_list):
				continue

			new_node = Node(current_node, node_position)
			children.append(new_node)
		return children

	def reconstruct_path(self, current_node):
		path = []
		while current_node is not None:
			path.append(current_node.position)
			current_node = current_node.parent
		return path[::-1]

	def treat_patient(self):
		cell_mates = self.model.grid.get_cell_list_contents([self.pos])
		for mate in cell_mates:
			if mate.type == PATIENT:
				mate.injury_level = 0
				mate.TTL = 100
				break
	
	# doctor agent estimates if he can reach the patient before it dies
	def estimate_survivability(self, patient, path):
		estimated_time_of_death = (int)(patient.TTL / (patient.injury_level / 2)) # roughly how many steps the patient has left before death
		print(f"steps left before death for patient {str(patient.unique_id)}: {estimated_time_of_death}")
		print(f"path length: {len(path) - 1}")
		survival_prediction = estimated_time_of_death - (len(path) - 1)
		return survival_prediction


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
		print("\n---------- NEW STEP ----------\n")
		self.datacollector.collect(self) # start the data collector
		self.schedule.step() # randomly call step function of each agent once per model step

class Node():
	def __init__(self, parent=None, position=None):
		self.parent = parent
		self.position = position
		self.g = 0  # Cost from start to current node
		self.h = 0  # Estimated cost from current to end
		self.f = 0  # Total cost

	def __lt__(self, other):
		# This method allows nodes to be compared based on their f value
		# It's used by the heapq to maintain the min heap based on node f value
		return self.f < other.f

	def __gt__(self, other):
		# Similar to __lt__, but for greater than comparison
		return self.f > other.f

