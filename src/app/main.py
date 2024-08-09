from curses import KEY_ENTER
from tkinter import W
import pygame
import os
import time 
import random
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,  
    QUIT,
)
import pygame.freetype
import copy

##############################################
# DESC
##############################################

# A BLOCK = 
"#"
# A BRICK = 
"####"
# THE PLAYFIELD = 
"""
___#____
___#____
___##___
________
________
###__##_
#######_
########
########
"""

##############################################
# VARS
##############################################

PATH_IMGS="assets/imgs/"
PATH_FONTS="assets/fonts/"
PATH_SOUNDS="assets/sounds/"
X_SCREEN = 640
Y_SCREEN = 430
N = 10  # TODO: RENAME
        # WARN: 10 + 1 for allowing tests (change test method for reduce table ?)   
M = 22  # TODO: RENAME 
CELL_SIZE=18
PLAYFIELD_X_OFFSET=28
PLAYFIELD_Y_OFFSET=-5
INITIAL_SPEED=0.20
RGB_BLACK=(0,0,0)
RGB_RED=(255,0,0)
RGB_WHITE=(255,255,255)
RGB_GREY=(192,192,192)
FPS_GAME = 60
FPS_MENU = 15
NB_LINES_BY_LEVEL = 25
SFX_VOLUME = 0.075
MUSIC_VOLUME = 0.01
#KEY_DOWN_SPEED=0.05

##############################################
# STRUCTURES
##############################################
"""
+-------------+ 1  n +---------+ 1  4 +--------+
|  PLAYFIELD  | <--- +  BRICK  + ---> |  CELL  |
+-------------+      +---------+      +--------+
"""
#
# CELL
#
class Cell():
    # DESC: a celle for the brick and (interface with) the playground
    def __init__(self, x=0, y=0, value=0):
        self.x=x
        self.y=y
        self.value=value
    def setX(self,x):
        self.x=x
    def setY(self,y):
        self.y=y
    def setColor(self,value):
        self.value=value
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def getColor(self):
        return self.value
#
# PLAYFIELD
#    
class playfield():
    # DESC: the TETRIS main playfield
    # WARN: USE ONLY NUMBER INSTEAD OF CELL "INSIDE", MAYBE CHANGE THAT OR ADD "EXPLICIT" CELL CONVERTER 
    def __init__(self):
        self.__sprite_block = SPRITE_BLOCK
        self.__field=[]
        for y in range(M): # TODO: more efficient
            self.__field.append([])
            for x in range(N):
                self.__field[y].append(0) # TODO: MAKE A INTERNAL CELL VERSION ?   
        #self.__field=[[0]*N]*M  # DESC: M*[LINE of Nx0] not work cause of memory copy as adress in PYTHON
    def set(self,cell):
        # TODO: RENAME FUNCTION AND HAVE A ALL CELLS VERSION
        # TODO: MAKE A INTERNAL CELL VERSION ?
        self.__field[cell.getY()][cell.getX()] = cell.getColor()
    def get(self,cell):
        # TODO: RENAME FUNCTION AND HAVE A ALL CELLS VERSION
        # TODO: MAKE A INTERNAL CELL VERSION ?
        return Cell(cell.getX(),cell.getY(),self.__field[cell.getY()][cell.getX()])
    def draw(self, level):
        # TODO: MAKE A INTERNAL CELL VERSION ?
        for idxLine, line in  enumerate(self.__field):
            for idxColumn,int_cell in enumerate(line):
                if int_cell==0:
                    continue
                pg_Window.blit(     
                            self.__sprite_block, 
                            (idxColumn*CELL_SIZE+PLAYFIELD_X_OFFSET,idxLine*CELL_SIZE+PLAYFIELD_Y_OFFSET), 
                            (int_cell*CELL_SIZE+8*CELL_SIZE,CELL_SIZE*(level%4),CELL_SIZE,CELL_SIZE)
                        )                
    def cleanLines(self):
        linesCounter=0
        for idxLine, line in enumerate(self.__field):
            if 0 in line:
                # ALGO: FOR NOT A FULL LINE
                continue
            # ALGO: FOR A FULL LINE
            for onTopY in range(idxLine,0,-1):
                for column in range(N):
                    self.__field[onTopY][column]=self.__field[onTopY-1][column]
                for column in range(N):
                    self.__field[0][column] = 0
            linesCounter = linesCounter + 1    
            time.sleep(0.10) # ALGO: LATENCY FOR AUDIO & VISUUAL EFFECT
        # ALGO: FOR ALL THE PLAYGROUND FROM TOP
        # TODO: BETTER HOLE DETECTION ON PLAYGROUND
        freeEmptyCells=len(self.__field)*len(self.__field[0])
        for idxY in range(M):
            for idxX in range(N):
                neddToBeCount=True
                if self.__field[idxY][idxX] != 0:
                   freeEmptyCells =  freeEmptyCells - 1
                # TODO: A FLOOD ALGO TO FIND "OPEN" CELLS ONLY 
        return linesCounter, freeEmptyCells
    
    def isOverLoad(self):
        # TODO : REFACTOR
        for column in range(N):
            if self.__field[2][column] != 0:
                return True
        for column in range(N):
            if self.__field[1][column] != 0:
                return True
        for column in range(N):
            if self.__field[0][column] != 0:
                return True
        return False
