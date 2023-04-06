# Plant Nanny

## Notes
https://wili.52pi.com/index.php?title=Z-0235

pip install liquidcrystal_i2c

## Implementation

- [ ] User Interface
	- [X] Display Tabs
	- [X] Implement Tab Switching
	- [ ] Implement Changing Tab Settings
		- [ ] Implement Settings Datastructures
			- [X] Time Delay Class (printable, stores DAY/WEEK and number of)
			- [ ] Moisture%  Class? (depends on sensor data, un-needed?)
		- [ ] Make input change selection
		- [ ] "Roll" to beginning once end met
		- [ ] !! Always display SELECTED setting on change to tab !!

	- [ ] Button Inputs
		- [ ] Recieve Button Presses
		- [ ] Equate Button Presses to Tab/Setting switching

- [ ] Watering 

OPTIONAL:
- [ ] UI - Countdown timer
- [ ] Save User Settings
	- [ ] Write user settings to local file
	- [ ] Startup check + read user settings
		- [ ] Set run time variables per settings 

- [ ] Remember Timing
	- [ ] Write start of wait to local file
	- [ ] Routinely update current time in local file


