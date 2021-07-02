import random, sys, copy, os, pygame
from pygame.locals import *

FPS = 30
winWidth = 800
winHeight = 600
half_winWidth = int(winWidth / 2)
half_winHeight = int(winHeight / 2)

tileWidth = 50
tileHeight = 85
tileFloorHeight = 45

cam_move_speed = 5
outside_decoration_pct = 20

brightBlue = (0, 170, 255)
white = (255, 255, 255)
BGcolor = brightBlue
textColor = white

up = 'up'
down = 'down'
left = 'left'
right = 'right'

def main():
    global FPSclock, displaySurf, imagesDict, tileMapping, outsideDecoMapping, basicFont, playerImages, currentImage

    pygame.init()
    FPSclock = pygame.time.Clock()

    displaySurf = pygame.display.set_mode((winWidth, winHeight))
    pygame.display.set_caption('Star Pusher')
    basicFont = pygame.font.Font('freesansbold.ttf' , 18)

    imagesDict = {'uncovered goal': pygame.image.load('RedSelector.png'),
                  'covered goal': pygame.image.load('Selector.png'),
                  'star': pygame.image.load('Star.png'),
                  'corner': pygame.image.load('Wall_Block_Tall.png'),
                  'wall': pygame.image.load('Wood_Block_Tall.png'),
                  'inside floor': pygame.image.load('Plain_Block.png'),
                  'outside floor': pygame.image.load('Grass_Block.png'),
                  'title': pygame.image.load('star_title.png'),
                  'solved': pygame.image.load('star_solved.png'),
                  'princess': pygame.image.load('princess.png'),
                  'boy': pygame.image.load('boy.png'),
                  'catgirl': pygame.image.load('catgirl.png'),
                  'horngirl': pygame.image.load('horngirl.png'),
                  'pinkgirl': pygame.image.load('pinkgirl.png'),
                  'rock': pygame.image.load('Rock.png'),
                  'short tree': pygame.image.load('Tree_Short.png'),
                  'tall tree': pygame.image.load('Tree_Tall.png'),
                  'ugly tree': pygame.image.load('Tree_Ugly.png')}

    tileMapping = {'x': imagesDict['corner'],
                   '#': imagesDict['wall'],
                   'o': imagesDict['inside floor'],
                   ' ': imagesDict['outside floor']}

    outsideDecoMapping = {'1': imagesDict['rock'],
                          '2': imagesDict['short tree'],
                          '3': imagesDict['tall tree'],
                          '4': imagesDict['ugly tree']}

    currentImage = 0
    playerImages = [imagesDict['princess'],
                    imagesDict['boy'],
                    imagesDict['catgirl'],
                    imagesDict['horngirl'],
                    imagesDict['pinkgirl']]

    startScreen()
    levels = readLevelsFile('starPusherLevels.txt')
    currentLevelIndex = 0

    while True:
        result = runLevel(levels, currentLevelIndex)

        if result in ('solved', 'next'):
            currentLevelIndex += 1
            if currentLevelIndex >= len(levels):
                currentLevelIndex = 0
        elif result == 'back':
            currentLevelIndex -= 1
            if currentLevelIndex < 0:
                currentLevelIndex = len(levels)-1
        elif result == 'reset':
            pass



