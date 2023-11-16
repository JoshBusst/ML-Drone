
'''
@brief
Converts a world point into a pixel coordinate in the sim
'''
def world2Screen(worldPoint):
    from numpy import subtract, multiply
    from Lib import roundc

    # offset the world point
    offset = [dim[0] for dim in worldDimsXY]
    offsetPoint = subtract( worldPoint,  offset )
    screenPoint = multiply( offsetPoint, screen2WorldRatioXY )
    
    # account for pixel coordinate frame (+Xscreen -> left, +Yscreen -> down)
    screenPoint[1] = screen_size[1] - screenPoint[1]

    return roundc(screenPoint)
 


'''
@brief
Converts a pixel coordinate in the sim to a world coordinate
'''
def screen2World(screenPoint):
    from numpy import divide, add

    rawWorldPoint    = divide( screenPoint, screen2WorldRatioXY )
    offsetWorldPoint = add( rawWorldPoint, [dim[0] for dim in worldDimsXY] )

    return offsetWorldPoint



'''
@brief
Blits an image from its centre. This ensures graphics are drawn
where they are intended and that the drone rotates around its
centre of mass.
'''
def drawImgCentre(img, point):
    assert(len(point) == 2)

    # centre image exactly on point
    rect = img.get_rect()
    rect.center = tuple(point)

    # draw image to graphics object
    screen.blit( img, rect )



'''
@brief
Collects the relevant drone sprite colour and draws
it to the graphics object. Does not update to screen.
'''
def drawDrone(drone):
    from numpy import degrees
    from pygame import transform

    # get and rotate sprite
    droneSprite = droneSprites[drone.spriteColour]
    droneSprite = transform.rotate(droneSprite, degrees(drone.state.theta))

    # draw drone at point
    pointIJ = world2Screen( [drone.state.x, drone.state.y] ) # pixel coordinates
    drawImgCentre(droneSprite, pointIJ)



'''
@brief
For the sake of consistency with the drawDrone and
drawText functions. This function draws a target
sprite at the given point.
'''
def drawTarget(point):
    pointIJ = world2Screen(point)
    drawImgCentre(targetSprite, pointIJ)



'''
@brief
Draws a text string to the console
'''
def drawText(text, loc=(0,0), textColour=(0,0,0), fontSize=20):
    from pygame import font

    font = font.SysFont('Comic Sans MS', fontSize)
    textSurface = font.render(text, False, tuple(textColour))
    
    screen.blit(textSurface, tuple(loc))



'''
@brief
Fills the screen with background colour. Overwrites
all drawn graphics
'''
def clearScreen():
    screen.fill(backgroundColour)



'''
@brief
Initialises the pygame interface and loads sprites.
'''
def consoleInit():
    global droneSprites, targetSprite, screen
    import pygame

    # initialise pygame and generate screen handle
    pygame.init()
    screen = pygame.display.set_mode( tuple(screen_size) )
    pygame.display.set_caption("AI Drone")


    # load target sprite
    targetSprite = pygame.image.load("graphics/target.png")
    targetSprite = pygame.transform.scale(targetSprite, (200,200))
    

    # load drones sprites
    droneSprites = {}

    for colour in droneSpriteColours:
        drone =  pygame.image.load(f"graphics/drone-{colour}.png")
        droneResized = pygame.transform.scale( drone, tuple(character_size) )
        droneSprites[colour] = droneResized
        
    pygame.font.init()



'''
@brief
Packs down and closes the pygame interface.
'''
def consoleClose():
    from pygame import quit

    quit()



'''
@brief
Calls to relevant functions to display graphics
that have been draw to the screen.
'''
def updateScreen():
    from pygame import display

    display.update()



##### Define package fields #####

# screen parameters
character_size = [48, 48]
screen_size = [1000, 500]


# user-defined world dimensions (uneven "screen:world size" ratio will warp graphics)
worldDimsXY = [[-15, 15], # [xmin, xmax]
               [ 0,  15]] # [ymin, ymax]


# 1x3 RBG colour index
backgroundColour = [210, 210, 210]
    

# drone sprite colours. Static property. Relies on predesigned sprite PNGs
droneSpriteColours = ["blue", "green", "grey", "pink", "purple", "red", "yellow"]


# ratio for mapping world coordinates to screen pixel coordinates
from Lib import absc
screen2WorldRatioXY = [screen_size[0] / ( sum( absc(worldDimsXY[0]) ) ),
                       screen_size[1] / ( sum( absc(worldDimsXY[1]) ) )]
    

# warn user if screen ratios are inconsistent
if screen2WorldRatioXY[0] != screen2WorldRatioXY[1]:
    from Lib import warning

    warning(f"Screen ratio is uneven. X: {screen2WorldRatioXY[0]}, Y: {screen2WorldRatioXY[1]}\n" +
             "This may lead to warped graphics.")
    

droneSprites = None
targetSprite = None
screen = None


# import pygame
# import matplotlib.pyplot as plt
# from math import degrees
# from numpy import multiply, divide, subtract, add

# from Lib import clip, roundc, absc
# from Physics import *


if __name__ == "__main__":
    from time import sleep
    from Simulation import *

    clearScreen()
    drawText("Your text")
    updateScreen()

    while True:
        flushUserInputs()