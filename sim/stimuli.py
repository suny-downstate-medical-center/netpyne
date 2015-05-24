"""
STIMULI

This code defines properties of different type of stimuli
and defines functions to generate the stimuli

"""

from pylab import array, rand, exp, zeros, hstack

import params as p
import shared as s # Import population and connection data

#PMd, ASC, DSC, ER2, IF2, IL2, ER5, EB5, IF5, IL5, ER6, IF6, IL6, AMPA, NMDA, GABAA, GABAB, opsin, Epops, Ipops, allpops = cpd.names2inds() # Define populations

# Class with natural touch stimulus
class touch:
    name = 'touch'
    receptor = 0 #s.l.AMPA  # Set which receptor to stimulate
    isi = 0.5 # Interstimulus interval in s
    var = 0.0 # Variation in ISI in s
    width = 0.005 # Stimulus width in s
    weight = 100 # Weight of stimuli
    sta = [] # Starting time in s -- usually defined below
    fin = [] # Finishing time in s
    shape = 'gaussian' # Shape of stimulus
    #pops = [TCR]
    fraction = 1 # No idea what this should be...
    rate = 200 # 500 is the highest rate that can be used without significantly slowing down the simulation
    noise = 0 # Variability in onset time
    loc = array([[0.4,0.6],[0.4,0.6]]) # Location of cells to be stimulated
    falloff = [array([0.5,0.5]), 1e9] # Weight fall-off characteristics of the stimulus: center and Gaussian width in um

# class with optogenetic stimulus
class opto:
    name = 'opto'
    receptor = 4 #s.l.opsin # Set which receptor to stimulate
    isi = 0.100 # Interstimulus interval in s
    var = 0.0 # Variation in ISI
    width = 0.2 # Stimulus width in s
    weight = 10 # Weight of stimuli
    sta = 3 # Starting time in s
    fin = 6 # Finishing time in s
    shape = 'square' # Shape of stimulus
    pops = [] #[s.ER5, s.EB5, s.ER6]
    fraction = 0.4 # No idea what this should be...
    rate = 500 # 500 is the highest rate that can be used without significantly slowing down the simulation
    noise = 0
    loc = array([[0.0,1.0],[0.0,1.0]]) # Location of cells to be stimulated
    falloff = [array([0.5,0.5]), 2000] # Weight fall-off characteristics of the stimulus: center and Gaussian width in um


# Allow defaults to be overriden by name, e.g. instead of touch(), stimmod(touch,sta=1,fin=3)
def stimmod(stimclass, name=None, receptor=None, isi=None, var=None, width=None, weight=None, sta=None, fin=None, shape=None, pops=None, fraction=None, rate=None, noise=None, loc=None, falloff=None):
    stiminstance = stimclass()    
    stimproperties = ['name', 'receptor', 'isi', 'var', 'width', 'weight', 'sta', 'fin', 'shape', 'pops', 'fraction', 'rate', 'noise', 'loc', 'falloff'];
    for prop in stimproperties:
        thisproperty = eval(prop)
        if thisproperty!=None:
            exec('stiminstance.' + prop + ' = thisproperty')
    return stiminstance


## Define stimulus-making code
def makestim(isi=1, variation=0, width=0.05, weight=10, start=0, finish=1, stimshape='gaussian'):
    from pylab import r_, convolve, shape
    
    # Create event times
    timeres = 0.005 # Time resolution = 5 ms = 200 Hz
    pulselength = 10 # Length of pulse in units of width
    currenttime = 0
    timewindow = finish-start
    allpts = int(timewindow/timeres)
    output = []
    while currenttime<timewindow:
        if currenttime>=0 and currenttime<timewindow: output.append(currenttime)
        currenttime = currenttime+isi+variation*(rand()-0.5)
    
    # Create single pulse
    npts = min(pulselength*width/timeres,allpts) # Calculate the number of points to use
    x = (r_[0:npts]-npts/2+1)*timeres
    if stimshape=='gaussian': 
        pulse = exp(-(x/width*2-2)**2) # Offset by 2 standard deviations from start
        pulse = pulse/max(pulse)
    elif stimshape=='square': 
        pulse = zeros(shape(x))
        pulse[int(npts/2):int(npts/2)+int(width/timeres)] = 1 # Start exactly on time
    else:
        raise Exception('Stimulus shape "%s" not recognized' % stimshape)
    
   # Create full stimulus
    events = zeros((allpts))
    events[array(array(output)/timeres,dtype=int)] = 1
    fulloutput = convolve(events,pulse,mode='same')*weight # Calculate the convolved input signal, scaled by rate
    fulltime = (r_[0:allpts]*timeres+start)*1e3 # Create time vector and convert to ms
    fulltime = hstack((0,fulltime,fulltime[-1]+timeres*1e3)) # Create "bookends" so always starts and finishes at zero
    fulloutput = hstack((0,fulloutput,0)) # Set weight to zero at either end of the stimulus period
    events = hstack((0,events,0)) # Ditto
    stimvecs = [fulltime, fulloutput, events] # Combine vectors into a matrix
    
    return stimvecs

stimpars = [stimmod(touch,name='LTP',sta=p.ltptimes[0],fin=p.ltptimes[1]), stimmod(touch,name='ZIP',sta=p.ziptimes[0],fin=p.ziptimes[1])] # Turn classes into instances
