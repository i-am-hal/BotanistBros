from math import ceil
from enum import Enum, auto
import liquidcrystal_i2c

#Instantiates the lcd screen that we will be using this whole time
screen = liquidcrystal_i2c.LiquidCrystal_I2C(0x27, 1, numlines=4)

#Time unit, can be day or week
class Time(Enum):
	DAY   = auto()
	WEEK  = auto()
	#HOUR  = auto()
	#MONTH = auto()

#An option for delay, some number of days/weeks
class DelayOption:
	def __init__(self, unit, amount):
		self.unit   = unit
		self.amount = amount
	
	def __repr__(self):
		suffix = {Time.DAY:'D', Time.WEEK:'W'}
		
		return str(self.amount) + suffix.get(self.unit, " UKN")
	
	def __str__(self):
		return self.__repr__()

	def __len__(self):
		return len(self.__str__())		  

class WaterOption:
	def __init__(self, percent):
		self.percet = percent

		#if 0 >= percent =< 1:
		#	self.percent = int(percent * 100)
	
	__repr__ = lambda self: f"{self.percent}%"
	__str__ = lambda self: self.__repr__()
	__len__ = lambda self: len(self.__repr__())

#Given some text, adds spaces to the left to center the text
def center(text, maxlength=20):
	#Throw error at runtime if text is too long
	if len(text) > maxlength:
		raise ValueError(f"Provided string \"{text}\" is longer than max of {maxlength} characters!")
	
	#Create number of spaces left of text to center it
	left_buffer = " " * ceil((maxlength - len(text))/2)
	
	return left_buffer + text

#Clears out a line so we have no leftover chars
def clearline(display, line,  maxchars=20):
	display.printline(line, " " * maxchars)

#Variable used to nab the current selected option in each tab
SELECTION = "SELECTION"
#Variable used to grab the options which the user can pick between in relevant tab
OPTIONS   = "OPTIONS"

#The two seperate 'tabs' where user can make relevant options
UI_tabs = {
	"Delay": {
		SELECTION: 0,
		OPTIONS: [DelayOption(Time.DAY, 1), DelayOption(Time.DAY, 2)]
		},

	"Water": {
		SELECTION: 0,
		OPTIONS: ["NONE"]
		} 
}

#The line below tab name that indicates selection
tabSelLines = {
	0: " " * 7 + "-" * 13,
	1: "-" * 6 + " " * 9 + 5 * "-"
}

#The index (which tab) is selected
tab_select = 0

#Takes tab index, wraps to first tab if going past options, else, next option
wrapTab = lambda n: 0 if n >= len(list(UI_tabs)) else n

def update_ui():
	#Using the current selection, pick relevent line below tab names
	screen.printline(1, tabSelLines[tab_select])

	tab     = list(UI_tabs)[tab_select]
	options = UI_tabs[tab][OPTIONS]
	opt_sel = UI_tabs[tab][SELECTION]

	clearline(screen, 2) #clear out second line, remove remaining chars
	screen.printline(2, center(str(options[opt_sel])))

#
def display_ui():
	#Display the tab names at the very top
	screen.printline(0, " | ".join(UI_tabs) + " |")
	update_ui()

if __name__ == "__main__":
	from time import sleep
	
	display_ui()
	
	cmd = ""	

	print("Enter 1 or s to change tab.\nEnter 2 or o to change option.\n\n")

	while True:
		cmd = input()[:1]
		
		#Go to next tab
		if cmd in "1s":
			tab_select = wrapTab(tab_select+1)
			print(f"Next tab {tab_select}")
			update_ui()
		
		#
		elif cmd in "2o":
			tab = list(UI_tabs)[tab_select]
			tab_options  = UI_tabs[tab][OPTIONS]
			tab_curr_sel = UI_tabs[tab][SELECTION]
			
			if tab_curr_sel >= len(tab_options)-1:
				UI_tabs[tab][SELECTION] = 0
			else:
				UI_tabs[tab][SELECTION] += 1
			
		
