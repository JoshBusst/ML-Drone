
'''
@brief
Container for all simulation parameters, logs, etc.
'''
class Simulation:
    def __init__(self, timeout=20, dt=0.05):
        from Lib import zeros


        # time and FPS tracking
        self.dt_target  = dt # desired time step, seconds
        self.dt = dt # measured timestep, seconds
        self.timeout  = timeout # simulation timeout, seconds
        self.lastTime = None
        self.FPS = 0
        self.cpu_util = 0
        self.timeElapsed = 0
        self.quit = False

        self.generation = 0

        # sliding window filter for time tracking parameters
        filterWindowSize = 10
        self.timeFilter = {'fps': zeros(filterWindowSize),
                           'cpu': zeros(filterWindowSize)}

        # data logging
        self.stateLog  = [[]]
        self.thrustLog = [[]]
        self.distLog   = [[]]

    '''
    @brief
    Resets logs and ensures they can account for updated number
    of drones.
    '''
    def resetSim(self, dt, numDrones):
        assert(numDrones >= 0)
        assert(dt > 0)

        # initialise desired time step
        self.dt_target = dt

        # initialise logs to account for variable number of drones
        self.stateLog  = [[] for _ in range(numDrones)]
        self.distLog   = [[] for _ in range(numDrones)]
        self.thrustLog = [[] for _ in range(numDrones)]

        self.flushTimeTracker()

    def logData(self, state, thrust, dist, droneInd):
        self.stateLog[droneInd].append(state)
        self.thrustLog[droneInd].append(thrust)
        self.distLog[droneInd].append(dist)

    def delay(self):
        from numpy import mean
        from Lib import psleep
        from time import time


        # track time elapsed
        runtime = self.getdt()
        self.timeElapsed += runtime

        if self.timeElapsed >= self.timeout - self.dt_target:
            self.quit = True


        # calculate delay time for dt < dt_target
        delayTime = max(self.dt_target - self.dt, 0)
        self.timeElapsed += delayTime

        # calculate fps and cpu util and put through a sliding window average filter
        fps = 1/(max(self.dt + delayTime, 0.001))
        cpu_util = min(self.dt, self.dt_target)/self.dt_target*100

        self.timeFilterUpdate(fps, cpu_util)

        # calculate filtered cpu and fps
        self.FPS = mean(self.timeFilter['fps'])
        self.cpu_util = mean(self.timeFilter['cpu'])


        # delay for the required time
        psleep(delayTime)

        # measuring next time step starts here
        self.lastTime = time()
        
    def getdt(self):
        from time import time

        t = time()

        if self.lastTime == None:
            self.lastTime = t - self.dt_target

        self.dt = t - self.lastTime
        self.lastTime = t

        return self.dt
    
    '''
    @brief
    Sets the internal target timestep. The system attempts to reach
    this timestep but does not guaruntee it.
    '''
    def setTargetdt(self, dt):
        self.dt_target = dt

    '''
    @brief
    To be run directly before starting a simulation. 
    Flushes the tracker to ensure up to date timestep
    values even at the very start of the simulation.
    '''
    def flushTimeTracker(self):
        self.getdt()
        self.getdt()

    def timeFilterUpdate(self, fps, cpu):
        self.timeFilter['fps'] = self.timeFilter['fps'][1:] + [fps]
        self.timeFilter['cpu'] = self.timeFilter['cpu'][1:] + [cpu]



'''
@brief
Calculates thrusts based on the drones neural net.
'''
def getNetThrust(drone, addNoise=False):
    from numpy import multiply, add, subtract, random, array
    from Physics import squaredDist, maxThrust, minThrust
    from Lib import clip

    # calculate drone/target position error
    positionError = subtract(drone.currentTarget(), [drone.state.x, drone.state.y])
    distanceError = squaredDist(*positionError)

    net_inputs = [positionError[0],
                  positionError[1],
                  drone.state.vx,
                  drone.state.vy,
                  drone.state.theta,
                  drone.state.omega]
    
    # ensure inputs are always float type
    net_inputs = array([net_inputs])
    
    
    if addNoise:
        # generate and add noise
        noise = multiply( random.rand(1,6), net_inputs ) * 0.0001
        net_inputs = add(*net_inputs, noise)


    # calculate thrusts
    thrust = maxThrust * drone.net(net_inputs)
    thrust = clip(list(*thrust), minThrust, maxThrust)

    return thrust, distanceError



