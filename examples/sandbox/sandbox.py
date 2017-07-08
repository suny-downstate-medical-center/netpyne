from neuron import h, gui

pc = h.ParallelContext()
pc.set_maxstep(10)
idhost = int(pc.id())
nhost = int(pc.nhost())

# Create presyn cell 1
pre1_gid = 0
pre1_host = 0
if idhost == pre1_host:
    pre1 = h.Section(name='pre1')
    pc.set_gid2node(pre1_gid, pre1_host)
    nc = h.NetCon(pre1(0.5)._ref_v, None, sec = pre1)
    nc.threshold = 20.0
    pc.cell(pre1_gid, nc)

# Create presyn cell 2
pre2_gid = 1
pre2_host = 1 if nhost>1 else 0
if idhost == pre2_host:
    pre2 = h.Section(name='pre2')
    pc.set_gid2node(pre2_gid, pre2_host)
    nc = h.NetCon(pre2(0.5)._ref_v, None, sec = pre2) 
    nc.threshold = 20.0
    pc.cell(pre2_gid, nc)

# Create postsyn cell
post_gid = 2
post_host = 0
if idhost == post_host:
    post = h.Section(name='post')
    postsyn = h.Exp2Syn(post(0.5))
    pc.set_gid2node(post_gid, post_host)
    nc = h.NetCon(post(0.5)._ref_v, None, sec = post)
    pc.cell(post_gid, nc) # Associate the cell with this host and gid


# Connect pre to post cells
if pc.gid_exists(post_gid):
    nc1 = pc.gid_connect(pre1_gid, postsyn)
    nc1.threshold = 5.0
    nc2 = pc.gid_connect(pre2_gid, postsyn)
    nc2.threshold = 5.0


# run sim
h.stdinit()

for i in range(3):
    if pc.gid_exists(i):
        print '\ngid: %d, pc.threshold: %.1f' % (i, pc.threshold(i))

