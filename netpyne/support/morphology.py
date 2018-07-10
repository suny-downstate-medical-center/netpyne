# Code adapted from https://github.com/ahwillia/PyNeuron-Toolbox under MIT license

from __future__ import division
import numpy as np
import pylab as plt
from matplotlib.pyplot import cm
import string
from neuron import h
import numbers

# a helper library, included with NEURON
h.load_file('stdlib.hoc')
h.load_file('import3d.hoc')

class Cell:
    def __init__(self,name='neuron',soma=None,apic=None,dend=None,axon=None):
        self.soma = soma if soma is not None else []
        self.apic = apic if apic is not None else []
        self.dend = dend if dend is not None else []
        self.axon = axon if axon is not None else []
        self.all = self.soma + self.apic + self.dend + self.axon

    def delete(self):
        self.soma = None
        self.apic = None
        self.dend = None
        self.axon = None
        self.all = None

    def __str__(self):
        return self.name

def load(filename, fileformat=None, cell=None, use_axon=True, xshift=0, yshift=0, zshift=0):
    """
    Load an SWC from filename and instantiate inside cell. Code kindly provided
    by @ramcdougal.

    Args:
        filename = .swc file containing morphology
        cell = Cell() object. (Default: None, creates new object)
        filename = the filename of the SWC file
        use_axon = include the axon? Default: True (yes)
        xshift, yshift, zshift = use to position the cell

    Returns:
        Cell() object with populated soma, axon, dend, & apic fields

    Minimal example:
        # pull the morphology for the demo from NeuroMorpho.Org
        from PyNeuronToolbox import neuromorphoorg
        with open('c91662.swc', 'w') as f:
            f.write(neuromorphoorg.morphology('c91662'))
        cell = load_swc(filename)

    """

    if cell is None:
        cell = Cell(name=string.join(filename.split('.')[:-1]))

    if fileformat is None:
        fileformat = filename.split('.')[-1]

    name_form = {1: 'soma[%d]', 2: 'axon[%d]', 3: 'dend[%d]', 4: 'apic[%d]'}

    # load the data. Use Import3d_SWC_read for swc, Import3d_Neurolucida3 for
    # Neurolucida V3, Import3d_MorphML for MorphML (level 1 of NeuroML), or
    # Import3d_Eutectic_read for Eutectic.
    if fileformat == 'swc':
        morph = h.Import3d_SWC_read()
    elif fileformat == 'asc':
        morph = h.Import3d_Neurolucida3()
    else:
        raise Exception('file format `%s` not recognized'%(fileformat))
    morph.input(filename)

    # easiest to instantiate by passing the loaded morphology to the Import3d_GUI
    # tool; with a second argument of 0, it won't display the GUI, but it will allow
    # use of the GUI's features
    i3d = h.Import3d_GUI(morph, 0)

    # get a list of the swc section objects
    swc_secs = i3d.swc.sections
    swc_secs = [swc_secs.object(i) for i in xrange(int(swc_secs.count()))]

    # initialize the lists of sections
    sec_list = {1: cell.soma, 2: cell.axon, 3: cell.dend, 4: cell.apic}

    # name and create the sections
    real_secs = {}
    for swc_sec in swc_secs:
        cell_part = int(swc_sec.type)

        # skip everything else if it's an axon and we're not supposed to
        # use it... or if is_subsidiary
        if (not(use_axon) and cell_part == 2) or swc_sec.is_subsidiary:
            continue
        
        # figure out the name of the new section
        if cell_part not in name_form:
            raise Exception('unsupported point type')
        name = name_form[cell_part] % len(sec_list[cell_part])

        # create the section
        sec = h.Section(name=name)
        
        # connect to parent, if any
        if swc_sec.parentsec is not None:
            sec.connect(real_secs[swc_sec.parentsec.hname()](swc_sec.parentx))

        # define shape
        if swc_sec.first == 1:
            h.pt3dstyle(1, swc_sec.raw.getval(0, 0), swc_sec.raw.getval(1, 0),
                        swc_sec.raw.getval(2, 0), sec=sec)

        j = swc_sec.first
        xx, yy, zz = [swc_sec.raw.getrow(i).c(j) for i in xrange(3)]
        dd = swc_sec.d.c(j)
        if swc_sec.iscontour_:
            # never happens in SWC files, but can happen in other formats supported
            # by NEURON's Import3D GUI
            raise Exception('Unsupported section style: contour')

        if dd.size() == 1:
            # single point soma; treat as sphere
            x, y, z, d = [dim.x[0] for dim in [xx, yy, zz, dd]]
            for xprime in [x - d / 2., x, x + d / 2.]:
                h.pt3dadd(xprime + xshift, y + yshift, z + zshift, d, sec=sec)
        else:
            for x, y, z, d in zip(xx, yy, zz, dd):
                h.pt3dadd(x + xshift, y + yshift, z + zshift, d, sec=sec)

        # store the section in the appropriate list in the cell and lookup table               
        sec_list[cell_part].append(sec)    
        real_secs[swc_sec.hname()] = sec

    cell.all = cell.soma + cell.apic + cell.dend + cell.axon
    return cell