'''
@brief
Calculates thrust from user inputs.
'''
def getUserThrust(drone):
    from UI import handleUserInputs
    from Physics import response2Thrust

    response = handleUserInputs()
    thrust = response2Thrust(response, drone)

    return thrust



'''
@brief
Separates all GUI calls for readability. Handles graphics calls and 
user interface updates as needed.
'''
def updateGUI(sim, drones):
    from UI import flushUserInputs
    from Graphics import clearScreen, drawTarget, drawDrone, drawText, updateScreen

    # draw graphics to screen
    clearScreen()

    for drone in drones:
        drawDrone(drone)

        if drone.targets != [None]:
            drawTarget(drone.currentTarget())

    drawText(f"Time: {round(sim.timeElapsed, 2)}s")
    drawText(f"Frames: {round(sim.FPS, 2)}fps", loc=(0,20))
    drawText(f"CPU: {round(sim.cpu_util, 2)}%", loc=(0,40))
    drawText(f"Generation: {sim.generation}", loc=(0,60))


    # display updated graphics
    updateScreen()


    # allow screen to be repositioned or closed
    flushUserInputs()



'''
@brief
This function takes initial conditions and runs a single simulation
of the drones in flight.
'''
def simulate(sim: Simulation, drones: list, addNoise=False, Kd=1, Kw=1):

    # assertions and dependency imports
    assert(isinstance(drones, list))

    from numpy import mean, subtract

    from UI import flushUserInputs
    from Lib import zeros
    from Physics import updateAccelerations, updateState, squaredDist
    

    # sim setup
    numDrones = len(drones)
    scores = zeros(numDrones)

    sim.resetSim(sim.dt, numDrones)
    maxLoops = round(sim.timeout/sim.dt_target)
    

    # simulation main loop
    for _ in range(maxLoops):
        for droneInd, drone in enumerate(drones):
            if drone.userControlled:
                thrust = getUserThrust(drone)

                positionError = subtract(drone.currentTarget(), [drone.state.x, drone.state.y])
                distanceError = squaredDist(*positionError)
            else:
                thrust, distanceError = getNetThrust(drone, addNoise)
                flushUserInputs()


            # update physics
            updateAccelerations(drone.state, *thrust)
            updateState(drone.state, max(sim.dt, sim.dt_target))

            # log data
            sim.logData(drone.state, thrust, distanceError, droneInd)


        updateGUI(sim, drones)


        # handle simulation time tracking
        if sim.quit: break
        sim.delay()
    

    # score drone flight based on stability (small omega) and distance to target
    for i, drone in enumerate(drones):
        thetaLog = [abs(state.theta) for state in sim.stateLog[i]]
        omegaLog = [abs(state.omega) for state in sim.stateLog[i]]

        scores[i] = Kd*mean(sim.distLog[i])**2 +\
                    Kw*mean(omegaLog)**2 +\
                    mean(thetaLog)**2
    
    return scores






if __name__ == "__main__":
    from time import time

    from UI import *
    from Drone import *
    from Physics import *
    from Graphics import *
    from NeuralNet import *

    consoleInit()

    for i in range(1):
        sim = Simulation(timeout=10, dt=0.02)
        drones = []

        # initialise multiple drone objects
        for colour in droneSpriteColours[:1]:
            drone = Drone(colour, userControlled=False)
            drone.setTarget([[0, 8]])
            drones.append(drone)

        scores = simulate(sim, drones)