def runLevel(levels, levelNum):
    global currentImage
    levelObj = levels[levelNum]
    mapObj = decorateMap(levelObj['mapObj'], levelObj['startState']['player']) #
    gameStateObj = copy.deepcopy(levelObj['startState'])

    mapNeedsRedraw = True
    levelSurf = basicFont.render('Level %s of %s' % (levelNum+1 , len(levels)), 1, textColor)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, winHeight - 35) #
    mapWidth = len(mapObj) * tileWidth
    mapHeight = (len(mapObj[0]) - 1) * tileFloorHeight + tileHeight #because of the overlaping
    max_cam_x_pan = abs(half_winHeight - int(mapHeight / 2)) + tileWidth
    max_cam_y_pan = abs(half_winWidth - int(mapWidth / 2)) + tileHeight

    levelIsComplete = False

    cameraOffsetX = 0
    cameraOffsetY = 0

    cameraUp = False
    cameraDown = False
    cameraLeft = False
    cameraRight = False

    while True:

        playerMoveTo = None
        keyPressed = False

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                keyPressed = True
                if event.key == K_LEFT:
                    playerMoveTo = left
                elif event.key == K_RIGHT:
                    playerMoveTo = right
                elif event.key == K_UP:
                    playerMoveTo = up
                elif event.key == K_DOWN:
                    playerMoveTo = down

                elif event.key == K_a:
                    cameraLeft = True
                elif event.key == K_d:
                    cameraRight = True
                elif event.key == K_w:
                    cameraUp = True
                elif event.key == K_s:
                    cameraDown = True

                elif event.key == K_n:
                    return 'next'
                elif event.key == K_b:
                    return 'back'

                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_BACKSPACE:
                    return 'reset'
                elif event.key == K_p:
                    currentImage += 1
                    if currentImage >= len(playerImages):
                        currentImage = 0
                    mapNeedsRedraw = True

            elif event.type == KEYUP:
                if event.key == K_a:
                    cameraLeft = False
                elif event.key == K_d:
                    cameraRight = False
                elif event.key == K_w:
                    cameraUp = False
                elif event.key == K_s:
                    cameraDown = False

        if playerMoveTo != None and not levelIsComplete:
            moved = makeMove(mapObj, gameStateObj, playerMoveTo)

            if moved:
                gameStateObj['stepCounter'] += 1 #
                mapNeedsRedraw = True

            if isLevelFinished(levelObj, gameStateObj):
                levelIsComplete = True
                keyPressed = False

        displaySurf.fill(BGcolor)

        if mapNeedsRedraw:
            mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'])
            mapNeedsRedraw = False

        if cameraUp and cameraOffsetY < max_cam_x_pan:  #
            cameraOffsetY += cam_move_speed
        elif cameraDown and cameraOffsetY > -max_cam_x_pan:
            cameraOffsetY -= cam_move_speed
        if cameraLeft and cameraOffsetX < max_cam_y_pan:
            cameraOffsetX += cam_move_speed
        elif cameraRight and cameraOffsetX > -max_cam_y_pan:
            cameraOffsetX -= cam_move_speed


        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = (half_winWidth + cameraOffsetX, half_winHeight + cameraOffsetY)

        displaySurf.blit(mapSurf, mapSurfRect)

        displaySurf.blit(levelSurf, levelRect)
        stepSurf = basicFont.render('Steps: %s' %(gameStateObj['stepCounter']), 1, textColor)
        stepRect = stepSurf.get_rect()
        stepRect.bottomleft = (20, winHeight - 10)
        displaySurf.blit(stepSurf, stepRect)

        if levelIsComplete:
            solvedRect = imagesDict['solved'].get_rect()
            solvedRect.center = (half_winWidth, half_winHeight)
            displaySurf.blit(imagesDict['solved'], solvedRect)

            if keyPressed:
                return 'solved'

        pygame.display.update()
        FPSclock.tick()



def isWall(mapObj, x, y):
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False
    elif mapObj[x][y] in ('#' , 'x'):
        return True
    return False


def decorateMap(mapObj, startxy):
    startx, starty = startxy

    mapObjCopy = copy.deepcopy(mapObj)

    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in ('$', '.', '@', '+', '*'):
                mapObjCopy[x][y] = ' '

    floodFill(mapObjCopy, startx, starty, ' ', 'o')

    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] == '#':
                if (isWall(mapObjCopy, x, y-1) and isWall(mapObjCopy, x+1, y)) or \
                   (isWall(mapObjCopy, x+1, y) and isWall(mapObjCopy, x, y+1)) or \
                   (isWall(mapObjCopy, x, y+1) and isWall(mapObjCopy, x-1, y)) or \
                   (isWall(mapObjCopy, x-1, y) and isWall(mapObjCopy, x, y-1)):
                    mapObjCopy[x][y] = 'x'

            elif mapObjCopy[x][y] == ' ' and random.randint(0, 99) < outside_decoration_pct:    #?
                mapObjCopy[x][y] = random.choice(list(outsideDecoMapping.keys()))

    return mapObjCopy


def isBlocked(mapObj, gameStateObj, x, y):
    if isWall(mapObj, x, y):
       return True
    elif x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
       return True
    elif (x, y) in gameStateObj['stars']:
       return True
    return False


def makeMove(mapObj, gameStateObj, playerMoveTo):

    playerx, playery = gameStateObj['player']
    stars = gameStateObj['stars']

    if playerMoveTo == up:
        xOffset = 0
        yOffset = -1
    elif playerMoveTo == right:
        xOffset = 1
        yOffset = 0
    elif playerMoveTo == down:
        xOffset = 0
        yOffset = 1
    elif playerMoveTo == left:
        xOffset = -1
        yOffset = 0

    if isWall(mapObj, playerx + xOffset, playery + yOffset):
        return False
    else:
        if (playerx + xOffset, playery + yOffset) in stars:
            if not isBlocked(mapObj, gameStateObj, playerx + (xOffset*2), playery + (yOffset*2)):
               ind = stars.index((playerx + xOffset, playery + yOffset))
               stars[ind] = (stars[ind][0] + xOffset, stars[ind][1] + yOffset) #why tuple and "[ind][0]"
            else:
                return False

        gameStateObj['player'] = (playerx + xOffset, playery + yOffset)
        return True