#
# BRICK
#        
class Brick(): 
    # 
    # DESC: BASIC CATALOG         
    _lst_brickModels={
            "I":{"shape":[1,5,3,7], 'color':1},
            "Z":{"shape":[2,5,4,7], 'color':2},
            "S":{"shape":[3,5,4,6], 'color':3},
            "T":{"shape":[3,5,4,7], 'color':4},
            "L":{"shape":[2,5,3,7], 'color':5},
            "J":{"shape":[3,5,7,6], 'color':6},
            "O":{"shape":[2,3,4,5], 'color':7},
                        }

    def __init__(self, playfield):
        self.counterRotation = 0
        self._isOnplayfield = False
        self._playfield=playfield
        self._sprite_block = SPRITE_BLOCK
        self._brickActualPos=[Cell(),Cell(),Cell(),Cell()]
        self._brickmodel=random.choice(list(self._lst_brickModels.keys()))
        #self._brickmodel="S"
        brickModel=self._lst_brickModels[self._brickmodel]["shape"]
        self._color=self._lst_brickModels[self._brickmodel]["color"]
       
        sumX=0
        for idx,cell  in enumerate(self._brickActualPos):
            x=self._lst_brickModels[self._brickmodel]["shape"][idx] %2
            y=self._lst_brickModels[self._brickmodel]["shape"][idx] //2
            sumX=sumX+x
            cell.setX(x)
            cell.setY(y)     
            cell.setColor(self._color)
        self._brickPreviousPos=copy.deepcopy(self._brickActualPos)   
        #for _ in range(random.randrange(0,4)):
        #    self.rotate()
        while not sumX/4 >= 4.5:
            for cell in self._brickActualPos:
                cell.setX(cell.getX()+1)
                sumX=sumX+1  
        while not sumX/4 <= 5.5:
            for cell in self._brickActualPos:
                cell.setX(cell.getX()-1)
                sumX=sumX-1            
        self._brickPreviousPos=copy.deepcopy(self._brickActualPos)
        
    def get(self):
        return self._brickActualPos
    def getCell(self, offset_cell):
        return self._brickActualPos[offset_cell]
    def getColor(self):
        return self._color
    def set(self, brick):
        self._brickActualPos = copy.deepcopy(brick)
    def setCell(self, offset_cell, cell):
        self._brickActualPos[offset_cell] = cell
    def setColor(self, color):
        self._color = color
    def isPositionFree(self):
        for cell in self._brickActualPos:
            try:
                if cell.getX() <0:
                    self._playfield
                    return False 
                if cell.getX() >=N:
                    return False
                if cell.getY() >M-1:
                    return False
                if (self._playfield.get(cell).getColor() != 0):
                    return False 
            except Exception as err:
                return False 
        return True
    
    def isOnPlayfieldY(self):
        for cell in self._brickActualPos:
            if cell.getY() <2:
                return False
        return True
    
    def isOnPlayfieldX(self):
        for cell in self._brickActualPos:
            if cell.getX() <0:
                return False
            if cell.getX() >=N:
                return False
        return True
        
    def enterPlayfield(self):
        self._isOnplayfield =True
        
    def HMove(self, dx):
        self._brickPreviousPos = copy.deepcopy(self._brickActualPos)
        for cell in self._brickActualPos:
            cell.x=cell.x + dx
        if not self.isPositionFree():
            self._brickActualPos = copy.deepcopy(self._brickPreviousPos) # "//" what is B ?
            return False
        return True
    
    def VMove(self, dy):
        self._brickPreviousPos = copy.deepcopy(self._brickActualPos)
        for cell in self._brickActualPos:
            cell.y=cell.y + dy
        if not self.isPositionFree():
            return False
        return True  
    
    def delete(self):
        for cell in self._brickPreviousPos:
            self._playfield.set(cell)
            
    def rotate(self):
        if self._brickmodel =="O":
            return True
        if self._brickmodel =="I":
            newX=[]
            newY=[]
            refV=1
            # TODO : refactor with a better tech if time
            if self._brickActualPos[0].x==self._brickActualPos[1].x:
                newX.append(self._brickActualPos[refV].x+1)
                newX.append(self._brickActualPos[refV].x)
                newX.append(self._brickActualPos[refV].x-1)
                newX.append(self._brickActualPos[refV].x-2)
                newY.append(self._brickActualPos[refV].y)
                newY.append(self._brickActualPos[refV].y)
                newY.append(self._brickActualPos[refV].y)
                newY.append(self._brickActualPos[refV].y)
            else:    
                newX.append(self._brickActualPos[refV].x)
                newX.append(self._brickActualPos[refV].x)
                newX.append(self._brickActualPos[refV].x)
                newX.append(self._brickActualPos[refV].x)
                newY.append(self._brickActualPos[refV].y+1)
                newY.append(self._brickActualPos[refV].y)
                newY.append(self._brickActualPos[refV].y-1)
                newY.append(self._brickActualPos[refV].y-2)
            for x in newX:
                if not(x >= 0 and x <N):
                    return True    
            for idx,cell in enumerate(self._brickActualPos): 
                cell.x = newX[idx]
                cell.y = newY[idx]
            
            if not self.isPositionFree():
                self._brickActualPos = copy.deepcopy(self._brickPreviousPos)
                return False
            return True
        
        if self._brickmodel =="Z":
            newX=[]
            newY=[]
            refV=1
            # TODO : refactor with a better tech if time
            if self._brickActualPos[1].x==self._brickActualPos[3].x:
                newX.append(self._brickActualPos[refV].x+1)
                newX.append(self._brickActualPos[refV].x)
                newX.append(self._brickActualPos[refV].x)
                newX.append(self._brickActualPos[refV].x-1)
                newY.append(self._brickActualPos[refV].y-1)
                newY.append(self._brickActualPos[refV].y)
                newY.append(self._brickActualPos[refV].y-1)
                newY.append(self._brickActualPos[refV].y)  
            else:    
                newX.append(self._brickActualPos[refV].x-1)
                newX.append(self._brickActualPos[refV].x)
                newX.append(self._brickActualPos[refV].x-1)
                newX.append(self._brickActualPos[refV].x)
                newY.append(self._brickActualPos[refV].y-1)
                newY.append(self._brickActualPos[refV].y)
                newY.append(self._brickActualPos[refV].y)
                newY.append(self._brickActualPos[refV].y+1)
            for x in newX:
                if not(x >= 0 and x <N):
                    return True    
            for idx,cell in enumerate(self._brickActualPos): 
                cell.x = newX[idx]
                cell.y = newY[idx]
            if not self.isPositionFree():
                self._brickActualPos = copy.deepcopy(self._brickPreviousPos)
                return False
            return True
        
        if self._brickmodel =="S":
            newX=[]
            newY=[]
            refV=3
            # TODO : refactor with a better tech if time
            if self._brickActualPos[0].x!=self._brickActualPos[3].x-1:
                newX.append(self._brickActualPos[refV].x-1)
                newX.append(self._brickActualPos[refV].x+1)
                newX.append(self._brickActualPos[refV].x)#
                newX.append(self._brickActualPos[refV].x)
                newY.append(self._brickActualPos[refV].y)
                newY.append(self._brickActualPos[refV].y+1)
                newY.append(self._brickActualPos[refV].y)#
                newY.append(self._brickActualPos[refV].y+1)
            else:    
                newX.append(self._brickActualPos[refV].x+1)
                newX.append(self._brickActualPos[refV].x+1)
                newX.append(self._brickActualPos[refV].x)#
                newX.append(self._brickActualPos[refV].x)
                newY.append(self._brickActualPos[refV].y-1)
                newY.append(self._brickActualPos[refV].y)
                newY.append(self._brickActualPos[refV].y)#
                newY.append(self._brickActualPos[refV].y+1)
            for x in newX:
                if not(x >= 0 and x <N):
                    return True    
            for idx,cell in enumerate(self._brickActualPos): 
                cell.x = newX[idx]
                cell.y = newY[idx]
            if not self.isPositionFree():
                self._brickActualPos = copy.deepcopy(self._brickPreviousPos)
                return False
            return True
             
        if self._brickmodel =="L" or self._brickmodel =="J" or self._brickmodel =="T":
            massCenterX=copy.deepcopy(self._brickActualPos)[1].x
            massCenterY=copy.deepcopy(self._brickActualPos)[1].y    
            assignNew=True
            for cell in self._brickActualPos:
                newX=massCenterX - (cell.y-massCenterY)
                newY=massCenterY + (cell.x-massCenterX)
                for cell in self._brickActualPos:
                    if not(newX >= 0 and newX <N):
                        assignNew=False
            if assignNew:      
                for cell in self._brickActualPos: 
                    newX=massCenterX - (cell.y-massCenterY)
                    newY=massCenterY + (cell.x-massCenterX)      
                    cell.x = newX
                    cell.y = newY
            if not self.isPositionFree():
                self._brickActualPos = copy.deepcopy(self._brickPreviousPos)
                return False
            return True
        
    def draw(self, level):
        if self._isOnplayfield:
            for idxC, cell in enumerate(self._brickActualPos):
                if cell.y > 1:
                    pg_Window.blit( 
                                    self._sprite_block, 
                                    (cell.x*CELL_SIZE+PLAYFIELD_X_OFFSET, cell.y*CELL_SIZE+PLAYFIELD_Y_OFFSET), 
                                    (self._color*CELL_SIZE,CELL_SIZE*(level%4),CELL_SIZE,CELL_SIZE) 
                                )#self._color
        else:
            for idxC, cell in enumerate(self._brickActualPos):
                pg_Window.blit( 
                                self._sprite_block, 
                                (194+cell.x*CELL_SIZE+PLAYFIELD_X_OFFSET, 320-36+cell.y*CELL_SIZE+PLAYFIELD_Y_OFFSET), 
                                (self._color*CELL_SIZE,0+CELL_SIZE*(level%4),CELL_SIZE,CELL_SIZE) 
                            )#self._color
