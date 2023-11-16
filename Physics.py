
'''
@brief
SUVAT maths function. Takes distance, velocity acceleration and time
to calculate new distance and velocity values.
'''
def suvat(params, dt):
    [s0, v0, a0] = params

    s = s0 + v0*dt + 0.5*a0*dt**2
    v = v0 + a0*dt

    return [s, v]



'''
@brief
Updates position and velocity states from SUVAT equations. Includes
bouncy collision physics and static friction logic.
'''
def updateState(state, dt):

    # calculate state update from current state
    [state.x,     state.vx]    = suvat(state.getx(), dt)
    [state.y,     state.vy]    = suvat(state.gety(), dt)
    [state.theta, state.omega] = suvat(state.getAng(), dt)


    # add drag on velocity parameters
    state.vx -= linearDragCoeff * state.vx * dt
    state.omega -= angDragCoeff * state.omega * dt


    # static friction stops the drone below a certain velocity if acceleration is 0
    if abs(state.vx) < minLinearVelocity and state.ax == 0: state.vx = 0
    if abs(state.omega) < minAngularVelocity and state.alpha == 0: state.omega = 0


    # enforce position and angle limits and add y offset
    [xmin, xmax] = worldDimsXY[0]
    [ymin, ymax] = worldDimsXY[1]


    # enforce additional padding for graphics
    xmin += screenPadding
    ymin += screenPadding
    xmax -= screenPadding
    ymax -= screenPadding

    state.x = clip( state.x, xmin, xmax )
    state.y = clip( state.y, ymin, ymax )
    state.theta = wrapToPi(state.theta)


    # bouncy collision logic
    if   state.x == xmin:  state.vx =  bouncePercent*abs(state.vx)
    elif state.x == xmax:  state.vx = -bouncePercent*abs(state.vx)

    if   state.y == ymin:  state.vy =  bouncePercent*abs(state.vy)
    elif state.y == ymax:  state.vy = -bouncePercent*abs(state.vy)



'''
@brief
Converts response percentages into useable thrust values.
'''
def response2Thrust(response, drone):

    # NOTE: up/right positive. down/left negative
    upPercent   = response[0] - response[1]
    turnPercent = response[3] - response[2]

    # the desired rotational acceleration
    targetAlpha = turnPercent * maxAlpha

    # reverse engineer alpha calculations to get thrust differential
    K = 3
    thrustDiff = K * targetAlpha * I / r
    turnThrust = [thrustDiff, -thrustDiff]

    upThrust = [maxThrust * upPercent]

    thrust = clip(list( add(turnThrust, upThrust) ), minThrust, maxThrust)

    return thrust



'''
@brief
Updates only the acceleration values (ax, ay, alpha) in the state
matrix based on input thrust values.
'''
def updateAccelerations(state, lThrust, rThrust):
    F =  (lThrust + rThrust)
    M = (-lThrust + rThrust)*r

    # angular
    state.ax    = -F * sin( state.theta ) / mass
    state.ay    =  F * cos( state.theta ) / mass - g
    state.alpha =  M / I



'''
@brief
Returns the quared distance from [0, 0] to point [x, y].
'''
def squaredDist(x, y):
    return sqrt(x**2 + y**2)



from math import radians, pi

# environment constants
g = 9.81
mass = 1.38 # kg
length = 0.215 # m
I = 50*(mass*length**2)/12 # mass moment of inertia ?
r = length/2
bouncePercent   = 0.2 # % of velocity that rebounds when colliding with a wall
linearDragCoeff = 0.6 # drag
angDragCoeff    = 0.4


### Drone Physics Parameters ###
# thrust and angle limiters
maxThrust = 20
minThrust = 0

maxTheta = pi/4 # max turn angle [rad]
maxOmega = pi/2 # max turning velocity [rad/s]
maxAlpha = pi   # max turning acceleration [rad/s^2]

# friction
minLinearVelocity  = 0.6 # below this speed threshold, the drone will stop
minAngularVelocity = radians(15) # below this threshold, the drone will stop rotating

# position padding to ensure drone graphics remain on screen
screenPadding = 0.8 # metre


from numpy import sqrt, sin, cos, add

from Lib import wrapToPi, clip
from Graphics import worldDimsXY


if __name__ == "__main__":
    print(squaredDist([1, 1]))