def sequential_spherical(xyz):
    """
    Converts sequence of cartesian coordinates into a sequence of
    line segments defined by spherical coordinates.
    
    Args:
        xyz = 2d numpy array, each row specifies a point in
              cartesian coordinates (x,y,z) tracing out a
              path in 3D space.
    
    Returns:
        r = lengths of each line segment (1D array)
        theta = angles of line segments in XY plane (1D array)
        phi = angles of line segments down from Z axis (1D array)
    """
    d_xyz = np.diff(xyz,axis=0)
    
    r = np.linalg.norm(d_xyz,axis=1)
    theta = np.arctan2(d_xyz[:,1], d_xyz[:,0])
    hyp = d_xyz[:,0]**2 + d_xyz[:,1]**2
    phi = np.arctan2(np.sqrt(hyp), d_xyz[:,2])
    
    return (r,theta,phi)

def spherical_to_cartesian(r,theta,phi):
    """
    Simple conversion of spherical to cartesian coordinates
    
    Args:
        r,theta,phi = scalar spherical coordinates
    
    Returns:
        x,y,z = scalar cartesian coordinates
    """
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)
    return (x,y,z)

def find_coord(targ_length,xyz,rcum,theta,phi):
    """
    Find (x,y,z) ending coordinate of segment path along section
    path.

    Args:
        targ_length = scalar specifying length of segment path, starting
                      from the begining of the section path
        xyz = coordinates specifying the section path
        rcum = cumulative sum of section path length at each node in xyz
        theta, phi = angles between each coordinate in xyz
    """
    #   [1] Find spherical coordinates for the line segment containing
    #           the endpoint.
    #   [2] Find endpoint in spherical coords and convert to cartesian
    i = np.nonzero(rcum <= targ_length)[0][-1]
    if i == len(theta):
        return xyz[-1,:]
    else:
        r_lcl = targ_length-rcum[i] # remaining length along line segment
        (dx,dy,dz) = spherical_to_cartesian(r_lcl,theta[i],phi[i])
        return xyz[i,:] + [dx,dy,dz]

def interpolate_jagged(xyz,nseg):
    """
    Interpolates along a jagged path in 3D
    
    Args:
        xyz = section path specified in cartesian coordinates
        nseg = number of segment paths in section path
        
    Returns:
        interp_xyz = interpolated path
    """
    
    # Spherical coordinates specifying the angles of all line
    # segments that make up the section path
    (r,theta,phi) = sequential_spherical(xyz)
    
    # cumulative length of section path at each coordinate
    rcum = np.append(0,np.cumsum(r))

    # breakpoints for segment paths along section path
    breakpoints = np.linspace(0,rcum[-1],nseg+1)
    np.delete(breakpoints,0)
    
    # Find segment paths
    seg_paths = []
    for a in range(nseg):
        path = []
        
        # find (x,y,z) starting coordinate of path
        if a == 0:
            start_coord = xyz[0,:]
        else:
            start_coord = end_coord # start at end of last path
        path.append(start_coord)

        # find all coordinates between the start and end points
        start_length = breakpoints[a]
        end_length = breakpoints[a+1]
        mid_boolean = (rcum > start_length) & (rcum < end_length)
        mid_indices = np.nonzero(mid_boolean)[0]
        for mi in mid_indices:
            path.append(xyz[mi,:])

        # find (x,y,z) ending coordinate of path
        end_coord = find_coord(end_length,xyz,rcum,theta,phi)
        path.append(end_coord)

        # Append path to list of segment paths
        seg_paths.append(np.array(path))
    
    # Return all segment paths
    return seg_paths

def get_section_path(h,sec):
    n3d = int(h.n3d(sec=sec))
    xyz = []
    for i in range(0,n3d):
        xyz.append([h.x3d(i,sec=sec),h.y3d(i,sec=sec),h.z3d(i,sec=sec)])
    xyz = np.array(xyz)
    return xyz

def get_section_diams(h,sec):
    n3d = int(h.n3d(sec=sec))
    diams = []
    for i in range(0,n3d):
        diams.append(h.diam3d(i,sec=sec))
    return diams