#
# (HMOVING)TIMER
#
class HMovingTimer():
    def __init__(self, delay=0):
        self.__delay=delay
        self.reset()
    def reset(self):
        self.__actualTime=time.clock_gettime(time.CLOCK_REALTIME)
        self.__startTime=self.__actualTime
    def getDifference(self):
        self.__actualTime=time.clock_gettime(time.CLOCK_REALTIME)
        return self.__actualTime-self.__startTime
    def setDelay(self, delay):
        self.__delay=delay
    def isOverdelay(self):
        return self.getDifference() > self.__delay
    def getAndResetOnDelay(self):
        if self.isOverdelay():
            self.reset()
            return True
        return False     
    
##############################################
# PYGAME INIT & ASSETS LOADING
##############################################

pygame.init()
pygame.mixer.init()
pg_Window = pygame.display.set_mode((X_SCREEN, Y_SCREEN))
# DEPRECATED : pg_Window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)   
# ALCO: CONFIGURE INPUTS
pygame.key.set_repeat(150, 45)
# ALGO: LOAD ASSETS
# DESC: fonts
SCORE_FONT = pygame.freetype.Font(os.path.join(PATH_FONTS, f"unifont-14.0.04.ttf"), 16)
LARGE_FONT = pygame.freetype.Font(os.path.join(PATH_FONTS, f"unifont-14.0.04.ttf"),115)
SMALL_FONT = pygame.freetype.Font(os.path.join(PATH_FONTS, f"unifont-14.0.04.ttf"),10)

