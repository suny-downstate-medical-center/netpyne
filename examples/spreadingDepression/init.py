from netpyne import sim
from netParams import netParams
from cfg import cfg
import numpy as np
import os 
import sys
import pickle
from neuron import h 
import random 
from matplotlib import pyplot as plt 

# Instantiate network 
sim.initialize(netParams, cfg)        # create network object and set cfg and net params
sim.net.createPops()                  # instantiate network populations
sim.net.createCells()                 # instantiate network cells based on defined populations
sim.net.connectCells()                # create connections between cells based on params
sim.net.addStims()                    # add external stimulation to cells (IClamps etc)
sim.net.addRxD(nthreads=6)            # add reaction-diffusion (RxD)

# Additional sim setup 
## parallel context 
pc = h.ParallelContext()
pcid = pc.id()
nhost = pc.nhost()
pc.timeout(0)
pc.set_maxstep(100) # required when using multiple processes

random.seed(pcid+120194)
all_secs = [sec for sec in h.allsec()]
cells_per_node = len(all_secs)
rec_inds = random.sample(range(cells_per_node), int(cfg.nRec / nhost))
rec_cells = [h.Vector().record(all_secs[ind](0.5)._ref_v) for ind in rec_inds]
pos = [[all_secs[ind].x3d(0), all_secs[ind].y3d(0), all_secs[ind].z3d(0)] for ind in rec_inds]
pops = [str(all_secs[ind]).split('.')[1].split('s')[0] for ind in rec_inds]

