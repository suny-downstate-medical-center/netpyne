: $Id: vecstim.mod,v 1.3 2010/12/13 21:29:27 samn Exp $ 
:  Vector stream of events

NEURON {
  THREADSAFE
       ARTIFICIAL_CELL VecStim 
}

ASSIGNED {
	index
	etime (ms)
	space
}

INITIAL {
	index = 0
	element()
	if (index > 0) {
		if (etime - t>=0) {
			net_send(etime - t, 1)
		} else {
			printf("Event in the stimulus vector at time %g is omitted since has value less than t=%g!\n", etime, t)
			net_send(0, 2)
		}
	}
}

NET_RECEIVE (w) {
	if (flag == 1) { net_event(t) }
	if (flag == 1 || flag == 2) {
		element()
		if (index > 0) {	
			if (etime - t>=0) {
				net_send(etime - t, 1)
			} else {
				printf("Event in the stimulus vector at time %g is omitted since has value less than t=%g!\n", etime, t)
				net_send(0, 2)
			}
		}
	}
}

VERBATIM
extern double* vector_vec();
extern int vector_capacity();
extern void* vector_arg();
ENDVERBATIM

PROCEDURE element() {
VERBATIM	
  { void* vv; int i, size; double* px;
	i = (int)index;
	if (i >= 0) {
		vv = *((void**)(&space));
		if (vv) {
			size = vector_capacity(vv);
			px = vector_vec(vv);
			if (i < size) {
				etime = px[i];
				index += 1.;
			}else{
				index = -1.;
			}
		}else{
			index = -1.;
		}
	}
  }
ENDVERBATIM
}

PROCEDURE play() {
VERBATIM
	void** vv;
	vv = (void**)(&space);
	*vv = (void*)0;
	if (ifarg(1)) {
		*vv = vector_arg(1);
	}
ENDVERBATIM
}
        

