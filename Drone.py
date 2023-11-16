


'''
NOTE:
This function statically imports keras tensorflow through
the NeuralNet static import. Therefore this function must
also be exclusively a static import.
'''



'''
@brief
Maps the pose and pose derivatives of the drone in 2D.
'''
class State:
    def __init__(self,
                 pos = [0, 0, 0],
                 vel = [0, 0, 0],
                 acc = [0, 0, 0]):
        
        # always assumes units of metres and radians
        [self.x,  self.y,  self.theta] = pos
        [self.vx, self.vy, self.omega] = vel
        [self.ax, self.ay, self.alpha] = acc

    def getPos(self):
        return [self.x, self.y, self.theta]
    
    def getVel(self):
        return [self.vx, self.vy, self.omega]
    
    def getAcc(self):
        return [self.ax, self.ay, self.alpha]
    
    def getx(self):
        return [self.x, self.vx, self.ax]
    
    def gety(self):
        return [self.y, self.vy, self.ay]
    
    def getAng(self):
        return [self.theta, self.omega, self.alpha]
    
    def printState(self):
        from Lib import roundList

        print('\n\n\n')
        print(roundList(self.getPos(), 1))
        print(roundList(self.getVel(), 1))
        print(roundList(self.getAcc(), 1))



'''
@brief
Contains drone related parameters and shorthand methods.
'''
class Drone:
    def __init__(self, colour='green', net=None, userControlled=False):
        from Graphics import droneSpriteColours

        assert(colour in droneSpriteColours)
        assert(isinstance(userControlled, bool))

        self.score = 0
        self.state: State = State()
        self.targets = [None]
        self.targetInd = 0
        self.spriteColour = colour
        self.userControlled = userControlled
        self.net = net

        if not userControlled:
            self.net = createNet([6,8,8,2], 'tanh')
            self.targets = [[0, 8]]

    '''
    @brief
    Check drone is within a stable positional and
    angular boundary.
    '''
    def stable(self):
        from numpy import radians
        from Lib import isbounded
        from Graphics import worldDimsXY


        thetaLim = radians(80)

        # test drone position boundary and max allowable tilt
        rangeBounded = isbounded(self.state.x, *worldDimsXY[0]) and\
                       isbounded(self.state.y, *worldDimsXY[1])
        angleBounded = isbounded(self.state.theta, -thetaLim, thetaLim)
        stable = rangeBounded and angleBounded

        return stable

    def currentTarget(self):
        return self.targets[self.targetInd]
    
    def nextTarget(self):
        self.targetInd += 1

        if self.targetInd >= len(self.targets):
            self.targetInd = 0

        return self.currentTarget()
    
    def lastTarget(self):
        self.targetInd -= 1

        if self.targetInd < 0:
            self.targetInd = len(self.targets) - 1

        return self.currentTarget()

    '''
    @brief
    Allows a user to clear and set the entire targets list
    at once
    '''
    def setTarget(self, targets):
        assert(len(targets) > 0)
        assert(isinstance(targets[0], list))
        
        self.targets = targets

    '''
    @brief
    Adds a target point at the given index. Defaults
    to last index of the targets list.
    '''
    def addTarget(self, target, i=-1):
        assert(isinstance(target, list))
        assert(len(target) == 2)

        if self.targets == [None]:
            self.targets = [target]
            self.targetInd = 0
        elif i == -1:
            self.targets.append(target)
        else:
            self.targets.insert(target, i)

    '''
    @brief
    Removes the first instance of the given target
    from the targets list.
    '''
    def removeTarget(self, target):
        self.targets.remove(target)



'''
@brief
A basic proportional controller for piloting the drone to a target.
'''
def getControllerThrust(drone: Drone):
    from numpy import subtract
    from math import atan

    from Lib import wrapToPi, angdiff, debug
    from Physics import squaredDist

    targetPos = drone.currentTarget()

    eq = subtract(targetPos, drone.state.getPos()[0:2])
    et = wrapToPi(angdiff(drone.state.theta, atan(eq[1]/eq[0])))
    ed = squaredDist(eq[0], eq[1])

    debug(et)
    debug(atan(eq[1]/eq[0]))


'''
@brief
Initialises an arbitrary number of drones with configurable
mutation rate and seed net.
'''
def initDrones(numDrones=1, netSeed=None, mRate=0.1):
    from Graphics import droneSpriteColours

    assert(numDrones > 0 and numDrones <= len(droneSpriteColours))


    if netSeed == None:
        netSeed = createNet([6,8,8,2], 'tanh')

    # load desired number of drones
    drones = []

    for colour in droneSpriteColours[:numDrones]:
            drone = Drone(colour=colour)

            drone.net = mutateNet(netSeed, mRate)
            drones.append(drone)

    return drones



from NeuralNet import createNet, mutateNet


if __name__ == "__main__":
    drone = Drone()
    drone.setTarget([[-1,0]])
    drone.state.x = 1
    drone.state.y = 0
    drone.state.theta = -3.1415/2

    getControllerThrust(drone)

