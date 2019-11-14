COMMENT
/**
 * @file VecStim.mod
 * @brief
 * @author king
 * @date 2011-03-16
 * @remark Copyright © BBP/EPFL 2005-2011; All rights reserved. Do not distribute without further notice.
 */
ENDCOMMENT


: Vector stream of events
NEURON {
    THREADSAFE
    ARTIFICIAL_CELL VecStim
    RANGE ping, index, etime
}

PARAMETER {
    ping = 1 (ms)
}

ASSIGNED {
    index
    etime (ms)
    space
}

INITIAL {
VERBATIM
 #ifndef CORENEURON_BUILD
ENDVERBATIM
    index = 0
    element()
    if (index > 0) {
        net_send(etime - t, 1)
    }
    if (ping > 0) {
        net_send(ping, 2)
    }
VERBATIM
 #endif
ENDVERBATIM
}

NET_RECEIVE (w) {
    if (flag == 1) {
        net_event(t)
        element()
        if (index > 0) {
            if (etime < t) {
                printf("Warning in VecStim: spike time (%g ms) before current time (%g ms)\n",etime,t)
            } else {
                net_send(etime - t, 1)
            }
        }
    } else if (flag == 2) { : ping - reset index to 0
        :printf("flag=2, etime=%g, t=%g, ping=%g, index=%g\n",etime,t,ping,index)
        if (index == -2) { : play() has been called
            printf("Detected new vector\n")
            index = 0
            : the following loop ensures that if the vector
            : contains spiketimes earlier than the current
            : time, they are ignored.
            while (etime < t && index >= 0) {
                element()
                : printf("element(): index=%g, etime=%g, t=%g\n",index,etime,t)
            }
            if (index > 0) {
                net_send(etime - t, 1)
            }
        }
        net_send(ping, 2)
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
                } else {
                    index = -1.;
                }
            } else {
                index = -1.;
            }
        }
    }
ENDVERBATIM
}

PROCEDURE play() {
VERBATIM
    #ifndef CORENEURON_BUILD
    void** vv;
    vv = (void**)(&space);
    *vv = (void*)0;
    if (ifarg(1)) {
        *vv = vector_arg(1);
    }
    index = -2;
    #endif
ENDVERBATIM
}

