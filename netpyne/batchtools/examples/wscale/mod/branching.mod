COMMENT

ENDCOMMENT

NEURON { SUFFIX nothing }

VERBATIM

ENDVERBATIM
PROCEDURE init_files(){
	VERBATIM {
		
		
	}
	ENDVERBATIM
}





FUNCTION GetA(x) {
VERBATIM {
#if defined(t)
	NrnThread* _nt = nrn_threads;
#endif
Section* sec;
	Node* nd;
	sec = chk_access();
	if (_lx < 0. || _lx > 1.) {
	//printf("_lx is %f and _lx*(double)(sec->nnode-1) is %f\n",_lx,_lx*(double)(sec->nnode-1));
		hoc_execerror("out of range, must be 0 < x <= 1", (char*)0);
	}
	if (_lx == 1.) {
		nd = sec->pnode[sec->nnode-1];
	}else{
		nd = sec->pnode[(int) (_lx*(double)(sec->nnode-1))];
	}
	return NODEA(nd);
}
ENDVERBATIM
}
FUNCTION GetB(x) {
VERBATIM {
#if defined(t)
	NrnThread* _nt = nrn_threads;
#endif
Section* sec;
	Node* nd;
	sec = chk_access();
	if (_lx < 0. || _lx > 1.) {
		//printf("_lx is %f and _lx*(double)(sec->nnode-1) is %f\n",_lx,_lx*(double)(sec->nnode-1));
		hoc_execerror("out of range, must be 0 < x <= 1", (char*)0);
	}
	if (_lx == 1.) {
		nd = sec->pnode[sec->nnode-1];
	}else{
		nd = sec->pnode[(int) (_lx*(double)(sec->nnode-1))];
	}
	return NODEB(nd);
}
ENDVERBATIM
}
FUNCTION SetA(x,a) {
VERBATIM {
#if defined(t)
	NrnThread* _nt = nrn_threads;
#endif
Section* sec;
	Node* nd;
	sec = chk_access();
	if (_lx < 0. || _lx > 1.) {
		hoc_execerror("out of range, must be 0 < x <= 1", (char*)0);
	}
	if (_lx == 1.) {
		nd = sec->pnode[sec->nnode-1];
	}else{
		nd = sec->pnode[(int) (_lx*(double)(sec->nnode-1))];
	}
	//printf("index is %d,NODEA(nd) is %f _la is %f\n",nd->v_node_index,NODEA(nd),_la);
	NODEA(nd) = _la;
}
ENDVERBATIM
}
FUNCTION SetB(x,b) {
VERBATIM {
#if defined(t)
	NrnThread* _nt = nrn_threads;
#endif
Section* sec;
	Node* nd;
	sec = chk_access();
	if (_lx < 0. || _lx > 1.) {
		hoc_execerror("out of range, must be 0 < x <= 1", (char*)0);
	}
	if (_lx == 1.) {
		nd = sec->pnode[sec->nnode-1];
	}else{
		nd = sec->pnode[(int) (_lx*(double)(sec->nnode-1))];
	}
	//printf("index is %d,NODEB(nd) is %f _lb is %f\n",nd->v_node_index,NODEB(nd),_lb);
	NODEB(nd) = _lb;
}
ENDVERBATIM
}

PROCEDURE MyPrintMatrix() {
VERBATIM {
	Section* sec;
	FILE* fm;
	fm= fopen("C:\fmatrix.dat", "wb");
	Node* nd;
	int ii;
#if defined(t)
	NrnThread* _nt = nrn_threads;
#endif
for(ii=0;ii<_nt->end;ii++){
nd=_nt->_v_node[ii];
fprintf(fm,"%d %1.15f %1.15f %1.15f %1.15f\n", ii, NODEB(nd), NODEA(nd), NODED(nd), NODERHS(nd));
}
fclose(fm);
}
ENDVERBATIM
}
PROCEDURE MyAdb() {
VERBATIM {
	int ii;
#if defined(t)
	NrnThread* _nt = nrn_threads;
#endif
for(ii=0;ii<_nt->end;ii++){

printf("%d,%1.15f %1.15f %1.15f %1.15f\n",ii, _nt->_actual_a[ii],_nt->_actual_d[ii],_nt->_actual_b[ii],_nt->_actual_rhs[ii]);
}
}
ENDVERBATIM
}

PROCEDURE PrintRHS_D() {
VERBATIM {
	int ii;
#if defined(t)
	NrnThread* _nt = nrn_threads;
#endif
Node* nd;
for(ii=0;ii<_nt->end;ii++){
nd=_nt->_v_node[ii];
printf("%d,%1.15f %1.15f \n",ii,  NODED(nd), NODERHS(nd));
}
}
ENDVERBATIM
}

PROCEDURE MyTopology() {
VERBATIM {
	int ii;
#if defined(t)
	NrnThread* _nt = nrn_threads;
#endif
for(ii=0;ii<_nt->end;ii++){

printf("%d %d\n", ii, _nt->_v_parent_index[ii]);
}
}
ENDVERBATIM
}

PROCEDURE MyTopology2() {
VERBATIM {
	FILE * pFile;
	int ii;
#if defined(t)
	NrnThread* _nt = nrn_threads;
#endif
pFile = fopen ("parent.txt","w");
for(ii=0;ii<_nt->end;ii++){

fprintf(pFile,"%d ", _nt->_v_parent_index[ii]);
}
fclose (pFile);
}
ENDVERBATIM
}

PROCEDURE MyTopology1() {
VERBATIM {
	FILE * pFile;
	int ii;
#if defined(t)
	NrnThread* _nt = nrn_threads;
#endif
pFile = fopen ("64TL.csv","w");
for(ii=0;ii<_nt->end;ii++){

fprintf(pFile,"%d %d\n", ii, _nt->_v_parent_index[ii]);
}
fclose (pFile);
}
ENDVERBATIM
}

PROCEDURE MyPrintMatrix1() {
VERBATIM {
	Section* sec;
	FILE* fm;
	fm= fopen("64TL.csv", "w");
	Node* nd;
	int ii;
#if defined(t)
	NrnThread* _nt = nrn_threads;
#endif
for(ii=0;ii<_nt->end;ii++){
nd=_nt->_v_node[ii];
fprintf(fm,"%d %1.15f %1.15f %1.15f %1.15f\n", ii, NODEB(nd), NODEA(nd), NODED(nd), NODERHS(nd));
}
fclose (fm);
}
ENDVERBATIM
}

PROCEDURE MyPrintMatrix3() {
VERBATIM {
	Section* sec;
	FILE* fm;
	fm= fopen("Fmatrix.csv", "w");
	Node* nd;
	int ii;
#if defined(t)
	NrnThread* _nt = nrn_threads;
#endif
for(ii=0;ii<_nt->end;ii++){
nd=_nt->_v_node[ii];
fprintf(fm,"%d %1.15f %1.15f %1.15f %1.15f\n", ii, NODEB(nd), NODEA(nd), NODED(nd), NODERHS(nd));
}
fclose (fm);
}
ENDVERBATIM
}