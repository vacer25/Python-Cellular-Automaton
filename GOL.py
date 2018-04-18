import pygame
import random
from enum import Enum

class UpdateMode(Enum):
     SIMPLE = 1
     BOUNDING = 2
     ACTIVE = 3

# Constants

frameRate = 60

bgCol = (0, 0, 0)
textCol = (255, 255, 255)
runningTextCol = (32, 255, 32)
pausedTextCol = (255, 255, 32)
liveCellCol = (32, 200, 32)
deadCellCol = (16, 16, 16)
boundingBoxCol = (200, 200, 32)

topBarSizeY = 30
bottomBarSizeY = 20

numCellsX = 80
numCellsY = 60
sizeCellsX = 10
sizeCellsY = 10

sizeX = numCellsX*sizeCellsX
sizeY = numCellsY*sizeCellsY + topBarSizeY + bottomBarSizeY

# Variables

cells = [[[0 for col in range(numCellsX)]for row in range(numCellsY)] for x in range(2)]

currentBuffer = 0
otherBuffer = 1 - currentBuffer
currentMode = UpdateMode.SIMPLE

boundingBoxMinX = 0
boundingBoxMaxX = numCellsX - 1
boundingBoxMinY = 0
boundingBoxMaxY = numCellsY - 1

step = False
paused = True
done = False

# Init
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((sizeX, sizeY))

font = pygame.font.SysFont("consolas", 20)
smallFont = pygame.font.SysFont("consolas", 12)

runningText = font.render("RUNNING", True, runningTextCol, bgCol)
stepText = font.render("STEP", True, runningTextCol, bgCol)
pausedText = font.render("PAUSED", True, pausedTextCol, bgCol)

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
	pygame.draw.rect(screen, color, pygame.Rect(col*sizeCellsX + 1, topBarSizeY + row*sizeCellsY + 1, sizeCellsX-2, sizeCellsY-2))

	
# Process drawing function
def processCell(col, row, idle):
	
	minX = clamp((col-1), 0, (numCellsX-1))
	maxX = clamp((col+1), 0, (numCellsX-1))
	minY = clamp((row-1), 0, (numCellsY-1))
	maxY = clamp((row+1), 0, (numCellsY-1))
	
	neighborCount = 0
	 
	#print("CurrX: %d, CurrY: %d" % (col, row))
	#print("MinX: %d, MaxX: %d" % (minX, maxX))
	#print("MinY: %d, MaxY: %d" % (minY, maxY))
	
	for currY in range(minY, maxY+1):
		for currX in range(minX, maxX+1):
			#print("Reading cell at col: %d, row: %d, buff: %d" % (col, row, otherBuffer))
			neighborCount += cells[otherBuffer][currY][currX]
	
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
	
	boundingBoxMinX = clamp(currMinX - 2, 0, (numCellsX-1))
	boundingBoxMaxX = clamp(currMaxX + 2, 0, (numCellsX-1))
	boundingBoxMinY = clamp(currMinY - 2, 0, (numCellsY-1))
	boundingBoxMaxY = clamp(currMaxY + 2, 0, (numCellsY-1))
	
	#print("Calculated bounding box: (%d, %d, %d, %d)" % (boundingBoxMinX, boundingBoxMinY, boundingBoxMaxX, boundingBoxMaxY))
	
	
def updateBoard():

	if currentMode == UpdateMode.SIMPLE:
		# Loop over all cells, updating (if not paused or if stepping) and drawing each one
		for row in range(numCellsY-1, -1, -1):
			for col in range(numCellsX-1, -1, -1):
				if not paused or step:
					processCell(col, row, False)
				else:
					processCell(col, row, True)
				drawCell(col, row)
				
	elif currentMode == UpdateMode.BOUNDING:
		# Loop over all cells within bounding box, updating (if not paused or if stepping) and drawing each one
		for row in range(boundingBoxMaxY, boundingBoxMinY-1, -1):
			for col in range(boundingBoxMaxX, boundingBoxMinX-1, -1):
				if not paused or step:
					processCell(col, row, False)
				else:
					processCell(col, row, True)
					
		for row in range(numCellsY-1, -1, -1):
			for col in range(numCellsX-1, -1, -1):
				drawCell(col, row)
		calculateBoundingBox()
		
		#print("Bounding box: (%d, %d, %d, %d)" % (boundingBoxMinX, boundingBoxMinY, boundingBoxMaxX, boundingBoxMaxY))
		
		# Draw the bounding box
		pygame.draw.rect(screen, boundingBoxCol, pygame.Rect(boundingBoxMinX*sizeCellsX, topBarSizeY + boundingBoxMinY*sizeCellsY, (boundingBoxMaxX - boundingBoxMinX + 1) * sizeCellsX, (boundingBoxMaxY - boundingBoxMinY + 1) * sizeCellsY), 1)
		

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
		# Check to switch mode
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				paused = not paused
				#print("Paused")
			if event.key == pygame.K_RETURN:
				paused = True
				step = True
			if event.key == pygame.K_g:
				initBoardGliders()
			if event.key == pygame.K_r:
				initBoardRandom()
			if event.key == pygame.K_m:
				if currentMode == UpdateMode.SIMPLE: 
					currentMode = UpdateMode.BOUNDING
					calculateBoundingBox()
				elif currentMode == UpdateMode.BOUNDING:
					currentMode = UpdateMode.SIMPLE
				# Active Cell mode is not implemented yet...
				#elif currentMode == UpdateMode.ACTIVE: currentMode = UpdateMode.SIMPLE
	
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
	
	# Draw current frame time text
	updateTimeText = font.render("Update time: " + str(updateTime) + "ms", True, textCol, bgCol)
	screen.blit(updateTimeText, (sizeX - updateTimeText.get_width() - 5, 5))
	
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
	keyControlsText = smallFont.render("Keys: [Space] = Start/Pause, [Enter] = Step, [M] = Change mode, [G] = Glider pattern, [R] = Random pattern", True, textCol, bgCol)
	screen.blit(keyControlsText, (5, sizeY - bottomBarSizeY + 5))
	
	# Update the screen
	pygame.display.flip()
	clock.tick(frameRate)

	# Clear flags
	step = False