def startScreen():

    titleRect = imagesDict['title'].get_rect()
    topCoord = 50
    titleRect.top = topCoord
    titleRect.centerx = half_winWidth
    topCoord += titleRect.height

    instructionText = ['Push the stars over the marks.',
                       'Arrow keys to move, WASD for camera control, P to change character.',
                       'Backspace to reset level, Esc to quit.',
                       'N for next level, B to go back a level.']

    displaySurf.fill(BGcolor)
    displaySurf.blit(imagesDict['title'], titleRect)

    for i in range(len(instructionText)):
        instSurf = basicFont.render(instructionText[i], 1, textColor)
        instRect = instSurf.get_rect()
        topCoord += 10
        instRect.top = topCoord
        instRect.centerx = half_winWidth
        topCoord += instRect.height
        displaySurf.blit(instSurf, instRect)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return

        pygame.display.update()
        FPSclock.tick()


def readLevelsFile(filename):
    assert os.path.exists(filename), 'Cannot find the level file: %s' % (filename) #

    mapFile = open(filename, 'r')
    content = mapFile.readlines() + ['\r\n']  # \r??
    mapFile.close()

    levels = []
    levelNum = 0
    mapTextLines = []
    mapObj = []
    for lineNum in range(len(content)):
        line = content[lineNum].rstrip('\r\n')  #

        if ';' in line:
            line = line[:line.find(';')]

        if line != '':
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0:
            maxWidth = -1
            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])

            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i]))

            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x])

            startx = None
            starty = None
            goals = []
            stars = []
            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    #searching in each colomn "mapobj[x] is a colomn"
                    if mapObj[x][y] in ('@', '+'):
                        startx = x
                        starty = y
                    if mapObj[x][y] in ('.', '+', '*'):
                        goals.append((x, y))
                    if mapObj[x][y] in ('$', '*'):
                        stars.append((x, y))

            assert startx != None and starty != None,  'Level %s (around line %s) in %s is missing a "@" or "+" to mark the start point.' % (levelNum+1, lineNum, filename)
            assert len(goals) > 0, 'Level %s (around line %s) in %s must have at least one goal.' % (levelNum+1, lineNum, filename)
            assert len(stars) >= len(goals), 'Level %s (around line %s) in %s is impossible to solve. It has %s goals but only %s stars.' % (levelNum+1, lineNum, filename, len(goals), len(stars))

            gameStateObj = {'player': (startx, starty),
                            'stepCounter' : 0,
                            'stars' : stars}
            levelObj = {'widht' : maxWidth,
                        'height' : len(mapObj), #how it represents the height
                        'mapObj' : mapObj,
                        'goals' : goals,
                        'startState' : gameStateObj}

            levels.append(levelObj)

            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            levelNum += 1
    return levels


def floodFill(mapObj, x, y, oldCharacter, newCharacter):
    #I do floodFill to the conected components

    if mapObj[x][y] == oldCharacter:
        mapObj[x][y] = newCharacter

    if x < len(mapObj) - 1 and mapObj[x+1][y] == oldCharacter:
        floodFill(mapObj, x+1, y, oldCharacter, newCharacter) #right
    if x > 0 and mapObj[x-1][y] == oldCharacter:
        floodFill(mapObj, x-1, y, oldCharacter, newCharacter) #left
    if y < len(mapObj[x]) - 1 and mapObj[x][y+1] == oldCharacter:
        floodFill(mapObj, x, y+1, oldCharacter, newCharacter) #down
    if y > 0 and mapObj[x][y-1] == oldCharacter:
        floodFill(mapObj, x, y-1, oldCharacter, newCharacter) #up


def drawMap(mapObj, gameStateObj, goals):

    mapSurfWidth = len(mapObj) * tileWidth
    mapSurfHeight = (len(mapObj[0]) - 1) * tileFloorHeight + tileHeight
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(BGcolor)

    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect((x * tileWidth, y * tileFloorHeight, tileWidth, tileHeight))  ##
            if mapObj[x][y] in tileMapping:
                baseTile = tileMapping[mapObj[x][y]]
            elif mapObj[x][y] in outsideDecoMapping:
                baseTile = tileMapping[' ']

            mapSurf.blit(baseTile, spaceRect)

            if mapObj[x][y] in outsideDecoMapping:
                mapSurf.blit(outsideDecoMapping[mapObj[x][y]], spaceRect)
            elif (x, y) in gameStateObj['stars']:
                if (x, y) in goals:
                    mapSurf.blit(imagesDict['covered goal'], spaceRect)
                mapSurf.blit(imagesDict['star'], spaceRect)
            elif (x, y) in goals:
                mapSurf.blit(imagesDict['covered goal'], spaceRect)

            if (x, y) == gameStateObj['player']:
                mapSurf.blit(playerImages[currentImage], spaceRect)
        
    return mapSurf


def isLevelFinished(levelObj, gameStateObj):
    for goal in levelObj['goals']:
        if goal not in gameStateObj['stars']:
            return False
    return True


def terminate():
    pygame.quit()
    sys.exit()
 



if __name__ == '__main__':
    main()















    
    
        
        

    

    