# DESC: images
SPRITE_BLOCK = pygame.image.load(os.path.join(PATH_IMGS, f"tiles2.png")).convert_alpha()
backBackground = pygame.image.load(os.path.join(PATH_IMGS, f"redArea.png")).convert_alpha()
background = pygame.image.load(os.path.join(PATH_IMGS, f"background2.png")).convert_alpha()
frame = pygame.image.load(os.path.join(PATH_IMGS, f"frame2.png")).convert_alpha()
# DESC: sounds
snd_struggle = pygame.mixer.Sound(os.path.join(PATH_SOUNDS, 'sfx-struggle.wav'))
tetrisTheme = pygame.mixer.music.load(os.path.join(PATH_SOUNDS, 'Tetris8BitRemixCover.wav'))
pygame.mixer.Sound.set_volume(snd_struggle, SFX_VOLUME)
pygame.mixer.music.set_volume(MUSIC_VOLUME)
clock = pygame.time.Clock()

##############################################
# PYGAME DRAWING SCREENS & BOXES
##############################################
#
# SCREEN: SCORE
#
def drawScreenScore(dict_score, hOffset=1, vOffset=-50, haveTitle=True, Title=f"last game"):
    if haveTitle is True:
        text_surface, rect = SCORE_FONT.render(Title,  RGB_WHITE)
        pg_Window.blit(text_surface, (265+hOffset,60+vOffset))     
    text_surface, rect = SCORE_FONT.render(f"score:", RGB_WHITE)
    pg_Window.blit(text_surface, (265+hOffset,90+vOffset))
    text_surface, rect = SCORE_FONT.render(f'    {str(dict_score["score"]).zfill(9)}', RGB_WHITE)
    pg_Window.blit(text_surface, (265+hOffset,105+vOffset))
    text_surface, rect = SCORE_FONT.render(f"lines:",  RGB_WHITE) 
    pg_Window.blit(text_surface, (265+hOffset,125+vOffset))
    text_surface, rect = SCORE_FONT.render(f'    {str(dict_score["totalCleanedLines"]).zfill(9)}',  RGB_WHITE)
    pg_Window.blit(text_surface, (265+hOffset,140+vOffset))
    text_surface, rect = SCORE_FONT.render(f"level:",  RGB_WHITE) 
    pg_Window.blit(text_surface, (265+hOffset,160+vOffset))
    text_surface, rect = SCORE_FONT.render(f'    {str(dict_score["level"]).zfill(9)}',  RGB_WHITE)
    pg_Window.blit(text_surface, (265+hOffset,175+vOffset))   
