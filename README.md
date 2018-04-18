# Python Cellular Automaton
Implementation of cellular automaton in python using pygame (mainly Conway's Game of Life)

## Projects so far:                                         
* **GOL**  
	- Conway's Game of Life, developed to test speed of various cell update modes
	- Simple mode: all cells are updated
	- Bounding mode: The bounding box of the live cells is calculates and only cells within it are updated (faster)
	- Active mode: only the cells around the active cells are updated (work in progress)
	- Controls:
		- `SPACE` = Start/Pause
		- `ENTER` = Step
		- `M` = Change mode
		- `G` = Glider pattern
		- `R` = Random pattern
	
	<br>
	<img src="Screenshots/GOL.gif" alt="GOL" style="width: 500px;"/>