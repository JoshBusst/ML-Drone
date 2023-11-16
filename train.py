

from time import sleep
from numpy import mean
from tensorflow.keras.models import load_model
from Simulation import *
from NeuralNet import *
from Drone import *
from Graphics import consoleInit, droneSpriteColours
from Lib import debug

consoleInit()


# TODO: update UI to run cleaner key tracking algorithm


'''
@brief
Batch tests drones from a seed model on a number of increasingly difficult
targets. Use to test drone performance in general.
'''
def gauntlet(model):
    targets =  [[0,9],[0,11],   # target high
                [0,7],[0,4],    # target low
                [1,8],[2,8],    # target right
                [-1,8],[-2,8],  # target left
                [1,9],[2,11],   # target right high
                [-1,9],[-2,11], # target left high
                [2,6],[3,5],    # target right low
                [-2,6],[-3,5]   # target left low
                ]
    startPos = [0,8]

    mRate = 0.15 # mutation rate
    numGenerations = 2
    timeout = 10
    bestNet = model

    for target in targets:
        bestScore = 10**6 # as score -> 0, performance improves

        for i in range(numGenerations):

            # initialise new simulation parameters
            sim = Simulation(timeout)
            numDrones = len(droneSpriteColours)
            drones = initDrones(numDrones, netSeed=bestNet, mRate=mRate)

            for drone in drones:
                drone.setTarget([target])
                [drone.state.x, drone.state.y] = startPos
                
            sim.generation = i + 1
            

            # score updates and net reparenting
            scores = simulate(sim, drones, addNoise=True)

            for i, score in enumerate(scores):
                if score < bestScore:
                    bestNet = drones[i].net
                    bestScore = score

                    bestNet.save('model')
                    print(f"Best score: {round(bestScore, 4)}")



'''
@brief
'''
def train():
    pass



if __name__ == "__main__":
    model = load_model('models/stability')
    gauntlet(model)