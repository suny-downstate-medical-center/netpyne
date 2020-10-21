'''
    The main function that's called by the NeytPyNE loader, i.e.
    
        from np import load_netpyne
        netParams, simConfig = load_netpyne()
    
    That functionality should fail if this method is missing or doesn't 
    return 2 dict like objects
'''
def load_netpyne():
    from netParams import netParams
    from cfg import cfg

    return netParams, cfg


'''
    Not necessary to have this here, just a useful way to serialise the model 
    note: this can be part of netpyne package
'''
def save_as_json(filename):
    netParams, simConfig = load_netpyne()
    
    info = {'netParams':netParams.todict(),
            'simConfig':simConfig.todict()}
            
    from netpyne.sim.save import saveJSON
    saveJSON(filename, info)
    
    print('Saved netParams and simConfig to file: %s'%filename)
   
    
'''
    This obviously wouldn't be called with: from np import load_netpyne
'''
if __name__ == "__main__":
    save_as_json('/params/params_v1.json')