# Plant Nanny

## Notes
https://wiki.52pi.com/index.php?title=Z-0235

https://www.instructables.com/Raspberry-PI-Multiple-I2c-Devices/

pip install liquidcrystal_i2c

## Save Data

The Plant Nanny will routinely save data related to user settings,
last recorded system time, and upcoming moisture check time. This
will be put into some kind of text document that will organize
this data as such:

```
1 time of next moisture check
2 last recorded system time
3 moisture check delay setting
4 moisture level setting
```

## Implementation

- [ ] User Interface
	- [X] Display Tabs
	- [X] Implement Tab Switching
	- [X] Implement Changing Tab Settings
		- [X] Implement Settings Datastructures
			- [X] Time Delay Class (printable, stores DAY/WEEK and number of)
			- [X] Moisture%  Class? (depends on sensor data, un-needed?)
		- [X] Make input change selection
		- [X] "Roll" to beginning once end met
		- [X] !! Always display SELECTED setting on change to tab !!
		- [X] Display setting number at bottom ("1/6" for example)

	- [ ] Button Inputs
		- [ ] Recieve Button Presses
		- [ ] Equate Button Presses to Tab/Setting switching

- [ ] Watering 
	- [ ] Sensor Data
		- [ ] Be able to recieve moissture%

	- [ ] Clock
		- [ ] Read system time
		- [ ] Recognize 'check time' (when to start water cycle)

	- [ ] Water Cycle
		- [ ] Control water pump (deposit water)
		- [ ] Functional moisture-check-loop

OPTIONAL:
- [ ] Detect permiation time - incorperate in system - CALIBRATE
- [ ] UI - Countdown timer
- [ ] Save User Settings
	- [ ] Write user settings to local file
	- [X] Startup check + read user settings
		- [X] Set run time variables per settings 

- [ ] Remember Timing
	- [ ] Write start of wait to local file
	- [ ] Routinely update current time in local file