#
# SCREEN: PAUSE
#     
def drawScreenPause(isGaming=True, isRunnig=True):
    isPaused = True
    pg_Window.fill(RGB_BLACK)
    text_surface, rect = LARGE_FONT.render("paused", RGB_WHITE)
    rect.center = ((X_SCREEN/2),(Y_SCREEN/2))
    pg_Window.blit(text_surface, rect)
    while isPaused:
        try:
            # TODO: Key Loop Manager function (factory & configuration key-funct by hashtable)
            for event in pygame.event.get():

                if event.type == KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        isPaused = False
                    if event.key == pygame.K_ESCAPE:
                        isPaused = False
                        isGaming = False
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    quit()                   
        except:
            pass
        pygame.display.update()
        clock.tick(FPS_MENU)
    return isGaming, isRunnig
#
# SCREEN: TITLE
#  
def drawScreenTitle(dict_highScore,dict_score, isGaming=False, isRunning=True):
    titleVOffset = -50
    pg_Window.fill(RGB_BLACK)
    text_surface, rect = SMALL_FONT.render("today I need a little bit of...",  RGB_GREY)
    pg_Window.blit(text_surface, (150,335+titleVOffset))
    text_surface, rect = LARGE_FONT.render("TETRIS",  RGB_WHITE)
    pg_Window.blit(text_surface, (150,350+titleVOffset))
    text_surface, rect = SCORE_FONT.render(f"<SPACE> to start --- <ESC> to quit",  RGB_WHITE)
    pg_Window.blit(text_surface, (180,300+titleVOffset))
    if dict_highScore["score"]>0:            
        drawScreenScore(dict_score, hOffset=-120, vOffset=(50+titleVOffset), haveTitle=True, Title=f"last game")
        drawScreenScore(dict_highScore, hOffset=120, vOffset=(50+titleVOffset), haveTitle=True, Title=f"high score")
    isWaiting = True
    while isWaiting:
        try:
            # TODO: Key Loop Manager function (factory & configuration key-funct by hashtable)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        isWaiting = False
                        isGaming = True
                    if event.key == K_ESCAPE:
                        isWaiting = False
                        isRunning = False
                        isGaming = False 
                elif event.type == QUIT:
                    isWaiting = False
                    isRunning = False
                    isGaming = False
        except:
            pass   # TODO: ERROR MANAGEMENT   
        pygame.display.update()
        clock.tick(FPS_MENU)
    return isGaming, isRunning

##############################################
# PYGAME GAME LOOP
##############################################
#
# HELPER FUNCTION: SCORE
#      
def updateScore(dict_score, CleanedLines=0, freeEmptyCells=0):
    dict_score=copy.deepcopy(dict_score)
    gain=[0,40,100,300,1200]
    dict_score["totalCleanedLines"]= dict_score["totalCleanedLines"]+CleanedLines
    if (dict_score["totalCleanedLines"])%NB_LINES_BY_LEVEL ==0: # TODO: pass each brick posed, do better than that !
        dict_score["level"]=(dict_score["totalCleanedLines"])//NB_LINES_BY_LEVEL
    dict_score["score"] = dict_score["score"] + gain[CleanedLines]*(dict_score["level"]+1)
    dict_score["score"] = dict_score["score"] + freeEmptyCells
    return dict_score

