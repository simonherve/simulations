import pandas as pd
import streamlit as st
import numpy as np
from plotly import graph_objs as go
import math


#=======================================================
def distance_tag(dist):

	if dist == "100":
		return "S100"
	elif dist == "300":
		return "S200"
	elif dist == "500":
		return "S300"
	elif dist == "700":
		return "S400"

def transformation(df):
    
    df = df.reset_index()
    df = pd.pivot_table(df, columns="index")
    df = df.reset_index()
    df = df.rename(columns={"index":"Np"})
    df["Np"] = pd.to_numeric(df["Np"])
    df = df.sort_values(by=["Np"])
    df = df.reset_index(drop=True)
    return df

def truck_tag(model):
	
	if (model == "M2") | (model == "M1"):
		return "PT50"
	elif model == "M3":
		return "PT100"

def transshipment_tag(model, transshipmentpoint):

	if model == "M1":
		return ""
	elif model == "M2":
		return "TP1"
	elif model == "M3":
		return f"TP{transshipmentpoint}"

def drone_tag(model):

	if model == "M1":
		return ""
	elif (model == "M2") | (model == "M3"):
		return "PD3.3"

def payload_tag(model, payload):

	if model == "M1":
		return ""
	elif model == "M2":
		return "K1"
	elif model == "M3":
		return f"K{payload}"

def dronespeed_tag(model, dronespeed):

	if model == "M1":
		return ""
	elif model == "M2":
		return "VD70"
	elif model == "M3":
		return f"VD{dronespeed}"

def get_nb_trucks(Nptot, Np, Tin, W):
    
    return int(math.ceil(Nptot/(int(W/Tin)*Np)))

def plot_data(dfs, demand, prefix):


	fig = go.Figure()
	index = 1
	for df in dfs:
		if prefix == "T":
			fig.add_trace(go.Scatter(x = df["Np"], y = df[prefix], name= f"curve {index}"))
		else:
			fig.add_trace(go.Scatter(x = df["Np"], y = df[prefix+str(demand)], name= f"curve {index}"))
		index += 1
	st.plotly_chart(fig)

def set_parameters(curve):

	st.sidebar.title(f"Input parameters curve {curve}")
	model = st.sidebar.selectbox("Model: ", ["M1", "M2", "M3"])

	if model == "M1":
		city = st.sidebar.selectbox("City (km²): ", ["C1", "C2", "C3"])
		distance = st.sidebar.selectbox("Distance (m): ", ["100", "300", "500", "700"])
		radius = st.sidebar.selectbox("Radius (km): ", ["10", "20", "30"])
		transshipmentpoint = "#"
		dronespeed = "#"
		payload = "#"

	elif model == "M2":
		city = st.sidebar.selectbox("City (km²): ", ["C1", "C2", "C3"])
		distance = st.sidebar.selectbox("Distance (m): ", ["100", "300", "500", "700"])
		radius = st.sidebar.selectbox("Radius (km): ", ["10", "20", "30"])
		transshipmentpoint = "#"
		dronespeed = "#"
		payload = "#"

	elif model == "M3":
		city = st.sidebar.selectbox("City (km²): ", ["C1", "C2", "C3"])
		distance = st.sidebar.selectbox("Distance (m): ", ["100", "300", "500", "700"])
		radius = st.sidebar.selectbox("Radius (km): ", ["10", "20", "30"])
		dronespeed = st.sidebar.selectbox("Drone speed (km/h): ", ["50", "60", "70", "80", "90"])
		if dronespeed == "70":
			#transshipmentpoint = st.sidebar.selectbox("# Transshipment point: ", ["1", "2", "3", "4", "5", "6"])
			transshipmentpoint = str(st.sidebar.slider("# Transshipment point: ", 1, 6))
			print(transshipmentpoint)
			if transshipmentpoint == "1":
				#payload = st.sidebar.selectbox("# Parcels: ", ["1", "2", "3", "4", "5", "6"])
				payload = st.sidebar.slider("# Parcels: ", 1, 6)
			else:
				payload = 1
		else:
			transshipmentpoint = 1
			payload = 1

	return [model, city, distance, radius, transshipmentpoint, dronespeed, payload]
	

	

def init_curves(nbcurves):

	return [["#" for i in range(7)] for i in range(nbcurves)]

def get_nb_trips(Nptot, Np):
    
    return math.ceil(Nptot/Np)

def get_max_offset(W, Tout, Tin, Nt, Ntrip):
    
    Nomax = 0
    for i in range(int(Nt)):
        No = Tout * i + Ntrip*Tin
        if No <= W:
            Nomax=i
    return Nomax

def get_nb_drones(W, Np, kd, Tout, Tin, Nt, Ntrip):
    
    Nomax = get_max_offset(W, Tout, Tin, Nt, Ntrip)
    Nf = math.ceil(Nt/(Nomax+1))
    return math.ceil(Nf*Np/kd)

def get_capital_cost(Nt, Pt, Nd, Pd, Vd, kd):

	if Vd == 50:
		addPdV = -660
	elif Vd == 60:
		addPdV = -330
	elif Vd == 80:
		addPdV = 330
	elif Vd == 90:
		addPdV = 660
	else:
		addPdV = 0

	if kd == 2:
		addPdk = 330
	elif kd == 3:
		addPdk = 660
	elif kd == 4:
		addPdk = 990
	elif kd == 5:
		addPdk = 1320
	elif kd == 6:
		addPdk = 1650
	else:
		addPdk = 0

	Pd = Pd + addPdk + addPdV

	return (Nt*Pt + Nd*Pd)/(365*24)