## only single core stuff
if pcid == 0:
    ### create output dir 
    if not os.path.exists(cfg.filename):
        try:
            os.makedirs(cfg.filename)
        except:
            print("Unable to create the directory %r for the data and figures"
                % cfg.filename)
            os._exit(1)

    ### set variables for ecs concentrations 
    k_ecs = sim.net.rxd['species']['k']['hObj'][sim.net.rxd['regions']['ecs']['hObj']]
    na_ecs = sim.net.rxd['species']['na']['hObj'][sim.net.rxd['regions']['ecs']['hObj']]
    cl_ecs = sim.net.rxd['species']['k']['hObj'][sim.net.rxd['regions']['ecs']['hObj']]
    o2_ecs = sim.net.rxd['species']['o2_extracellular']['hObj'][sim.net.rxd['regions']['ecs_o2']['hObj']]

    ### manually record from cells according to distance from the center of the slice
    cell_positions = [((sec.x3d(0)-cfg.sizeX/2.0)**2 + (sec.y3d(0)+cfg.sizeY/2.0)**2 + (sec.z3d(0)-cfg.sizeZ/2.0)**2)**(0.5) for sec in h.allsec()]
    t = h.Vector().record(h._ref_t)
    soma_v = []
    soma_ki = []
    soma_nai = []
    soma_cli = []
    soma_nao = []
    soma_ko = []
    soma_clo = []
    soma_o2 = []
    rpos = []
    cell_type = []
    for i in range(int(cfg.sizeX//10)):
        for r, soma in zip(cell_positions, h.allsec()):
            if (10.0*i-2.5) < r < (10.0*i+2.5):
                print(i,r)
                rpos.append((soma.x3d(0)-cfg.sizeX/2, soma.y3d(0)+cfg.sizeY/2, soma.z3d(0)-cfg.sizeZ/2))
                cell_type.append(soma.name().split('.')[1].split('s')[0])
                soma_v.append(h.Vector().record(soma(0.5)._ref_v))
                soma_nai.append(h.Vector().record(soma(0.5)._ref_nai))
                soma_ki.append(h.Vector().record(soma(0.5)._ref_ki))
                soma_cli.append(h.Vector().record(soma(0.5)._ref_cli))
                soma_nao.append(h.Vector().record(soma(0.5)._ref_nao))
                soma_ko.append(h.Vector().record(soma(0.5)._ref_ko))
                soma_clo.append(h.Vector().record(soma(0.5)._ref_clo))
                soma_o2.append(h.Vector().record(o2_ecs.node_by_location(soma.x3d(0),soma.y3d(0),soma.z3d(0))._ref_concentration))
                break

    recs = {'v':soma_v, 'ki':soma_ki, 'nai':soma_nai, 'cli':soma_cli,
            't':t,      'ko':soma_ko, 'nao':soma_nao, 'clo':soma_clo,
            'pos':rpos, 'o2':soma_o2, 'rad':cell_positions, 
            'cell_type' : cell_type}

# Function definitions
def saveconc():
    np.save(os.path.join(cfg.filename,"k_%i.npy" % int(h.t)), k_ecs.states3d)
    np.save(os.path.join(cfg.filename,"na_%i.npy" % int(h.t)), na_ecs.states3d)
    np.save(os.path.join(cfg.filename,"cl_%i.npy" % int(h.t)), cl_ecs.states3d)
    np.save(os.path.join(cfg.filename,'o2_%i.npy' % int(h.t)), o2_ecs.states3d)

def progress_bar(tstop, size=40):
    """ report progress of the simulation """
    prog = h.t/float(tstop)
    fill = int(size*prog)
    empt = size - fill
    progress = '#' * fill + '-' * empt
    sys.stdout.write('[%s] %2.1f%% %6.1fms of %6.1fms\r' % (progress, 100*prog, h.t, tstop))
    sys.stdout.flush()

def run(tstop):
    """ Run the simulations saving figures every 100ms and recording the wave progression every time step"""
    if pcid == 0:
        # record the wave progress (shown in figure 2)
        name = ''
        fout = open(os.path.join(cfg.filename,'wave_progress%s.txt' % name),'a')
    last_print = 0
    time = []
    saveint = 100

    while h.t < tstop:
        time.append(h.t)
        if int(h.t) % saveint == 0:
            # plot extracellular concentrations averaged over depth every 100ms 
            if pcid == 0:
                saveconc()

        if pcid == 0: progress_bar(tstop)
        pc.psolve(pc.t(0)+h.dt)  # run the simulation for 1 time step

        # h.fadvance()
        # determine the furthest distance from the origin where
        # extracellular potassium exceeds cfg.Kceil (dist)
        # And the shortest distance from the origin where the extracellular
        # extracellular potassium is below cfg.Kceil (dist1)
        if pcid == 0 and h.t - last_print > 1.0:
            last_print = h.t
            dist = 0
            dist1 = 1e9
            for nd in sim.net.rxd.species['k']['hObj'].nodes:
                if str(nd.region).split('(')[0] == 'Extracellular':
                    r = ((nd.x3d-cfg.sizeX/2.0)**2+(nd.y3d+cfg.sizeY/2.0)**2+(nd.z3d-cfg.sizeZ/2.0)**2)**0.5
                    if nd.concentration>cfg.Kceil and r > dist:
                        dist = r
                    if nd.concentration<=cfg.Kceil and r < dist1:
                        dist1 = r
            fout.write("%g\t%g\t%g\n" %(h.t, dist, dist1))
            fout.flush()

    if pcid == 0:
        progress_bar(tstop)
        fout.close()
        with open(os.path.join(cfg.filename,"recs.pkl"),'wb') as fout:
            pickle.dump(recs,fout)
        print("\nSimulation complete. Plotting membrane potentials")

    with open(os.path.join(cfg.filename,"centermembrane_potential_%i.pkl" % pcid),'wb') as pout:
        pickle.dump([rec_cells, pos, pops, time], pout)

    pc.barrier()    # wait for all processes to save

## final sim setup
h.load_file('stdrun.hoc')
h.finitialize(cfg.hParams['v_init'])
h.celsius = cfg.hParams['celsius']
h.dt = cfg.dt

run(cfg.duration)

# basic plotting
if pcid == 0:
    from analysis import traceExamples, compareKwaves
    traceExamples(cfg.filename, cfg.filename + 'traces.png', iss=[0,4,8,12,13])
    plt.close()
    compareKwaves([cfg.filename], [cfg.ox], 'Condition', colors=['r'], figname=cfg.filename+'kwave.png')

pc.barrier()
h.quit()
