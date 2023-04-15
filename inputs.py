

#Reads moisture percentage from serial input
def readMoisture(serialInput):
	line = ""
	
	while line == "":
		line = serialInput.readline().strip()
	
	#print(f"RAW STR:'{line}'")

	return int(str(line, "utf-8"))


