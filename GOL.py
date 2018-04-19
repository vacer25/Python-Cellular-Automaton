import pygame
import random
from enum import Enum

# Constants

#targetFrameRate = 60

bgCol = (0, 0, 0)
textCol = (255, 255, 255)
redTextCol = (255, 32, 32)
yellowTextCol = (255, 255, 32)
greenTextCol = (32, 255, 32)
blueTextCol = (64, 64, 255)
runningTextCol = (32, 255, 32)
pausedTextCol = (255, 255, 32)
liveCellCol = (32, 200, 32)
deadCellCol = (16, 16, 16)
boundingBoxCol = (200, 200, 32)
mousePosCol = (200, 200, 200)

topBarSizeY = 30
bottomBarSizeY = 30

numCellsX = 80
numCellsY = 60
sizeCellsX = 10
sizeCellsY = 10

sizeX = numCellsX*sizeCellsX
sizeY = numCellsY*sizeCellsY + topBarSizeY + bottomBarSizeY

# Variables

class UpdateMode(Enum):
     SIMPLE = 1
     BOUNDING = 2
     ACTIVE = 3

cells = [[[0 for col in range(numCellsX)]for row in range(numCellsY)] for x in range(2)]

numberOfMemoryAccesses = 0

currentBuffer = 0
otherBuffer = 1 - currentBuffer
currentMode = UpdateMode.SIMPLE

boundingBoxMinX = 0
boundingBoxMaxX = numCellsX - 1
boundingBoxMinY = 0
boundingBoxMaxY = numCellsY - 1

mousePos = (-1, -1)
mouseLeftClicked = False
mouseRightClicked = False

displayPrevIteration = True
separateCells = True
step = False
paused = True
done = False

# Init
pygame.init()
pygame.display.set_caption('Game of Life')
clock = pygame.time.Clock()
screen = pygame.display.set_mode((sizeX, sizeY))

font = pygame.font.SysFont("consolas", 20)
smallFont = pygame.font.SysFont("consolas", 12)
updateTimeTextOffsetX = smallFont.size("2")[0]*10
updateFPSTextOffsetX = smallFont.size("2")[0]*3

runningText = font.render("RUNNING", True, runningTextCol, bgCol)
stepText = font.render("STEP", True, runningTextCol, bgCol)
pausedText = font.render("PAUSED", True, pausedTextCol, bgCol)
updateTimeStringText = smallFont.render("Update time:     ms/    fps", True, textCol, bgCol)
memAccessStringText = smallFont.render("# of memory access:", True, textCol, bgCol)
keyControlsLine1Text = smallFont.render("Controls: [Space/MMB] = Run/Pause, [Enter] = Step, [M] = Change mode, [S] = Toggle cell separation, [ESC] = Quit", True, textCol, bgCol)
keyControlsLine2Text = smallFont.render("          [C] = Clear all, [P] = Toggle display of prev. iteration, [G] = Glider pattern, [R] = Random pattern", True, textCol, bgCol)


# Clamp number within range function
def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

	
# Create glider (on both buffers) function
def createGlider(col, row, ori):
	for i in range (0, 2):
		if ori == 0: # Facing left
			cells[i][row+0][col+1] = 1
			cells[i][row+1][col+2] = 1
			cells[i][row+2][col+0] = 1
			cells[i][row+2][col+1] = 1
			cells[i][row+2][col+2] = 1
			
		if ori == 1: # Facing right
			cells[i][row+0][col+1] = 1
			cells[i][row+1][col+0] = 1
			cells[i][row+2][col+0] = 1
			cells[i][row+2][col+1] = 1
			cells[i][row+2][col+2] = 1	
		

# Initialize board (with 2 gliders) function
def initBoardGliders():
	clearCells()
	createGlider(1, 1, 0)
	createGlider((40 - 4), 2, 1)
	currentBuffer = 0

	
