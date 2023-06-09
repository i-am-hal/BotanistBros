import RPi.GPIO as GPIO

#Given the pin for the motor, turn it on
def motor_on(pin):
	GPIO.output(pin, GPIO.HIGH)

#Given the pin for the motor, turn it on
def motor_off(pin):
	GPIO.output(pin, GPIO.LOW)

#Reads moisture percentage from serial input
def readMoisture(serialInput):
	line = ""
	
	#Continually read input until positive reading
	while line == "":
		line = serialInput.readline().strip()
	
	#Convert the reading into an integer
	percent = int(str(line, "utf-8"))

	#Constrain the values from 0-100 moisture percentage
	if percent < 0:
		percent = 0

	elif percent > 100:
		percent = 100

	return percent