def shapeplot(h,ax,sections=None,order='pre',cvals=None,\
              clim=None,cmap=cm.YlOrBr_r, legend=True,  **kwargs):  # meanLineWidth=1.0, maxLineWidth=10.0,
    """
    Plots a 3D shapeplot

    Args:
        h = hocObject to interface with neuron
        ax = matplotlib axis for plotting
        sections = list of h.Section() objects to be plotted
        order = { None= use h.allsec() to get sections
                  'pre'= pre-order traversal of morphology }
        cvals = list/array with values mapped to color by cmap; useful
                for displaying voltage, calcium or some other state
                variable across the shapeplot.
        **kwargs passes on to matplotlib (e.g. color='r' for red lines)

    Returns:
        lines = list of line objects making up shapeplot
    """
    
    # Default is to plot all sections. 
    if sections is None:
        if order == 'pre':
            sections = allsec_preorder(h) # Get sections in "pre-order"
        else:
            sections = list(h.allsec())
    
    # Determine color limits
    if cvals is not None and clim is None: 
        clim = [np.nanmin(cvals), np.nanmax(cvals)]

    # Plot each segement as a line
    lines = []
    i = 0

    allDiams = []
    for sec in sections:
        allDiams.append(get_section_diams(h,sec))
    #maxDiams = max([max(d) for d in allDiams])
    #meanDiams = np.mean([np.mean(d) for d in allDiams])

    for isec,sec in enumerate(sections):
        xyz = get_section_path(h,sec)
        seg_paths = interpolate_jagged(xyz,sec.nseg)
        diams = allDiams[isec]  # represent diams as linewidths
        linewidths = diams # linewidth is in points so can use actual diams to plot
        # linewidths = [min(d/meanDiams*meanLineWidth, maxLineWidth) for d in diams]  # use if want to scale size 

        for (j,path) in enumerate(seg_paths):
            line, = plt.plot(path[:,0], path[:,1], path[:,2], '-k', **kwargs)
            try:
                line.set_linewidth(linewidths[j])
            except:
                pass
            if cvals is not None:
                if isinstance(cvals[i], numbers.Number):
                    # map number to colormap
                    try:
                        col = cmap(int((cvals[i]-clim[0])*255/(clim[1]-clim[0])))
                    except:
                        col = cmap(0)
                else:
                    # use input directly. E.g. if user specified color with a string.
                    col = cvals[i]
                line.set_color(col)
            lines.append(line)
            i += 1
    return lines

def shapeplot_animate(v,lines,nframes=None,tscale='linear',\
                      clim=[-80,50],cmap=cm.YlOrBr_r):
    """ Returns animate function which updates color of shapeplot """
    if nframes is None:
        nframes = v.shape[0]
    if tscale == 'linear':
        def animate(i):
            i_t = int((i/nframes)*v.shape[0])
            for i_seg in range(v.shape[1]):
                lines[i_seg].set_color(cmap(int((v[i_t,i_seg]-clim[0])*255/(clim[1]-clim[0]))))
            return []
    elif tscale == 'log':
        def animate(i):
            i_t = int(np.round((v.shape[0] ** (1.0/(nframes-1))) ** i - 1))
            for i_seg in range(v.shape[1]):
                lines[i_seg].set_color(cmap(int((v[i_t,i_seg]-clim[0])*255/(clim[1]-clim[0]))))
            return []
    else:
        raise ValueError("Unrecognized option '%s' for tscale" % tscale)

    return animate

def mark_locations(h,section,locs,markspec='or',**kwargs):
    """
    Marks one or more locations on along a section. Could be used to
    mark the location of a recording or electrical stimulation.

    Args:
        h = hocObject to interface with neuron
        section = reference to section
        locs = float between 0 and 1, or array of floats
        optional arguments specify details of marker

    Returns:
        line = reference to plotted markers
    """

    # get list of cartesian coordinates specifying section path
    xyz = get_section_path(h,section)
    (r,theta,phi) = sequential_spherical(xyz)
    rcum = np.append(0,np.cumsum(r))

    # convert locs into lengths from the beginning of the path
    if type(locs) is float or type(locs) is np.float64:
        locs = np.array([locs])
    if type(locs) is list:
        locs = np.array(locs)
    lengths = locs*rcum[-1]

    # find cartesian coordinates for markers
    xyz_marks = []
    for targ_length in lengths:
        xyz_marks.append(find_coord(targ_length,xyz,rcum,theta,phi))
    xyz_marks = np.array(xyz_marks)

    # plot markers
    line, = plt.plot(xyz_marks[:,0], xyz_marks[:,1], \
                     xyz_marks[:,2], markspec, **kwargs)
    return line

