from time import sleep
from math import ceil
import liquidcrystal_i2c

#Instantiates the lcd screen that we will be using this whole time
screen = liquidcrystal_i2c.LiquidCrystal_I2C(0x27, 1, numlines=4)

#Given some text, adds spaces to the left to center the text
def center(text, maxlength=20):
	#Throw error at runtime if text is too long
	if len(text) > maxlength:
		raise ValueError(f"Provided string \"{text}\" is longer than max of {maxlength} characters!")
	
	#Create number of spaces left of text to center it
	left_buffer = " " * ceil((maxlength - len(text))/2)
	
	return left_buffer + text

screen.printline(1, center("Hello, World!"))
