COMMENT

STDP + RL weight adjuster mechanism

Original STDP code adapted from:
http://senselab.med.yale.edu/modeldb/showmodel.asp?model=64261&file=\bfstdp\stdwa_songabbott.mod

Adapted to implement a "nearest-neighbor spike-interaction" model (see 
Scholarpedia article on STDP) that just looks at the last-seen pre- and 
post-synaptic spikes, and implementing a reinforcement learning algorithm based
on (Chadderdon et al., 2012):
http://www.plosone.org/article/info%3Adoi%2F10.1371%2Fjournal.pone.0047251

Example Python usage:

from neuron import h

## Create cells
dummy = h.Section() # Create a dummy section to put the point processes in
ncells = 2
cells = []
for c in range(ncells): cells.append(h.IntFire4(0,sec=dummy)) # Create the cells

## Create synapses
threshold = 10 # Set voltage threshold
delay = 1 # Set connection delay
singlesyn = h.NetCon(cells[0],cells[1], threshold, delay, 0.5) # Create a connection between the cells
stdpmech = h.STDP(0,sec=dummy) # Create the STDP mechanism
presyn = h.NetCon(cells[0],stdpmech, threshold, delay, 1) # Feed presynaptic spikes to the STDP mechanism -- must have weight >0
pstsyn = h.NetCon(cells[1],stdpmech, threshold, delay, -1) # Feed postsynaptic spikes to the STDP mechanism -- must have weight <0
h.setpointer(singlesyn._ref_weight[0],'synweight',stdpmech) # Point the STDP mechanism to the connection weight

Version: 2013oct24 by cliffk

ENDCOMMENT

NEURON {
    POINT_PROCESS STDP : Definition of mechanism
    POINTER synweight : Pointer to the weight (in a NetCon object) to be adjusted.
    RANGE tauhebb, tauanti : LTP/LTD decay time constants (in ms) for the Hebbian (pre-before-post-synaptic spikes), and anti-Hebbian (post-before-pre-synaptic) cases. 
    RANGE hebbwt, antiwt : Maximal adjustment (can be positive or negative) for Hebbian and anti-Hebbian cases (i.e., as inter-spike interval approaches zero).  This should be set positive for LTP and negative for LTD.
    RANGE RLwindhebb, RLwindanti : Maximum interval between pre- and post-synaptic events for an starting an eligibility trace.  There are separate ones for the Hebbian and anti-Hebbian events.
    RANGE useRLexp : Use exponentially decaying eligibility traces?  If 0, then the eligibility traces are binary, turning on at the beginning and completely off after time has passed corresponding to RLlen.
    RANGE RLlenhebb, RLlenanti : Length of the eligibility Hebbian and anti-Hebbian eligibility traces, or the decay time constants if the traces are decaying exponentials.
    RANGE RLhebbwt, RLantiwt : Maximum gains to be applied to the reward or punishing signal by Hebbian and anti-Hebbian eligibility traces.  
    RANGE wmax : The maximum weight for the synapse.
    RANGE softthresh : Flag turning on "soft thresholding" for the maximal adjustment parameters.
    RANGE STDPon : Flag for turning STDP adjustment on / off.
    RANGE RLon : Flag for turning RL adjustment on / off.
    RANGE verbose : Flag for turning off prints of weight update events for debugging.
    RANGE tlastpre, tlastpost : Remembered times for last pre- and post-synaptic spikes.
    RANGE tlasthebbelig, tlastantielig : Remembered times for Hebbian anti-Hebbian eligibility traces.
    RANGE interval : Interval between current time t and previous spike.
    RANGE deltaw : The calculated weight change.
    RANGE newweight : New calculated weight.
}

ASSIGNED {
    synweight        
    tlastpre   (ms)    
    tlastpost  (ms)   
    tlasthebbelig   (ms)    
    tlastantielig  (ms)        
    interval    (ms)    
    deltaw
    newweight          
}

INITIAL {
    tlastpre = -1            : no spike yet
    tlastpost = -1           : no spike yet
    tlasthebbelig = -1      : no eligibility yet
    tlastantielig = -1  : no eligibility yet   
    interval = 0
    deltaw = 0
    newweight = 0
}

PARAMETER {
    tauhebb  = 10  (ms)   
    tauanti  = 10  (ms)    
    hebbwt = 1.0
    antiwt = -1.0
    RLwindhebb = 10 (ms)
    RLwindanti = 10 (ms)
    useRLexp = 0   : default to using binary eligibility traces
    RLlenhebb = 100 (ms)
    RLlenanti = 100 (ms)
    RLhebbwt = 1.0
    RLantiwt = -1.0
    wmax  = 15.0
    softthresh = 0
    STDPon = 1
    RLon = 1
    verbose = 0
}