def root_sections(h):
    """
    Returns a list of all sections that have no parent.
    """
    roots = []
    for section in h.allsec():
        sref = h.SectionRef(sec=section)
        # has_parent returns a float... cast to bool
        if sref.has_parent() < 0.9:
            roots.append(section)
    return roots

def leaf_sections(h):
    """
    Returns a list of all sections that have no children.
    """
    leaves = []
    for section in h.allsec():
        sref = h.SectionRef(sec=section)
        # nchild returns a float... cast to bool
        if sref.nchild() < 0.9:
            leaves.append(section)
    return leaves

def root_indices(sec_list):
    """
    Returns the index of all sections without a parent.
    """
    roots = []
    for i,section in enumerate(sec_list):
        sref = h.SectionRef(sec=section)
        # has_parent returns a float... cast to bool
        if sref.has_parent() < 0.9:
            roots.append(i)
    return roots

def allsec_preorder(h):
    """
    Alternative to using h.allsec(). This returns all sections in order from
    the root. Traverses the topology each neuron in "pre-order"
    """
    #Iterate over all sections, find roots
    roots = root_sections(h)

    # Build list of all sections
    sec_list = []
    for r in roots:
        add_pre(h,sec_list,r)
    return sec_list

def add_pre(h,sec_list,section,order_list=None,branch_order=None):
    """
    A helper function that traverses a neuron's morphology (or a sub-tree)
    of the morphology in pre-order. This is usually not necessary for the
    user to import.
    """

    sec_list.append(section)
    sref = h.SectionRef(sec=section)

    if branch_order is not None:
        order_list.append(branch_order)
        if len(sref.child) > 1:
            branch_order += 1
    
    for next_node in sref.child:
        add_pre(h,sec_list,next_node,order_list,branch_order)

def dist_between(h,seg1,seg2):
    """
    Calculates the distance between two segments. I stole this function from
    a post by Michael Hines on the NEURON forum
    (www.neuron.yale.edu/phpbb/viewtopic.php?f=2&t=2114)
    """
    h.distance(0, seg1.x, sec=seg1.sec)
    return h.distance(seg2.x, sec=seg2.sec)

def all_branch_orders(h):
    """
    Produces a list branch orders for each section (following pre-order tree
    traversal)
    """
    #Iterate over all sections, find roots
    roots = []
    for section in h.allsec():
        sref = h.SectionRef(sec=section)
        # has_parent returns a float... cast to bool
        if sref.has_parent() < 0.9:
            roots.append(section)

    # Build list of all sections
    order_list = []
    for r in roots:
        add_pre(h,[],r,order_list,0)
    return order_list

def branch_order(h,section, path=[]):
    """
    Returns the branch order of a section
    """
    path.append(section)
    sref = h.SectionRef(sec=section)
    # has_parent returns a float... cast to bool
    if sref.has_parent() < 0.9:
        return 0 # section is a root
    else:
        nchild = len(list(h.SectionRef(sec=sref.parent).child))
        if nchild <= 1.1:
            return branch_order(h,sref.parent,path)
        else:
            return 1+branch_order(h,sref.parent,path)

def dist_to_mark(h, section, secdict, path=[]):
    path.append(section)
    sref = h.SectionRef(sec=section)
    # print 'current : '+str(section)
    # print 'parent  : '+str(sref.parent)
    if secdict[sref.parent] is None:
        # print '-> go to parent'
        s = section.L + dist_to_mark(h, sref.parent, secdict, path)
        # print 'summing, '+str(s)
        return s
    else:
        # print 'end <- start summing: '+str(section.L)
        return section.L # parent is marked

def branch_precedence(h):
    roots = root_sections(h)
    leaves = leaf_sections(h)
    seclist = allsec_preorder(h)
    secdict = { sec:None for sec in seclist }

    for r in roots:
        secdict[r] = 0
    
    precedence = 1
    while len(leaves)>0:
        # build list of distances of all paths to remaining leaves
        d = []
        for leaf in leaves:
            p = []
            dist = dist_to_mark(h, leaf, secdict, path=p)
            d.append((dist,[pp for pp in p]))
        
        # longest path index
        i = np.argmax([ dd[0] for dd in d ])
        leaves.pop(i) # this leaf will be marked

        # mark all sections in longest path
        for sec in d[i][1]:
            if secdict[sec] is None:
                secdict[sec] = precedence

        # increment precedence across iterations
        precedence += 1

    #prec = secdict.values()
    #return [0 if p is None else 1 for p in prec], d[i][1]
    return [ secdict[sec] for sec in seclist ]


