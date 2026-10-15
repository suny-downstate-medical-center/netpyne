"""
Jaxley synapse models used by the experimental NetPyNE Jaxley backend.

Jaxley 0.13 ships IonotropicSynapse (graded, voltage-dependent), Tanh* synapses,
and TestSynapse. An AlphaSynapse / Exp2Syn-like dual-exponential synapse exists
in newer Jaxley betas but is not on PyPI yet — so ``Exp2Synapse`` is provided
here for reference / future wiring. The active path currently uses
``IonotropicSynapse`` only (see ``makeJaxleySynapse``).
"""

from typing import Dict, Optional

import jax.numpy as jnp

from jaxley.solver_gate import exponential_euler, save_exp
from jaxley.synapses.synapse import Synapse


class Exp2Synapse(Synapse):
    """Dual-exponential conductance synapse (NEURON Exp2Syn / Jaxley AlphaSynapse).

    Driven by rising-edge spike detection on the presynaptic voltage (works for
    binary NetStim clamps and for biophysical spikes that cross ``v_th``).

    Kinetics (impulse response of ``s``)::

        s(t) ∝ exp(-t/tau2) - exp(-t/tau1)

    Current::

        I = gS * factor * s * (V_post - e_syn)

    where ``factor`` normalizes the peak of the dual-exp kernel to 1 (NEURON Exp2Syn).
    """

    def __init__(self, name: Optional[str] = None):
        super().__init__(name)
        prefix = self._name
        self.synapse_params = {
            f'{prefix}_gS': 1e-4,  # uS (peak conductance after factor)
            f'{prefix}_e_syn': 0.0,  # mV
            f'{prefix}_tau1': 0.1,  # ms rise
            f'{prefix}_tau2': 1.0,  # ms decay
            f'{prefix}_v_th': 0.0,  # mV spike detection threshold
        }
        self.synapse_states = {
            f'{prefix}_r': 0.0,
            f'{prefix}_s': 0.0,
            f'{prefix}_last_v': -70.0,
        }

    @staticmethod
    def _peak_factor(tau1, tau2):
        """NEURON Exp2Syn peak-normalization factor."""
        tau1 = jnp.minimum(tau1, 0.9999 * tau2)
        tp = (tau1 * tau2) / (tau2 - tau1) * jnp.log(tau2 / tau1)
        return 1.0 / (-save_exp(-tp / tau1) + save_exp(-tp / tau2))

    def update_states(
        self,
        states: Dict,
        delta_t: float,
        pre_voltage: float,
        post_voltage: float,
        params: Dict,
    ) -> Dict:
        prefix = self._name
        r = states[f'{prefix}_r']
        s = states[f'{prefix}_s']
        last_v = states[f'{prefix}_last_v']
        tau1 = params[f'{prefix}_tau1']
        tau2 = params[f'{prefix}_tau2']
        v_th = params[f'{prefix}_v_th']

        spiked = (pre_voltage >= v_th) & (last_v < v_th)
        r_inf = jnp.where(spiked, 1.0 / delta_t, 0.0)
        r_new = exponential_euler(r, delta_t, r_inf, tau1)
        s_new = exponential_euler(s, delta_t, r, tau2)

        return {
            f'{prefix}_r': r_new,
            f'{prefix}_s': s_new,
            f'{prefix}_last_v': pre_voltage,
        }

    def compute_current(
        self, states: Dict, pre_voltage: float, post_voltage: float, params: Dict
    ) -> float:
        prefix = self._name
        factor = self._peak_factor(params[f'{prefix}_tau1'], params[f'{prefix}_tau2'])
        g_syn = params[f'{prefix}_gS'] * factor * states[f'{prefix}_s']
        return g_syn * (post_voltage - params[f'{prefix}_e_syn'])


def makeJaxleySynapse(syn_mech, name=None, v_th=None, use_exp2=False):
    """
    Build a Jaxley synapse from a NetPyNE ``synMechParams`` entry.

    Currently always returns ``IonotropicSynapse``. ``Exp2Synapse`` is kept in this
    module for study / future use; pass ``use_exp2=True`` (and ``mod`` in
    ``Exp2Syn`` / ``AlphaSynapse`` / ``ExpSyn``) to opt in.
    """
    from jaxley.synapses import IonotropicSynapse

    syn_mech = syn_mech or {}
    mod = str(syn_mech.get('mod', '') or '')
    if use_exp2 and mod in ('Exp2Syn', 'AlphaSynapse', 'ExpSyn'):
        return Exp2Synapse(name=name), 'exp2'
    return IonotropicSynapse(name=name), 'ionotropic'


def applyJaxleySynapseParams(net, syn_name, kind, weight, e_syn, syn_mech=None, v_th=None):
    """Set conductance / kinetics on a named synapse after ``connect``."""
    syn_mech = syn_mech or {}
    net.set(f'{syn_name}_gS', float(weight))
    net.set(f'{syn_name}_e_syn', float(e_syn))
    if kind == 'exp2':
        tau1 = float(syn_mech.get('tau1', syn_mech.get('tau', 0.1)))
        tau2 = float(syn_mech.get('tau2', 1.0))
        if tau2 <= tau1:
            tau2 = tau1 * 1.01
        net.set(f'{syn_name}_tau1', tau1)
        net.set(f'{syn_name}_tau2', tau2)
        if v_th is not None:
            net.set(f'{syn_name}_v_th', float(v_th))
        try:
            net.set(f'{syn_name}_r', 0.0)
            net.set(f'{syn_name}_s', 0.0)
        except Exception:
            pass
    else:
        try:
            net.set(f'{syn_name}_s', 0.0)
        except Exception:
            pass