def get_operational_cost(Nt, Hdri):
   
     return Nt*Hdri

def apply_formula(df, demand, price, fee, model, dronespeed, payload):

	if (model == "M1") | (model == "M2"):
		H = 18.52
	elif model == "M3":
		H = 15.21

	
	df["Nt"+str(demand)] = df.apply(lambda x: get_nb_trucks(demand, x["Np"], x["Tin"], 8), axis=1)
	df["trip"+str(demand)] = df.apply(lambda x: get_nb_trips(demand,x["Np"]), axis=1)
	if model == "M1":
		df["Nd"+str(demand)] = 0
		df["Cc"+str(demand)] = df.apply(lambda x: get_capital_cost(x["Nt"+str(demand)], 50000, 0, 0, 0, 1),axis=1)
	elif model == "M2":    
		df["Nd"+str(demand)] = df.apply(lambda x: get_nb_drones(8, x["Np"], 1, x["Tout"], x["Tin"], x["Nt"+str(demand)], x["trip"+str(demand)]/x["Nt"+str(demand)]), axis=1)                          
		df["Cc"+str(demand)] = df.apply(lambda x: get_capital_cost(x["Nt"+str(demand)], 50000, x["Nd"+str(demand)], 3300, dronespeed, payload),axis=1)
	elif model == "M3":
		df["Nd"+str(demand)] = df.apply(lambda x: get_nb_drones(8, x["Np"], 1, x["Tout"], x["Tin"], x["Nt"+str(demand)], x["trip"+str(demand)]/x["Nt"+str(demand)]), axis=1)                          
		df["Cc"+str(demand)] = df.apply(lambda x: get_capital_cost(x["Nt"+str(demand)], price, x["Nd"+str(demand)], 3300, dronespeed, payload),axis=1)
	df["Co"+str(demand)] = df.apply(lambda x: get_operational_cost(x["Nt"+str(demand)], H), axis=1)
	df["Ct"+str(demand)] = df["Cc"+str(demand)] + df["Co"+str(demand)]
	df["ROI"+str(demand)] = demand*fee - df["Ct"+str(demand)] * 8

	return df

def get_price(price):

    return float(price.split("$")[1].replace(",",""))

def get_fee(fee):
    
    return float(fee.split("$")[1])
#=======================================================

#Init

nbcurves = 1
#curves_param = init_curves(nbcurves)




if st.sidebar.button('Reset'):
	st.write('Curves configuration reseted!')
	curves_param = []
	pd.DataFrame(curves_param).to_csv("data.csv")

st.sidebar.title("Graph parameters")

nbcurves= st.sidebar.slider("# Curves: ", 1, 10)

curves_param = init_curves(nbcurves)

output = st.sidebar.selectbox("Output parameter to display: ", ["T","Nt", "Nd", "Ct", "ROI", "trip"])

demand = st.sidebar.slider(" # Total parcels: ", 100, 1000, step=5)

st.sidebar.title("Money Parameters ($)")
fee = st.sidebar.selectbox("Select delivery fee: ", ["$3.99", "$6.19", "$6.694625", "$6.99", "$10.8551575", "$14.95", "$19.99"])
price = st.sidebar.selectbox("Select truck purchace price: ", ["$60,000", "$75,000", "$100,000", "$120,000", "$150,000"])



st.sidebar.title("Curves")
curve = st.sidebar.radio("Select curve",[str(i+1) for i in range(nbcurves)])

#st.sidebar.title(f"Parameter of curve {curve}")
param = set_parameters(curve)
if st.sidebar.button('Validate'):
	curves_param = pd.read_csv("data.csv", index_col=0).values.tolist()
	curves_param.insert(int(curve)-1, param)
	pd.DataFrame(curves_param).to_csv("data.csv")


st.markdown("# Simulation results")


curves_param = pd.read_csv("data.csv", index_col=0).values.tolist()
#st.write(len(curves_param))
tab_df = []
index = 1
for i in curves_param:
	try:
		i[5] = int(i[5])
		i[6] = int(i[6])
	except:
		pass

	file = f"{i[0]}{i[1]}{distance_tag(str(i[2]))}R{i[3]}{transshipment_tag(i[0], i[4])}VTO90VTI25{dronespeed_tag(i[0], i[5])}{truck_tag(i[0])}{drone_tag(i[0])}{payload_tag(i[0], i[6])}.csv"
	df = pd.read_csv(file, index_col=0)
	df = transformation(df)[4:]
	df = apply_formula(df, demand, get_price(price), get_fee(fee),i[0], i[5], i[6])
	tab_df.append(df)
	st.subheader(f"curve {index}: " +  file)
	index +=1
#	st.dataframe(df)
#	plot_data(df, [100, 1000], "NtD")
st.header(f"Column: {output} / demand: {demand} ")
plot_data(tab_df, demand, output)
index = 1
for elem in tab_df:
	st.subheader(f"curve {index}: ")
	st.dataframe(elem)
	index +=1



#test = init_curves(nbcurves)
#st.write(test)


#curvetest = set_parameters(curves)
#st.write(curvetest)


#file = f"{model}{city}{distance_tag(distance)}R{radius}{transshipment_tag(model, transshipmentpoint)}VTO90VTI25{dronespeed_tag(model, dronespeed)}{truck_tag(model)}{drone_tag(model)}{payload_tag(model, payload)}.csv"
#df = pd.read_csv(file, index_col=0)
#df = transformation(df)
#df = apply_formula(df, [100, 1000], "NtD")


#st.dataframe(df)
#plot_data(df, [100, 1000], "NtD")


#st.header(file)