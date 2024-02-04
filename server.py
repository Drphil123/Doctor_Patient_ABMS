import mesa

from doctor_patient_model import DoctorPatientModel as dpm

def agent_portrayal(agent):
	portrayal = {"Shape": "circle", "Filled": "true", "r": 0.5, "Layer": 0, "Color": "rgb(255, 0, 0)"}

	# shape and colors for patients
	if agent.type == 3:
		if agent.state == 1:
			if agent.TTL >= 91 and agent.TTL <= 100:
				portrayal["Shape"] = "circle"
				portrayal["Filled"] = "true"
				portrayal["r"] = 0.6
				portrayal["Color"] = "rgb(247, 247, 0)"
				portrayal["Layer"] = 0
			elif agent.TTL >= 81 and agent.TTL <= 90:
				portrayal["Shape"] = "circle"
				portrayal["Filled"] = "true"
				portrayal["r"] = 0.6
				portrayal["Color"] = "rgb(247, 207, 0)"
				portrayal["Layer"] = 0
			elif agent.TTL >= 71 and agent.TTL <= 80:
				portrayal["Shape"] = "circle"
				portrayal["Filled"] = "true"
				portrayal["r"] = 0.6
				portrayal["Color"] = "rgb(247, 187, 0)"
				portrayal["Layer"] = 0
			elif agent.TTL >= 61 and agent.TTL <= 70:
				portrayal["Shape"] = "circle"
				portrayal["Filled"] = "true"
				portrayal["r"] = 0.6
				portrayal["Color"] = "rgb(247, 167, 0)"
				portrayal["Layer"] = 0
			elif agent.TTL >= 51 and agent.TTL <= 60:
				portrayal["Shape"] = "circle"
				portrayal["Filled"] = "true"
				portrayal["r"] = 0.6
				portrayal["Color"] = "rgb(247, 147, 0)"
				portrayal["Layer"] = 0
			elif agent.TTL >= 41 and agent.TTL <= 50:
				portrayal["Shape"] = "circle"
				portrayal["Filled"] = "true"
				portrayal["r"] = 0.6
				portrayal["Color"] = "rgb(247, 107, 0)"
				portrayal["Layer"] = 0
			elif agent.TTL >= 31 and agent.TTL <= 40:
				portrayal["Shape"] = "circle"
				portrayal["Filled"] = "true"
				portrayal["r"] = 0.6
				portrayal["Color"] = "rgb(247, 87, 0)"
				portrayal["Layer"] = 0
			elif agent.TTL >= 21 and agent.TTL <= 30:
				portrayal["Shape"] = "circle"
				portrayal["Filled"] = "true"
				portrayal["r"] = 0.6
				portrayal["Color"] = "rgb(247, 57, 0)"
				portrayal["Layer"] = 0
			elif agent.TTL >= 11 and agent.TTL <= 20:
				portrayal["Shape"] = "circle"
				portrayal["Filled"] = "true"
				portrayal["r"] = 0.6
				portrayal["Color"] = "rgb(247, 27, 0)"
				portrayal["Layer"] = 0
			elif agent.TTL >= 1 and agent.TTL <= 10:
				portrayal["Shape"] = "circle"
				portrayal["Filled"] = "true"
				portrayal["r"] = 0.6
				portrayal["Color"] = "rgb(247, 7, 0)"
				portrayal["Layer"] = 0
		else:
			portrayal["Shape"] = "circle"
			portrayal["Filled"] = "true"
			portrayal["r"] = 0.6
			portrayal["Color"] = "black"
			portrayal["Layer"] = 0
	# shape and colors for doctors
	else:
		portrayal["Shape"] = "circle"
		portrayal["Filled"] = "true"
		portrayal["r"] = 0.4
		portrayal["Color"] = "blue"
		portrayal["Layer"] = 1

	return portrayal

grid = mesa.visualization.CanvasGrid(agent_portrayal, 15, 15, 500, 500) # grid to draw the agents
chart = mesa.visualization.ChartModule([{"Label": "Doctor Efficiency", "Color": "rgb(247, 50, 0)"}], data_collector_name = "datacollector")

model_params = {
    "P": mesa.visualization.Slider(
        "Number of patient agents",
        2,
        2,
        20,
        1,
        description="Choose how many patient agents to include in the model",
    ),
    "width": 10,
    "height": 10,

    "D": mesa.visualization.Slider(
        "Number of doctor agents",
        2,
        1,
        1,
        1,
        description="Choose how many doctor agents to include in the model",
    ),
    "width": 10,
    "height": 10,
}

server = mesa.visualization.ModularServer(dpm, [grid, chart], "Doctor-Patient Model", model_params)
server.port = 8521











