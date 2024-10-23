"""
Module for importing and exporting NeuroML 2

"""

import logging
import math
import pprint
from collections import OrderedDict
from typing import Dict, Any, Optional, Tuple

from .. import specs

try:
    from typing import override
except ImportError:
    from overrides import override


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
pp = pprint.PrettyPrinter(depth=6, indent=4)
ROUND_PRECISION = 10

try:
    import neuroml
    from neuroml.neuro_lex_ids import neuro_lex_ids
    from pyneuroml import pynml
    from pyneuroml import __version__ as pynml_ver
    from distutils.version import StrictVersion

    min_pynml_ver_required = "0.3.13"  # pyNeuroML will have a dependency on the correct version of libNeuroML...

    if not StrictVersion(pynml_ver) >= StrictVersion(min_pynml_ver_required):
        from neuron import h

        pc = h.ParallelContext()  # MPI: Initialize the ParallelContext class
        if int(pc.id()) == 0:
            logger.critical(
                "Note: pyNeuroML version %s is installed but at least v%s is required"
                % (pynml_ver, min_pynml_ver_required)
            )
            neuromlExists = False
    else:
        neuromlExists = True

except ImportError:
    from neuron import h

    pc = h.ParallelContext()  # MPI: Initialize the ParallelContext class
    if False and int(pc.id()) == 0:  # only print for master node
        logger.critical(
            "Warning: NeuroML import failed; import/export functions for NeuroML will not be available. \n  To install the pyNeuroML & libNeuroML Python packages visit: https://www.neuroml.org/getneuroml"
        )
    neuromlExists = False


def _convertNetworkRepresentation(net, gids_vs_pop_indices):
    """Get connection centric network representation as used in NeuroML2.

    Parameters
    ----------
    net: netpyne.sim.net
        a NetPyNE simulation network object
        **Default:** required

    gids_vs_pop_indices: dict
        a dictionary with NetPyNE gids as keys and indices of cells in NetPyNE
        populations as values
        **Default:** required
    """

    from .. import sim

    nn = {}

    for np_pop in list(net.pops.values()):
        print("Adding conns for: %s" % np_pop.tags)
        if "cellModel" in np_pop.tags and not np_pop.tags["cellModel"] == "NetStim":
            for cell in net.cells:
                if cell.gid in np_pop.cellGids:
                    popPost, indexPost = gids_vs_pop_indices[cell.gid]
                    # print("Cell %s: %s\n    %s[%i]\n"%(cell.gid,cell.tags,popPost, indexPost))
                    for conn in cell.conns:
                        preGid = conn["preGid"]
                        if not preGid == "NetStim":
                            popPre, indexPre = gids_vs_pop_indices[preGid]
                            loc = conn["loc"]
                            weight = conn["weight"]
                            delay = conn["delay"]
                            sec = conn["sec"]
                            synMech = conn["synMech"]
                            # threshold = conn['threshold']

                            if sim.cfg.verbose:
                                print(
                                    "      Conn %s[%i]->%s[%i] with %s, w: %s, d: %s"
                                    % (
                                        popPre,
                                        indexPre,
                                        popPost,
                                        indexPost,
                                        synMech,
                                        weight,
                                        delay,
                                    )
                                )

                            projection_info = (popPre, popPost, synMech)
                            if projection_info not in list(nn.keys()):
                                nn[projection_info] = []

                            nn[projection_info].append(
                                {
                                    "indexPre": indexPre,
                                    "indexPost": indexPost,
                                    "weight": weight,
                                    "delay": delay,
                                }
                            )
                        else:
                            # print("      Conn NetStim->%s[%s] with %s"%(popPost, indexPost, '??'))
                            pass

    return nn


def _convertStimulationRepresentation(
    net, gids_vs_pop_indices, nml_doc, populations_vs_components
):
    """Get stimulations in representation as used in NeuroML2.

    Parameters
    ----------
    net: netpyne.sim.net
        a NetPyNE simulation network object
        **Default:** required

    gids_vs_pop_indices: dict
        a dictionary with NetPyNE gids as keys and indices of cells in NetPyNE
        populations as values
        **Default:** required

    nml_doc: neuroml.NeuroMLDocument
        a NeuroML document object
        **Default:** required

    populations_vs_components: dict
        a dictionary with populations as keys, and cell components for those
        populations as values
        **Default:** required

    """
    stims = {}

    for np_pop in list(net.pops.values()):
        if "cellModel" in np_pop.tags and not np_pop.tags["cellModel"] == "NetStim":
            print("Adding stims for: %s" % np_pop.tags)
            for cell in net.cells:
                if cell.gid in np_pop.cellGids:
                    pop, index = gids_vs_pop_indices[cell.gid]
                    # print("    Cell %s:\n    Tags:  %s\n    Pop:   %s[%i]\n    Stims: %s\n    Conns: %s\n"%(cell.gid,cell.tags,pop, index,cell.stims,cell.conns))
                    for stim in cell.stims:
                        if stim["type"] == "IClamp":
                            il_id = "%s__%s" % (stim["label"], pop)
                            # print('      adding IClamp stim %s: %s '%(il_id,stim))
                            input_list = None
                            for ii in nml_doc.networks[0].input_lists:
                                if ii.id == il_id:
                                    input_list = ii
                            if not input_list:
                                input_list = neuroml.InputList(
                                    id=il_id, component=stim["source"], populations=pop
                                )
                                nml_doc.networks[0].input_lists.append(input_list)

                            input = neuroml.Input(
                                id=len(input_list.input),
                                target="../%s/%i/%s"
                                % (pop, index, populations_vs_components[pop]),
                                destination="synapses",
                            )
                            input_list.input.append(input)

                        elif stim["type"] == "NetStim":
                            # print('      adding NetStim stim: %s'%stim)

                            ref = stim["source"]
                            rate = stim["rate"]
                            noise = stim["noise"]

                            netstim_found = False
                            for conn in cell.conns:
                                if (
                                    conn["preGid"] == "NetStim"
                                    and conn["preLabel"] == ref
                                ):
                                    assert not netstim_found
                                    netstim_found = True
                                    synMech = conn["synMech"]
                                    # threshold = conn['threshold']
                                    delay = conn["delay"]
                                    weight = conn["weight"]

                            assert netstim_found
                            name_stim = "NetStim_%s_%s_%s_%s_%s" % (
                                ref,
                                pop,
                                rate,
                                noise,
                                synMech,
                            )

                            stim_info = (name_stim, pop, rate, noise, synMech)
                            if stim_info not in list(stims.keys()):
                                stims[stim_info] = []

                            stims[stim_info].append(
                                {"index": index, "weight": weight, "delay": delay}
                            )
                            # stims[stim_info].append({'index':index,'weight':weight,'delay':delay,'threshold':threshold})

    # print(stims)
    return stims


def H(x):
    """Heaviside function, required for expressions in <inhomogeneousValue>

    Short description of `netpyne.conversion.neuromlFormat.H`

    Parameters
    ----------
    x :
        Short description of x

        **Default:** ``Required``

        **Options:**



    """

    if x == 0:
        return 0.5

    return 1 * (x > 0)


def _export_synapses(net, nml_doc):
    """Export synapses to NeuroML2.

    Parameters
    ----------
    net: netpyne.sim.net
        a NetPyNE network object
        **Default:** required

    nml_doc: neuroml.NeuroMLDocument
        a NeuroML Document object
        **Default:** required
    """

    from .. import sim

    syn_types = {}
    for id, syn in net.params.synMechParams.items():
        syn_types[id] = syn["mod"]
        if sim.cfg.verbose:
            print("Exporting details of syn: %s" % syn)
        if syn["mod"] == "Exp2Syn":
            syn0 = neuroml.ExpTwoSynapse(
                id=id,
                gbase="1uS",
                erev="%rmV" % syn["e"],
                tau_rise="%rms" % syn["tau1"],
                tau_decay="%rms" % syn["tau2"],
            )

            nml_doc.exp_two_synapses.append(syn0)
        elif syn["mod"] == "ExpSyn":
            syn0 = neuroml.ExpOneSynapse(
                id=id,
                gbase="1uS",
                erev="%rmV" % syn["e"],
                tau_decay="%rms" % syn["tau"],
            )

            nml_doc.exp_one_synapses.append(syn0)
        elif syn["mod"] == "ElectSyn":
            syn0 = neuroml.GapJunction(id=id, conductance="%rmS" % syn["g"])

            nml_doc.gap_junctions.append(syn0)
        else:
            raise Exception("Cannot yet export synapse type: %s" % syn["mod"])

    return syn_types


hh_nml2_chans = """

<neuroml xmlns="http://www.neuroml.org/schema/neuroml2"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.neuroml.org/schema/neuroml2  https://raw.githubusercontent.com/NeuroML/NeuroML2/master/Schemas/NeuroML2/NeuroML_v2beta3.xsd"
            id="kChan">

    <ionChannelHH id="leak_hh" conductance="10pS" type="ionChannelPassive">

        <notes>Single ion channel in NeuroML2 format: passive channel providing a leak conductance </notes>

    </ionChannelHH>

    <ionChannelHH id="na_hh" conductance="10pS" species="na">

        <notes>Single ion channel in NeuroML2 format: standard Sodium channel from the Hodgkin Huxley model</notes>

        <gateHHrates id="m" instances="3">
            <forwardRate type="HHExpLinearRate" rate="1per_ms" midpoint="-40mV" scale="10mV"/>
            <reverseRate type="HHExpRate" rate="4per_ms" midpoint="-65mV" scale="-18mV"/>
        </gateHHrates>

        <gateHHrates id="h" instances="1">
            <forwardRate type="HHExpRate" rate="0.07per_ms" midpoint="-65mV" scale="-20mV"/>
            <reverseRate type="HHSigmoidRate" rate="1per_ms" midpoint="-35mV" scale="10mV"/>
        </gateHHrates>

    </ionChannelHH>

    <ionChannelHH id="k_hh" conductance="10pS" species="k">

        <notes>Single ion channel in NeuroML2 format: standard Potassium channel from the Hodgkin Huxley model</notes>

        <gateHHrates id="n" instances="4">
            <forwardRate type="HHExpLinearRate" rate="0.1per_ms" midpoint="-55mV" scale="10mV"/>
            <reverseRate type="HHExpRate" rate="0.125per_ms" midpoint="-65mV" scale="-80mV"/>
        </gateHHrates>

    </ionChannelHH>


</neuroml>
"""