# Initialize board (randomly) function
def initBoardRandom():
	clearCells()
	currentBuffer = 0
	
	for row in range(numCellsY-1, -1, -1):
		for col in range(numCellsX-1, -1, -1):
			for i in range (0, 2):
				cells[i][row][col] = random.randint(0, 1)
			

# Clear all cells (from both buffers) function
def clearCells():
	for row in range(numCellsY-1, -1, -1):
		for col in range(numCellsX-1, -1, -1):
			for i in range (0, 2):
				cells[i][row][col] = 0


# Cell drawing function
def drawCell(col, row):
	
	#print("Drawing cell at col: %d, row: %d, i: %d" % (col, row, i))

	if cells[currentBuffer][row][col]: color = liveCellCol
	else: color = deadCellCol
	if separateCells:
		pygame.draw.rect(screen, color, pygame.Rect(col*sizeCellsX + 1, topBarSizeY + row*sizeCellsY + 1, sizeCellsX-2, sizeCellsY-2))
	else:
		pygame.draw.rect(screen, color, pygame.Rect(col*sizeCellsX, topBarSizeY + row*sizeCellsY, sizeCellsX, sizeCellsY))

	if displayPrevIteration and cells[otherBuffer][row][col]: 
		color = yellowTextCol
		pygame.draw.rect(screen, color, pygame.Rect(col*sizeCellsX + 4, topBarSizeY + row*sizeCellsY + 4, sizeCellsX-8, sizeCellsY-8))
	
# Process drawing function
def processCell(col, row, idle):
	
	global numberOfMemoryAccesses
	
	minX = clamp((col-1), 0, (numCellsX-1))
	maxX = clamp((col+1), 0, (numCellsX-1))
	minY = clamp((row-1), 0, (numCellsY-1))
	maxY = clamp((row+1), 0, (numCellsY-1))
	
	neighborCount = 0
	
	for currY in range(minY, maxY+1):
		for currX in range(minX, maxX+1):
			#print("Reading cell at col: %d, row: %d, buff: %d" % (col, row, otherBuffer))
			neighborCount += cells[otherBuffer][currY][currX]
			numberOfMemoryAccesses += 1
	
	neighborCount -= cells[otherBuffer][row][col]
	thisCellIsAlive = cells[otherBuffer][row][col]
	
	#if thisCellIsAlive:
		#pygame.draw.rect(screen, boundingBoxCol, pygame.Rect(minX*sizeCellsX, topBarSizeY + minY*sizeCellsY, (maxX - minX + 1) * sizeCellsX, (maxY - minY + 1) * sizeCellsY), 1)
		#pygame.display.flip()
		
	if not idle:
		if thisCellIsAlive and neighborCount < 2:
			cells[currentBuffer][row][col] = 0
		elif thisCellIsAlive and neighborCount > 3:
			cells[currentBuffer][row][col] = 0
		elif not thisCellIsAlive and neighborCount == 3:
			cells[currentBuffer][row][col] = 1
		else:
			cells[currentBuffer][row][col] = cells[otherBuffer][row][col]


# Calculate bounding box (based on prev. alive cells) function
def calculateBoundingBox():

	global boundingBoxMinX
	global boundingBoxMaxX
	global boundingBoxMinY
	global boundingBoxMaxY
	global numberOfMemoryAccesses

	currMinX = numCellsX - 1
	currMaxX = 0
	currMinY = numCellsY - 1
	currMaxY = 0

	for row in range(numCellsY-1, -1, -1):
		for col in range(numCellsX-1, -1, -1):
			if cells[otherBuffer][row][col]:
				currMinX = min(currMinX, col)
				currMaxX = max(currMaxX, col)
				currMinY = min(currMinY, row)
				currMaxY = max(currMaxY, row)
			numberOfMemoryAccesses += 1
	
	boundingBoxMinX = clamp(currMinX - 2, 0, (numCellsX-1))
	boundingBoxMaxX = clamp(currMaxX + 2, 0, (numCellsX-1))
	boundingBoxMinY = clamp(currMinY - 2, 0, (numCellsY-1))
	boundingBoxMaxY = clamp(currMaxY + 2, 0, (numCellsY-1))
	
	#print("Calculated bounding box: (%d, %d, %d, %d)" % (boundingBoxMinX, boundingBoxMinY, boundingBoxMaxX, boundingBoxMaxY))
	

