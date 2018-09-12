
"""
network/modify.py 

Network class methods to modify the network instance

Contributors: salvadordura@gmail.com
"""


# -----------------------------------------------------------------------------
# Modify cell params
# -----------------------------------------------------------------------------
def modifyCells (self, params, updateMasterAllCells=False):
    import sim

    # Instantiate network connections based on the connectivity rules defined in params
    sim.timing('start', 'modifyCellsTime')
    if sim.rank==0: 
        print('Modfying cell parameters...')

    for cell in self.cells:
        cell.modify(params)

    if updateMasterAllCells:
        sim._gatherCells()  # update allCells

    sim.timing('stop', 'modifyCellsTime')
    if sim.rank == 0 and sim.cfg.timing: print('  Done; cells modification time = %0.2f s.' % sim.timingData['modifyCellsTime'])


# -----------------------------------------------------------------------------
# Modify synMech params
# -----------------------------------------------------------------------------
def modifySynMechs (self, params, updateMasterAllCells=False):
    import sim

    # Instantiate network connections based on the connectivity rules defined in params
    sim.timing('start', 'modifySynMechsTime')
    if sim.rank==0: 
        print('Modfying synaptic mech parameters...')

    for cell in self.cells:
        cell.modifySynMechs(params)

    if updateMasterAllCells:
         sim._gatherCells()  # update allCells

    sim.timing('stop', 'modifySynMechsTime')
    if sim.rank == 0 and sim.cfg.timing: print('  Done; syn mechs modification time = %0.2f s.' % sim.timingData['modifySynMechsTime'])


# -----------------------------------------------------------------------------
# Modify conn params
# -----------------------------------------------------------------------------
def modifyConns (self, params, updateMasterAllCells=False):
    import sim

    # Instantiate network connections based on the connectivity rules defined in params
    sim.timing('start', 'modifyConnsTime')
    if sim.rank==0: 
        print('Modfying connection parameters...')

    for cell in self.cells:
        cell.modifyConns(params)

    if updateMasterAllCells:
        sim._gatherCells()  # update allCells

    sim.timing('stop', 'modifyConnsTime')
    if sim.rank == 0 and sim.cfg.timing: print('  Done; connections modification time = %0.2f s.' % sim.timingData['modifyConnsTime'])


# -----------------------------------------------------------------------------
# Modify stim source params
# -----------------------------------------------------------------------------
def modifyStims (self, params, updateMasterAllCells=False):
    import sim
    
    # Instantiate network connections based on the connectivity rules defined in params
    sim.timing('start', 'modifyStimsTime')
    if sim.rank==0: 
        print('Modfying stimulation parameters...')

    for cell in self.cells:
        cell.modifyStims(params)

    if updateMasterAllCells:
        sim._gatherCells()  # update allCells

    sim.timing('stop', 'modifyStimsTime')
    if sim.rank == 0 and sim.cfg.timing: print('  Done; stims modification time = %0.2f s.' % sim.timingData['modifyStimsTime'])


