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
    KEYDOWN,
    QUIT,
)
import pygame.freetype
import copy

PATH_IMGS="assets/imgs/"
PATH_FONTS="assets/fonts/"
X_SCREEN = 640
Y_SCREEN = 480
N = 10 # WARN: 10 + 1 for allowing tests (change test method for reduce table ?)   
M = 22
CELL_SIZE=18
PLAYFIELD_X_OFFSET=28
PLAYFIELD_Y_OFFSET=-5
INITIAL_SPEED=0.45
KEY_DOWN_SPEED=0.05

class Cell():
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
    
class playfield():
    def __init__(self):
        self.__sprite_block = SPRITE_BLOCK
        self.__field=[]
        for y in range(M): # TODO: more efficient
            self.__field.append([])
            for x in range(N):
                self.__field[y].append(0)       
        #self.__field=[[0]*N]*M  # DESC: M*[LINE of Nx0] not work cause of memory copy as adress in PYTHON
    def set(self,cell):
        self.__field[cell.getY()][cell.getX()] = cell.getColor()
    def get(self,cell):
        return Cell(cell.getX(),cell.getY(),self.__field[cell.getY()][cell.getX()])
    def draw(self):
        for idxLine, line in  enumerate(self.__field):
            for idxColumn,int_cell in enumerate(line):
                if int_cell==0:
                    continue
                pg_Window.blit(     
                            self.__sprite_block, 
                            (idxColumn*CELL_SIZE+PLAYFIELD_X_OFFSET,idxLine*CELL_SIZE+PLAYFIELD_Y_OFFSET), 
                            (int_cell*CELL_SIZE+8*CELL_SIZE,0,CELL_SIZE,CELL_SIZE)
                        )                
    def cleanLines(self):
        linesCounter=0
        for idxLine, line in enumerate(self.__field):
            if 0 in line:
                continue
            for onTopY in range(idxLine,0,-1):
                for column in range(N):
                    self.__field[onTopY][column]=self.__field[onTopY-1][column]
                for column in range(N):
                    self.__field[0][column] = 0
            linesCounter = linesCounter + 1    
            time.sleep(0.25)
        print(linesCounter)
        return linesCounter
    
    def isOverLoad(self):
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
        
