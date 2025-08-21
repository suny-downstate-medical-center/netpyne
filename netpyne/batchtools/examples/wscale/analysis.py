import pandas
import ast
from scipy.interpolate import interp1d
import pickle
import numpy

def parse_sec_loc(sec_loc):
    return ast.literal_eval(sec_loc)

EPSPNORM = 0.5
df = pandas.read_csv('wscale_search.csv')[['config/sec_loc', 'config/weight', 'epsp']]
sec_locs = df['config/sec_loc'].apply(parse_sec_loc)
df[['sec', 'loc']] = pandas.DataFrame(sec_locs.tolist(), index=df.index)
secs = df['sec'].unique()

wscale = {}
for sec in secs:
    locs = df[df['sec'] == sec]['loc'].unique()
    locs.sort()
    wscale[sec] = []
    for loc in locs:
        # for each section and location calculate the weight where the epsp at soma == 0.5
        entries = df[(df['sec'] == sec) & (df['loc'] == loc)].sort_values(by='config/weight')
        #print(entries)
        weights = entries['config/weight']
        epsps = entries['epsp']
        f = interp1d(epsps, weights, fill_value='extrapolate')
        #print([*zip(weights, epsps)])
        wnorm = f(EPSPNORM) / EPSPNORM
        if numpy.isnan(wnorm):
            print('Warning: for sec {}, loc {}, weight norm has been evaluated to be NaN'.format(sec, loc))
            print('EPSPs:', epsps)
            print('f(EPSPNORM) / EPSPNORM: {}/{}'.format(f(EPSPNORM), EPSPNORM))
        wscale[sec].append(wnorm)
    print(sec, wscale[sec])
with open('wscale_weights.pkl', 'wb') as fptr:
    pickle.dump(wscale, fptr)