def exportNeuroML2(
    reference, connections=True, stimulations=True, format="xml", default_cell_radius=5
):
    """
    Exports the current NetPyNE network to NeuroML format

    Parameters
    ----------
    reference : str
        Will be used for id of the network

    connections : bool
        Should connections also be exported?
        **Default:** ``True``

    stimulations : bool
        Should stimulations (current clamps etc) also be exported?
        **Default:** ``True``

    format : str
        Which format, xml or hdf5
        **Default:** ``'xml'``
        **Options:** ``'xml'`` Export as XML format ``'hdf5'`` Export as binary HDF5 format


    default_cell_radius : int
        For abstract cells, e.g. izhikevich, what value should be used in the optional radius property of a population, which can be used in 3D visualizations, etc.
        **Default:** ``5``


    """

    from .. import sim

    net = sim.net

    import random

    myrandom = random.Random(12345)

    print(
        "Exporting the network to NeuroML 2, reference: %s, connections: %s, stimulations: %s, format: %s"
        % (reference, connections, stimulations, format)
    )

    import neuroml
    import neuroml.writers as writers

    nml_doc = neuroml.NeuroMLDocument(id="%s" % reference)
    nml_net = neuroml.Network(id="%s" % reference)
    nml_doc.networks.append(nml_net)

    import netpyne

    nml_doc.notes = "NeuroML 2 file exported from NetPyNE v%s" % (netpyne.__version__)

    gids_vs_pop_indices = {}
    populations_vs_components = {}

    cells_added = []

    sim.cfg.verbose = False

    chans_added = []

    for np_pop_id in net.pops:
        np_pop = net.pops[np_pop_id]
        if sim.cfg.verbose:
            print("-- Adding a population %s: %s" % (np_pop_id, np_pop.tags))

        cell_param_set = {}

        if (
            ("cellModel" not in np_pop.tags or np_pop.tags["cellModel"] == "")
            and "cellType" in np_pop.tags
            and np_pop.tags["cellType"] in net.params.cellParams.keys()
        ):
            # SIMPLE POP/CELLTYPE FORMAT
            if sim.cfg.verbose:
                print("Assuming simple pop/cell type format...")
            cell_param_set = net.params.cellParams[np_pop.tags["cellType"]]
            if sim.cfg.verbose:
                print(
                    "  -- Simple format for populations being used for pop %s with cell %s: %s"
                    % (np_pop_id, np_pop.tags["cellType"], cell_param_set)
                )
            np_pop.tags["cellModel"] = np_pop.tags["cellType"]

        else:
            for cell_name in list(net.params.cellParams.keys()):
                cell_param_set0 = net.params.cellParams[cell_name]
                someMatches = False
                someMisMatches = False
                if sim.cfg.verbose:
                    print(
                        "  -- Checking whether pop %s matches %s: %s"
                        % (np_pop_id, cell_name, cell_param_set0)
                    )
                if "conds" in cell_param_set0:
                    for cond in cell_param_set0["conds"]:
                        if len(cell_param_set0["conds"][cond]) > 0:
                            if (
                                cond in np_pop.tags
                                and cell_param_set0["conds"][cond] == np_pop.tags[cond]
                            ):
                                if sim.cfg.verbose:
                                    print("    Cond: %s matches..." % cond)
                                someMatches = True
                            else:
                                if sim.cfg.verbose:
                                    print(
                                        "    Cond: %s DOESN'T match (%s != %s)..."
                                        % (
                                            cond,
                                            cell_param_set0["conds"][cond],
                                            np_pop.tags[cond]
                                            if cond in np_pop.tags
                                            else "???",
                                        )
                                    )
                                someMisMatches = True
                if someMatches and not someMisMatches:
                    if sim.cfg.verbose:
                        print("   Matches: %s" % cell_param_set0)
                    cell_param_set.update(cell_param_set0)

            if (
                "cellModel" in np_pop.tags
                and not np_pop.tags["cellModel"] == "NetStim"
                and len(cell_param_set) == 0
            ):
                print("Is %s in %s...?" % (np_pop_id, net.params.cellParams.keys()))
                if np_pop_id in net.params.cellParams:
                    print(
                        "Proceeding with assumption %s defines which cellParams..."
                        % np_pop
                    )
                    cell_param_set0 = net.params.cellParams[np_pop_id]
                    cell_param_set.update(cell_param_set0)
                    cell_param_set["conds"] = {}
                    cell_param_set["conds"]["cellType"] = np_pop.tags["cellType"]
                    cell_param_set["conds"]["cellModel"] = np_pop.tags["cellModel"]
                    print(
                        "Now cell params for %s are: %s..."
                        % (np_pop_id, cell_param_set)
                    )

                else:
                    print("Error, could not find cellParams for %s" % np_pop.tags)
                    exit(-1)

        if not np_pop.tags["cellModel"] == "NetStim":
            if "conds" in cell_param_set and len(cell_param_set["conds"]) > 0:
                if (
                    "cellModel" not in cell_param_set["conds"]
                    or cell_param_set["conds"]["cellModel"] == {}
                ):
                    cell_id = "CELL_%s" % (cell_param_set["conds"]["cellType"])
                elif (
                    "cellType" not in cell_param_set["conds"]
                    or cell_param_set["conds"]["cellType"] == {}
                ):
                    cell_id = "CELL_%s" % (cell_param_set["conds"]["cellModel"])
                else:
                    cell_id = "CELL_%s_%s" % (
                        cell_param_set["conds"]["cellModel"],
                        cell_param_set["conds"]["cellType"],
                    )
            else:
                # SIMPLE POP/CELLTYPE FORMAT
                cell_id = "CELL_%s" % (np_pop.tags["cellType"])

            populations_vs_components[np_pop.tags["pop"]] = cell_id

        if sim.cfg.verbose:
            print(
                "Checking whether to add cell: %s; already added: %s"
                % (cell_param_set, cells_added)
            )
        if (
            "cellModel" in np_pop.tags
            and np_pop.tags["cellModel"] != "NetStim"
            and cell_id not in cells_added
        ):
            if sim.cfg.verbose:
                print(
                    "---------------  Adding a cell from pop %s: \n%s"
                    % (np_pop.tags, cell_param_set)
                )

            # print("=====  Adding the cell %s: \n%s"%(cell_name,pp.pprint(cell_param_set)))

            # Single section; one known mechanism...
            soma = cell_param_set["secs"]["soma"]

            if (
                len(cell_param_set["secs"]) == 1
                and soma is not None
                and "mechs" not in soma
                and len(soma["pointps"]) == 1
            ):
                pproc = list(soma["pointps"].values())[0]

                print(
                    "Assuming abstract cell with behaviour set by single point process: %s!"
                    % pproc
                )

                if pproc["mod"] == "Izhi2007b":
                    izh = neuroml.Izhikevich2007Cell(id=cell_id)
                    izh.a = "%r per_ms" % pproc["a"]
                    izh.b = "%r nS" % pproc["b"]
                    izh.c = "%r mV" % pproc["c"]
                    izh.d = "%r pA" % pproc["d"]

                    izh.v0 = "%r mV" % pproc["vr"]  # Note: using vr for v0
                    izh.vr = "%r mV" % pproc["vr"]
                    izh.vt = "%r mV" % pproc["vt"]
                    izh.vpeak = "%r mV" % pproc["vpeak"]
                    izh.C = "%r pF" % (pproc["C"] * 100)
                    izh.k = "%r nS_per_mV" % pproc["k"]

                    nml_doc.izhikevich2007_cells.append(izh)
                else:
                    print(
                        "Unknown point process: %s; can't convert to NeuroML 2 equivalent!"
                        % pproc["mod"]
                    )
                    exit(1)
            else:
                print(
                    "Assuming normal cell with behaviour set by ion channel mechanisms!"
                )

                cell = neuroml.Cell(id=cell_id)
                cell.notes = "Cell exported from NetPyNE:\n%s" % cell_param_set
                cell.morphology = neuroml.Morphology(id="morph_%s" % cell_id)
                cell.biophysical_properties = neuroml.BiophysicalProperties(
                    id="biophys_%s" % cell_id
                )
                mp = neuroml.MembraneProperties()
                cell.biophysical_properties.membrane_properties = mp
                ip = neuroml.IntracellularProperties()
                cell.biophysical_properties.intracellular_properties = ip

                count = 0

                import neuroml.nml.nml

                chans_doc = neuroml.nml.nml.parseString(hh_nml2_chans)

                nml_segs = {}

                parentDistal = neuroml.Point3DWithDiam(x=0, y=0, z=0, diameter=0)

                # First create all nml segs
                for np_sec_name in list(cell_param_set["secs"].keys()):
                    nml_seg = neuroml.Segment(id=count, name=np_sec_name)
                    nml_segs[np_sec_name] = nml_seg
                    count += 1

                count = 0
                for np_sec_name in list(cell_param_set["secs"].keys()):
                    parent_seg = None

                    np_sec = cell_param_set["secs"][np_sec_name]
                    nml_seg = nml_segs[np_sec_name]

                    if "topol" in np_sec and len(np_sec["topol"]) > 0:
                        parent_seg = nml_segs[np_sec["topol"]["parentSec"]]
                        nml_seg.parent = neuroml.SegmentParent(segments=parent_seg.id)
                        if np_sec["topol"]["parentX"] == 0:
                            nml_seg.fract_along = 0
                        if not (
                            (
                                np_sec["topol"]["parentX"] == 1.0
                                or np_sec["topol"]["parentX"] == 0.0
                            )
                            and np_sec["topol"]["childX"] == 0.0
                        ):
                            print(
                                "Currently only support cell topol with (parentX == 1 or 0) and childX == 0"
                            )
                            exit(1)

                    if not (
                        ("pt3d" not in np_sec["geom"])
                        or len(np_sec["geom"]["pt3d"]) == 0
                        or len(np_sec["geom"]["pt3d"]) == 2
                    ):
                        print(
                            "Currently only support cell geoms with 2 pt3ds (or 0 and diam/L specified): %s"
                            % np_sec["geom"]
                        )
                        exit(1)

                    if "pt3d" not in np_sec["geom"] or len(np_sec["geom"]["pt3d"]) == 0:
                        if parent_seg is None:
                            nml_seg.proximal = neuroml.Point3DWithDiam(
                                x=parentDistal.x,
                                y=parentDistal.y,
                                z=parentDistal.z,
                                diameter=np_sec["geom"]["diam"],
                            )

                        nml_seg.distal = neuroml.Point3DWithDiam(
                            x=parentDistal.x,
                            y=(parentDistal.y + np_sec["geom"]["L"]),
                            z=parentDistal.z,
                            diameter=np_sec["geom"]["diam"],
                        )
                    else:
                        prox = np_sec["geom"]["pt3d"][0]

                        nml_seg.proximal = neuroml.Point3DWithDiam(
                            x=prox[0], y=prox[1], z=prox[2], diameter=prox[3]
                        )
                        dist = np_sec["geom"]["pt3d"][1]
                        nml_seg.distal = neuroml.Point3DWithDiam(
                            x=dist[0], y=dist[1], z=dist[2], diameter=dist[3]
                        )

                    nml_seg_section = neuroml.SegmentGroup(
                        id="%s_SECTION" % np_sec_name, neuro_lex_id="sao864921383"
                    )
                    nml_seg_section.members.append(neuroml.Member(segments=count))
                    cell.morphology.segment_groups.append(nml_seg_section)

                    nml_seg_group = neuroml.SegmentGroup(id="%s_group" % np_sec_name)
                    nml_seg_group.includes.append(
                        neuroml.Include(segment_groups=nml_seg_section.id)
                    )
                    cell.morphology.segment_groups.append(nml_seg_group)

                    cell.morphology.segments.append(nml_seg)

                    count += 1

                    ip.resistivities.append(
                        neuroml.Resistivity(
                            value="%r ohm_cm" % np_sec["geom"]["Ra"],
                            segment_groups=nml_seg_group.id,
                        )
                    )

                    """
                    See https://github.com/Neurosim-lab/netpyne/issues/130
                    """
                    cm = np_sec["geom"]["cm"] if "cm" in np_sec["geom"] else 1
                    if isinstance(cm, dict) and len(cm) == 0:
                        cm = 1
                    mp.specific_capacitances.append(
                        neuroml.SpecificCapacitance(
                            value="%r uF_per_cm2" % cm, segment_groups=nml_seg_group.id
                        )
                    )

                    vinit = np_sec["vinit"] if "vinit" in np_sec else -65

                    if isinstance(vinit, dict) and len(vinit) == 0:
                        vinit = -65

                    if len(mp.init_memb_potentials) == 0:
                        mp.init_memb_potentials.append(
                            neuroml.InitMembPotential(value="%r mV" % vinit)
                        )

                    if len(mp.spike_threshes) == 0:
                        mp.spike_threshes.append(
                            neuroml.SpikeThresh(
                                value="%r mV" % sim.net.params.defaultThreshold
                            )
                        )

                    # While testing HNN...
                    mechs_to_ignore = [
                        "dipole",
                        "dipole_pp",
                        "ar_hnn",
                        "ca_hnn",
                        "cat_hnn",
                        "cad",
                        "kca",
                        "km",
                        "ar",
                        "ca",
                        "cat",
                        "vecevent",
                    ]
                    # mechs_to_ignore = []

                    for mech_name in list(np_sec["mechs"].keys()):
                        mech = np_sec["mechs"][mech_name]
                        if mech_name in mechs_to_ignore:
                            print("Ignoring mechanism: %s" % mechs_to_ignore)
                        elif mech_name == "hh" or mech_name == "hh2":
                            for chan in chans_doc.ion_channel_hhs:
                                if (
                                    chan.id == "leak_hh"
                                    or chan.id == "na_hh"
                                    or chan.id == "k_hh"
                                ):
                                    if chan.id not in chans_added:
                                        print(
                                            " > Adding %s since it's not in %s"
                                            % (chan.id, chans_added)
                                        )
                                        nml_doc.ion_channel_hhs.append(chan)
                                        chans_added.append(chan.id)

                            leak_cd = neuroml.ChannelDensity(
                                id="leak_%s" % nml_seg_group.id,
                                ion_channel="leak_hh",
                                cond_density="%r S_per_cm2" % mech["gl"],
                                erev="%r mV" % mech["el"],
                                ion="non_specific",
                            )
                            mp.channel_densities.append(leak_cd)

                            k_cd = neuroml.ChannelDensity(
                                id="k_%s" % nml_seg_group.id,
                                ion_channel="k_hh",
                                cond_density="%r S_per_cm2" % mech["gkbar"],
                                erev="%r mV" % -77.0,
                                ion="k",
                            )
                            mp.channel_densities.append(k_cd)

                            na_cd = neuroml.ChannelDensity(
                                id="na_%s" % nml_seg_group.id,
                                ion_channel="na_hh",
                                cond_density="%r S_per_cm2" % mech["gnabar"],
                                erev="%r mV" % 50.0,
                                ion="na",
                            )
                            mp.channel_densities.append(na_cd)

                        elif mech_name == "pas":
                            for chan in chans_doc.ion_channel_hhs:
                                if chan.id == "leak_hh":
                                    if chan.id not in chans_added:
                                        nml_doc.ion_channel_hhs.append(chan)
                                        chans_added.append(chan.id)

                            leak_cd = neuroml.ChannelDensity(
                                id="leak_%s" % nml_seg_group.id,
                                ion_channel="leak_hh",
                                cond_density="%r mS_per_cm2" % mech["g"],
                                erev="%r mV" % mech["e"],
                                ion="non_specific",
                            )
                            mp.channel_densities.append(leak_cd)
                        else:
                            print(
                                "Currently NML2 export only supports mech hh, not: %s"
                                % mech_name
                            )
                            exit(1)

                nml_doc.cells.append(cell)

            cells_added.append(cell_id)

    for np_pop in list(net.pops.values()):
        index = 0
        print("Adding population: %s" % np_pop.tags)

        type = "populationList"
        if "cellModel" in np_pop.tags and not np_pop.tags["cellModel"] == "NetStim":
            comp_id = populations_vs_components[np_pop.tags["pop"]]
            # print(net.params.cellParams)
            if np_pop.tags["pop"] in net.params.cellParams:
                cell_param_set = net.params.cellParams[np_pop.tags["pop"]]
            else:
                cell_param_set = net.params.cellParams[np_pop.tags["cellType"]]

            print(
                "Population (%s) has comp: %s (%s)"
                % (np_pop.tags, comp_id, cell_param_set)
            )

            pop = neuroml.Population(
                id=np_pop.tags["pop"], component=comp_id, type=type
            )

            # Is it an abstract cell? If so set radius...
            if (
                "pointps" in cell_param_set["secs"]["soma"]
                and len(cell_param_set["secs"]["soma"]["pointps"]) == 1
            ):
                pop.properties.append(neuroml.Property("radius", default_cell_radius))

            pop.properties.append(
                neuroml.Property(
                    "color",
                    "%s %s %s"
                    % (myrandom.random(), myrandom.random(), myrandom.random()),
                )
            )

            nml_net.populations.append(pop)

            for cell in net.cells:
                if cell.gid in np_pop.cellGids:
                    gids_vs_pop_indices[cell.gid] = (np_pop.tags["pop"], index)
                    inst = neuroml.Instance(id=index)
                    index += 1
                    pop.instances.append(inst)
                    inst.location = neuroml.Location(
                        cell.tags["x"], cell.tags["y"], cell.tags["z"]
                    )

            pop.size = index

    syn_types = _export_synapses(net, nml_doc)

    if connections:
        nn = _convertNetworkRepresentation(net, gids_vs_pop_indices)

        half_elect_conns_added = []
        for proj_info in list(nn.keys()):
            prefix = "NetConn"
            popPre, popPost, synMech = proj_info
            if sim.cfg.verbose:
                print("Adding proj: %s->%s (%s)" % (popPre, popPost, synMech))

            if syn_types[synMech] != "ElectSyn":
                projection = neuroml.Projection(
                    id="%s_%s_%s_%s" % (prefix, popPre, popPost, synMech),
                    presynaptic_population=popPre,
                    postsynaptic_population=popPost,
                    synapse=synMech,
                )

                nml_net.projections.append(projection)
            else:
                projection = neuroml.ElectricalProjection(
                    id="%s_%s_%s_%s" % (prefix, popPre, popPost, synMech),
                    presynaptic_population=popPre,
                    postsynaptic_population=popPost,
                )

                nml_net.electrical_projections.append(projection)

            index = 0

            for conn in nn[proj_info]:
                if sim.cfg.verbose:
                    print("Adding conn %s" % conn)

                if syn_types[synMech] != "ElectSyn":
                    connection = neuroml.ConnectionWD(
                        id=index,
                        pre_cell_id="../%s/%i/%s"
                        % (popPre, conn["indexPre"], populations_vs_components[popPre]),
                        pre_segment_id=0,
                        pre_fraction_along=0.5,
                        post_cell_id="../%s/%i/%s"
                        % (
                            popPost,
                            conn["indexPost"],
                            populations_vs_components[popPost],
                        ),
                        post_segment_id=0,
                        post_fraction_along=0.5,
                        delay="%r ms" % conn["delay"],
                        weight=conn["weight"],
                    )

                    projection.connection_wds.append(connection)

                else:
                    """<electricalConnectionInstance id="0" preCell="../iafPop1/0/iaf" postCell="../iafPop2/0/iaf" preSegment="0"
                    preFractionAlong="0.5" postSegment="0" postFractionAlong="0.5" synapse="gj1"/>"""
                    weight = conn["weight"]
                    if weight != 1:
                        raise Exception(
                            "Cannot yet support electrical connections where weight !=1!"
                        )

                    connection = neuroml.ElectricalConnectionInstance(
                        id=index,
                        pre_cell="../%s/%i/%s"
                        % (popPre, conn["indexPre"], populations_vs_components[popPre]),
                        pre_segment=0,
                        pre_fraction_along=0.5,
                        post_cell="../%s/%i/%s"
                        % (
                            popPost,
                            conn["indexPost"],
                            populations_vs_components[popPost],
                        ),
                        post_segment=0,
                        post_fraction_along=0.5,
                        synapse=synMech,
                    )

                    other_half_elect_conn = "%s_%s_%s_%s -> %s_%s_%s_%s" % (
                        popPost,
                        connection.post_cell,
                        connection.post_segment,
                        connection.post_fraction_along,
                        popPre,
                        connection.pre_cell,
                        connection.pre_segment,
                        connection.pre_fraction_along,
                    )

                    if other_half_elect_conn not in half_elect_conns_added:
                        projection.electrical_connection_instances.append(connection)
                        half_elect_conns_added.append(
                            "%s_%s_%s_%s -> %s_%s_%s_%s"
                            % (
                                popPre,
                                connection.pre_cell,
                                connection.pre_segment,
                                connection.pre_fraction_along,
                                popPost,
                                connection.post_cell,
                                connection.post_segment,
                                connection.post_fraction_along,
                            )
                        )

                index += 1

    if stimulations:
        for ssp in net.params.stimSourceParams:
            ss = net.params.stimSourceParams[ssp]
            print("Adding the stim source: %s = %s" % (ssp, ss))
            if ss["type"] == "IClamp":
                pg = neuroml.PulseGenerator(
                    id=ssp,
                    delay="%rms" % ss["del"],
                    duration="%rms" % ss["dur"],
                    amplitude="%f nA" % ss["amp"],
                )

                nml_doc.pulse_generators.append(pg)

        stims = _convertStimulationRepresentation(
            net, gids_vs_pop_indices, nml_doc, populations_vs_components
        )

        for stim_info in list(stims.keys()):
            name_stim, post_pop, rate, noise, synMech = stim_info

            if sim.cfg.verbose:
                print("Adding a NetStim stim: %s" % [stim_info])

            if noise == 0:
                source = neuroml.SpikeGenerator(
                    id=name_stim, period="%rs" % (1.0 / rate)
                )
                nml_doc.spike_generators.append(source)
            elif noise == 1:
                source = neuroml.SpikeGeneratorPoisson(
                    id=name_stim, average_rate="%r Hz" % (rate)
                )
                nml_doc.spike_generator_poissons.append(source)
            else:
                raise Exception(
                    "Noise = %s in a spike generator is not yet supported for NeuroML export!"
                    % noise
                )

            stim_pop = neuroml.Population(
                id="Pop_%s" % name_stim, component=source.id, size=len(stims[stim_info])
            )
            nml_net.populations.append(stim_pop)

            proj = neuroml.Projection(
                id="NetConn_%s__%s" % (name_stim, post_pop),
                presynaptic_population=stim_pop.id,
                postsynaptic_population=post_pop,
                synapse=synMech,
            )

            nml_net.projections.append(proj)

            count = 0
            for stim in stims[stim_info]:
                # print("  Adding stim: %s"%stim)

                connection = neuroml.ConnectionWD(
                    id=count,
                    pre_cell_id="../%s[%i]" % (stim_pop.id, count),
                    pre_segment_id=0,
                    pre_fraction_along=0.5,
                    post_cell_id="../%s/%i/%s"
                    % (post_pop, stim["index"], populations_vs_components[post_pop]),
                    post_segment_id=0,
                    post_fraction_along=0.5,
                    delay="%r ms" % stim["delay"],
                    weight=stim["weight"],
                )
                count += 1

                proj.connection_wds.append(connection)

    nml_file_name = "%s.net.nml" % reference

    if format == "xml":
        print(
            "Writing %s to %s (%s)" % (nml_doc, nml_file_name, nml_file_name.__class__)
        )
        writers.NeuroMLWriter.write(nml_doc, nml_file_name)
    elif format == "hdf5":
        nml_file_name += ".h5"
        writers.NeuroMLHdf5Writer.write(nml_doc, nml_file_name)

    import pyneuroml.lems

    pyneuroml.lems.generate_lems_file_for_neuroml(
        "Sim_%s" % reference,
        nml_file_name,
        reference,
        sim.cfg.duration,
        sim.cfg.dt,
        "LEMS_%s.xml" % reference,
        ".",
        copy_neuroml=False,
        include_extra_files=[],
        gen_plots_for_all_v=False,
        gen_plots_for_only_populations=list(populations_vs_components.keys()),
        gen_saves_for_all_v=False,
        plot_all_segments=False,
        gen_saves_for_only_populations=list(populations_vs_components.keys()),
        save_all_segments=False,
    )


