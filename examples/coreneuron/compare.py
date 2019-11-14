# read orig output
import json
with open('model_output.json', 'r') as f:
    data = json.load(f)
    spkt = list(data['simData']['spkt'])
    spkid = list(data['simData']['spkt'])


# read coreneuron output
core_spkt, core_spkid = [], [] 
with open('out.dat', 'r') as f: 
    lines=f.read().splitlines() 
    for line in lines: 
        core_spkt.append(float(line.split('\t')[0])) 
        core_spkid.append(float(line.split('\t')[1]))
            
# print comparison
for i in range(len(spkt)):
    print('Original  : t=%.2f, id=%d' % (spkt[i], core_spkid[i]))
    print('coreNEURON: t=%.2f, id=%d\n' % (core_spkt[i], core_spkid[i]))