# ALGO: STARTING CONDITIONS
isRunning  = True # ALGO: SWITCH ON RUNNING MODE
isGaming = False  # ALGO: NOT SWITCHING ON AUTO GAMING AT START
dict_score={"score":0,"level":0,"totalCleanedLines":0,} 
dict_highScore={"score":0,"level":0,"totalCleanedLines":0,}
while isRunning:
    # ALGO: MAIN LOOP & TITLE SCREEN
    if dict_highScore["score"] < dict_score["score"]:
        dict_highScore=copy.deepcopy(dict_score)
    isGaming, isRunning=drawScreenTitle(dict_highScore, dict_score, isGaming, isRunning)
    while isGaming:
        # ALGO: STARTING A NEW GAME
        dict_score={"score":0,"level":0,"totalCleanedLines":0,}
        dx=0
        dy=1
        rotate=False
        timer=0
        movingTimer=HMovingTimer()
        speed = INITIAL_SPEED
        movingTimer.setDelay(speed) 
        pf_playfield=playfield() # DESC: need the playfield 
        b_brick=Brick(pf_playfield) # DEsc: add the first brick on the playfield 
        b_brick.enterPlayfield() # DESC: activate first brick 
        b_nextBrick=Brick(pf_playfield) # DESC: add the "next" brick 
        pygame.mixer.music.play(-1)
        while isGaming:
            # ALGO: STARTING THE PLAYER LOOP 
            movingTimer.setDelay(speed)
            # ALGO: MESSAGES PUMP
            for event in pygame.event.get():
                # TODO: Key Loop Manager function (factory & configuration key-funct by hashtable)
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        # ALGO: SWITCH TO A QUIET PAUSE MODE
                        pygame.mixer.music.stop() # DESC: all sonud is managed in main program
                        isGaming, isRunning=drawScreenPause(isGaming, isRunning)
                        pygame.mixer.music.play(-1)  
                    if event.key == K_ESCAPE:
                        # ALGO: SWITCH GAMING MODE
                        isGaming = False 
                    if (event.key == K_UP):
                        # DESC: be "free" = can rotate
                        isFree = b_brick.rotate() 
                        if not isFree:
                            movingTimer.setDelay(0.0) # DESC: move/test line NOW on can't rotate   
                    if (event.key == K_LEFT):
                        isFree = b_brick.HMove(-1) 
                    if (event.key == K_RIGHT):
                        isFree = b_brick.HMove(1)
                    if (event.key == K_DOWN):
                        movingTimer.setDelay(speed/4) # DESC: move quickly
                elif event.type == QUIT:
                    isRunning = False
                    isGaming = False
            isBrickAlive =True        
            if movingTimer.getAndResetOnDelay(): # DESC: if needed to test the brick posiiion
                isBrickAlive = b_brick.VMove(1)
            if not isBrickAlive: # DESC: if brick can't move
                b_brick.delete() # DESC: transform brick to colored "background" on playfield
                CleanedLines, freeEmptyCells=pf_playfield.cleanLines() # DESC: clean lines in background of playfield 
                # ALGO: LINE FOUND
                if CleanedLines >0:
                    pygame.mixer.Sound.play(snd_struggle) 
                dict_score=updateScore(dict_score, CleanedLines, freeEmptyCells)     
                b_brick = b_nextBrick 
                b_brick.enterPlayfield()
                b_nextBrick=Brick(pf_playfield)
                pg_Window.fill(RGB_BLACK)
            # ALGO: PYGAME DRAWING
            pg_Window.blit(backBackground, (-150, -50))   
            pg_Window.blit(background, (0, 0))
            drawScreenScore(dict_score, hOffset=1, vOffset=-4, haveTitle=False, Title=None)
            b_brick.draw(dict_score["level"])
            b_nextBrick.draw(dict_score["level"])
            pf_playfield.draw(dict_score["level"])
            pg_Window.blit(frame, (0, 0))
            # ALGO: GO TO NEXT GAME "FRAME"
            clock.tick(FPS_GAME)
            # ALGO: TEST IF GAME ENDED
            if pf_playfield.isOverLoad():
                isGaming = False
            else:
                pygame.display.flip()
        pygame.mixer.music.stop()
pygame.quit()
quit()