# Update board function
def updateBoard():

	global numberOfMemoryAccesses

	if currentMode == UpdateMode.SIMPLE:
		# Loop over all cells, updating (if not paused or if stepping)
		for row in range(numCellsY-1, -1, -1):
			for col in range(numCellsX-1, -1, -1):
				if not paused or step:
					processCell(col, row, False)
				else:
					processCell(col, row, True)
				numberOfMemoryAccesses += 1
		
		# Loop over all cells, drawing each one
		for row in range(numCellsY-1, -1, -1):
			for col in range(numCellsX-1, -1, -1):
				drawCell(col, row)
				
	elif currentMode == UpdateMode.BOUNDING:
		# Loop over all cells within bounding box, updating (if not paused or if stepping)
		for row in range(boundingBoxMaxY, boundingBoxMinY-1, -1):
			for col in range(boundingBoxMaxX, boundingBoxMinX-1, -1):
				if not paused or step:
					processCell(col, row, False)
				else:
					processCell(col, row, True)
				numberOfMemoryAccesses += 1
		
		# Loop over all cells, drawing each one
		for row in range(numCellsY-1, -1, -1):
			for col in range(numCellsX-1, -1, -1):
				drawCell(col, row)
		calculateBoundingBox()
		
		#print("Bounding box: (%d, %d, %d, %d)" % (boundingBoxMinX, boundingBoxMinY, boundingBoxMaxX, boundingBoxMaxY))
		
		# Draw the bounding box
		pygame.draw.rect(screen, boundingBoxCol, pygame.Rect(boundingBoxMinX*sizeCellsX, topBarSizeY + boundingBoxMinY*sizeCellsY, (boundingBoxMaxX - boundingBoxMinX + 1) * sizeCellsX, (boundingBoxMaxY - boundingBoxMinY + 1) * sizeCellsY), 1)
	

def processMouseInput():
	# Loop over all cells, drawing each one
		for row in range(numCellsY-1, -1, -1):
			for col in range(numCellsX-1, -1, -1):
			
				cellBorderRect = pygame.Rect(col*sizeCellsX, topBarSizeY + row*sizeCellsY, sizeCellsX, sizeCellsY)
				if cellBorderRect.collidepoint(mousePos):
					pygame.draw.rect(screen, mousePosCol, cellBorderRect, 1)
					
					if mouseLeftClicked:
						for i in range (0, 2):
							cells[i][row][col] = 1
							
					if mouseRightClicked:
						for i in range (0, 2):
							cells[i][row][col] = 0

# Initialize the board with 2 gliders facing each other
initBoardGliders()

# Initialize the board randomly
#initBoardRandom()

