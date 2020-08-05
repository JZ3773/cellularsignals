import json
import requests
import datetime

#Using the API to get the full list of sensors/details about each sensor
URL = "https://JeremyZ:Awesome73@electrosense.org/api/sensor/list"
response = requests.get(url = URL)

#Cleaning up the output to just leave one big list
sensorlist=response.text.strip("][").split(", ")
updatedsensorlist = sensorlist[0].replace("},{", "} , {")
newsensorlist = updatedsensorlist.split(" , ")

#Dividing up the sensors into 4 geographical locations
grouponelist=[]
grouptwolist=[]
groupthreelist=[]
groupfourlist=[]
groupfivelist=[]
for x in newsensorlist:
	try:
		#Converting strings of lists into lists - this occasionally gives errors, so it's under a try statement
		x=json.loads(x)
	except:
		continue
	serialnumber=x["serial"]
	if x["position"]["longitude"]<-20:
		grouponelist.append(serialnumber) #Americas
	elif -20 < x["position"]["longitude"] < 40:
		grouptwolist.append(serialnumber) #Europe
	elif 40 < x["position"]["longitude"] < 115:
		groupthreelist.append(serialnumber) #China
	else:
		if x["position"]["latitude"]>0:
			groupfourlist.append(serialnumber) #Japan
		else:
			groupfivelist.append(serialnumber) #Australia

#The username and password should replace the words "username" and "password"
URL = "https://Username:Password@electrosense.org/api/spectrum/aggregated"
myfile = open("GSMCelldata.csv", "w+")

#Choose what geographical location you want to look at
for serial in grouptwolist:
	myfile.write(f"{serial}\n")
	#These are the parameters for the get function. The beginning time and end time can (and should) be adjusted by the user
	#The frequency should also be changed based on whatever range you want to look at
	#Using "AVG" tends to give clearer results than "MAX"
	PARAMS={'sensor': serial, 'timeBegin': 1593403200, 'timeEnd': 1593748800, 'freqMin': 890000000,'freqMax': 960000000, 'aggFreq': 500000, 'aggTime': 60, 'aggFun': "AVG"}
	response = requests.get(url=URL, params=PARAMS)
	responsetext=response.text
	try:
		#Converting the string of all data into an array of the data - this also sometimes gives an error so it's in a try statement
		datastring=json.loads(responsetext)
		dataarray=datastring["values"]
	except:
		continue
	time=PARAMS["timeBegin"]
	while time<=PARAMS["timeEnd"]:
		#Writing out all of the different times
		myfile.write(f"{datetime.datetime.fromtimestamp(time).strftime('%c')},")
		time+=PARAMS["aggTime"]
	myfile.write("\n")
	myfile.write("Average dB value:")
	for innerlist in dataarray:
		count=0
		countsum=0
		for value in innerlist:
			if type(value)==float or type(value)==int:
				#Avoid error of adding a null
				count+=1
				countsum+=value
		try:
			#Avoiding a 0/0 error if the sensor has no data for the range
			average=countsum/count
			myfile.write(f"{average},")
		except:
			myfile.write(",")
	myfile.write("\n\n")
myfile.close()