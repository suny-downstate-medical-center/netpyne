#include <stdio.h>
#include "hocdec.h"
#define IMPORT extern __declspec(dllimport)
IMPORT int nrnmpi_myid, nrn_nobanner_;

extern void _izhi2007b_reg();
extern void _nsloc_reg();
extern void _stdp_reg();

modl_reg(){
	//nrn_mswindll_stdio(stdin, stdout, stderr);
    if (!nrn_nobanner_) if (nrnmpi_myid < 1) {
	fprintf(stderr, "Additional mechanisms from files\n");

fprintf(stderr," izhi2007b.mod");
fprintf(stderr," nsloc.mod");
fprintf(stderr," stdp.mod");
fprintf(stderr, "\n");
    }
_izhi2007b_reg();
_nsloc_reg();
_stdp_reg();
}