class Brick():          
    _lst_brickModels={
            "I":{"shape":[1,5,3,7], 'color':1},
            "Z":{"shape":[2,4,5,7], 'color':2},
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
        
    def draw(self):
        if self._isOnplayfield:
            for idxC, cell in enumerate(self._brickActualPos):
                if cell.y > 1:
                    pg_Window.blit( 
                                    self._sprite_block, 
                                    (cell.x*CELL_SIZE+PLAYFIELD_X_OFFSET, cell.y*CELL_SIZE+PLAYFIELD_Y_OFFSET), 
                                    (self._color*CELL_SIZE,0,CELL_SIZE,CELL_SIZE) 
                                )#self._color
        else:
            for idxC, cell in enumerate(self._brickActualPos):
                pg_Window.blit( 
                                self._sprite_block, 
                                (194+cell.x*CELL_SIZE+PLAYFIELD_X_OFFSET, 320-36+cell.y*CELL_SIZE+PLAYFIELD_Y_OFFSET), 
                                (self._color*CELL_SIZE,0,CELL_SIZE,CELL_SIZE) 
                            )#self._color
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
        #print(("delay",self.__delay,"start",self.__startTime,"actual",self.__actualTime, "diff", self.getDifference(),"isOverdelay",self.isOverdelay()))
        if self.isOverdelay():
            self.reset()
            return True
        return False     
         
pygame.init()
pg_Window = pygame.display.set_mode((X_SCREEN, Y_SCREEN))
pygame.key.set_repeat(400, 30)
SCORE_FONT = pygame.freetype.Font(os.path.join(PATH_FONTS, f"unifont-14.0.04.ttf"), 24)
SPRITE_BLOCK = pygame.image.load(os.path.join(PATH_IMGS, f"tiles2.png")).convert()
background = pygame.image.load(os.path.join(PATH_IMGS, f"background2.png")).convert()
frame = pygame.image.load(os.path.join(PATH_IMGS, f"frame2.png")).convert_alpha()
clock = pygame.time.Clock()
movingTimer=HMovingTimer()
movingTimer.setDelay(INITIAL_SPEED)
pf_playfield=playfield() 
b_brick=Brick(pf_playfield)
b_brick.enterPlayfield()
b_nextBrick=Brick(pf_playfield)
dx=0
dy=1
rotate=False
timer=0
running = True
score = 0
totalCleanedLines=0
level=0
while running:
    
    movingTimer.setDelay(INITIAL_SPEED)
    
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False 
            if (event.key == K_UP):
                free = b_brick.rotate()
                if not free:
                    movingTimer.setDelay(0.0)    
            if (event.key == K_LEFT):
                free = b_brick.HMove(-1) 
            if (event.key == K_RIGHT):
                free = b_brick.HMove(1)
            if (event.key == K_DOWN):
                movingTimer.setDelay(KEY_DOWN_SPEED) 
        elif event.type == QUIT:
            running = False  
    isBrickAlive =True        
    if movingTimer.getAndResetOnDelay():
        isBrickAlive = b_brick.VMove(1)
    if not isBrickAlive:
        b_brick.delete()
        CleanedLines=pf_playfield.cleanLines()
        print(("CleanedLines",CleanedLines))
        totalCleanedLines= totalCleanedLines+CleanedLines
        if CleanedLines ==1:
            score = score+ 40*(level+1)
        if CleanedLines ==2:
            score = score+ 100*(level+1)
        if CleanedLines ==3:
            score = score+ 300*(level+1)
        if CleanedLines ==4:
            score = score+ 1200*(level+1)    
        b_brick = b_nextBrick
        b_brick.enterPlayfield()
        b_nextBrick=Brick(pf_playfield)
    pg_Window.fill((255,255,255))    
    pg_Window.blit(background, (0, 0))
    text_surface, rect = SCORE_FONT.render(str(score), (0, 0, 0))
    pg_Window.blit(text_surface, (300,100))
    b_brick.draw()
    b_nextBrick.draw()
    #time.sleep(0.1)
    pf_playfield.draw()
    pg_Window.blit(frame, (0, 0))
    if pf_playfield.isOverLoad():
            running = False  
    #time.sleep(0.1)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()

exit(0)






while running:
    fl_time = time.clock_gettime(time.CLOCK_REALTIME)-actualTime
    actualTime=time.clock_gettime(time.CLOCK_REALTIME)
    timer += fl_time
    
    
    for i in range(4):
        b[i]=copy.deepcopy(a[i])
        a[i].x+=dx
    
    print(check)
    for i in range(4):
        if not check():
           a[i]=copy.deepcopy(b[i])
           
    if rotate:
        p=copy.deepcopy(a[i])
        for i in range(4):
            x = a[i].y-p.y
            y = a[i].x-p.x
            a[i].x = p.x - x
            a[i].y = p.y + y
            for i in range(4):
                if not check():
                    a[i]=copy.deepcopy(b[i])
    
    if timer>delay:
        for i in range(4):
            b[i]=copy.deepcopy(a[i])
            a[i].y=a[i].y+1
        if not check():
            for i in range(4):
                PLAY_FIELD[b[i].y][b[i].x]=colorNum
            colorNum=1+random.randrange(0, 7)
            n = random.randrange(0, 7)
            for i in range(4):
                a[i].x = figures[n][i] % 2
                a[i].y = figures[n][i] // 2
        timer=0           
    
    k=M-1
    for i in range(M-1,0,-1):
        print((M,i))
        count=0
        for j in range(0,N):
            if not PLAYFIELD[i][j]==0:
                count=count+1
            PLAYFIELD[k][j]=PLAYFIELD[i][j]
        if count < N:
            k = k-1
    dx=0
    rotate=False
    delay=0.3 
    
    pg_Window.blit(background, (0, 0))
    for i in range(0,M):
        for j in range(0,N):
            if PLAYFIELD[i][j]==0:
                continue
            #pg_Window.blit( s, (j*18,i*18), (FIELD[i][j]*18,0,18,18) )
            pg_Window.blit( s, (j*18+28,i*18+31), (PLAY_FIELD[i][j]*18,0,18,18) )
    for i in range(0,4):
            pg_Window.blit( s, (a[i].x*18+28,a[i].y*18+31), (colorNum*18,0,18,18) )
    #pg_Window.blit(frame, (0, 0))