# Main loop
while not done:
	for event in pygame.event.get():
		# Check to exit
		if event.type == pygame.QUIT:
			done = True
		# Check keyboard input
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				done = True
			if event.key == pygame.K_SPACE:
				paused = not paused
			if event.key == pygame.K_RETURN:
				paused = True
				step = True
			if event.key == pygame.K_c:
				clearCells()
			if event.key == pygame.K_g:
				initBoardGliders()
			if event.key == pygame.K_r:
				initBoardRandom()
			if event.key == pygame.K_s:
				separateCells = not separateCells
			if event.key == pygame.K_p:
				displayPrevIteration = not displayPrevIteration
			if event.key == pygame.K_m:
				if currentMode == UpdateMode.SIMPLE: 
					currentMode = UpdateMode.BOUNDING
					calculateBoundingBox()
				elif currentMode == UpdateMode.BOUNDING:
					currentMode = UpdateMode.SIMPLE
				# Active Cell mode is not implemented yet...
				#elif currentMode == UpdateMode.ACTIVE: currentMode = UpdateMode.SIMPLE
		# Check mouse down input
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1: # Left button down
				paused = True
				mouseLeftClicked = True
			if event.button == 2: # Mouse wheel button down
				paused = not paused
			elif event.button == 3: # Right button down
				paused = True
				mouseRightClicked = True
		# Check for mouse up input
		if event.type == pygame.MOUSEBUTTONUP:
			if event.button == 1: # Left button up
				mouseLeftClicked = False
			elif event.button == 3: # Right button up
				mouseRightClicked = False    
		# Get the mouse position	
		if event.type == pygame.MOUSEMOTION:
			mousePos = event.pos
	
	# Clear the screen
	screen.fill(bgCol)
	
	if not paused or step:
		# Swap buffers
		otherBuffer = currentBuffer
		currentBuffer = 1 - currentBuffer
	
	# Start timing
	starUpdateTime = pygame.time.get_ticks()
	
	# Update the board using the method based on the current mode
	updateBoard()
	
	# Stop Timing
	updateTime = pygame.time.get_ticks() - starUpdateTime
	
	processMouseInput()
	
	# Draw current frame time text
	timeTextCol = redTextCol
	updateFPS = (1000 // updateTime)
	if updateFPS >= 10:	timeTextCol = yellowTextCol
	if updateFPS >= 20:	timeTextCol = greenTextCol
	updateTimeValueText = smallFont.render(str(updateTime), True, timeTextCol, bgCol)
	updateFPSValueText = smallFont.render(str(updateFPS), True, timeTextCol, bgCol)
	screen.blit(updateTimeStringText, (sizeX - updateTimeStringText.get_width() - 5, 4))
	screen.blit(updateTimeValueText, (sizeX - updateTimeValueText.get_width() - updateTimeTextOffsetX - 5, 4))
	screen.blit(updateFPSValueText, (sizeX - updateFPSValueText.get_width() - updateFPSTextOffsetX - 5, 4))
	
	# Draw current number of memory accesses text
	memAccessValueText = smallFont.render(str(numberOfMemoryAccesses), True, blueTextCol, bgCol)
	screen.blit(memAccessStringText, (sizeX - updateTimeStringText.get_width() - 5, 17))
	screen.blit(memAccessValueText, (sizeX - memAccessValueText.get_width() - 5, 17))
	
	if not paused:
		# Draw running text
		screen.blit(runningText, ((sizeX - runningText.get_width()) // 2, 5))
		
	if step:
		# Draw step text
		screen.blit(stepText, ((sizeX - stepText.get_width()) // 2, 5))

	if paused and not step:
		# Draw paused text
		screen.blit(pausedText, ((sizeX - pausedText.get_width()) // 2, 5))
	
	# Draw current mode text
	if currentMode == UpdateMode.SIMPLE: currentModeString = "Simple"
	elif currentMode == UpdateMode.BOUNDING: currentModeString = "Bounding Box"
	elif currentMode == UpdateMode.ACTIVE: currentModeString = "Active Cells"
	currentModeText = font.render("Mode: " + currentModeString, True, textCol, bgCol)
	screen.blit(currentModeText, (5, 5))
	
	# Draw bottom key controls text
	screen.blit(keyControlsLine1Text, (5, sizeY - bottomBarSizeY + 4))
	screen.blit(keyControlsLine2Text, (5, sizeY - bottomBarSizeY + 17))
	
	# Update the screen
	pygame.display.flip()
	# Don't pause, update screen as fast as possible
	#clock.tick(targetFrameRate)

	# Reset variables
	step = False
	numberOfMemoryAccesses = 0