NET_RECEIVE (w) {
     deltaw = 0.0 : Default the weight change to 0.
     
    : If we receive a non-negative weight value, we are receiving a pre-synaptic spike (and thus need to check for an anti-Hebbian event, since the post-synaptic weight must be earlier).
    if (w >= 0) {           
        interval = tlastpost - t  : Get the interval; interval is negative
        if  ((tlastpost > -1) && (interval != 0)) { : If we had a post-synaptic spike and a non-zero interval...
            if (STDPon == 1) { : If STDP learning is turned on...
                deltaw = antiwt * exp(interval / tauanti) : Use the anti-Hebbian decay to set the anti-Hebbian weight adjustment.
                if (softthresh == 1) { deltaw = softthreshold(deltaw) } : If we have soft-thresholding on, apply it.
                if (verbose > 0) { printf("anti-Hebbian STDP event: t = %f ms; deltaw = %f\n",t,deltaw) } : Show weight update information if debugging on. 
            }
            if ((RLon == 1) && (-interval <= RLwindanti)) { tlastantielig = t } : If RL and anti-Hebbian eligibility traces are turned on, and the interval falls within the maximum window for eligibility, remember the eligibilty trace start at the current time.
        }
        tlastpre = t : Remember the current spike time for next NET_RECEIVE.  
    
    : Else, if we receive a negative weight value, we are receiving a post-synaptic spike (and thus need to check for an anti-Hebbian event, since the post-synaptic weight must be earlier).    
    } else {            
        interval = t - tlastpre : Get the interval; interval is positive
        if  ((tlastpre > -1) && (interval != 0)) { : If we had a pre-synaptic spike and a non-zero interval...
            if (STDPon == 1) { : If STDP learning is turned on...
                deltaw = hebbwt * exp(-interval / tauhebb) : Use the Hebbian decay to set the Hebbian weight adjustment. 
                if (softthresh == 1) { deltaw = softthreshold(deltaw) } : If we have soft-thresholding on, apply it.
                if (verbose > 0) { printf("Hebbian STDP event: t = %f ms; deltaw = %f\n",t,deltaw) } : Show weight update information if debugging on.
            }
            if ((RLon == 1) && (interval <= RLwindhebb)) { tlasthebbelig = t } : If RL and Hebbian eligibility traces are turned on, and the interval falls within the maximum window for eligibility, remember the eligibilty trace start at the current time.
        }
        tlastpost = t : Remember the current spike time for next NET_RECEIVE.
    }
    adjustweight(deltaw) : Adjust the weight.
}

PROCEDURE reward_punish(reinf) {
    if (RLon == 1) { : If RL is turned on...
        deltaw = 0.0 : Start the weight change as being 0.
        deltaw = deltaw + reinf * hebbRL() : If we have the Hebbian eligibility traces on, add their effect in.   
        deltaw = deltaw + reinf * antiRL() : If we have the anti-Hebbian eligibility traces on, add their effect in.
        if (softthresh == 1) { deltaw = softthreshold(deltaw) }  : If we have soft-thresholding on, apply it.  
        adjustweight(deltaw) : Adjust the weight.
        if (verbose > 0) { printf("RL event: t = %f ms; deltaw = %f\n",t,deltaw) } : Show weight update information if debugging on.     
    }
}

FUNCTION hebbRL() {
    if ((RLon == 0) || (tlasthebbelig < 0.0)) { hebbRL = 0.0  } : If RL is turned off or eligibility has not occurred yet, return 0.0.
    else if (useRLexp == 0) { : If we are using a binary (i.e. square-wave) eligibility traces...
        if (t - tlasthebbelig <= RLlenhebb) { hebbRL = RLhebbwt } : If we are within the length of the eligibility trace...
        else { hebbRL = 0.0 } : Otherwise (outside the length), return 0.0.
    } 
    else { hebbRL = RLhebbwt * exp((tlasthebbelig - t) / RLlenhebb) } : Otherwise (if we're using an exponential decay traces)...use the Hebbian decay to calculate the gain.
      
}

FUNCTION antiRL() {
    if ((RLon == 0) || (tlastantielig < 0.0)) { antiRL = 0.0 } : If RL is turned off or eligibility has not occurred yet, return 0.0.
    else if (useRLexp == 0) { : If we are using a binary (i.e. square-wave) eligibility traces...
        if (t - tlastantielig <= RLlenanti) { antiRL = RLantiwt } : If we are within the length of the eligibility trace...
        else {antiRL = 0.0 } : Otherwise (outside the length), return 0.0.
    }
    else { antiRL = RLantiwt * exp((tlastantielig - t) / RLlenanti) } : Otherwise (if we're using an exponential decay traces), use the anti-Hebbian decay to calculate the gain.  
}

FUNCTION softthreshold(rawwc) {
    if (rawwc >= 0) { softthreshold = rawwc * (1.0 - synweight / wmax) } : If the weight change is non-negative, scale by 1 - weight / wmax.
    else { softthreshold = rawwc * synweight / wmax } : Otherwise (the weight change is negative), scale by weight / wmax.    
}

PROCEDURE adjustweight(wc) {
   synweight = synweight + wc : apply the synaptic modification, and then clip the weight if necessary to make sure it's between 0 and wmax.
   if (synweight > wmax) { synweight = wmax }
   if (synweight < 0) { synweight = 0 }
}
