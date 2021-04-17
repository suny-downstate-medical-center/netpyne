from neuron import h, gui

soma = h.Section()
soma.insert('hh')

def pname(msname):
    s = h.ref('')
    for i in range(-1, 4):
        ms = h.MechanismStandard(msname, i)
        print('\n', msname, '  vartype=%d' % i)  # vartype = 1 -> PARAMETER
        for j in range(int(ms.count())):
            k = ms.name(s, j)
            print('%-5d %-20s size=%d' % (j, s[0], k))

def ptype():
    msname = h.ref('')
    propList = {}
    for i, mechtype in enumerate(['mechs','pointps']):
        mt = h.MechanismType(i)  # either distributed mechs (0) or point process (1)
        propList[mechtype] = {}
        for j in range(int(mt.count())):
            mt.select(j)
            mt.selected(msname)
            print('\n\n', msname[0], ' mechanismtype=%d' % j)
            pname(msname[0])
            ms = h.MechanismStandard(msname[0], 1) # PARAMETER (modifiable)
            propList[mechtype][msname[0]] = []
            propName = h.ref('')
            for prop in range(int(ms.count())):
                k = ms.name(propName, prop)
                propList[mechtype][msname[0]].append(propName[0])
    print(propList)



ptype()
