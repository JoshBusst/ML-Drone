


'''
NOTE:
Since this library imports keras tensorflow by default,
and since all keras tensorflow imports must be static,
this library must only be imported STATICALLY.
'''



def createNet(structure, activationFunc):
    model = tf.Sequential()
    model.add( tf.layers.Input(shape=(structure[0])) )

    for layer in structure[1:]:
        model.add(tf.layers.Dense(layer, activation=activationFunc))

    return model



def mutateNet(net, r):
    # from numpy.random import uniform


    # # generate random noise as a percentage 
    # layers = seedNet.get_weights()
    # newNet = []
    
    # for layer in layers:
    #     layerSize = (1, len(layer), 1)
    #     noise = uniform(0, mutationRate, layerSize)

    #     newLayer = layer * (1 + noise)
    #     newNet.append(newLayer)


    # # generate a clone of the original net and set the new weights
    # mutatedNet = tf.models.clone_model(newNet)
    # mutatedNet.set_weights(newNet)
    
    # return mutatedNet

    w = net.get_weights()
    w_new = w
    for i in np.arange(0,len(w)-1,2):
        for j in range(len(w[i][:,0])):
            for k in range(len(w[i][0,:])):
                #w_new[i][j,k] = np.random.choice([w[i][j,k],w[i][j,k]+random.uniform(-.5,.5)],1,p=[1-r,r])
                #w_new[i][j,k] = np.random.choice([w[i][j,k], np.random.randn(), w[i][j,k]+random.uniform(-.5,.5)], 1, p=[1-r,r*1/10,r*9/10])
                w_new[i][j,k] = np.random.choice([w[i][j,k], w[i][j,k]+np.random.uniform(-.5,.5)], 1, p=[1-r,r])

    mutant = tf.models.clone_model(net)
    mutant.set_weights(w_new)
    return mutant



def mutateBias(net,r):
    w = net.get_weights()
    w_new = w

    for i in np.arange(1,len(w),2):
        for j in range(len(w[i])):
            w_new[i][j] = np.random.choice([w[i][j], w[i][j]+np.random.uniform(-.5,.5)],1,p=[1-r,r])

    mutant = tf.models.clone_model(net)
    mutant.set_weights(w_new)
    
    return mutant



def clearNet(net):
    from Lib import zeros

    layers = net.get_weights()
    newNet = []

    for layer in layers:
        newNet.append(zeros(len(layer)))

    model = tf.models.clone_model(net)
    model.set_weights(newNet)

    return model





# this library is huge and slow to import. Ensure imports are always static
import tensorflow.keras as tf
import numpy as np