###############################################################################
# Class for handling NeuroML2 constructs and generating the equivalent in
# NetPyNE's internal representation
###############################################################################
try:
    from neuroml.hdf5.DefaultNetworkHandler import DefaultNetworkHandler

    class NetPyNEBuilder(DefaultNetworkHandler):
        """
        Class for handling NeuroML2 constructs and generating the equivalent in
        NetPyNE's internal representation.

        Works with libNeuroML's NeuroMLXMLParser and/or NeuroMLHdf5Parser to parse the NML & build equivalent in NetPyNE

        """

        # TODO: narrow down type hints to specific types instead of Any
        cellParams: Dict[Any, Any] = OrderedDict()
        popParams: Dict[Any, Dict[str, Any]] = OrderedDict()

        # population ids and dictionary of segment ids and their segment
        # objects
        pop_ids_vs_seg_ids_vs_segs: Dict[Any, Any] = {}
        # population ids and the components they consist of
        pop_ids_vs_components: Dict[Any, Any] = {}
        # track whether unbranched segment groups are being used as Neuron
        # sections for populations
        pop_ids_vs_use_segment_groups_for_neuron: Dict[Any, Any] = {}
        # population ids and segments in order
        pop_ids_vs_ordered_segs: Dict[Any, Any] = {}
        # population ids and cumulative segment lengths
        pop_ids_vs_cumulative_lengths: Dict[Any, Any] = {}

        projection_infos: Dict[Any, Any] = OrderedDict()
        connections: Dict[Any, Any] = OrderedDict()

        popStimSources: Dict[Any, Any] = OrderedDict()
        stimSources: Dict[Any, Any] = OrderedDict()
        popStimLists: Dict[Any, Any] = OrderedDict()
        stimLists: Dict[Any, Any] = OrderedDict()

        gids: Dict[Any, Any] = OrderedDict()
        next_gid = 0
        stochastic_input_count = 0

        def __init__(
            self,
            netParams: Dict[Any, Any],
            simConfig: Optional[Dict[Any, Any]] = None,
            verbose: bool = False,
        ):
            self.netParams = netParams
            self.simConfig = simConfig
            self.verbose = verbose

            if self.verbose:
                logger.setLevel(logging.DEBUG)

        def finalise(self):
            for popParam in list(self.popParams.keys()):
                self.netParams.popParams[popParam] = self.popParams[popParam]

            for cellParam in list(self.cellParams.keys()):
                self.netParams.cellParams[cellParam] = self.cellParams[cellParam]

            for proj_id in list(self.projection_infos.keys()):
                projName, prePop, postPop, synapse, ptype = self.projection_infos[
                    proj_id
                ]

                self.netParams.synMechParams[synapse] = {"mod": synapse}

            for stimName in list(self.stimSources.keys()):
                self.netParams.stimSourceParams[stimName] = self.stimSources[stimName]
                self.netParams.stimTargetParams[stimName] = self.stimLists[stimName]

        def _get_prox_dist(
            self, seg: neuroml.Segment, seg_ids_vs_segs: Dict[str, neuroml.Segment]
        ) -> Tuple[neuroml.Point3DWithDiam, neuroml.Point3DWithDiam]:
            """Get proximal and distal points for a segment.

            Parameters
            -----------

            seg: neuroml.Segment
                segment object
                **Default:**: required

            seg_ids_vs_segs: dict
                dictionary with segment ids as keys and segment objects as
                values
                **Default:**: required
            """
            prox = None
            if seg.proximal:
                prox = seg.proximal
            else:
                parent_seg = seg_ids_vs_segs[seg.parent.segments]
                prox = parent_seg.distal

            dist = seg.distal

            # Spherical root segment
            if (
                seg.parent is None
                and prox.x == dist.x
                and prox.y == dist.y
                and prox.z == dist.z
            ):
                if prox.diameter == dist.diameter:
                    dist.y = prox.diameter
                else:
                    raise Exception(
                        "Unsupported geometry in segment: %s of cell" % (seg.name)
                    )

            return prox, dist

        @override
        def handle_network(self, network_id, notes, temperature=None):
            """Handle the network

            Currently, only sets the temperature if provided.

            Parameters
            -----------

            network_id: str
                id of the network
                **Default:** required

            notes: str
                notes (currently unused)
                **Default:** None

            temperature: str
                network temperature
                **Default:** None
            """
            if temperature:
                self.simConfig.hParams["celsius"] = round(
                    pynml.convert_to_units(temperature, "degC"),
                    ROUND_PRECISION
                )
                logger.info(
                    "Setting global temperature to %s"
                    % self.simConfig.hParams["celsius"]
                )

        @override
        def handle_population(
            self,
            population_id,
            component,
            size,
            component_obj,
            properties={},
            notes=None,
        ):
            """Handle a population.

            Parameters
            -----------

            population_id: str
                id of population
                **Default:** required

            component: str
                id of the component used in the population
                **Default:** required

            size: int
                size of population
                **Default:** required

            component_object: object
                object of the component used in the population
                **Default:** required

            properties: dict
                dictionary of properties (currently unused)
                **Default:** {}

            notes: str
                notes (currently unused)
                **Default:** None
            """

            if self.verbose:
                logger.debug(
                    "A population: %s with %i of %s (%s) "
                    % (population_id, size, component, str(component_obj.id).strip())
                )

            self.pop_ids_vs_components[population_id] = component_obj

            assert component == component_obj.id

            # dictionary used to populate netParams.popParams
            popInfo: Dict[str, Any] = OrderedDict()
            popInfo["pop"] = population_id
            # popInfo['cellModel'] = component

            # SIMPLE POP/CELLTYPE FORMAT
            popInfo["cellType"] = component
            popInfo["originalFormat"] = (
                "NeuroML2"  # This parameter is required to distinguish NML2 "point processes" from abstract cells
            )
            popInfo["cellsList"] = []
            popInfo["numCells"] = size

            if population_id == "pop":
                logger.error(
                    """
                    ***************************** ERROR *****************************
                    The 'pop' label for populations is reservered.
                    Please use something else.

                    See
                    http://doc.netpyne.org/user_documentation.html#population-parameters

                    Exiting.
                    ***************************** ERROR *****************************
                    """
                )
                quit()

            self.popParams[population_id] = popInfo

            # Now, let us handle the component of the population #

            # Cell with morphology and biophysics
            # https://docs.neuroml.org/Userdocs/Schemas/Cells.html#cell
            if isinstance(component_obj, neuroml.Cell):
                # popInfo['cellType'] = component

                cell = component_obj
                """
                cellRule = {'conds':{'cellType': component,
                                        'cellModel': component},
                            'secs': {},
                            'secLists':{}}
                """
                # construct NetPyNE cellParams object
                # http://doc.netpyne.org/modeling-specification-v1.0.html#cell-types
                cellRule = {"secs": {}, "secLists": {}}

                # set spike threshold for the cell
                if (
                    len(cell.biophysical_properties.membrane_properties.spike_threshes)
                    > 0
                ):
                    st = cell.biophysical_properties.membrane_properties.spike_threshes[
                        0
                    ]
                    # Ensure threshold is same everywhere on cell
                    assert st.segment_groups == "all"
                    assert (
                        len(
                            cell.biophysical_properties.membrane_properties.spike_threshes
                        )
                        == 1
                    )
                    threshold = pynml.convert_to_units(st.value, "mV")
                else:
                    threshold = 0

                # Handle segments and segment groups #
                # segment groups and their corresponding Neuron sections
                seg_grps_vs_nrn_sections = {}
                seg_grps_vs_nrn_sections["all"] = []

                use_segment_groups_for_neuron = False

                # Go over segment groups to see if unbranched segment groups
                # are marked using the neurolex id.
                # If they are, these directly become sections
                for seg_grp in cell.morphology.segment_groups:
                    # Unbranched segment group -> NEURON section
                    if (
                        hasattr(seg_grp, "neuro_lex_id")
                        and seg_grp.neuro_lex_id == neuro_lex_ids["section"]
                    ):
                        use_segment_groups_for_neuron = True
                        cellRule["secs"][seg_grp.id] = {
                            "geom": {"pt3d": []},
                            "mechs": {},
                            "ions": {},
                        }
                        for prop in seg_grp.properties:
                            if prop.tag == "numberInternalDivisions":
                                cellRule["secs"][seg_grp.id]["geom"]["nseg"] = int(
                                    prop.value
                                )
                        # seg_grps_vs_nrn_sections[seg_grp.id] = seg_grp.id
                        seg_grps_vs_nrn_sections["all"].append(seg_grp.id)

                        cellRule["secs"][seg_grp.id]["threshold"] = threshold

                # track whether unbranched segment groups are used as
                # Neuron sections for this population
                self.pop_ids_vs_use_segment_groups_for_neuron[population_id] = (
                    use_segment_groups_for_neuron
                )

                if not use_segment_groups_for_neuron:
                    # Unbranched segment groups not marked, so we construct
                    # sections and geometry from individual segments
                    for seg in cell.morphology.segments:
                        seg_grps_vs_nrn_sections["all"].append(seg.name)
                        cellRule["secs"][seg.name] = {
                            "geom": {"pt3d": []},
                            "mechs": {},
                            "ions": {},
                        }

                        prox, dist = self._get_prox_dist(
                            seg, cell.segment_ids_vs_segments
                        )

                        cellRule["secs"][seg.name]["geom"]["pt3d"].append(
                            (prox.x, prox.y, prox.z, prox.diameter)
                        )
                        cellRule["secs"][seg.name]["geom"]["pt3d"].append(
                            (dist.x, dist.y, dist.z, dist.diameter)
                        )

                        if seg.parent:
                            parent_seg = cell.segment_ids_vs_segments[
                                seg.parent.segments
                            ]
                            cellRule["secs"][seg.name]["topol"] = {
                                "parentSec": parent_seg.name,
                                "parentX": float(seg.parent.fraction_along),
                                "childX": 0,
                            }

                else:
                    # Get geometry from the unbranched segment groups
                    ordered_segs, cumulative_lengths = (
                        cell.get_ordered_segments_in_groups(
                            list(cellRule["secs"].keys()),
                            include_cumulative_lengths=True,
                        )
                    )
                    self.pop_ids_vs_ordered_segs[population_id] = ordered_segs
                    self.pop_ids_vs_cumulative_lengths[population_id] = (
                        cumulative_lengths
                    )

                    for section in cellRule["secs"].keys():
                        logger.debug("Processing section: %s", section)
                        # print("ggg %s: %s"%(section,ordered_segs[section]))
                        for seg in ordered_segs[section]:
                            logger.debug("Processing segment: %s", seg)
                            prox, dist = self._get_prox_dist(
                                seg, cell.segment_ids_vs_segments
                            )

                            if seg.id == ordered_segs[section][0].id:
                                logger.debug(
                                    "Processing first segment %s of section %s",
                                    seg,
                                    section,
                                )
                                # If it's the first segment, add the proximal
                                # point to mark the start of the section
                                cellRule["secs"][section]["geom"]["pt3d"].append(
                                    (prox.x, prox.y, prox.z, prox.diameter)
                                )
                                if seg.parent:
                                    parent_seg = cell.segment_ids_vs_segments[
                                        seg.parent.segments
                                    ]
                                    parent_sec = None
                                    for sec, segments in ordered_segs.items():
                                        if parent_seg in segments:
                                            parent_sec = sec
                                            break

                                    fract = float(seg.parent.fraction_along)

                                    # TODO: implement conversion of NeuroML segment's parent's fractAlong to
                                    # Neuron's unbranched section's parentX.
                                    # Until this is implemented, we only handle cases where the the first
                                    # segment of a segment group is either attached to its parent at the
                                    # parent's proximal or distal point.
                                    if (fract != 1.0) and (
                                        math.isclose(fract, 1.0, rel_tol=1e-4)
                                    ):
                                        logger.warning(
                                            "Approximating fract of %f to 1.0", fract
                                        )
                                        fract = 1.0
                                    if (fract != 0.0) and (
                                        math.isclose(fract, 0.0, rel_tol=1e-4)
                                    ):
                                        logger.warning(
                                            "Approximating fract of %f to 0.0", fract
                                        )
                                        fract = 0.0

                                    if fract != 1.0 and fract != 0.0:
                                        logger.critical(
                                            "Segment (%s) must be attached to parent (%s) at proximal or distal point",
                                            seg,
                                            seg.parent,
                                        )
                                    assert fract == 1.0 or fract == 0.0

                                    cellRule["secs"][section]["topol"] = {
                                        "parentSec": parent_sec,
                                        "parentX": fract,
                                        "childX": 0,
                                    }

                            # add distal point for all segments
                            cellRule["secs"][section]["geom"]["pt3d"].append(
                                (dist.x, dist.y, dist.z, dist.diameter)
                            )

                # Inhomogeneous Parameters
                inhomogeneous_parameters = {}
                for seg_grp in cell.morphology.segment_groups:
                    # 'all' has been populated, now populate individual groups
                    seg_grps_vs_nrn_sections[seg_grp.id] = []

                    if not use_segment_groups_for_neuron:
                        for member in seg_grp.members:
                            seg_grps_vs_nrn_sections[seg_grp.id].append(
                                cell.segment_ids_vs_segments[member.segments].name
                            )

                    for inc in seg_grp.includes:
                        if not use_segment_groups_for_neuron:
                            for section_name in seg_grps_vs_nrn_sections[
                                inc.segment_groups
                            ]:
                                seg_grps_vs_nrn_sections[seg_grp.id].append(
                                    section_name
                                )
                        else:
                            seg_grps_vs_nrn_sections[seg_grp.id].append(
                                inc.segment_groups
                            )
                            if seg_grp.id not in cellRule["secLists"]:
                                cellRule["secLists"][seg_grp.id] = []
                            cellRule["secLists"][seg_grp.id].append(inc.segment_groups)

                    if (
                        not seg_grp.neuro_lex_id
                        or seg_grp.neuro_lex_id != neuro_lex_ids["section"]
                    ):
                        cellRule["secLists"][seg_grp.id] = seg_grps_vs_nrn_sections[
                            seg_grp.id
                        ]

                    for ip in seg_grp.inhomogeneous_parameters:
                        logger.debug(
                            "Processing inhomogeneous_parameter (%s, %s) in segment group (%s)",
                            ip.id,
                            ip.variable,
                            seg_grp.id,
                        )

                        # print("=====================\ninhomogeneousParameter: %s"%ip)

                        inhomogeneous_parameters[seg_grp.id] = {}

                        # Some checks here to ensure the defaults/recommended values are selected
                        # Can be made more general
                        assert ip.metric == "Path Length from root"
                        assert ip.variable == "p"
                        if ip.proximal:
                            assert float(ip.proximal.translation_start) == 0.0

                        ordered_segs, cumulative_lengths, path_prox, path_dist = (
                            cell.get_ordered_segments_in_groups(
                                [seg_grp.id],
                                include_cumulative_lengths=True,
                                include_path_lengths=True,
                            )
                        )

                        nrn_secs = seg_grps_vs_nrn_sections[seg_grp.id]
                        for nrn_sec in nrn_secs:
                            sec_segs = cell.get_ordered_segments_in_groups(nrn_sec)
                            first = sec_segs[nrn_sec][0]
                            last = sec_segs[nrn_sec][-1]
                            start_len = path_prox[seg_grp.id][first.id]
                            end_len = path_dist[seg_grp.id][last.id]

                            inhomogeneous_parameters[seg_grp.id][nrn_sec] = (
                                round(start_len, ROUND_PRECISION),
                                round(end_len, ROUND_PRECISION),
                            )
                            logger.debug(
                                "Inhomogeneous parameter: Seg: %s (%s) -> %s (%s)",
                                first,
                                start_len,
                                last,
                                end_len,
                            )

                # Channel Densities
                for (
                    cm
                ) in cell.biophysical_properties.membrane_properties.channel_densities:
                    logger.debug("Processing channel density %s", cm.id)
                    group = "all" if not cm.segment_groups else cm.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        gmax = round(
                            pynml.convert_to_units(cm.cond_density,
                                                   "S_per_cm2"),
                            ROUND_PRECISION
                        )
                        if cm.ion_channel == "pas":
                            mech = {"g": gmax}
                        else:
                            mech = {"gmax": gmax}
                        erev = round(pynml.convert_to_units(cm.erev, "mV"),
                                     ROUND_PRECISION)

                        cellRule["secs"][section_name]["mechs"][cm.ion_channel] = mech

                        ion = self._determine_ion(cm)
                        if ion == "non_specific":
                            mech["e"] = erev
                        else:
                            if ion not in cellRule["secs"][section_name]["ions"]:
                                cellRule["secs"][section_name]["ions"][ion] = {}
                            cellRule["secs"][section_name]["ions"][ion]["e"] = erev

                # Channel Densities v-shifts
                for cm in cell.biophysical_properties.membrane_properties.channel_density_v_shifts:
                    logger.debug("Processing channel density v-shift %s", cm.id)
                    group = "all" if not cm.segment_groups else cm.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        gmax = round(
                            pynml.convert_to_units(cm.cond_density,
                                                   "S_per_cm2"),
                            ROUND_PRECISION
                        )
                        if cm.ion_channel == "pas":
                            mech = {"g": gmax}
                        else:
                            mech = {"gmax": gmax}
                        erev = round(pynml.convert_to_units(cm.erev, "mV"),
                                     ROUND_PRECISION)

                        cellRule["secs"][section_name]["mechs"][cm.ion_channel] = mech

                        ion = self._determine_ion(cm)
                        if ion == "non_specific":
                            mech["e"] = erev
                        else:
                            if ion not in cellRule["secs"][section_name]["ions"]:
                                cellRule["secs"][section_name]["ions"][ion] = {}
                            cellRule["secs"][section_name]["ions"][ion]["e"] = erev
                        mech["vShift"] = pynml.convert_to_units(cm.v_shift, "mV")

                # Channel Densities Nernsts
                for cm in cell.biophysical_properties.membrane_properties.channel_density_nernsts:
                    logger.debug("Processing channel density Nernst %s", cm.id)
                    group = "all" if not cm.segment_groups else cm.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        gmax = round(
                            pynml.convert_to_units(cm.cond_density,
                                                   "S_per_cm2"),
                            ROUND_PRECISION
                        )
                        if cm.ion_channel == "pas":
                            mech = {"g": gmax}
                        else:
                            mech = {"gmax": gmax}

                        cellRule["secs"][section_name]["mechs"][cm.ion_channel] = mech

                        ion = self._determine_ion(cm)
                        if ion == "non_specific":
                            pass
                        else:
                            if ion not in cellRule["secs"][section_name]["ions"]:
                                cellRule["secs"][section_name]["ions"][ion] = {}

                # Channel Densities GHK
                for cm in (
                    cell.biophysical_properties.membrane_properties.channel_density_ghks
                ):
                    logger.debug("Processing channel density GHK %s", cm.id)
                    group = "all" if not cm.segment_groups else cm.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        permeability = round(
                            pynml.convert_to_units(cm.permeability,
                                                   "cm_per_s"), ROUND_PRECISION
                        )
                        mech = {"permeability": permeability}

                        cellRule["secs"][section_name]["mechs"][cm.ion_channel] = mech

                        ion = self._determine_ion(cm)
                        if ion == "non_specific":
                            pass
                        else:
                            if ion not in cellRule["secs"][section_name]["ions"]:
                                cellRule["secs"][section_name]["ions"][ion] = {}

                # Channel Densities GHK2
                for cm in cell.biophysical_properties.membrane_properties.channel_density_ghk2s:
                    logger.debug("Processing channel density GHK2 %s", cm.id)
                    group = "all" if not cm.segment_groups else cm.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        gmax = round(
                            pynml.convert_to_units(cm.cond_density,
                                                   "S_per_cm2"),
                            ROUND_PRECISION
                        )
                        if cm.ion_channel == "pas":
                            mech = {"g": gmax}
                        else:
                            mech = {"gmax": gmax}

                        cellRule["secs"][section_name]["mechs"][cm.ion_channel] = mech

                        ion = self._determine_ion(cm)
                        if ion == "non_specific":
                            pass
                        else:
                            if ion not in cellRule["secs"][section_name]["ions"]:
                                cellRule["secs"][section_name]["ions"][ion] = {}

                # Channel Densities non uniform, non uniform nernst, non
                # uniform GHK
                for cm in (
                    cell.biophysical_properties.membrane_properties.channel_density_non_uniforms
                    + cell.biophysical_properties.membrane_properties.channel_density_non_uniform_nernsts
                    + cell.biophysical_properties.membrane_properties.channel_density_non_uniform_ghks
                ):
                    # erev does not need to be set for nernsts
                    set_erev = True
                    if (
                        cm
                        in cell.biophysical_properties.membrane_properties.channel_density_non_uniforms
                    ):
                        logger.debug("Processing channel density non uniform %s", cm.id)
                        set_erev = True
                    elif (
                        cm
                        in cell.biophysical_properties.membrane_properties.channel_density_non_uniform_nernsts
                    ):
                        logger.debug(
                            "Processing channel density non uniform nernsts %s", cm.id
                        )
                        set_erev = False
                    else:
                        logger.debug(
                            "Processing channel density non uniform GHK %s", cm.id
                        )
                        set_erev = False

                    for vp in cm.variable_parameters:
                        if vp.parameter == "condDensity":
                            iv = vp.inhomogeneous_value
                            grp = vp.segment_groups
                            expr = iv.value.replace("exp(", "math.exp(")
                            logger.debug(
                                "variable_parameter: %s, %s, %s" % (grp, iv, expr)
                            )

                            for section_name in seg_grps_vs_nrn_sections[grp]:
                                path_start, path_end = inhomogeneous_parameters[grp][
                                    section_name
                                ]
                                p = path_start
                                gmax_start = pynml.convert_to_units(
                                    "%r S_per_m2" % eval(expr), "S_per_cm2"
                                )
                                p = path_end
                                gmax_end = pynml.convert_to_units(
                                    "%r S_per_m2" % eval(expr), "S_per_cm2"
                                )

                                nseg = (
                                    cellRule["secs"][section_name]["geom"]["nseg"]
                                    if "nseg" in cellRule["secs"][section_name]["geom"]
                                    else 1
                                )

                                logger.debug(
                                    "Cond dens %s: %r S_per_cm2 (%r um) -> %r S_per_cm2 (%r um); nseg = %s",
                                    section_name,
                                    gmax_start,
                                    path_start,
                                    gmax_end,
                                    path_end,
                                    nseg,
                                )

                                gmax = []
                                for fract in [
                                    (2 * i + 1.0) / (2 * nseg) for i in range(nseg)
                                ]:
                                    p = path_start + fract * (path_end - path_start)
                                    gmax_i = pynml.convert_to_units(
                                        "%r S_per_m2" % eval(expr), "S_per_cm2"
                                    )
                                    gmax.append(gmax_i)

                                    logger.debug(
                                        "Point %s at %r = %r", p, fract, gmax_i
                                    )

                                if cm.ion_channel == "pas":
                                    mech = {"g": gmax}
                                else:
                                    mech = {"gmax": gmax}

                                cellRule["secs"][section_name]["mechs"][
                                    cm.ion_channel
                                ] = mech

                                ion = self._determine_ion(cm)
                                if ion == "non_specific":
                                    if set_erev:
                                        mech["e"] = erev
                                else:
                                    if (
                                        ion
                                        not in cellRule["secs"][section_name]["ions"]
                                    ):
                                        cellRule["secs"][section_name]["ions"][ion] = {}
                                    if set_erev:
                                        cellRule["secs"][section_name]["ions"][ion][
                                            "e"
                                        ] = erev

                for vi in (
                    cell.biophysical_properties.membrane_properties.init_memb_potentials
                ):
                    group = "all" if not vi.segment_groups else vi.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        cellRule["secs"][section_name]["vinit"] = (
                            pynml.convert_to_units(vi.value, "mV")
                        )

                for sc in cell.biophysical_properties.membrane_properties.specific_capacitances:
                    group = "all" if not sc.segment_groups else sc.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        cellRule["secs"][section_name]["geom"]["cm"] = (
                            pynml.convert_to_units(sc.value, "uF_per_cm2")
                        )

                for (
                    ra
                ) in cell.biophysical_properties.intracellular_properties.resistivities:
                    group = "all" if not ra.segment_groups else ra.segment_groups
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        cellRule["secs"][section_name]["geom"]["Ra"] = (
                            pynml.convert_to_units(ra.value, "ohm_cm")
                        )

                for (
                    specie
                ) in cell.biophysical_properties.intracellular_properties.species:
                    group = (
                        "all" if not specie.segment_groups else specie.segment_groups
                    )
                    for section_name in seg_grps_vs_nrn_sections[group]:
                        ion = specie.ion
                        if ion not in cellRule["secs"][section_name]["ions"]:
                            cellRule["secs"][section_name]["ions"][ion] = {}

                        cellRule["secs"][section_name]["ions"][ion]["o"] = (
                            pynml.convert_to_units(
                                specie.initial_ext_concentration, "mM"
                            )
                        )
                        cellRule["secs"][section_name]["ions"][ion]["i"] = (
                            pynml.convert_to_units(specie.initial_concentration, "mM")
                        )

                        cellRule["secs"][section_name]["mechs"][
                            specie.concentration_model
                        ] = {}

                self.cellParams[component] = cellRule

                # for cp in self.cellParams.keys():
                #    pp.pprint(self.cellParams[cp])

                self.pop_ids_vs_seg_ids_vs_segs[population_id] = (
                    cell.segment_ids_vs_segments
                )

            else:  # Abstract cell
                # popInfo['cellType'] = component

                if self.verbose:
                    print(
                        "Abstract cell: %s"
                        % (isinstance(component_obj, neuroml.BaseCell))
                    )

                if hasattr(component_obj, "thresh"):
                    threshold = pynml.convert_to_units(component_obj.thresh, "mV")
                elif hasattr(component_obj, "v_thresh"):
                    threshold = float(component_obj.v_thresh)  # PyNN cells...
                else:
                    threshold = 0.0

                if not isinstance(component_obj, neuroml.BaseCell):
                    popInfo["originalFormat"] = "NeuroML2_SpikeSource"

                cellRule = {
                    "label": component,
                    "secs": {},
                }  # This parameter is required to distinguish NML2 "point processes" from artificial cells

                soma = {"geom": {}, "pointps": {}}  # soma properties
                default_diam = 10
                soma["geom"] = {"diam": default_diam, "L": default_diam}
                soma["threshold"] = threshold

                # TODO: add correct hierarchy to Schema for baseCellMembPotCap etc. and use this...
                if hasattr(component_obj, "C"):
                    capTotSI = pynml.convert_to_units(component_obj.C, "F")
                    area = math.pi * default_diam * default_diam
                    specCapNeu = 10e13 * capTotSI / area

                    # print("c: %s, area: %s, sc: %s"%(capTotSI, area, specCapNeu))

                    soma["geom"]["cm"] = specCapNeu
                # PyNN cells
                elif hasattr(component_obj, "cm") and "IF_c" in str(
                    type(component_obj)
                ):
                    capTotSI = component_obj.cm * 1e-9
                    area = math.pi * default_diam * default_diam
                    specCapNeu = 10e13 * capTotSI / area

                    soma["geom"]["cm"] = specCapNeu
                else:
                    soma["geom"]["cm"] = 318.319
                    # print("sc: %s"%(soma['geom']['cm']))

                soma["pointps"][component] = {"mod": component}
                cellRule["secs"] = {"soma": soma}  # add sections to dict
                self.cellParams[component] = cellRule

            self.gids[population_id] = [-1] * size

        def _determine_ion(self, channel_density):
            ion = channel_density.ion
            if not ion:
                if "na" in channel_density.ion_channel.lower():
                    ion = "na"
                elif "k" in channel_density.ion_channel.lower():
                    ion = "k"
                elif "ca" in channel_density.ion_channel.lower():
                    ion = "ca"
                else:
                    ion = "non_specific"
            return ion

        def _convert_to_nrn_section_location(self, population_id, seg_id, fract_along):
            if (
                population_id not in self.pop_ids_vs_seg_ids_vs_segs
                or seg_id not in self.pop_ids_vs_seg_ids_vs_segs[population_id]
            ):
                return "soma", 0.5

            if not self.pop_ids_vs_use_segment_groups_for_neuron[population_id]:
                return self.pop_ids_vs_seg_ids_vs_segs[population_id][
                    seg_id
                ].name, fract_along
            else:
                fract_sec = -1
                for sec in list(self.pop_ids_vs_ordered_segs[population_id].keys()):
                    ind = 0
                    for seg in self.pop_ids_vs_ordered_segs[population_id][sec]:
                        if seg.id == seg_id:
                            nrn_sec = sec
                            if (
                                len(self.pop_ids_vs_ordered_segs[population_id][sec])
                                == 1
                            ):
                                fract_sec = fract_along
                            else:
                                lens = self.pop_ids_vs_cumulative_lengths[
                                    population_id
                                ][sec]
                                to_start = 0.0 if ind == 0 else lens[ind - 1]
                                to_end = lens[ind]
                                tot = lens[-1]
                                # print to_start, to_end, tot, ind, seg, seg_id
                                fract_sec = (
                                    to_start + fract_along * (to_end - to_start)
                                ) / (tot)

                        ind += 1
                logger.debug(
                    "=============  Converted %s:%s on pop %s to %s on %s"
                    % (seg_id, fract_along, population_id, nrn_sec, fract_sec)
                )
                return nrn_sec, fract_sec

        @override
        def handle_location(self, id, population_id, component, x, y, z):
            DefaultNetworkHandler.print_location_information(
                self, id, population_id, component, x, y, z
            )

            cellsList = self.popParams[population_id]["cellsList"]

            cellsList.append(
                {
                    "cellLabel": id,
                    "x": x if x else 0,
                    "y": y if y else 0,
                    "z": z if z else 0,
                }
            )
            self.gids[population_id][id] = self.next_gid
            self.next_gid += 1

        @override
        def handle_projection(
            self,
            projName,
            prePop,
            postPop,
            synapse,
            hasWeights=False,
            hasDelays=False,
            type="projection",
            synapse_obj=None,
            pre_synapse_obj=None,
        ):
            if self.verbose:
                print(
                    "A projection: %s (%s) from %s -> %s with syn: %s"
                    % (projName, type, prePop, postPop, synapse)
                )
            self.projection_infos[projName] = (projName, prePop, postPop, synapse, type)
            self.connections[projName] = []

        @override
        def handle_connection(
            self,
            projName,
            id,
            prePop,
            postPop,
            synapseType,
            preCellId,
            postCellId,
            preSegId=0,
            preFract=0.5,
            postSegId=0,
            postFract=0.5,
            delay=0,
            weight=1,
        ):
            pre_seg_name, pre_fract = self._convert_to_nrn_section_location(
                prePop, preSegId, preFract
            )
            post_seg_name, post_fract = self._convert_to_nrn_section_location(
                postPop, postSegId, postFract
            )

            # self.log.debug("A connection "+str(id)+" of: "+projName+": "+prePop+"["+str(preCellId)+"]."+pre_seg_name+"("+str(pre_fract)+")" \
            #                      +" -> "+postPop+"["+str(postCellId)+"]."+post_seg_name+"("+str(post_fract)+")"+", syn: "+ str(synapseType) \
            #                      +", weight: "+str(weight)+", delay: "+str(delay))

            self.connections[projName].append(
                (
                    self.gids[prePop][preCellId],
                    pre_seg_name,
                    pre_fract,
                    self.gids[postPop][postCellId],
                    post_seg_name,
                    post_fract,
                    delay,
                    weight,
                )
            )

        @override
        def handle_input_list(
            self, inputListId, population_id, component, size, input_comp_obj=None
        ):
            DefaultNetworkHandler.print_input_information(
                self, inputListId, population_id, component, size
            )

            import neuroml

            format = "NeuroML2"

            # TODO Make better check for stoch/poisson/noisy inputs!
            if (
                isinstance(input_comp_obj, neuroml.PoissonFiringSynapse)
                or isinstance(input_comp_obj, neuroml.TransientPoissonFiringSynapse)
                or "noisy" in component.lower()
                or "poisson" in component.lower()
            ):
                format = "NeuroML2_stochastic_input"

            self.popStimSources[inputListId] = {
                "label": inputListId,
                "type": component,
                "originalFormat": format,
            }
            self.popStimLists[inputListId] = {
                "source": inputListId,
                "conds": {"pop": population_id},
            }

            if component == "IClamp":
                print(
                    "\n\n*****************************\nReconsider calling your input 'IClamp' in NeuroML; it leads to some errors due to clash with native NEURON IClamp!\n*****************************\n\n"
                )
                exit()

            # TODO: build just one stimLists/stimSources entry for the inputList
            # Issue: how to specify the sec/loc per individual stim??
            """
            self.stimSources[inputListId] = {'label': inputListId, 'type': component}
            self.stimLists[inputListId] = {
                        'source': inputListId,
                        'sec':'soma',
                        'loc': 0.5,
                        'conds': {'pop':population_id, 'cellList': []}}"""

        @override
        def handle_single_input(
            self, inputListId, id, cellId, segId=0, fract=0.5, weight=1.0
        ):
            pop_id = self.popStimLists[inputListId]["conds"]["pop"]
            nrn_sec, nrn_fract = self._convert_to_nrn_section_location(
                pop_id, segId, fract
            )

            # seg_name = self.pop_ids_vs_seg_ids_vs_segs[pop_id][segId].name if self.pop_ids_vs_seg_ids_vs_segs.has_key(pop_id) else 'soma'

            stimId = "%s_%s_%s_%s_%s_%s" % (
                inputListId,
                id,
                pop_id,
                cellId,
                nrn_sec,
                (str(fract)).replace(".", "_"),
            )

            self.stimSources[stimId] = {
                "label": stimId,
                "type": self.popStimSources[inputListId]["type"],
                "originalFormat": self.popStimSources[inputListId]["originalFormat"],
            }
            if (
                self.popStimSources[inputListId]["originalFormat"]
                == "NeuroML2_stochastic_input"
            ):
                # self.stimSources[stimId]['stim_count'] = self.stochastic_input_count
                self.stochastic_input_count += 1

            self.stimLists[stimId] = {
                "source": stimId,
                "sec": nrn_sec,
                "loc": nrn_fract,
                "conds": {"pop": pop_id, "cellList": [cellId]},
            }

            if weight != 1:
                self.stimLists[stimId]["weight"] = weight

            if self.verbose:
                print(
                    "Input: %s[%s] on %s, cellId: %i, seg: %i (nrn: %s), fract: %f (nrn: %f); ref: %s; weight: %s"
                    % (
                        inputListId,
                        id,
                        pop_id,
                        cellId,
                        segId,
                        nrn_sec,
                        fract,
                        nrn_fract,
                        stimId,
                        weight,
                    )
                )

            # TODO: build just one stimLists/stimSources entry for the inputList
            # Issue: how to specify the sec/loc per individual stim??
            # self.stimLists[inputListId]['conds']['cellList'].append(cellId)
            # self.stimLists[inputListId]['conds']['secList'].append(seg_name)
            # self.stimLists[inputListId]['conds']['locList'].append(fract)

    ###############################################################################
    # Import network from NeuroML2
    ###############################################################################
    def importNeuroML2(
        fileName, simConfig, simulate=True, analyze=True, return_net_params_also=False
    ):
        """
        Import network from NeuroML2 and convert internally to NetPyNE format

        Parameters
        ----------
        fileName : str
            The filename of the NeuroML file
            **Default:** ``Required``

        simConfig : ``simConfig object``
            NetPyNE simConfig object specifying simulation configuration.
            **Default:** ``Required``

        simulate : bool
            Go ahead and run a simulation of it already
            **Default:** ``True``

        analyze : bool
            Run sim.saveData() and sim.analysis.plotData()
            **Default:** ``True``

        """

        from .. import sim

        netParams = specs.NetParams()

        logger.info("Importing NeuroML 2 network from: %s" % fileName)

        nmlHandler = None

        if fileName.endswith(".nml"):
            from neuroml.hdf5.NeuroMLXMLParser import NeuroMLXMLParser

            nmlHandler = NetPyNEBuilder(netParams, simConfig=simConfig)

            currParser = NeuroMLXMLParser(
                nmlHandler
            )  # The XML handler knows of the structure of NeuroML and calls appropriate functions in NetworkHandler

            currParser.parse(fileName)

            nmlHandler.finalise()

            logger.debug(
                "Finished import of NeuroML2; populations vs gids NML has calculated: "
            )
            for pop in nmlHandler.gids:
                g = nmlHandler.gids[pop]
                logger.debug(
                    "   %s: %s"
                    % (
                        pop,
                        g
                        if len(g) < 10
                        else str(g[:8]).replace("]", ", ..., %s]" % g[-1]),
                    )
                )
            # print('Connections: %s'%nmlHandler.connections)

        if fileName.endswith(".h5"):
            from neuroml.hdf5.NeuroMLHdf5Parser import NeuroMLHdf5Parser

            nmlHandler = NetPyNEBuilder(netParams, simConfig=simConfig)

            currParser = NeuroMLHdf5Parser(
                nmlHandler
            )  # The HDF5 handler knows of the structure of NeuroML and calls appropriate functions in NetworkHandler

            currParser.parse(fileName)

            nmlHandler.finalise()

            logger.info("Finished import: %s" % nmlHandler.gids)
            # print('Connections: %s'%nmlHandler.connections)

        sim.initialize(
            netParams, simConfig
        )  # create network object and set cfg and net params

        # pp.pprint(netParams)
        # pp.pprint(simConfig)
        sim.net.createPops()
        cells = (
            sim.net.createCells()
        )  # instantiate network cells based on defined populations

        # Check gids equal....
        for popLabel, pop in sim.net.pops.items():
            if sim.cfg.verbose:
                logger.debug("gid: %s: %s, %s" % (popLabel, pop, pop.cellGids))
            for gid in pop.cellGids:
                assert gid in nmlHandler.gids[popLabel]

        for proj_id in list(nmlHandler.projection_infos.keys()):
            projName, prePop, postPop, synapse, ptype = nmlHandler.projection_infos[
                proj_id
            ]
            if sim.cfg.verbose:
                logger.debug(
                    "Creating connections for %s (%s): %s->%s via %s"
                    % (projName, ptype, prePop, postPop, synapse)
                )

            """

            No longer used in connections, defined in section on cell...

            from neuroml import Cell
            preComp = nmlHandler.pop_ids_vs_components[prePop]

            if isinstance(preComp,Cell):
                if len(preComp.biophysical_properties.membrane_properties.spike_threshes)>0:
                    st = preComp.biophysical_properties.membrane_properties.spike_threshes[0]
                    # Ensure threshold is same everywhere on cell
                    assert(st.segment_groups=='all')
                    assert(len(preComp.biophysical_properties.membrane_properties.spike_threshes)==1)
                    threshold = pynml.convert_to_units(st.value,'mV')
                else:
                    threshold = 0
            elif hasattr(preComp,'thresh'):
                threshold = pynml.convert_to_units(preComp.thresh,'mV')
            elif hasattr(preComp,'v_thresh'):
                threshold = float(preComp.v_thresh) # PyNN cells...
            else:
                threshold = 0.0"""

            for conn in nmlHandler.connections[projName]:
                (
                    pre_id,
                    pre_seg,
                    pre_fract,
                    post_id,
                    post_seg,
                    post_fract,
                    delay,
                    weight,
                ) = conn

                # connParam = {'delay':delay,'weight':weight,'synsPerConn':1, 'sec':post_seg, 'loc':post_fract, 'threshold':threshold}
                connParam = {
                    "delay": delay,
                    "weight": weight,
                    "synsPerConn": 1,
                    "sec": post_seg,
                    "loc": post_fract,
                }

                if ptype == "electricalProjection":
                    if weight != 1:
                        raise Exception("Cannot yet support inputs where weight !=1!")
                    connParam = {
                        "synsPerConn": 1,
                        "sec": post_seg,
                        "loc": post_fract,
                        "gapJunction": True,
                        "weight": weight,
                    }
                else:
                    connParam = {
                        "delay": delay,
                        "weight": weight,
                        "synsPerConn": 1,
                        "sec": post_seg,
                        "loc": post_fract,
                    }
                    # 'threshold': threshold}

                connParam["synMech"] = synapse

                if (
                    post_id in sim.net.gid2lid
                ):  # check if postsyn is in this node's list of gids
                    sim.net._addCellConn(connParam, pre_id, post_id, preCellsTags={})

        # add gap junctions of presynaptic cells (need to do separately because could be in different ranks)
        for preGapParams in getattr(sim.net, "preCellPointerConns", []):
            if preGapParams["gid"] in sim.net.gid2lid:  # only cells in this rank
                cell = sim.net.cells[sim.net.gid2lid[preGapParams["gid"]]]
                cell.addConn(preGapParams)

        logger.info(
            "  Number of connections on node %i: %i "
            % (sim.rank, sum([len(cell.conns) for cell in sim.net.cells]))
        )

        # conns = sim.net.connectCells()                # create connections between cells based on params
        stims = sim.net.addStims()  # add external stimulation to cells (IClamps etc)
        simData = (
            sim.setupRecording()
        )  # setup variables to record for each cell (spikes, V traces, etc)

        if simulate:
            sim.runSim()  # run parallel Neuron simulation
            sim.gatherData()  # gather spiking data and cell info from each node

        if analyze:
            sim.saveData()  # save params, cell info and sim output to file (pickle,mat,txt,etc)
            sim.analysis.plotData()  # plot spike raster
            """
            h('forall psection()')
            h('forall  if (ismembrane("na_ion")) { print "Na ions: ", secname(), ": ena: ", ena, ", nai: ", nai, ", nao: ", nao } ')
            h('forall  if (ismembrane("k_ion")) { print "K ions: ", secname(), ": ek: ", ek, ", ki: ", ki, ", ko: ", ko } ')
            h('forall  if (ismembrane("ca_ion")) { print "Ca ions: ", secname(), ": eca: ", eca, ", cai: ", cai, ", cao: ", cao } ')"""

        if return_net_params_also:
            return nmlHandler.gids, netParams
        else:
            return nmlHandler.gids

except ImportError:
    logger.critical("Could not import neuroml.DefaultNetworkHandler. Exiting")
