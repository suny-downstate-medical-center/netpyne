: $Id: vecst.mod,v 1.499 2011/07/22 22:16:48 billl Exp $
 
:* COMMENT
COMMENT
thresh   turns analog vec to BVBASE,1 vec separating at thresh (scalar or vec)
triplet  return location of a triplet in a vector
onoff    turns state vec on or off depending on values in other vecs
bpeval   used by backprop: vo=outp*(1-outp)*del
w        like where but sets chosen nums // modified from .wh in 1.23
whi      find indices where vec equal to given values
dest.xing(src,tvec,thresh) determines where vector crosses in a positive direction 
dest.snap(src,tvec,dt) interpolate src with tvec to prior dt step, saves only highest value
xzero    count 0 crossings by putting in a 1 or -1
negwrap  wrap negative values around to pos (with flag just set to 0)
indset(ind,val) sets spots indexed by ind to val
ismono([arg]) checks if a vector is monotonically increaseing (-1 decreasing)
count(num) count the number of nums in vec
muladd(mul,add) mul*x+add
binfind(num) find index for num in a sorted vector
scr.fewind(ind,veclist) // uses ind as index into other vecs
ind.findx(vecAlist,vecBlist) // uses ind as index into vecA's to load in vecB's
ind.sindx(vecAlist,vecBlist) // replace ind elements in vecA's with vecB's values
ind.sindv(vecAlist,valvec) // replace ind elements in vecA's with vals
scr.nind(ind,vec1,vec2[,vec3,vec4]) // uses ind to elim elems in other vecs
yv.circ(xv,x0,y0,rad) // put coords of circle into xv and yv
ind.keyind(key,vec1,vec2[,vec3,vec4]) // pick out bzw. values from vectors
ind.slct(key,args,veclist) // pick out bzw. values from vectors
ind.slor(key,args,veclist) // do OR rather than AND function of slct
vdest.intrp(flag) // interpolate numbers replacing numbers given as flag
v.insct(v1,v2)   // return v1 intersect v2
vdest.cull(vsrc,key)   // remove values found in key
vdest.redundout(vsrc[,INDFLAG])  // remove repeat values, with flag return indices
ind.mredundout(veclistA[,INDFLAG,veclistB]) // remove repeats from parallel vectors
v.cvlv(v1,v2)   // convolve v1 with v2
v2d      copy into a double block
d2v      copy out of a double block NB: same as vec.from_double()
smgs     rewrite of sumgauss form ivovect.cpp
smsy     sum syn potentials off a tvec
iwr      write integers
ird      read integers
ident     give pointer addresses and sizes
lcat     concatentate all vectors from a list
fread2   like vec.fread but uses flag==6 for unsigned int
vfill    fill vdest with multiple instances of vsrc until reach size
inv    return inverse of number multiplied by optional num
slone(src,val) select indices where ==VAL from sorted vector SRC
piva.join(pivb,veclista,veclistb) copies values from one set of vecs to other
Non-vector routines
isojt    compare 2 objects to see if they're of the same type
eqojt    compare 2 object pointers to see if they point to same thing
sumabs   return sum of absolute values
rnd    round off to nearest integer
ENDCOMMENT

NEURON {
  SUFFIX nothing
  : BVBASE is bit vector base number (typically 0 or -1)
  GLOBAL BVBASE, RES, VECST_INSTALLED, DEBUG_VECST, VERBOSE_VECST, INTERP_VECST, LOOSE
}

PARAMETER {
  BVBASE = 0.
  VECST_INSTALLED=0
  DEBUG_VECST=0
  VERBOSE_VECST=1
  INTERP_VECST=1 : interpolation
  LOOSE=1e-6
  : code words
  ERR= -1.3480e121
  GET= -1.3479e121
  SET= -1.3478e121
  OK=  -1.3477e121
  NOP= -1.3476e121

  : 0 args
  ALL=-1.3479e120
  NEG=-1.3478e120
  POS=-1.3477e120
  CHK=-1.3476e120
  NOZ=-1.3475e120
  : 1 arg
  GTH=-1.3474e120
  GTE=-1.3473e120
  LTH=-1.3472e120
  LTE=-1.3471e120
  EQU=-1.3470e120
  EQV=-1.3469e120 : value equal to same row value in parallel vector
  EQW=-1.3468e120 : value found in other vector
  EQX=-1.3467e120 : value found in sorted vector
  EQY=-1.34665e120 : value found in sorted vector -- within LOOSE
  NEQ=-1.3466e120
  SEQ=-1.3465e120
  RXP=-1.3464e120
  : 2 args  
  IBE=-1.3463e120
  EBI=-1.3462e120
  IBI=-1.3461e120
  EBE=-1.3460e120
}

ASSIGNED { RES }

VERBATIM
#include "misc.h"
ENDVERBATIM

VERBATIM
// Maintain parallel int vector to avoid slowness of repeated casts 
int cmpdfn (double a, double b) {return ((a)<=(b))?(((a) == (b))?0:-1):1;}
static unsigned int bufsz=0;
unsigned int scrsz=0;
unsigned int *scr=0x0;
unsigned int dcrsz=0;
double   *dcr=0x0;

int *iscr=0x0;
unsigned int iscrsz=0;

int *iscrset (int nx) {
  if (nx>iscrsz) { 
    iscrsz=nx+10000;
    if (iscrsz>0) { iscr=(int *)realloc((void*)iscr,(size_t)iscrsz*sizeof(int));
    } else       { iscr=(int *)ecalloc(iscrsz, sizeof(int)); }
  }
  return iscr;
}

unsigned int *scrset (int nx) {
  if (nx>scrsz) { 
    scrsz=nx+10000;
    if (scrsz>0) { scr=(unsigned int *)realloc((void*)scr,(size_t)scrsz*sizeof(int));
    } else       { scr=(unsigned int *)ecalloc(scrsz, sizeof(int)); }
  }
  return scr;
}

double *dcrset (int nx) {
  if (nx>dcrsz) { 
    dcrsz=nx+10000;
    if (dcrsz>0) { dcr=(double*) realloc((void*)dcr,(size_t)dcrsz*sizeof(double)); 
    } else       { dcr=(double*)ecalloc(dcrsz, sizeof(double)); }
  }
  return dcr;
}
ENDVERBATIM

:* v1.ident() gives addresses and sizes
VERBATIM
static double ident (void* vv) {
  int nx,bsz; double* x;
  nx = vector_instance_px(vv, &x);
  bsz=vector_buffer_size(vv);
  printf("Obj*%x Dbl*%x Size: %d Bufsize: %d\n",(unsigned int)vv,(unsigned int)x,nx,bsz);
  return (double)nx;
}
ENDVERBATIM
 
:* v1.indset(ind,x[,y]) sets indexed values to x and other values to optional y
:  v1.indset(ind,vvec[,y]) sets indexed values to vvec values
:  v1.indset(ind,"INC",1) increments values
:  v1.indset(ind,"INC",-1) decrements values
:  v1.indset(v2, "EQU",val,x[,y]) checks if v2 is EQU to val
VERBATIM
static double indset (void* vv) {
  int i, nx, ny, nz, flag, equ; char *op;
  double *x, *y, *z, val, val2, inc;
  nx = vector_instance_px(vv, &x);
  ny = vector_arg_px(1, &y);
  val2=flag=equ=inc=0;
  if (hoc_is_object_arg(2)) { 
    flag=1;
    nz = vector_arg_px(2, &z); 
    if (ny!=nz) z=vector_newsize(vector_arg(2),ny);
  } else if (hoc_is_double_arg(2)) { 
    val=*getarg(2); 
  } else if (hoc_is_str_arg(2)) {
    op = gargstr(2);
    if (strcmp(op,"EQU")==0) equ=1; else if (strcmp(op,"INC")==0) inc=1; else {
      printf("indset %s not recog\n",op); hxe(); }
  }
  if (equ) {
    val2 = *getarg(3); val=*getarg(4);
    for (i=0; i<ny; i++) if (y[i]==val2) x[i]=val;
  } else {
    if (ifarg(3)) { 
      val2 = *getarg(3); 
      if (inc && val2==0) {printf("vecst:indset ERRA inc of 0\n"); hxe();}
      if (inc) inc=val2; else for (i=0; i<nx; i++) { x[i]=val2; } // fill it
    }
    for (i=0; i<ny; i++) {
      if (y[i] > nx) {printf("vecst:inset ERRB Index exceeds vector size %g %d\n",y[i],nx); hxe();}
      if (inc!=0) x[(int)y[i]]+=inc; else if (flag) x[(int)y[i]]=z[i]; else x[(int)y[i]]=val;
    }
  }
  return (double)i;
}
ENDVERBATIM

:* v1.mkind(ind) creates a simple index for starts of a sorted integer vector v1
VERBATIM
static double mkind(void* vv) {
  int i, j, nx, ny, flag;
  double *x, *y, flox, last, min, max;
  nx = vector_instance_px(vv, &x);
  ny = vector_arg_px(1, &y);
  flag=ifarg(2)?(int)*getarg(2):0;
  min=x[0]; max=x[nx-1]; 
  ny=max-min+4+(flag?0:min);
  if (ny>1e6) printf("vecst:mkind() WARNING: index of size %d being built\n",ny);
  y=vector_newsize(vector_arg(1),ny);
  y[0]=0.; y[ny-3]=nx; y[ny-2]=min; y[ny-1]=max; // last 2 record min,max
  if (min==max) {printf("vecst:mkind() ERRA: min==max %g %g\n",min,max); hxe();}
  if (!flag) for (j=1;j<=min;j++) y[j]=0.; else j=1;
  for (i=1,last=floor(min); i<nx; i++) {
    flox=floor(x[i]);
    if (flox==last) continue;
    if (flox<last) {printf("vecst:mkind() ERRB: non-mono vec.x[%d]<x[%d]\n",i,i-1);hxe();}
    for (;flox>=last+1;j++,last++) y[j]=(double)i;
    last=flox;
  }
  return min;
}
ENDVERBATIM

:* yv.circ(xv,x0,y0,rad) sets cartesian x,y coords for circle with center x0,y0; radius rad
VERBATIM
static double circ (void* vv) {
  int i, nx, ny, flag, lnew;
  double *x, *y, x0, y0, x1, y1, rad, theta;
  lnew=0;
  nx = vector_instance_px(vv, &x);
  ny = vector_arg_px(1, &y);
  if (ny!=nx) { hoc_execerror("v.circ: Vector sizes don't match.", 0); }
  x0=*getarg(2); y0=*getarg(3); rad=*getarg(4); 
  if (ifarg(6)) { // gives center and a point on the circle instead of radius
    x1=rad; y1=*getarg(5);
    rad=sqrt((x0-x1)*(x0-x1) + (y0-y1)*(y0-y1));
    lnew=*getarg(6); // resize the vectors
  } else if (ifarg(5)) lnew=*getarg(5); // resize the vectors
  if (lnew) { nx=lnew; x=vector_newsize(vv,nx); y=vector_newsize(vector_arg(1),ny=nx); }
  for (i=0,theta=0; i<nx; theta+=2*M_PI/(nx-1),i++) {
    x[i]=y0+rad*sin(theta); y[i]=x0+rad*cos(theta); 
  }
  return rad;
}
ENDVERBATIM

:* v1.roton(x) rotate 1-10 values onto end of constant-length queue
VERBATIM
static double roton (void* vv) {
	int i, j, nx, nz, flag;
	double *x, *z, val[10];
	nx = vector_instance_px(vv, &x);
        flag=0; 
        if (hoc_is_object_arg(1)) { 
          flag=1; nz = vector_arg_px(1, &z);
        } else { 
          for (i=1;i<=10 && ifarg(i);i++) val[i-1]= *getarg(i);
          nz=i-1;
        }
        if (nz>nx) {printf("v.roton: Can't rotate %d vals on vec of size %d\n",nz,nx); hxe();}
	for (i=nz,j=0; i<nx; i++,j++) x[j]=x[i];
	for (i=nx-nz,j=0; j<nz; i++,j++) x[i]=flag?z[j]:val[j];
	return (double)nz;
}
ENDVERBATIM

:* tmp.fewind(ind,veclist)
: picks out numbers from multiple vectors using index ind
VERBATIM
static double fewind (void* vv) {
  int i, j, k, nx, ni, nv[VRRY], num, flag; 
  Object* ob;
  double *x, *ind, *vvo[VRRY];
  char *ix;
  nx = vector_instance_px(vv, &x);
  ni = vector_arg_px(1, &ind);
  ob = *hoc_objgetarg(2);
  if (ifarg(3)) flag=(int)*getarg(3); else flag=0; // flag==1 for handling non-uniq indices
  num = ivoc_list_count(ob);
  if (num>VRRY) hoc_execerror("ERR: fewind can only handle VRRY vectors", 0);
  if (flag) ix=(char*)ecalloc(nx,sizeof(char));
  if (!flag && nx<ni) {printf("fewind WARNING nx!=ni: %d!=%d, setting nonuniq flag\n",nx,ni);
    flag=1; }
  for (i=0;i<num;i++) { 
    nv[i] = list_vector_px(ob, i, &vvo[i]);
    if (nx!=nv[i]) { printf("fewind ERR %d %d %d\n",i,nx,nv[i]);
      hoc_execerror("Vectors must all be same size: ", 0); }
  }
  if (nx>scrsz) { 
    if (scrsz>0) { free(scr); scr=(unsigned int *)NULL; }
    scrsz=nx+10000;
    scr=(unsigned int *)ecalloc(scrsz, sizeof(int));
  }
  if (flag) {
    for (i=0;i<nx;i++) ix[i]=0;
    for (i=0,k=0;i<ni && k<nx;i++) {
      j=(int)ind[i];
      if (ix[j]==0) {
        if (j>=nx || j<0) { printf("fewind ERR1A %d %d\n",j,nx); free(ix);hxe();}
        scr[k]=j;
        ix[j]=1; // indicate that has already been used
        k++;
      }
    }
    ni=nx; // index up to max
  } else for (i=0;i<ni;i++) { 
    scr[i]=(int)ind[i]; // copy into integer array 
    if (scr[i]>=nx || scr[i]<0) { printf("fewind ERR1 %d %d\n",scr[i],nx);
    hoc_execerror("Index vector out-of-bounds", 0); }
  }
  if (flag) for (i=0;i<ni;i++) if (ix[i]==0) {printf("fewind ERR2 %d\n",i); hxe();}
  for (j=0;j<num;j++) {
    for (i=0;i<ni;i++) x[i]=vvo[j][scr[i]];    
    for (i=0;i<ni;i++) vvo[j][i]=x[i];   
    vvo[j]=list_vector_resize(ob, j, ni);
  }
  if (flag) free(ix);
  return (double)ni;
}
ENDVERBATIM


:* ind.findx(vecAlist,vecBlist) 
: uses ind as index into vecA's to load in vecB's (for select); a nondestructive fewind()
VERBATIM
static double findx (void* vv) {
  int i, j, ni, nx, av[VRRY], bv[VRRY], num;
  Object *ob1, *ob2;
  double *ind, *avo[VRRY], *bvo[VRRY];
  ni = vector_instance_px(vv, &ind);
  ob1 = *hoc_objgetarg(1);
  ob2 = *hoc_objgetarg(2);
  num = ivoc_list_count(ob1);
  i = ivoc_list_count(ob2);
  if (i!=num) hoc_execerror("findx ****ERRA****: lists have different counts", 0);
  if (num>VRRY) hoc_execerror("findx ****ERRB****: can only handle VRRY vectors", 0);
  for (i=0;i<num;i++) { 
    av[i]=list_vector_px(ob1, i, &avo[i]); // source vectors
    if (av[0]!=av[i]) { printf("findx ****ERRC**** %d %d %d\n",i,av[0],av[i]);
      hoc_execerror("Src vectors must all be same size: ", 0); }
  }
  nx=av[0]; // size of source vecs
  for (i=0;i<num;i++) { 
    bv[i]=list_vector_px2(ob2, i, &bvo[i], &vv); // dest vectors 
    if (vector_buffer_size(vv)<ni) { 
      printf("findx ****ERRD**** arg#%d need:%d sz:%d\n",num+i+1,ni,vector_buffer_size(vv));
      hoc_execerror("Destination vector with insufficient size: ", 0); 
    } else {
      vector_resize(vv, ni);
    }
  }
  if (ni>scrsz) { 
    if (scrsz>0) { free(scr); scr=(unsigned int *)NULL; }
    scrsz=ni+10000;
    scr=(unsigned int *)ecalloc(scrsz, sizeof(int));
  }
  for (i=0;i<ni;i++) { scr[i]=(int)ind[i]; // copy into integer array
    if (scr[i]>=nx || scr[i]<0) { printf("findx ****ERRE**** **** IND:%d SZ:%d\n",scr[i],nx);
      hoc_execerror("Index vector out-of-bounds", 0); }
  }
  for (j=0,i=0;j<num;j++) for (i=0;i<ni;i++) bvo[j][i]=avo[j][scr[i]];    
  return (double)ni;
}
ENDVERBATIM

:* ind.lma(vecAlist,vecBlist,beg,end[,mul,add]) 
: copy each vector in Alist to Blist indices from beg to end; with sequential mul/add
: ind picks out specific vectors if not doing all of them
VERBATIM
static double lma (void* vv) {
  int i, j, k, ia, ib, ni, nj, nx, av[VRRY], bv[VRRY], num, numb, beg, end, *xx;
  Object *ob1, *ob2;
  double *ind, *avo[VRRY], *bvo[VRRY], mul,mmul,add,madd;
  ni = vector_instance_px(vv, &ind);
  xx=iscrset(ni);
  ob1 = *hoc_objgetarg(1);    ob2 = *hoc_objgetarg(2);
  beg = (int)*getarg(3);      end= (int)*getarg(4);
  mul=ifarg(5)?*getarg(5):1;  add=ifarg(6)?*getarg(6):0;
  num = ivoc_list_count(ob1);
  numb = ivoc_list_count(ob2);
  if ((ni==0 && numb!=num) || (ni>0 && ni!=num)) {
    printf("lma ERRA: wrong# of outvecs: %d (inlist:%d,inds:%d)\n",numb,num,ni); hxe();}
  for (i=0,j=0;i<ni;i++) { 
    if (ind[i]) xx[j++]=i; // make the index array out of a masking vector
    if (j>num){printf("lma ERRA1 OOB: %d %d\n",j,num); hxe();}
  }
  nj=j;
  if (num>VRRY){printf("lma ****ERRB****: can only handle %d vectors\n",VRRY); hxe();}
  for (i=0;i<num;i++) { 
    av[i]=list_vector_px(ob1, i, &avo[i]); // source vectors
    if (av[0]!=av[i]) { printf("lma ****ERRC**** %d %d %d\n",i,av[0],av[i]);
      hoc_execerror("Src vectors must all be same size: ", 0); }
  }
  nx=av[0]; // size of source vecs
  if (beg>=end || beg<0 || end>nx) {printf("lma ERRC1 OOB %d - %d (%d)\n",beg,end,nx); hxe();}
  for (i=0;i<num;i++) { 
    bv[i]=list_vector_px2(ob2, i, &bvo[i], &vv); // dest vectors 
    if (bv[i]!=(end-beg)) bvo[i]=vector_newsize(vv, end-beg);
  }
  if (nj>0) {
    for (ia=0,ib=0,mmul=1.,madd=0.;ia<nj;ia++,ib++) {
      j=xx[ia];
      for (i=beg,k=0;i<end;i++,k++) bvo[ib][k]=mmul*avo[j][i]+madd;    
      if (mul!=1) mmul*=mul; if (add!=0) madd+=add;
    }
  } else for (j=0,mmul=1,madd=0;j<num;j++) {
    for (i=beg,k=0;i<end;i++,k++) bvo[j][k]=mmul*avo[j][i]+madd;    
    if (mul!=1) mmul*=mul; if (add!=0) madd+=add;
  }
  return (double)j;
}
ENDVERBATIM

:* ind.sindx(vecAlist,vecBlist)
: uses ind as index into vecA's to replace with elements from vecB's
VERBATIM
static double sindx (void* vv) {
  int i, j, ni, nx, av[VRRY], bv[VRRY], num;
  Object *ob1, *ob2;
  double *ind, *avo[VRRY], *bvo[VRRY];
  ni = vector_instance_px(vv, &ind);
  ob1 = *hoc_objgetarg(1);
  ob2 = *hoc_objgetarg(2);
  num = ivoc_list_count(ob1);
  i = ivoc_list_count(ob2);
  if (num!=i) hoc_execerror("sindx ****ERRA****: two vec lists have different counts", 0);
  if (num>VRRY) hoc_execerror("sindx ****ERRB****: can only handle VRRY vectors", 0);
  for (i=0;i<num;i++) { 
    av[i]=list_vector_px(ob1, i, &avo[i]); // dest vectors
    if (av[0]!=av[i]) { printf("sindx ****ERRC**** %d %d %d\n",i,av[0],av[i]);
      hoc_execerror("Dest. vectors must all be same size: ", 0); }
  }
  nx=av[0]; // size of dest vecs
  for (i=0;i<num;i++) { 
    bv[i]=list_vector_px(ob2, i, &bvo[i]); // source vectors 
  if (bv[i]!=ni) { 
    printf("sindx ****ERRD**** arg#%d does note match ind length %d vs %d\n",num+i+1,ni,bv[i]);
    hoc_execerror("Source vector with insufficient size: ", 0); }
  }
  if (ni>scrsz) { 
    if (scrsz>0) { free(scr); scr=(unsigned int *)NULL; }
    scrsz=ni+10000;
    scr=(unsigned int *)ecalloc(scrsz, sizeof(int));
  }
  for (i=0;i<ni;i++) { scr[i]=(int)ind[i]; // copy into integer array
    if (scr[i]>=nx || scr[i]<0) { 
      printf("sindx ****ERRE**** IND:%d SZ:%d\n",scr[i],nx);
      hoc_execerror("Index vector out-of-bounds", 0); }
  }
  for (j=0,i=0;j<num;j++) for (i=0;i<ni;i++) avo[j][scr[i]]=bvo[j][i];
  return (double)ni;
}
ENDVERBATIM

:* ind.sindv(vecAlist,valvec)
: uses ind as index into vecA's to replace with values in valvec
VERBATIM
static double sindv(void* vv) {
  int i, j, ni, nx, av[VRRY], bv, num;
  Object* ob;
  double *ind, *avo[VRRY], *bvo;
  ni = vector_instance_px(vv, &ind);
  ob = *hoc_objgetarg(1);
  bv=vector_arg_px(2, &bvo); // source vector
  num = ivoc_list_count(ob);
  if (num>VRRY) hoc_execerror("sindv ****ERRA****: can only handle VRRY vectors", 0);
  for (i=0;i<num;i++) { 
    av[i]=list_vector_px(ob, i, &avo[i]); // dest vectors
    if (av[0]!=av[i]) { printf("sindv ****ERRC**** %d %d %d\n",i,av[0],av[i]);
      hoc_execerror("Dest. vectors must all be same size: ", 0); }
  }
  nx=av[0]; // size of source vecs
  if (bv!=num) { 
    printf("sindv ****ERRD**** Vector arg does note match list count %d vs %d\n",num,bv);
    hoc_execerror("Source vector is wrong size: ", 0); }
  if (ni>scrsz) { 
    if (scrsz>0) { free(scr); scr=(unsigned int *)NULL; }
    scrsz=ni+10000;
    scr=(unsigned int *)ecalloc(scrsz, sizeof(int));
  }
  for (i=0;i<ni;i++) { scr[i]=(int)ind[i]; // copy into integer array
    if (scr[i]>=nx || scr[i]<0) { 
      printf("sindv ****ERRE**** IND:%d SZ:%d\n",scr[i],nx);
      hoc_execerror("Index vector out-of-bounds", 0); }
  }
  for (j=0,i=0;j<num;j++) for (i=0;i<ni;i++) avo[j][scr[i]]=bvo[j];
  return (double)ni;
}
ENDVERBATIM

:* ind.slct(key,args,veclist)
: picks out indices of numbers in key from multiple vectors
VERBATIM
static double slct (void* vv) {
  int i, j, k, m, n, p, ni, nk, na, nv[VRRY], num, fl, lc, field[VRRY], lt, rt, flag;
  Object* lob;
  double *ind, *key, *arg, *vvo[VRRY], val;

  ni = vector_instance_px(vv, &ind); // vv is ind
  nk = vector_arg_px(1, &key);
  na = vector_arg_px(2, &arg);
  lob = *hoc_objgetarg(3);
  if (ifarg(4)) flag=(int)*getarg(4); else flag=0;// flag==1 to return first found
  num = ivoc_list_count(lob);
  if (num>VRRY) hoc_execerror("ERR: vecst::slct can only handle VRRY vectors", 0);

  for (i=0,j=0;i<num;i++,j++) {     // pick up vectors
    nv[i] = list_vector_px(lob, i, &vvo[i]);
    if (key[j]>=EQV && key[j]<=EQY) { // EQV-EQY take extra vec arg of any size
      i++;
      nv[i] = list_vector_px(lob, i, &vvo[i]);// pick up extra vector of any size
    } else if (ni!=nv[i]) {
      printf("vecst::slct ERR %d %d %d %d %d\n",i,j,k,ni,nv[i]);
      hoc_execerror("index and searched vectors must all be same size: ", 0); 
    }
  }
  for (j=0;j<nk;j++) { // look for fields in a mkcode() coded double
    field[j]=-1;
    if (key[j]<=EBE && key[j]>=ALL) { field[j]=0;
    } else for (m=1;m<=5;m++) {
      if (key[j]<=EBE*(m+1) && key[j]>=ALL*(m+1)) { // m is is field key 1-5
        key[j]/=(m+1);
        field[j]=m;
      }
    }
    if (field[j]==-1) {printf("vecst::slct ERRF %d %g\n",j,key[j]); hxe(); }
  }
  if (2*nk!=na) { printf("vecst::slct ERR3 %d %d\n",nk,na); 
    hoc_execerror("Arg vector must be double key length",0); }
  for (i=0,n=0;i<nk;i++) if (key[i]>=EQV && key[i]<=EQY) n++; // special cases take 2 vec args
  if (nk+n!=num) { 
    printf("vecst::slct ERR2 %d(keys)+%d(EQV/W)!=%d(vecs)\n",nk,n,num); 
    hoc_execerror("Key length must be number of vecs + num of EQV/W",0); }
  for (j=0,k=0,m=0;j<ni;j++) { // j steps through elements of vectors
    for (i=0,m=0,n=0,fl=1;i<num;i++,n++,m+=2) { // i steps thru key, m thru args
      if (field[n]==0) val=vvo[i][j]; else UNCODE(vvo[i][j],field[n],val);
      if (key[n]==ALL) continue; // OK - do nothing
      if (key[n]==NOZ)        { if (val==0.) {fl=0; break;} else continue; 
      } else if (key[n]==POS) { if (val<=0.) {fl=0; break;} else continue; 
      } else if (key[n]==NEG) { if (val>=0.) {fl=0; break;} else continue; 
      } else if (key[n]==GTH) { if (val<=arg[m]) {fl=0; break;} else continue; 
      } else if (key[n]==GTE) { if (val< arg[m]) {fl=0; break;} else continue; 
      } else if (key[n]==LTH) { if (val>=arg[m]) {fl=0; break;} else continue; 
      } else if (key[n]==LTE) { if (val> arg[m]) {fl=0; break;} else continue; 
      } else if (key[n]==EQU) { if (val!=arg[m]) {fl=0; break;} else continue; 
      } else if (key[n]==EQV) { if (val!=vvo[i+1][j]) { 
          fl=0; break;} else { i++; continue; }
      } else if (key[n]==EQW) {  // check value against values in following vec
        fl=0; // assume it's not going to match
        for (p=0;p<nv[i+1];p++) if (val==vvo[i+1][p]) {fl=1; break;}
        if (fl==0) break; else { i++; continue; }
      } else if (key[n]==EQX) {  // check value against values in sorted vec
        fl=0; // assume it's not going to match
        lt=0; rt=nv[i+1]-1;
        while (lt <= rt) {
          p = (lt+rt)/2;
          if (val>vvo[i+1][p]) lt=p+1; else if (val<vvo[i+1][p]) rt=p-1; else {fl=1; break;}
        }
        if (fl==0) break; else { i++; continue; }
      } else if (key[n]==EQY) {  // check value against values in sorted vec
        fl=0; // assume it's not going to match
        lt=0; rt=nv[i+1]-1;
        while (lt <= rt) {
          p = (lt+rt)/2;
          if (val>vvo[i+1][p]+LOOSE) lt=p+1; else if (val<vvo[i+1][p]-LOOSE) rt=p-1; else {
            fl=1; break; }
        }
        if (fl==0) break; else { i++; continue; }
      } else if (key[n]==NEQ) { if (val==arg[m]) {fl=0; break;} else continue; 
      } else if (key[n]==IBE) { if ((val< arg[m])||(val>=arg[m+1])) {
          fl=0; break; } else continue;  // IBE="[)" include-bracket-exclude
      } else if (key[n]==EBI) { if ((val<=arg[m])||(val> arg[m+1])) { 
          fl=0; break; } else continue;   // "(]" : exclude-bracket-include
      } else if (key[n]==IBI) { if ((val< arg[m])||(val> arg[m+1])) {
          fl=0; break; } else continue;   // "[]" : include-bracket-include
      } else if (key[n]==EBE) { if ((val<=arg[m])||(val>=arg[m+1])) {
          fl=0; break; } else continue;   // "()" : exclude-bracket-exclude
      } else {printf("vecst::slct ERR4 %g\n",key[n]); hoc_execerror("Unknown key",0);}
    }
    if (fl) { 
      ind[k++]=j; // all equal
      if (flag==1) break;
    } 
  }
  vector_resize(vv, k);
  return (double)k;
}
ENDVERBATIM

:* ind.slor(key,args,vec1,vec2[,vec3,vec4,...])
: picks out indices of numbers in key from multiple vectors
VERBATIM
static double slor (void* vv) {
  int i, j, k, m, n, p, ni, nk, na, nv[VRRY], num, fl, field[VRRY], lt, rt;
  Object* lob;
  double *ind, *key, *arg, *vvo[VRRY], val;

  ni = vector_instance_px(vv, &ind); // vv is ind
  nk = vector_arg_px(1, &key);
  na = vector_arg_px(2, &arg);
  lob = *hoc_objgetarg(3);
  num = ivoc_list_count(lob);
  if (num>VRRY) hoc_execerror("ERR: vecst::slor can only handle VRRY vectors", 0);

  for (i=0,j=0;i<num;i++,j++) {     // pick up vectors
    nv[i] = list_vector_px(lob, i, &vvo[i]);
    if (key[j]>=EQV && key[j]<=EQY) { // EQV-EQY take extra vec arg of any size
      i++;
      nv[i] = list_vector_px(lob, i, &vvo[i]);// pick up extra vector of any size
    } else if (ni!=nv[i]) {
      printf("vecst::slor ERR %d %d %d %d %d\n",i,j,k,ni,nv[i]);
      hoc_execerror("index and searched vectors must all be same size: ", 0); 
    }
  }
  for (j=0;j<num;j++) { // look for fields
    field[j]=-1;
    if (key[j]<=EBE && key[j]>=ALL) { field[j]=0;
    } else for (m=1;m<=5;m++) {
      if (key[j]<=EBE*(m+1) && key[j]>=ALL*(m+1)) { // m is is field key 1-5
        key[j]/=(m+1);
        field[j]=m;
      }
    }
    if (field[j]==-1) {printf("vecst::slor ERRF %g\n",key[j]); hxe(); }
  }
  if (2*nk!=na) { printf("vecst::slor ERR3 %d %d\n",nk,na); 
    hoc_execerror("Arg vector must be double key length",0); }
  for (i=0,n=0;i<nk;i++) if (key[i]>=EQV && key[i]<=EQY) n++; // special case takes 2 vec args
  if (nk+n!=num) { 
    printf("vecst::slor ERR2 %d(keys)+%d(EQV)!=%d(vecs)\n",nk,n,num); 
    hoc_execerror("Key length must be number of vecs + num of EQV",0); }
  for (j=0,k=0,m=0;j<ni;j++) { // j steps through elements of vectors
    for (i=0,m=0,n=0,fl=0;i<num;i++,n++,m+=2) { // i steps thru key, m thru args
      if (field[n]==0) val=vvo[i][j]; else UNCODE(vvo[i][j],field[n],val);
      if (key[n]==ALL) {fl=1; break;} // OK - do nothing
      if (key[n]==NOZ)        { if (val==0.) continue; else {fl=1; break;} 
      } else if (key[n]==POS) { if (val<=0.) continue; else {fl=1; break;} 
      } else if (key[n]==NEG) { if (val>=0.) continue; else {fl=1; break;} 
      } else if (key[n]==GTH) { if (val<=arg[m]) continue; else {fl=1; break;} 
      } else if (key[n]==GTE) { if (val< arg[m]) continue; else {fl=1; break;} 
      } else if (key[n]==LTH) { if (val>=arg[m]) continue; else {fl=1; break;} 
      } else if (key[n]==LTE) { if (val> arg[m]) continue; else {fl=1; break;} 
      } else if (key[n]==EQU) { if (val!=arg[m]) continue; else {fl=1; break;} 
      } else if (key[n]==EQV) { if (val!=vvo[i+1][j]) continue; else { 
          i++; fl=1; break; }
      } else if (key[n]==EQW) {  // check value against values in following vec
        fl=0; // assume it's not going to match
        for (p=0;p<nv[i+1];p++) if (val==vvo[i+1][p]) {fl=1; break;}
        if (fl==1) break; else { i++; continue; }
      } else if (key[n]==EQX) {  // check value against values in sorted vec
        fl=0; // assume it's not going to match
        lt=0; rt=nv[i+1]-1;
        while (lt <= rt) {
          p = (lt+rt)/2;
          if (val>vvo[i+1][p]) lt=p+1; else if (val<vvo[i+1][p]) rt=p-1; else {fl=1; break;}
        }
        if (fl==1) break; else { i++; continue; }
      } else if (key[n]==EQY) {  // check value against values in sorted vec
        printf("EQY not implemented for slor()\n"); hxe();
      } else if (key[n]==NEQ) { if (val==arg[m]) continue; else {fl=1; break;} 
      } else if (key[n]==IBE) { if ((val< arg[m])||(val>=arg[m+1])) {
          continue; } else {fl=1; break;}  // IBE="[)" include-bracket-exclude
      } else if (key[n]==EBI) { if ((val<=arg[m])||(val> arg[m+1])) { 
          continue; } else {fl=1; break;}   // "(]" : exclude-bracket-include
      } else if (key[n]==IBI) { if ((val< arg[m])||(val> arg[m+1])) {
          continue; } else {fl=1; break;}   // "[]" : include-bracket-include
      } else if (key[n]==EBE) { if ((val<=arg[m])||(val>=arg[m+1])) {
          continue; } else {fl=1; break;}   // "()" : exclude-bracket-exclude
      } else {printf("vecst::slor ERR4 %g\n",key[n]); hoc_execerror("Unknown key",0);}
    }
    if (fl) ind[k++]=j; // all equal
  }
  vector_resize(vv, k);
  return (double)k;
}
ENDVERBATIM

:* src.whi(valvec,indvec[,&i0,&i1,...]) returns index of first one for each val
VERBATIM
static double whi (void* vv) {
  int i, j, nx, na, nb, cnt; double *x, *val, *ind;
  nx = vector_instance_px(vv, &x);
  i = vector_arg_px(1, &val);
  na = vector_arg_px(2, &ind);
  if (i!=na) {printf("vecst:whi() takes 2 eq length vecs:%d %d\n",i,na); hxe();}
  scrset(na);  
  for (i=0;i<na;i++) {scr[i]=0; ind[i]=-1.;}
  for (i=0,cnt=0;i<nx;i++) for (j=0;j<na;j++) { 
    if (x[i]==val[j]) {
      if (scr[j]) printf("WARNING %g found mult times (%g,%d)\n",val[j],ind[j],i); else {
        ind[j]=(double)i; scr[j]=1; cnt++; 
      }
    }
  }
  for (nb=3;ifarg(nb);nb++) {} // count args
  nb--;
  if (nb>2) {
    if (nb-2!=na) {printf("vecst:whi() wrong #args:%d %d\n",na,nb-2); hxe();}
    for (i=3,j=0;j<na;i++,j++) *(hoc_pgetarg(i)) = ind[j];
  }
  return (double)cnt/na; // % found
}
ENDVERBATIM

:* v.iwr(FILEOBJ[,skipsz]) write Vector as integers to FileObj
: FILEOBJ must be open for writing
: skipsz is a flag to skip writing the # of ints to file
VERBATIM
static double iwr (void* vv) {
  int i, j, nx; size_t r;
  double *x;
  FILE* f, *hoc_obj_file_arg();
  f = hoc_obj_file_arg(1);
  nx = vector_instance_px(vv, &x);
  scrset(nx);
  for (i=0;i<nx;i++) scr[i]=(int)x[i]; // copy into integer array 
  if(!ifarg(2) || !((int)*getarg(2))) r=fwrite(&nx,sizeof(int),1,f);  // write out the size
  r=fwrite(scr,sizeof(int),nx,f);
  return (double)nx;
}
ENDVERBATIM

:* v.ird() read integers
VERBATIM
static double ird (void* vv) {
  int i, j, nx, n; size_t r;
  double *x;
  FILE* f, *hoc_obj_file_arg();
  f = hoc_obj_file_arg(1);
  nx = vector_instance_px(vv, &x);
  r=fread(&n,sizeof(int),1,f);  // size
  if (n>scrsz) { 
    if (scrsz>0) { free(scr); scr=(unsigned int *)NULL; }
    scrsz=n+10000;
    scr=(unsigned int *)ecalloc(scrsz, sizeof(int));
  }
  if (n!=nx) { 
    nx=vector_buffer_size(vv);
    if (n<=nx) {
      vector_resize(vv, n); nx=n; 
    } else {
      printf("%d > %d :: ",n,nx);
      hoc_execerror("Vector max capacity too small for ird ", 0);
    }
  }
  r=fread(scr,sizeof(int),n,f);
  for (i=0;i<nx;i++) x[i]=(double)scr[i];
  return (double)n;
}
ENDVERBATIM

:* v.fread2()
VERBATIM
static double fread2 (void* vv) {
  int i, j, nx, n, type, maxsz; size_t r;
  double *x;
  FILE* fp, *hoc_obj_file_arg();
  BYTEHEADER

  fp = hoc_obj_file_arg(1);
  nx = vector_instance_px(vv, &x);
  maxsz=vector_buffer_size(vv);
  n = (int)*getarg(2);
  type = (int)*getarg(3);
  if (n>maxsz) {
    printf("%d > %d :: ",n,maxsz);
    hoc_execerror("Vector max capacity too small for fread2 ", 0);
  } else {
    vector_resize(vv, n);
  }
  if (type==6 || type==16) {         // unsigned ints
    unsigned int *xs;
    if (n>scrsz) { 
      if (scrsz>0) { free(scr); scr=(unsigned int *)NULL; }
      scrsz=n+10000;
      scr=(unsigned int *)ecalloc(scrsz, sizeof(int));
    }
    xs=(unsigned int*)scr;
    r=fread(xs,sizeof(int),n,fp);
    if (type==16) BYTESWAP_FLAG=1;
    for (i=0;i<n;i++) {
      BYTESWAP(scr[i],int)
      x[i]=(double)scr[i];
    }
    return (double)n;
  } if (type==3 || type==13) { // straight float reads
    float *xf = (float *)malloc(n * (unsigned)sizeof(float));
    r=fread(xf,sizeof(float),n,fp);
    if (type==13) BYTESWAP_FLAG=1;
    for (i=0;i<n;i++) {
      BYTESWAP(xf[i],float)
      x[i]=(double)xf[i];
    }
    free((char *)xf);    
  } else hoc_execerror("Type unsupported in fread2 ", 0);
}
ENDVERBATIM

:* v.revec() -- append() except that sets vector to size 0 before appending
VERBATIM
static double revec (void* vv) {
  int i,j,k, nx, ny; double *x, *y;
  nx = vector_instance_px(vv, &x);
  if (nx==0) x=vector_newsize(vv,nx=100);
  for (i=1,k=0;ifarg(i);i++,k++) {
    if (hoc_is_double_arg(i)) {
      if (k>=nx) x=vector_newsize(vv,nx*=4);
      x[k]=*getarg(i);
    } else {
      ny=vector_arg_px(i, &y);
      if (k+ny>=nx) x=vector_newsize(vv,nx=2*(nx+ny));
      for (j=0;j<ny;j++,k++) x[k]=y[j];
      k--; // back up one
    }
  }
  vector_resize(vv,k);
}
ENDVERBATIM

:* v.has(val[,outvec]) -- a contains that returns the results
VERBATIM
static double has (void* vv) {
  int i, j, nx, ny;
  double *x, *y, val; void* vc;
  nx = vector_instance_px(vv, &x);
  val=*getarg(1);
  ny=0;
  if (ifarg(2)) if (hoc_is_object_arg(2)) {
    ny=vector_arg_px(2, &y); vc=vector_arg(2); 
    if (ny==0) y=vector_newsize(vc,ny=100);
  }
  for (i=0,j=0;i<nx;i++) if (x[i]==val) {
    if (ifarg(2)) {
      if (ny) {
        // append index to vector like indvwhere()
        if (j>=ny) y=vector_newsize(vc,ny*=4);
        y[j++]=(double)i;
      } else {
        *(hoc_pgetarg(2)) = (double)i;
        return 1.0;
      }
    } else return 1;
  }
  if (j>0) vector_resize(vc,j); // only fall through here when doing indvwhere
  return (double)j; 
}
ENDVERBATIM

:* ind.insct(v1,v2)
: return v1 intersect v2
VERBATIM
static double insct (void* vv) {
	int i, j, k, nx, nv1, nv2, maxsz;
	double *x, *v1, *v2;
	nx = vector_instance_px(vv, &x);
        if (maxsz==0) maxsz=1000;
        maxsz=vector_buffer_size(vv);
        x=vector_newsize(vv, maxsz);
	nv1 = vector_arg_px(1, &v1);
	nv2 = vector_arg_px(2, &v2);
        for (i=0,k=0;i<nv1;i++) for (j=0;j<nv2;j++) if (v1[i]==v2[j]) {
          if (k==maxsz) x=vector_newsize(vv, maxsz*=2);
          x[k++]=v1[i]; 
        }
        vector_resize(vv, k);
	return (double)k;
}
ENDVERBATIM

:* ind.linsct(vlist,this_many)
: return indices that show up this_many times or more in the vectors in vlist
VERBATIM
static double linsct (void* vv) {
  int i,j,k,nx,maxsz,min,cnt,lt,rt,p,iv,jv,jj,fl; ListVec* pL;
  double *x, val;
  nx = vector_instance_px(vv, &x);
  maxsz=vector_buffer_size(vv);
  if (maxsz==0) maxsz=1000;
  x=vector_newsize(vv, maxsz);
  pL = AllocListVec(*hoc_objgetarg(1));
  min= (int)*getarg(2);
  for (iv=0;iv<pL->isz;iv++) {
    if (!ismono1(pL->pv[iv],pL->plen[iv],2)){printf("linsct() ERRA not monotonic %d\n",iv); hxe();}
    if (pL->pv[iv][0]<0){printf("linsct() ERRB neg value in %d is %g\n",iv,pL->pv[iv][0]);hxe();}
  }
  for (iv=0,k=0;iv<=pL->isz-min+1;iv++) for (j=0;j<pL->plen[iv];j++) {
    val=pL->pv[iv][j];
    for (i=0,fl=0;i<k;i++) if (val==x[i]) {fl=1; break;}
    if (fl) continue;  // already on the list
    for (jv=iv+1,cnt=1;jv<pL->isz;jv++) {
      fl=lt=0; rt=pL->plen[jv]-1;
      while (lt <= rt) {
        p = (lt+rt)/2;
        if (val>pL->pv[jv][p]) lt=p+1; else if (val<pL->pv[jv][p]) rt=p-1; else {
          fl=1; break;}
      }
      if (fl) cnt++;
      if (cnt>=min) {
        if (k==maxsz) x=vector_newsize(vv, maxsz*=2);
        x[k++]=val;
        break;
      }
    }
  }
  vector_resize(vv, k);
  return (double)k;
}
ENDVERBATIM

:* vdest.vfill(vsrc)
: fill vdest with multiple instances of vsrc until reach size
VERBATIM
static double vfill (void* vv) {
	int i, nx, nv1;
	double *x, *v1;
	nx = vector_instance_px(vv, &x);
	nv1 = vector_arg_px(1, &v1);
        for (i=0;i<nx;i++) x[i]=v1[i%nv1];
}
ENDVERBATIM

:* vec.cull(src,key)
: remove numbers in vec that are found in the key
VERBATIM
static double cull (void* vv) {
	int i, j, k, nx, nv1, nv2, flag;
	double *x, *v1, *v2, val;
	nx = vector_instance_px(vv, &x);
	nv1 = vector_arg_px(1, &v1);
        if (hoc_is_double_arg(2)) { val=*getarg(2); nv2=0; } else nv2=vector_arg_px(2, &v2);
        x=vector_newsize(vv,nx=nv1);
        for (i=0,k=0;i<nv1;i++) {
          flag=1;
          if (nv2) { for (j=0;j<nv2;j++) if (v1[i]==v2[j]) flag=0;
          } else                         if (v1[i]==val  ) flag=0;
          if (flag) x[k++]=v1[i];
        }
        vector_resize(vv, k);
	return (double)k;
}
ENDVERBATIM

:* dest.redundout(src[,INDFLAG])
: flag redundant numbers; must sort src first
: with indflag set just returns indices of locations rather than values
VERBATIM
static double redundout (void* vv) {
  int i, j, nx, nv1, maxsz, ncntr, indflag, cntflag;
  double *x, *v1, *cntr, val;
  void *vc;
  if (ifarg(2)) indflag=(int)*getarg(2); else indflag=0; 
  if (ifarg(3)) { cntflag=1; 
    ncntr = vector_arg_px(3, &cntr);  vc=vector_arg(3); 
    ncntr = vector_buffer_size(vc);   vector_resize(vc, ncntr);
    for (i=0;i<ncntr;i++) cntr[i]=1.; // will be at least 1 of each #
  } else cntflag=0;
  nx = vector_instance_px(vv, &x);
  maxsz=vector_buffer_size(vv);  vector_resize(vv, maxsz);
  nv1 = vector_arg_px(1, &v1);
  val=v1[0]; x[0]=(indflag?0:val);
  if (cntflag) {
    for (j=1,i=1;i<nv1&&j<maxsz&&j<ncntr;i++) {
      if (v1[i]!=val) { val=v1[i]; x[j++]=(indflag?i:val); } else cntr[j-1]+=1;
    }
  } else {
    for (j=1,i=1;i<nv1&&j<maxsz;i++) if (v1[i]!=val) { val=v1[i]; x[j++]=(indflag?i:val); }
  }
  if (j>=maxsz) { 
    printf("\tredundout WARNING: ran out of room: %d<needed\n",maxsz);
  } else { vector_resize(vv, j); }
  if (cntflag) if (j>=ncntr) { 
    printf("\tredundout WARNING: cntr ran out of room: %d<needed\n",ncntr);
  } else { vector_resize(vc, j); }
  return (double)j;
}
ENDVERBATIM

:* ind.mredundout(veclistA[,INDFLAG,veclistB])
: check redundancy across multiple parallel vectors veclistA
: with indflag 1, returns index of matchs in ind but does not alter vecs in veclistA
: will also remove from veclistB in parallel 
: leaves the last of a series of matches 
: with indflag set just returns indices of locations rather than values
: NB using indices will to .remove match items will give results that differ from 
: direct use (last vs first of a series -- will be seen in the other columns -- ie veclistB)
VERBATIM
static double mredundout (void* vv) {
  int i, j, k, m, p, q, maxsz, ns, nx, av[VRRY], bv[VRRY], num, numb, indflag, match;
  Object *ob, *ob2;
  double *x, *avo[VRRY], *bvo[VRRY], val[VRRY];
  void *vva[VRRY],*vvb[VRRY];
  nx = vector_instance_px(vv, &x);
  ob = *hoc_objgetarg(1);
  if (ifarg(2)) indflag=(int)*getarg(2); else indflag=0; 
  if (ifarg(3)) { 
    ob2 = *hoc_objgetarg(3);
    numb = ivoc_list_count(ob2);
  } else numb=0;
  maxsz=vector_buffer_size(vv);
  if (indflag) vector_resize(vv, maxsz); // else vector is not used
  num = ivoc_list_count(ob);
  if (num>VRRY) hoc_execerror("mredundout ****ERRA****: can only handle VRRY vectors", 0);
  for (i=0;i<num;i++) { 
    av[i]=list_vector_px2(ob, i, &avo[i], &vva[i]);
    if (av[0]!=av[i]) { printf("mredundout ****ERRC**** %d %d %d\n",i,av[0],av[i]);
      hoc_execerror("Vectors must all be same size: ", 0); }
  }
  ns=av[0]; // size of source vecs
  for (i=0;i<numb;i++) { 
    bv[i]=list_vector_px2(ob2, i, &bvo[i], &vvb[i]);
    if (ns!=bv[i]) { printf("mredundout ****ERRC2**** %d %d %d\n",i,ns,bv[i]);
      hoc_execerror("Vectors must all be same size: ", 0); }
  }
  if (ns/4>scrsz) { 
    if (scrsz>0) { free(scr); scr=(unsigned int *)NULL; }
    scrsz=ns/4+10000;
    scr=(unsigned int *)ecalloc(scrsz, sizeof(int));
  }
  for (j=0;j<num;j++) val[j]=avo[j][0]; // initialize the val array
  for (i=1,k=0;i<ns;i++) { 
    for (j=0,match=1;j<num;j++) {
      if (val[j]!=avo[j][i]) { match=0; break; } // if no match say so
    }
    if (match) { // add this one to the list
      if (k>=scrsz){printf("mredundout****ERRD**** over scr size %d\n",k);hxe();}
      scr[k++]=i; // flag to get rid of this one
    } else for (j=0;j<num;j++) val[j]=avo[j][i]; // copy next set of vals
  }
  if (indflag) { // just fill ind with indices of the repeats
    if (k>maxsz){printf("mredundout****ERRE**** vec overflow %d>%d\n",k,maxsz);hxe();}
    for (i=0;i<k;i++) x[i]=(double)scr[i];
    vector_resize(vv, k);
  } else { // remove all the repeat rows
    if (k == 0) return (double)k;
    for (i=0,p=scr[0]; i<k-1; i++) { // iter thru the inds to remove
      for (m=scr[i],p--; m<scr[i+1]; m++,p++) { // move everything down till next ind
        for (j=0;j<num; j++) avo[j][p]=avo[j][m]; // go through all the A list vecs
        for (j=0;j<numb;j++) bvo[j][p]=bvo[j][m]; // go through B list vecs
      }
    }
    for (m=scr[i],p--; m<ns; m++,p++) { // finish up by moving down from last ind to end
      for (j=0;j<num; j++) avo[j][p]=avo[j][m]; 
      for (j=0;j<numb;j++) bvo[j][p]=bvo[j][m]; 
    }
    for (j=0;j<num; j++) vector_resize(vva[j], ns-k); // resize all the vectors
    for (j=0;j<numb;j++) vector_resize(vvb[j], ns-k);
  }
  return (double)k;
}
ENDVERBATIM

:* PIVOTA.join(PIVOTB,VECLISTA,VECLISTB)
:  NB must sort both pivots before use
VERBATIM
static double join (void* vv) {
  int i, j, k, m, p, q, maxsz, npiva, npivb, av[VRRY], bv[VRRY], num, numb, indflag, match;
  Object *ob, *ob2;
  double *piva, *pivb, *avo[VRRY], *bvo[VRRY], val[VRRY];
  void *vva[VRRY],*vvb[VRRY];
  npiva = vector_instance_px(vv, &piva);
  npivb = vector_arg_px(1, &pivb);
  ob = *hoc_objgetarg(2);
  ob2 = *hoc_objgetarg(3);
  num = ivoc_list_count(ob);
  numb = ivoc_list_count(ob2);
  if (num>VRRY) hoc_execerror("join ****ERRA****: can only handle VRRY vectors", 0);
  if (num!=numb) hoc_execerror("join ****ERRB****: different #of vecs in lists", 0);
  for (i=0;i<num;i++) { 
    av[i]=list_vector_px2(ob, i, &avo[i], &vva[i]);
    if (av[0]!=av[i]) { printf("join ****ERRC**** %d %d %d\n",i,av[0],av[i]);
      hoc_execerror("Vectors must all be same size: ", 0); }
  }
  for (i=0;i<numb;i++) { 
    bv[i]=list_vector_px2(ob2, i, &bvo[i], &vvb[i]);
    if (bv[0]!=bv[i]) { printf("join ****ERRC2**** %d %d %d\n",i,bv[0],bv[i]);
      hoc_execerror("Vectors must all be same size: ", 0); }
  }
  for (i=0,j=0;i<npiva;i++) {
    for (;piva[i]!=pivb[j] && j<npivb;j++); // move forward to find matching pivb[j]
    if (j==npivb) { printf("%g not found in PivotB\n",piva[i]);hxe();}
    for (k=0;k<num;k++) avo[k][i]=bvo[k][j];
  }
  return (double)k;
}
ENDVERBATIM

:* vscl() will scale a vector to -1,1
VERBATIM
static double vscl (double *x, double n) {
  int i; 
  double max,min,r,sf,b,a;
  max=-1e9; min=1e9; a=-1; b=1; 
  for (i=0;i<n;i++) { 
    if (x[i]>max) max=x[i];
    if (x[i]<min) min=x[i];
  }
  r=max-min;  // range
  sf = (b-a)/r; // scaling factor
  for (i=0;i<n;i++) x[i]=(x[i]-min)*sf+a;
}
ENDVERBATIM

:* vdest.scl(vsrc) nondestructive scaling
VERBATIM
static double scl (void* vv) {
  int i, j, k, nx, nsrc, nfilt, ntmp;
  double *x, *src, *filt, *tmp, sum, lpad, rpad;
  nx = vector_instance_px(vv, &x);
  nsrc = vector_arg_px(1, &src);
  if (nx!=nsrc) { hoc_execerror("scl:Vectors not same size: ", 0); }
  for (i=0;i<nx;i++) x[i]=src[i];
  vscl(x,nx);
}
ENDVERBATIM

:* vdest.sccvlv(vsrc,vfilt,tmp) // NOT CORRECT -- see scxing()
: scaled convolution -- scale section to -1,1 before multiplying by filter
VERBATIM
static double sccvlv (void* vv) {
  int i, j, k, nx, nsrc, nfilt, ntmp;
  double *x, *src, *filt, *tmp, sum, lpad, rpad;
  nx = vector_instance_px(vv, &x);
  nsrc = vector_arg_px(1, &src);
  nfilt = vector_arg_px(2, &filt);
  ntmp = vector_arg_px(3, &tmp);
  if (nx!=nsrc) { hoc_execerror("sccvlv:Vectors not same size: ", 0); }
  if (nfilt>nsrc) { hoc_execerror("sccvlv:Filter bigger than source ", 0); }
  if (nfilt!=ntmp){hoc_execerror("sccvlv:Filter (arg2) and tmp vector (arg3) diff size", 0);}
  for (i=0;i<nx;i++) {
    x[i]=0.0;
    for (j=0,k=i-(int)(nfilt/2);j<nfilt&&k>0&&k<nsrc;j++,k++) tmp[j]=src[k];
    vscl(tmp,j-1);
    for (k=0;k<j;k++) x[i]+=filt[k]*tmp[k];
  }
}
ENDVERBATIM

:* vdest.scxing(vsrc,tmp)
: scaled xing -- scale each section to -1,1 before checking # of 0-xing's
VERBATIM
static double scxing (void* vv) {
  int i, j, k, nx, nsrc, f, ntmp, maxsz;
  double *x, *src, *filt, *tmp, sum, maxsum, th;
  nx = vector_instance_px(vv, &x);
  nsrc = vector_arg_px(1, &src);
  ntmp = vector_arg_px(2, &tmp);
  if (nx!=nsrc) { hoc_execerror("scxing:Vectors not same size: ", 0); }
  th=0.0; 
  maxsum=-1e9;
  for (i=0;i<nx;i++) x[i]=0.; // clear
  for (i=ntmp/2+1;i<nx-ntmp/2-1;i++) {
    for (j=0,k=i-(int)(ntmp/2);j<ntmp;k++,j++) tmp[j]=src[k];
    vscl(tmp,j-1); // scale from -1 to 1
    for (k=0,f=0,sum=0.; k<nsrc; k++) {
      if (tmp[k]>th) { // ? passing thresh
        if (f==0) { 
          sum+=1; // just count the 0xing
          f=1; 
        }
      } else {       // below thresh 
        if (f==1) {
          f=0; // just passed going down 
          sum+=1;
        }
      }
    }
    if (sum>maxsum) maxsum=sum;
    x[i]=sum;
  }
  return (double)maxsum;
}
ENDVERBATIM

:* vdest.cvlv(vsrc,vfilt)
: convolution
VERBATIM
static double cvlv (void* vv) {
  int i, j, k, nx, nsrc, nfilt;
  double *x, *src, *filt, sum, lpad, rpad;
  nx = vector_instance_px(vv, &x);
  nsrc = vector_arg_px(1, &src);
  nfilt = vector_arg_px(2, &filt);
  if (nx!=nsrc) { hoc_execerror("Vectors not same size: ", 0); }
  if (nfilt>nsrc) { hoc_execerror("Filter bigger than source ", 0); }
  for (i=0;i<nx;i++) {
    x[i]=0.0;
    for (j=0,k=i-(int)(nfilt/2);j<nfilt;j++,k++) {
      if (k>0 && k<nsrc-1) x[i]+=filt[j]*src[k];
    }
  }
}
ENDVERBATIM

:* vdest.intrp(flag)
: interpolate numbers replacing numbers given as flag
VERBATIM
static double intrp (void* vv) {
  int i, la, lb, nx;
  double *x, fl, a, b;
  nx = vector_instance_px(vv, &x);
  fl = *getarg(1);
  i=0; a=x[0]; la=0;
  if (a==fl) a=0;
  while (i<nx-1) {
    for (i=la+1;x[i]==fl && i<nx-1; i++) ; // find the next one 
    b=x[i]; lb=i;
    for (i=la+1; i<lb; i++) x[i]= a + (b-a)/(lb-la)*(i-la);
    a=b; la=lb;
  }
  return (double)fl;
}
ENDVERBATIM

:* vec.sumabs()
: return sum of abs values
VERBATIM
static double sumabs (void* vv) {
  int i, nx;
  double *x, sum;
  nx = vector_instance_px(vv, &x);
  for (sum=0,i=0;i<nx; i++) sum+=fabs(x[i]);
  return sum;
}
ENDVERBATIM

:* vec.inv([NUMERATOR])
: element=NUMERATOR/element
VERBATIM
static double inv (void* vv) {
  int i, nx;
  double *x, nume;
  nx = vector_instance_px(vv, &x);
  if (ifarg(1)) nume=*getarg(1); else nume=1.; 
  for (i=0;i<nx; i++) x[i]=(x[i]==0)?1e9:nume/x[i];
  return (double)i;
}
ENDVERBATIM

:* tmp.nind(ind,vec1,vec2[,vec3,vec4,...])
: picks out numbers not in ind from multiple vectors
: ind must be sorted
VERBATIM
static double nind (void* vv) {
	int i, j, k, m, nx, ni, nv[VRRY], num, c, last;
	double *x, *ind, *vvo[VRRY];
	nx = vector_instance_px(vv, &x);
        for (i=0;ifarg(i);i++);
	if (i>VRRY) hoc_execerror("ERR: nind can only handle VRRY vectors", 0);
	num = i-2; // number of vectors to be picked apart 
        for (i=0;i<num;i++) { 
          nv[i] = vector_arg_px(i+2, &vvo[i]);
          if (nx!=nv[i]) { printf("nind ERR %d %d %d\n",i,nx,nv[i]);
            hoc_execerror("Vectors must all be same size: ", 0); }
        }
        ni = vector_arg_px(1, &ind);
        c = nx-ni; // the elems indexed are to be eliminated 
        if (ni>scrsz) { 
          if (scrsz>0) { free(scr); scr=(unsigned int *)NULL; }
          scrsz=ni+10000;
          scr=(unsigned int *)ecalloc(scrsz, sizeof(int));
        }
        for (i=0,last=-1;i<ni;i++) { 
          scr[i]=(int)ind[i]; // copy into integer array 
          if (scr[i]<0 || scr[i]>=nx) hoc_execerror("nind(): Index out of bounds", 0);
          if (scr[i]<=last) hoc_execerror("nind(): indices should mono increase", 0);
          last=scr[i];
        }
        for (j=0;j<num;j++) { // each output vec 
          for (i=0,last=-1,m=0;i<ni;i++) { // the indices of ind 
            for (k=last+1;k<scr[i];k++) { x[m++]=vvo[j][k]; }
            last=scr[i];
          }
          for (k=last+1;k<nx;k++,m++) { x[m]=vvo[j][k]; }
          for (i=0;i<c;i++) vvo[j][i]=x[i];   
          vv=vector_arg(j+2); vector_resize(vv, c);
        }
	return c;
}
ENDVERBATIM

:* ind.keyind(key,vec1,vec2[,vec3,vec4,...])
: picks out indices of numbers in key from multiple vectors
VERBATIM
static double keyind (void* vv) {
  int i, j, k, ni, nk, nv[VRRY], num;
  double *ind, *key, *vvo[VRRY];
  ni = vector_instance_px(vv, &ind); // vv is ind
  for (i=0;ifarg(i);i++); i--; // drop back by one to get numarg()
  if (i>VRRY) hoc_execerror("ERR: keyind can only handle VRRY vectors", 0);
  num = i-1; // number of vectors to be picked apart 
  for (i=0;i<num;i++) { 
    nv[i] = vector_arg_px(i+2, &vvo[i]);
    if (ni!=nv[i]) { printf("keyind ERR %d %d %d\n",i,ni,nv[i]);
    hoc_execerror("Non-key vectors must be same size: ", 0); }
  }
  nk = vector_arg_px(1, &key);
  if (nk!=num) { printf("keyind ERR2 %d %d\n",nk,num); 
    hoc_execerror("Key length must be number of vecs",0); }
  k=0;
  for (j=0;j<ni;j++) { // j steps through elements of vectors
    for (i=0;i<nk;i++) { // i steps through the key
      if (key[i]==ALL) continue; // OK - do nothing
      if (key[i]==NOZ)        { if (vvo[i][j]==0.) break; else continue; 
      } else if (key[i]==POS) { if (vvo[i][j]<=0.) break; else continue; 
      } else if (key[i]==NEG) { if (vvo[i][j]>=0.) break; else continue; 
      } else if (key[i]!=vvo[i][j]) break; // default
    }
    if (i==nk) ind[k++]=j; // all equal
  }
  vector_resize(vv, k);
  return (double)k;
}
ENDVERBATIM
 
:* v1.thresh() threshold above and below thresh
VERBATIM
static double thresh (void* vv) {
  int i, nx, ny, cnt;
  double *x, *y, th;
  nx = vector_instance_px(vv, &x);
  cnt=0;
  if (hoc_is_object_arg(1)) { 
    ny = vector_arg_px(1, &y); th=0;
    if (nx!=ny) { hoc_execerror("Vector sizes don't match in thresh.", 0); }
    for (i=0; i<nx; i++) { if (x[i]>=y[i]) { x[i]= 1.; cnt++;} else { x[i]= BVBASE; } }
  } else { th = *getarg(1);
    for (i=0; i<nx; i++) { if (x[i] >= th) { x[i]= 1.; cnt++;} else { x[i]= BVBASE; } }
  }
  return cnt;
}
ENDVERBATIM
 
:* v1.nearall(max,v2,tql) 
: tql from {tq=new NQS("diff","tmid","t1","t2") tq.listvecs(tql)}
: max is maximum diff to add to the tq db
VERBATIM
static double nearall (void* vv) {
  register int	lo, hi, mid;
  int i, j, k, kk, nx, ny, minind, nv[4];
  Object *ob;
  void* vvl[4];
  double *x, *y, *vvo[4], targ, dist, new, max, tmp;
  nx = vector_instance_px(vv, &x);
  max = *getarg(1);
  ny = vector_arg_px(2, &y);
  ob = *hoc_objgetarg(3);
  if ((nv[0]=ivoc_list_count(ob))!=4) {printf("VECST::nearall() ERRA: %d\n",nv[0]); hxe();}
  for (i=0;i<4;i++) { nv[i] = list_vector_px3(ob, i, &vvo[i], &vvl[i]);
    if (nv[i]!=nv[0]){printf("nearall ERRC: %d %d\n",nv[i],nv[0]); hxe();}
  }
  for (j=0,k=0;j<ny;j++) {
    targ=y[j];
    lo=0; hi=nx-1; mid=lo; // binary search from K&R Ch. 6, p. 125
    while (lo<=hi) {
      mid = (hi+lo)/2;
      if ((tmp=x[mid]-targ)>0.) hi=mid-1; else if (tmp<0) lo=mid+1; else break;
    }
    dist=fabs(x[mid]-targ); minind=mid;
    for (i=-1;i<=1;i+=2) { kk=mid+i; // check the flanking values
      if (kk>0 && kk<nx && (new=fabs(x[kk]-targ))<dist) { 
        dist=new;
        minind=kk;
      }
    }
    if (dist<=max) {
      if (k>=nv[1]) { printf("nearall WARN: oor %d %d\n",k,nv[1]); return -1.; }
      vvo[0][k]=dist; vvo[2][k]=targ; vvo[3][k]=x[minind];
      k++;
    }
  }
  if (k>scrsz) { 
    if (scrsz>0) { free(scr); scr=(unsigned int *)NULL; }
    scrsz=k+10000;
    scr=(unsigned int *)ecalloc(scrsz, sizeof(int));
  }
  for (kk=0,i=0;i<k;) {
    dist=vvo[0][i]; targ=vvo[3][i]; // value from x[]
    for (minind=i,j=i+1;vvo[3][j]==targ;j++) {
      if (vvo[0][j]<dist) { minind=j; dist=vvo[0][j]; } // find the closest of these
    }
    i=j;
    scr[kk++]=minind;
  }
  for (i=0;i<kk;i++) {
    vvo[0][i]=vvo[0][scr[i]];
    vvo[1][i]=(vvo[2][scr[i]]+vvo[3][scr[i]])/2.;
    vvo[2][i]=vvo[2][scr[i]];
    vvo[3][i]=vvo[3][scr[i]];
  }
  for (i=0;i<4;i++) vector_resize(vvl[i],kk);
  return (double)kk;
}
ENDVERBATIM

:* v1.nearest(val,&dist) value of v1 nearest to val, returns index and optional dist
VERBATIM
static double nearest (void* vv) {
  int i, nx, minind, flag=0;
  double *x, targ, dist, new, *to;
  nx = vector_instance_px(vv, &x);
  targ = *getarg(1);
  if (ifarg(3)) flag = (int)*getarg(3);
  dist = 1e9;
  for (i=0; i<nx; i++) if ((new=fabs(x[i]-targ))<dist) { 
    if (flag && new==0) continue; // flag signals to not pick self
    dist=new;
    minind=i;
  }
  if (ifarg(2)) *(hoc_pgetarg(2)) = dist;
  return (double)minind;
}
ENDVERBATIM
 
:* v1.approx(v2,epsilon) -- like .eq but looser -- good when have saved and restored a vec
VERBATIM
static double approx (void* vv) {
  int i, j, nx, ny;
  double *x, *y, epsilon;
  nx = vector_instance_px(vv, &x);
  ny = vector_arg_px(1, &y);
  if (nx!=ny) { printf("approx different size vectors %d %d\n",nx,ny); return 0; }
  epsilon = (ifarg(2)?*getarg(2):LOOSE);
  for (i=0; i<nx; i++) if (x[i]<y[i]-epsilon || x[i]>y[i]+epsilon) return 0;
  return 1;
}
ENDVERBATIM

:* v1.samp(VEC,rate) does something like a resample
VERBATIM
//linear interpolation
static double samp (void* vv) {
  int i, nx, cnt, iOrigSz, maxsz, iNewSz, isrcidx,isrcidx1;
  double *x, *y, dNewSz, scale, dsrcidx, frac;
  nx = vector_instance_px(vv, &x); // dest
  iOrigSz = vector_arg_px(1, &y); // source
  dNewSz = *getarg(2);  // new size
  maxsz=vector_buffer_size(vv); 
  iNewSz = (int)dNewSz;
  if (iNewSz>maxsz) {printf("VECST samp ERRA: dest vec too small: %d %d\n",iNewSz,maxsz); hxe();}
  vector_resize(vv,iNewSz);

  scale = (double) iOrigSz / (double) iNewSz;
  for(i=0;i<iNewSz;i++){
    dsrcidx = i * scale;
    isrcidx = (int) dsrcidx;
    isrcidx1 = isrcidx+1 < iOrigSz-1 ? isrcidx+1 : iOrigSz-1;
    frac = dsrcidx - isrcidx;
    x[i] = (1-frac) * y[isrcidx] + frac * y[isrcidx1];
  }

  return iNewSz;
}
ENDVERBATIM
 
:* v1.triplet() return location of a triplet
VERBATIM
static double triplet (void* vv) {
  int i, nx;
  double *x, *y, a, b;
  nx = vector_instance_px(vv, &x);
  a = *getarg(1); b = *getarg(2);
  for (i=0; i<nx; i+=3) if (x[i]==a&&x[i+1]==b) break;
  if (i<nx) return (double)i; else return -1.;
}
ENDVERBATIM

:* state.onoff(volts,OBon,thresh,dur,refr)
:  looks at volts vector to decide if have reached threshold thresh
:  OBon takes account of burst dur and refractory period
VERBATIM
static double onoff (void* vv) {
  int i, j, n, nv, non, nt, nd, nr, num;
  double *st, *vol, *obon, *thr, *dur, *refr;
  n = vector_instance_px(vv, &st);
  nv   = vector_arg_px(1, &vol);
  non  = vector_arg_px(2, &obon);
  nt   = vector_arg_px(3, &thr);
  nd   = vector_arg_px(4, &dur);
  nr   = vector_arg_px(5, &refr);
  if (n!=nv||n!=non||n!=nt||n!=nd||n!=nr) {
    hoc_execerror("v.onoff: vectors not all same size", 0); }
  for (i=0,num=0;i<n;i++) {
    obon[i]--;
    if (obon[i]>0.) { st[i]=1.; continue; } // cell must fire 
    if (vol[i]>=thr[i] && obon[i]<= -refr[i]) { // past refractory period 
        st[i]=1.; obon[i]=dur[i]; num++;
    } else { st[i]= BVBASE; }
  }
  return (double)num;
}
ENDVERBATIM
 
:* vo.bpeval(outp,del)
:  service routine for back-prop: vo=outp*(1-outp)*del
VERBATIM
static double bpeval (void* vv) {
  int i, n, no, nd, flag=0;
  double add,div;
  double *vo, *outp, *del;
  n = vector_instance_px(vv, &vo);
  no   = vector_arg_px(1, &outp);
  nd   = vector_arg_px(2, &del);
  if (ifarg(3) && ifarg(4)) { add= *getarg(3); div= *getarg(4); flag=1;}
  if (n!=no||n!=nd) hoc_execerror("v.bpeval: vectors not all same size", 0);
  if (flag) {
    for (i=0;i<n;i++) vo[i]=((outp[i]+add)/div)*(1.-1.*((outp[i]+add)/div))*del[i];
  } else {
    for (i=0;i<n;i++) vo[i]=outp[i]*(1.-1.*outp[i])*del[i];
  }
}
ENDVERBATIM
 
:* v1.sedit() string edit
VERBATIM
static double sedit (void* vv) {
  int i, n, ni, f=0;
  double *x, *ind, th, val;
  Symbol* s; char *op;
  op = gargstr(1);
  n = vector_instance_px(vv, &x);
  sprintf(op,"hello world");
  return (double)n;
}
ENDVERBATIM

:* v1.w() a .where that sets elements in source vector
VERBATIM
static double w (void* vv) {
  int i, n, ni, c, f;
  double *x, *ind, th, val;
  Symbol* s; char *op;
  if (! ifarg(1)) { 
    printf("v1.w('op',thresh[,val,v2])\n"); 
    printf("  a .where that sets elements in v1 to val (default 0), if v2 => only look at these elements\n");
    printf("  'op'=='function name' is a .apply targeted by v2 called as func(x[i],thresh,val)\n");
    return -1.;
  }
  op = gargstr(1);
  n = vector_instance_px(vv, &x);
  th = *getarg(2);
  f=c=0;
  if (ifarg(3)) { val = *getarg(3); } else { val = 0.0; }
  if (ifarg(4)) {ni = vector_arg_px(4, &ind); f=1;} // just look at the spots indexed
  if (!strcmp(op,"==")) { 
    if (f==1) {for (i=0; i<ni;i++) {if (x[(int)ind[i]]==th) { x[(int)ind[i]]=val;c++;}}
    } else {for (i=0; i<n; i++) {if (x[i]==th) { x[i]=val;c++;}}}
  } else if (!strcmp(op,"!=")) {
    if (f==1) {for (i=0; i<ni;i++) {if (x[(int)ind[i]]!=th) { x[(int)ind[i]]=val;c++;}}
    } else {for (i=0; i<n; i++) {if (x[i]!=th) { x[i]=val;c++;}}}
  } else if (!strcmp(op,">")) {
    if (f==1) {for (i=0; i<ni;i++) {if (x[(int)ind[i]]>th) { x[(int)ind[i]]=val;c++;}}
    } else {for (i=0; i<n; i++) {if (x[i]>th) { x[i]=val;c++;}}}
  } else if (!strcmp(op,"<")) {
    if (f==1) {for (i=0; i<ni;i++) {if (x[(int)ind[i]]<th) { x[(int)ind[i]]=val;c++;}}
    } else {for (i=0; i<n; i++) {if (x[i]<th) { x[i]=val;c++;}}}
  } else if (!strcmp(op,">=")) {
    if (f==1) {for (i=0; i<ni;i++) {if (x[(int)ind[i]]>=th) { x[(int)ind[i]]=val;c++;}}
    } else {for (i=0; i<n; i++) {if (x[i]>=th) { x[i]=val;c++;}}}
  } else if (!strcmp(op,"<=")) {
    if (f==1) {for (i=0; i<ni;i++) {if (x[(int)ind[i]]<=th) { x[(int)ind[i]]=val;c++;}}
    } else {for (i=0; i<n; i++) {if (x[i]<=th) { x[i]=val;c++;}}}
  } else if ((s=hoc_lookup(op))) { // same as .apply but only does indexed ones
    if (f==1) {for (i=0; i<ni;i++) {
        hoc_pushx(x[(int)ind[i]]); hoc_pushx(th); hoc_pushx(val);
      x[(int)ind[i]]=hoc_call_func(s, 3);}
    } else {for (i=0; i<n;i++) {hoc_pushx(x[i]); hoc_pushx(th); hoc_pushx(val);
        x[i]=hoc_call_func(s, 3);}}
  }
  return (double)c;
}
ENDVERBATIM
 
:* ind.slone(SRC,VAL) select indices where ==VAL from sorted vector SRC
VERBATIM
static double slone (void* vv) {
  int i, j, n, ni, nsrc, maxsz;
  double *x, *src, val, max, min;
  n = vector_instance_px(vv, &x);
  maxsz=vector_buffer_size(vv);  vector_resize(vv, maxsz);
  nsrc = vector_arg_px(1, &src);
  val = *getarg(2);
  if (ifarg(3)) ni=(int)*getarg(3); else {
    min=src[0];  max=src[nsrc-1];
    ni=(int)(val-min)/(max-min)*(double)(nsrc-1); // where expect to find it
  }
  if (src[ni]<val) {
    for (i=ni;src[i]!=val&&i<nsrc;i++); 
  } else {
    for (i=ni;src[i]!=val&&i>=0;i--); 
    for (    ;src[i]==val&&i>=0;i--); 
    i++; // go back to the first one
  }
  for (j=0;src[i]==val && j<maxsz && i<nsrc;i++,j++) x[j]=i;
  if (j==maxsz) printf("vecst slone WARN: OOR %d %d\n",j,maxsz);
  vector_resize(vv, j);
  return (double)(i-1);
}
ENDVERBATIM
  
:* dest.xing(src,tvec,thresh) 
:  dest.xing(src,thresh)  -- returns indices, change into time by .mul(tstep)
:  dest.xing(src)  -- default thresh=0; returns indices
: a .where that looks for threshold crossings and then doesn't pick another till
: comes back down again; places values from tvec in dest; interpolates with INTERP_VECST set
VERBATIM
static double xing (void* vv) {
  int i, j, d2f, nsrc, ndest, ntvec, f, maxsz, tvf;
  double *src, *dest, *dest2, *tvec, th;
  th=0.; tvf=0; // tvf==1: tvec being used
  ndest = vector_instance_px(vv, &dest);
  nsrc = vector_arg_px(1, &src);
  i=2;
  if (ifarg(i)) {
    if (hoc_is_double_arg(i)) th=*getarg(i); else {ntvec=vector_arg_px(i, &tvec); tvf=1;}
    i++;
    if (ifarg(i) && hoc_is_double_arg(i)) th=*getarg(i++);
  }
  maxsz=vector_buffer_size(vv);
  vector_resize(vv, maxsz);
  if (ifarg(i)){dest2=vector_newsize(vector_arg(i),maxsz); d2f=i;} else d2f=0;
  if (tvf && nsrc!=ntvec) hoc_execerror("v.xing: vectors not all same size", 0);
  for (i=0,f=0,j=0; i<nsrc; i++) {
    if (src[i]>th) { // ? passing thresh 
      if (f==0) { 
        if (j>=maxsz) {
          printf("(%d) :: ",maxsz);
          hoc_execerror("Dest vec too small in xing ", 0);
        }
        if (i>0) { // don't record if first value is above thresh 
          if (INTERP_VECST) {
            if (tvf) {
              dest[j++] = tvec[i-1] + (tvec[i]-tvec[i-1])*(th-src[i-1])/(src[i]-src[i-1]);
            } else {
              dest[j++] = (i-1) + (th-src[i-1])/(src[i]-src[i-1]);
            }
          } else {
            if (tvf) dest[j++]=tvec[i]; else dest[j++]=i;
          }
        }
        f=1; 
      }
    } else {       // below thresh 
      if (f==1) { f=0; } // just passed going down 
      if (d2f) {
        if (INTERP_VECST) {
          if (tvf) {
            dest2[j++] = tvec[i-1] + (tvec[i]-tvec[i-1])*(th-src[i-1])/(src[i]-src[i-1]);
          } else {
            dest2[j++] = (i-1) + (th-src[i-1])/(src[i]-src[i-1]);
          }
        } else {
          if (tvf) dest2[j++]=tvec[i]; else dest2[j++]=i;
        }
      }
    }
  }
  vector_resize(vv, j);
  if (d2f) vector_resize(vector_arg(d2f),j);
  return (double)j;
}
ENDVERBATIM

:* dest.snap(src,tvec,dt) 
: interpolate src with tvec to prior dt step, saves only highest value in each interval
: an .interpolate that doesn't loose spikes
VERBATIM
static double snap (void* vv) {
  int i, j, nsrc, ndest, ntvec, f, maxsz, size;
  double *src, *dest, *tvec, mdt, tstop, tt, val;
  ndest = vector_instance_px(vv, &dest);
  nsrc = vector_arg_px(1, &src);
  ntvec = vector_arg_px(2, &tvec);
  mdt = *getarg(3);
  maxsz=vector_buffer_size(vv);
  tstop = tvec[nsrc-1];
  size=(int)tstop/mdt;
  if (size>maxsz) { 
    printf("%d > %d\n",size,maxsz);
    hoc_execerror("v.snap: insufficient room in dest", 0); }
  vector_resize(vv, size);
  if (nsrc!=ntvec) hoc_execerror("v.snap: src and tvec not same size", 0);
  for (tt=0,i=0;i<size && tt<=tvec[0];i++,tt+=mdt) dest[i]=src[0];
  for (j=1, i--, tt-=mdt; i<size; i++, val=-1e9, tt+=mdt) {
    if (tvec[j]>tt) dest[i]=src[j-1]; else {
      for (;j<nsrc && tvec[j]<=tt;j++) if (src[j]>val) val=src[j];
      if (val==-1e9) printf("vecst:snap() internal ERROR\n");
      dest[i]=val;
    }
  }
  return (double)size;
}
ENDVERBATIM

:* v1.xzero(vec[,thresh]) finds indices of zero [or thresh] crossings in vec
VERBATIM
static double xzero (void* vv) {
  int i, n, nv, up, cnt;
  double *x, *vc, th;
  n = vector_instance_px(vv, &x);
  nv = vector_arg_px(1, &vc);
  if (ifarg(2)) { th = *getarg(2); } else { th=0.0;}
  if (vc[0]<th) up=0; else up=1;  // F or T 
  for (i=0,cnt=0; i<nv; i++) {
    if (up) { // look for passing down 
      if (vc[i]<th) up=0;
    } else if (vc[i]>th) { 
      up=1; 
      if (cnt>=nv) x=vector_newsize(vv,(n+=100));
      x[cnt++]=(double)i;
    }
  }
  x=vector_newsize(vv,cnt);
  return (double)cnt;
}
ENDVERBATIM

:* v1.peak(vec[,vamp]) puts indices of zero [or thresh] crossings of vec into v1
:  optional vamp gives amplitues
VERBATIM
static double peak (void* vv) {
  int i, n, nc, ny, up, cnt;
  double *x, *y, *vc, last; void* vy;
  n = vector_instance_px(vv, &x); // for indices
  nc = vector_arg_px(1, &vc); // source vectors
  if (n==0) x=vector_newsize(vv,n=100);
  if (ifarg(2)) y=vector_newsize(vy=vector_arg(2),ny=n); else ny=0; // same size as v1
  if (vc[1]-vc[0]<0) up=0; else up=1;  // F or T 
  last=vc[1];
  for (i=2,cnt=0; i<nc; i++) {
    if (up) { // look for starting down
      if (vc[i]-last<0) {
        up=0;
        if (cnt>=n) { x=vector_newsize(vv,(n+=100)); 
              if (ny) y=vector_newsize(vy,n);}
        x[cnt]=(double)(i-1); 
        if (ny) y[cnt]=last;
        cnt++;
      }
    } else if (vc[i]-last>0) up=1; 
    last=vc[i];
  }
  x=vector_newsize(vv,cnt);
  if (ny) y=vector_newsize(vy,cnt);
  return (double)cnt;
}
ENDVERBATIM

:* v1.negwrap([FLAG]) wrap neg values to pos, FLAG==0 set them to 0, FLAG!=0 wrap
:  above FLAG
VERBATIM
static double negwrap (void* vv) {
  int i, n;
  double *x, cnt, sig;
  n = vector_instance_px(vv, &x);
  if (ifarg(1)) sig = (int)*getarg(1); else sig=1e9; // default: do wrap
  if (sig==0.) {
    for (i=0,cnt=0; i<n; i++) if (x[i]<0) { 
      x[i]=0.;
      cnt++; 
    }
  } else if (sig==1e9) {
    for (i=0,cnt=0; i<n; i++) if (x[i]<0) { 
      x[i]=-x[i];
      cnt++; 
    }
  } else {
    for (i=0,cnt=0; i<n; i++) if (x[i]<sig) { 
      x[i]=2*sig-x[i]; // sig+(sig-x[i]) wraps around sig
      cnt++; 
    }
  }
  return cnt;
}
ENDVERBATIM
  
:* v1.sw(FROM,TO) switchs all FROMs to TO
VERBATIM
static double sw (void* vv) {
  int i, n;
  double *x, fr, to;
  n = vector_instance_px(vv, &x);
  fr = *getarg(1);
  to = *getarg(2);
  for (i=0; i<n; i++) {
    if (x[i]==fr) { x[i] = to;}
  }
  return (double)n;
}
ENDVERBATIM
 
:* v.b2v(bytevec) copies from vector to bytevec
VERBATIM
static double b2v (void* vv) {
  int i, n, num;
  double *x; bvec* to; Object *ob;
  n = vector_instance_px(vv, &x);
  ob = *(hoc_objgetarg(1));
  to = (bvec*)ob->u.this_pointer; // doesn't check that this is actually a bvec
  if (to->size!=n) { hoc_execerror("Vector and bytevec sizes don't match.", 0); }
  for (i=0; i<n; i++) x[i] = (double)to->x[i];
  return (double)n;
}
ENDVERBATIM

:* v.v2d(&x) copies from vector to double area -- a seg error waiting to happen
VERBATIM
static double v2d (void* vv) {
  int i, n, num;
  double *x, *to;
  n = vector_instance_px(vv, &x);
  to = hoc_pgetarg(1);
  if (ifarg(2)) { num = *getarg(2); } else { num=-1;}
  if (num>-1 && num!=n) { hoc_execerror("Vector size doesn't match.", 0); }
  for (i=0; i<n; i++) {to[i] = x[i];}
  return (double)n;
}
ENDVERBATIM
 
:* v.v2p(&x0[,&x1,&x2...]) copies from vector or vectors to doubles
VERBATIM
static double v2p (void* vv) {
  int i, j, n, cnt;
  double *x;
  n = vector_instance_px(vv, &x);
  for (i=0,j=1,cnt=0;ifarg(j) && i<n;i++,j++) {
    if (hoc_is_double_arg(j)) continue; // skip this one
    *hoc_pgetarg(j)=x[i];
    cnt++;
  }
  return (double)cnt;
}
ENDVERBATIM

:* v.l2p(veclist,index,[&x0,&x1,&x2...]) copies from list of vectors to vector and doubles
VERBATIM
static double l2p (void* vv) {
  int ix, i, j, n, num, cnt;
  double *x, *y;   Object* lob;
  n = vector_instance_px(vv, &x);
  lob = *hoc_objgetarg(1);
  ix=(int)*getarg(2);
  num = ivoc_list_count(lob);
  x=vector_newsize(vv,num);
  for (i=0;i<num;i++) {     // pick up vectors
    cnt = list_vector_px(lob, i, &y);
    if (ix>=cnt) {printf("vecst:l2p() ERRA: %d %d %d\n",i,ix,cnt); hxe();}
    x[i]=y[ix];
  }
  for (i=0,j=3,cnt=0;ifarg(j) && i<num;i++,j++) {
    if (hoc_is_double_arg(j)) continue; // skip this one
    *hoc_pgetarg(j)=x[i];
    cnt++;
  }
  return (double)cnt;
}
ENDVERBATIM

:* v.fetch(val,list,vec) fetches first eg NQS row where v holds val
:* v.fetch(val,list,&x0[,&x1,&x2...])
VERBATIM
static double fetch (void* vv) {
  int ix, i, j, n, ny, cnt;
  double *x, *y, val, ret; ListVec* pL;
  n = vector_instance_px(vv, &x);
  val = *getarg(1);
  pL = AllocListVec(*hoc_objgetarg(2));
  for (ix=0;ix<n;ix++) if (x[ix]==val) break;
  if (ix==n) {if (VERBOSE_VECST) printf("vecst:fetch() WARNING: %g not found\n",val); return ERR;}
  if (hoc_is_object_arg(3)) {
    ny = vector_arg_px(3, &y);
    if (ny>pL->isz) vector_resize(vector_arg(3),pL->isz); // don't make bigger if only want a few
    for (i=0,j=0,cnt=0;i<pL->isz && j<ny;i++,j++) {
      if (ix>pL->plen[i]) {printf("vecst:fetch()ERRB: %d %d %x\n",i,ix,(unsigned int)pL->pv[i]); 
        FreeListVec(&pL); hxe();}
      y[j]=pL->pv[i][ix];
      cnt++;
    }
    ret=y[j-1]; // final value
  } else {
    for (i=0,j=3,cnt=0;i<pL->isz && ifarg(j);i++,j++) {
      if (hoc_is_double_arg(j)) continue; // skip this one
      if (ix>pL->plen[i]) {printf("vecst:fetch()ERRB1: %d %d %x\n",i,ix,(unsigned int)pL->pv[i]); 
        FreeListVec(&pL); hxe();}
      *hoc_pgetarg(j)=ret=pL->pv[i][ix];
      cnt++;      
    }
  }
  FreeListVec(&pL);
  return ret;
}
ENDVERBATIM
 

:* v.covar(list,vec) generates covariance matrix in vec form
:  generally data are in the columns; here data are in the vectors -- ie as if in the rows
VERBATIM
static double covar (void* vv) {
  int ix, i, j, j2, n, m;
  double *x, *y, *mean; ListVec* pL;
  n = vector_instance_px(vv, &x); // number of data vectors
  if (n==0) { pL = AllocListVec(*hoc_objgetarg(1)); // get all of them
  } else       pL = AllocILV(*hoc_objgetarg(1),n,x);
  if (pL->isz<2) {printf("vecst:covar()ERRA: %d\n",pL->isz); FreeListVec(&pL); hxe();}
  n=pL->isz;     // number of data points
  m=pL->plen[0]; // dimensionality of data
  for (i=1;i<pL->isz;i++) if (m!=pL->plen[i]) {
    printf("vecst:covar()ERRB: sz mismatch %d %d@%d\n",m,pL->plen[i],i);FreeListVec(&pL);hxe();}
  y=vector_newsize(vector_arg(2),m*m);
  // pL->pv[i][j] -- i goes through the list and j goes through each vector
  mean=(double*)malloc(sizeof(double)*m);
  for (j=0;j<m;j++) { // Determine means of column vectors of input data matrix
    for (i=0,mean[j]=0.;i<n;i++) mean[j]+=pL->pv[i][j];
    mean[j]/=(double)n;
  }
  for (i=0;i<n;i++) for (j=0;j<m;j++) pL->pv[i][j] -= mean[j]; // center the vectors
  for (j=0;j<m;j++) for (j2=j;j2<m;j2++) { // Calculate the m*m covariance matrix
    for (i=0,y[j*m+j2]=0.;i<n;i++) y[j*m+j2]+=pL->pv[i][j]*pL->pv[i][j2];
    y[j*m+j2]/=(n-1);
    y[j2*m+j]=y[j*m+j2];
  }
  for (i=0;i<n;i++) for (j=0;j<m;j++) pL->pv[i][j] += mean[j]; // restore vectors
  free(mean);
  FreeListVec(&pL);
  return m;
}
ENDVERBATIM

:* ind.vlxpose(src_list,dest_list) does 'transpose'
VERBATIM
static double vlxpose (void* vv) {
  int i, j, k, n, c, c2, sz, err;
  double *x; ListVec *pL, *pL2; Object* obl;
  err=0;
  n = vector_instance_px(vv, &x); // vector of indices
  if (n==0) { pL = AllocListVec(*hoc_objgetarg(1)); // get all of them
  } else       pL = AllocILV(*hoc_objgetarg(1),n,x);
  pL2 = AllocListVec(obl=*hoc_objgetarg(2));
  c=pL->isz;  c2=pL2->isz;     // number of columns (list length)
  // pL->pv[i][j] -- i goes through the list and j goes through each vector
  for (j=0;j<c;j++) list_vector_resize(obl,j,pL2->pbuflen[j]);
  n=pL->plen[0]; // length of vector
  if (n!=c2) err=1;
  for (j=1;j<c;j++) if (n!=pL->plen[j] || err) {
    printf("vecst:vlxpose()ERRA: %d %d %d\n",n,pL->plen[j],c2); 
    FreeListVec(&pL); FreeListVec(&pL2); hxe(); }
  for (j=0,k=0;j<c;j++,k++) for (i=0;i<c2;i++) { 
    if (k>=pL2->pbuflen[i]) { sz=pL2->pbuflen[i]; // need to grow vector
      sz=(sz<10)?100:(sz*2);
      pL2->pv[i]=list_vector_resize(obl, i, pL2->pbuflen[i]=sz);
    }
    pL2->pv[i][k]=pL->pv[j][i];
  }
  for (j=0;j<c2;j++) list_vector_resize(obl,j,k);
  FreeListVec(&pL);  FreeListVec(&pL2);
  return (double)n;
}
ENDVERBATIM
 
:* ind.ixsort(vec,list) does list.o(ind.x[i]).append(vec.x[i])
VERBATIM
static double ixsort (void* vv) {
  int i, j, n, ntv, c;
  double *x, *tv; ListVec* pL; Object* obl;
  n = vector_instance_px(vv, &x); // vector of indices
  ntv = vector_arg_px(1, &tv);
  if (ntv!=n) {printf("vecst:ixsort()ERR0: diff size %d %d\n",n,ntv); hxe();}
  pL = AllocListVec(obl=*hoc_objgetarg(2));
  if (pL->isz<2) {printf("vecst:ixsort()ERRA: %d\n",pL->isz); FreeListVec(&pL); hxe();}
  c=pL->isz;     // number of columns (list length)
  // pL->pv[i][j] -- i goes through the list and j goes through each vector
  for (j=0;j<c;j++) list_vector_resize(obl, j, pL->pbuflen[j]);
  for (j=0;j<n;j++) {
    i=x[j]; 
    if (i>=c) {printf("vecst:ixsort()ERRB: OOB %d %d\n",i,c); FreeListVec(&pL); hxe();}
    if (pL->plen[i]>=pL->pbuflen[i]) {
      if (pL->pbuflen[i]) pL->pbuflen[i]*=2; else pL->pbuflen[i]=100;
      pL->pv[i]=list_vector_resize(obl, i, pL->pbuflen[i]);
    }
    pL->pv[i][pL->plen[i]++]=tv[j];
  }
  for (j=0;j<c;j++) list_vector_resize(obl, j, pL->plen[j]);
  FreeListVec(&pL);
  return (double)n;
}
ENDVERBATIM

:* v.d2v(&x) copies from double area to vector -- a seg error waiting to happen
VERBATIM
static double d2v (void* vv) {
  int i, n, num;
  double *x, *fr;
  n = vector_instance_px(vv, &x);
  fr = hoc_pgetarg(1);
  if (ifarg(2)) { num = *getarg(2); } else { num=-1;}
  if (num>-1 && num!=n) { hoc_execerror("Vector size doesn't match.", 0); }
  for (i=0; i<n; i++) {x[i] = fr[i];}
  return (double)n;
}
ENDVERBATIM
 
:* v.lcat(LIST)
VERBATIM
static double lcat (void* vv) {
  int i, j, k, n, lc, cap, maxsz;
  Object *ob1;
  double *x, *fr; 
  void *vw;
  n = vector_instance_px(vv, &x);
  vector_resize(vv,maxsz=vector_buffer_size(vv)); // open it up fully
  ob1 = *hoc_objgetarg(1);
  lc = ivoc_list_count(ob1);
  for (i=0,j=0;i<lc && j<maxsz;i++) {
    cap = list_vector_px2(ob1, i, &fr, &vw);
    for (k=0;k<cap && j<maxsz;k++,j++) x[j]=fr[k];
  }
  if (i<lc || k<cap) printf("vecst lcat WARN: not all vecs copied\n");
  vector_resize(vv,j);
  return (double)j;
}
ENDVERBATIM

:* v.mkcode(LIST,BITS) -- put together integer vectors from list by bit concatenating
VERBATIM
static double mkcode (void* vv) {
  int i, j, k, n, num, bits;
  Object *ob;
  double *x, *vvo[5];
  n = vector_instance_px(vv, &x);
  ob = *hoc_objgetarg(1);
  if (ifarg(2)) bits = *getarg(2); else bits=3;
  num = ivoc_list_count(ob);
  if (num!=5) hoc_execerror("mkcode ****ERRA****: can only handle 5 vectors", 0);
  for (i=0;i<num;i++) {  j=list_vector_px(ob, i, &vvo[i]);
    if (n!=j) { printf("mkcode ****ERRC**** %d %d %d\n",i,n,j);
      hoc_execerror("Vectors must all be same size: ", 0); }}
  for (i=0;i<n;i++) { // go through the vec length
    for (j=0,x[i]=0;j<5;j++) {
      if (vvo[j][i]<0. || vvo[j][i]>=sc[4] || floor(vvo[j][i]+0.5)!=vvo[j][i]) {
        printf("vec.mkcode OOB %g>%g in vec[%d].x[%d]\n",vvo[j][i],sc[4],j,i); hxe(); }
        x[i]+=vvo[j][i]*sc[j+1];
    }
  }
  return (double)i;
}
ENDVERBATIM

:* v.uncode(val) -- take apart val and place in vector
: v.uncode(VECLIST) -- take apart vector items and place in vectors in list (cf uncodf)
: v.uncode(vec,field) -- take apart v entries and place requested field in vec
: v.uncode(field,val) -- replace field in v with val (cf recodf)
: v.uncode(field,vec) -- replace field in v with values from vec
VERBATIM
static double uncode (void* vv) {
  int i, j, n, ny, num, field;
  Object *ob;
  double *x, *y, *vvo[5], val, old;
  void *vvv[5];
  n = vector_instance_px(vv, &x);
  field=0;
  if (!ifarg(1)) { // numarg()==0
    printf("\tv.uncode(val) -- take apart val and place in vector\n\tv.uncode(VECLIST) -- take apart vector items and place in vectors in list (cf uncodf)\n\tv.uncode(vec,field) -- take apart vector items and place requested field in vector\n\tv.uncode(field,val) -- replace field in v with val (cf recodf)\n\tv.uncode(field,vec) -- replace field in v with values from vec\n"); return 0.;
  } else if (!ifarg(2)) { // numarg()==1
    if (hoc_is_double_arg(1)) {
      val = *getarg(1);
      if (vector_buffer_size(vv)<5) {
        hoc_execerror("uncode ****ERRA****: vector too small to resize(5)", 0);}
      vector_resize(vv,5);
      for (i=1;i<=5;i++) UNCODE(val,i,x[i-1])
      return x[0];
    } else {
      ob = *hoc_objgetarg(1);
      num = ivoc_list_count(ob);
      if (num>5) hoc_execerror("uncode ****ERRA****: can only handle 5 vectors", 0);
      for (i=0;i<num;i++) if (! list_vector_px4(ob, i, &vvo[i], n)) {
        printf("uncode ****ERRC**** %d\n",i);
        hoc_execerror("Vectors not big enough: ", 0);
      }
      for (i=0;i<n;i++) for (j=1;j<=num;j++) UNCODE(x[i],j,vvo[j-1][i]);
      return (double)i;
    }
  } else { // numarg()==2
    if (hoc_is_double_arg(1)) { // replace values
      field = (int)chkarg(1,1.,5.);
      ny=-1;
      if (hoc_is_double_arg(2)) {
        val=chkarg(2,0.,sc[4]-1); 
        if (floor(val+0.5)!=val) hoc_execerror("uncode(vec) ****ERRG****: non-int val", 0);
      } else {
        ny=vector_arg_px(2, &y);
        if (ny!=n) hoc_execerror("uncode(vec) ****ERRH****: diff sized vecs", 0);
      }
      for (i=0;i<n;i++) {
        UNCODE(x[i],field,old)
        if (ny>0)  {
          if (y[i]<0.||y[i]>=sc[4]||floor(y[i]+0.5)!=y[i]) {
            printf("vec.uncode ERRJ OOB %g (%g max) at %d\n",y[i],sc[4],i);hxe();}
          x[i] += sc[field]*(y[i]-old);
        } else {
          x[i] += sc[field]*(val -old);
        }
      }
      return (double)i;
    } else {  // fill single vector with values
      ny = vector_arg_px(1, &y);
      field = (int)chkarg(2,1.,5.);
      if (ny!=n) hoc_execerror("uncode(vec) ****ERRI****: diff sized vecs", 0);
      for (i=0;i<n;i++) UNCODE(x[i],field,y[i])
      return (double)i;
    }
  }
}
ENDVERBATIM
 
VERBATIM
//* list_vector_px(LIST,ITEM#,DOUBLE PTR ADDRESS) 
// modeled on vector_arg_px() picks up a vec from a list
int list_vector_px (Object *ob, int i, double** px) {
  Object* obv;
  int sz;
  obv = ivoc_list_item(ob, i);
  if (! ISVEC(obv)) return -1;
  sz = vector_capacity(obv->u.this_pointer);
  *px = vector_vec(obv->u.this_pointer);
  return sz;
}

//* list_vector_px2(LIST,ITEM#,DOUBLE PTR ADDRESS,VEC POINTER ADDRESS) 
//  returns the vector pointer as well as the double pointer
int list_vector_px2 (Object *ob, int i, double** px, void** vv) {
  Object* obv;
  int sz;
  obv = ivoc_list_item(ob, i);
  if (! ISVEC(obv)) return -1;
  sz = vector_capacity(obv->u.this_pointer);
  *px = vector_vec(obv->u.this_pointer);
  *vv = (void*) obv->u.this_pointer;
  return sz;
}

//* list_vector_px3(LIST,ITEM#,DOUBLE PTR ADDRESS,VEC POINTER ADDRESS) 
//  same as px2 but returns max vec size instead of current vecsize
//  side effect -- increase vector size to maxsize
int list_vector_px3 (Object *ob, int i, double** px, void** vv) {
  Object* obv;
  int sz;
  obv = ivoc_list_item(ob, i);
  if (! ISVEC(obv)) return -1;
  sz = vector_buffer_size(obv->u.this_pointer);
  *px = vector_vec(obv->u.this_pointer);
  *vv = (void*) obv->u.this_pointer;
  vector_resize(*vv,sz);
  return sz;
}

//* list_vector_px4(LIST,ITEM#,DOUBLE PTR ADDRESS,desired size)
//  does resizing and returns true
int list_vector_px4 (Object *ob, int i, double** px, unsigned int n) {
  Object* obv;
  void* vv;
  int sz;
  obv = ivoc_list_item(ob, i);
  if (! ISVEC(obv)) return -1;
  sz = vector_buffer_size(obv->u.this_pointer);
  *px = vector_vec(obv->u.this_pointer);
  vv = (void*) obv->u.this_pointer;
  if (n>sz) {
    printf("List vector WARNING: unable to resize to %d requested (%d)\n",n,sz);
    vector_resize(vv,sz);
    return 0;
  } else vector_resize(vv,n);
  return 1;
}

//* list_vector_resize(LIST,ITEM#,NEW SIZE)
double *list_vector_resize (Object *ob, int i, int sz) {
  Object* obv;
  obv = ivoc_list_item(ob, i);
  if (! ISVEC(obv)) return 0x0;
  vector_resize(obv->u.this_pointer,sz);
  return vector_vec(obv->u.this_pointer);
}
ENDVERBATIM

:* v1.ismono([arg]) asks whether is monotonically increasing, with arg==-1 - decreasing
:  with arg==0:all same; 2:no consec ==; 3: incrementing by 1
VERBATIM
double ismono1 (double *x, int n, int flag) {
  int i; double last, gap, ret;
  last=x[0]; ret=1.; // default return value
  if (flag==1) {
    for (i=1; i<n && x[i]>=last; i++) last=x[i];
  } else if (flag==-1) {
    for (i=1; i<n && x[i]<=last; i++) last=x[i];
  } else if (flag==0) {
    for (i=1; i<n && x[i]==last; i++) ;
  } else if (flag==2) {
    for (i=1; i<n && x[i]>last; i++) last=x[i];
  } else if (flag==-2) {
    for (i=1; i<n && x[i]<last; i++) last=x[i];
  } else  if (flag==3) {
    for (i=1; i<n && x[i]==last+1; i++) last=x[i];
  } else  if (flag==4) {
    gap=x[1]-last; ret=gap;
    for (i=1; i<n && x[i]==last+gap; i++) last=x[i];
  } else  if (flag==-3) {
    for (i=1; i<n && x[i]==last-1; i++) last=x[i];
  }
  if (i==n) return ret; else return 0.;
}

static double ismono (void* vv) {
  int i, n, flag;
  double *x,last;
  n = vector_instance_px(vv, &x);
  if (ifarg(1)) { flag = (int)*getarg(1); } else { flag = 1; }
  return (double)ismono1(x,n,flag);
}
ENDVERBATIM
 
:* v1.count(num) returns number of instances of num
VERBATIM
static double count (void* vv) {
  int i, n, cnt;
  double *x,num;
  n = vector_instance_px(vv, &x);
  num = *getarg(1);
  for (cnt=0,i=0; i<n; i++) if (x[i]==num) cnt++;
  return cnt;
}
ENDVERBATIM

:* v1.muladd(mul,add) mul*x+add
: eg v1.muladd(-1,1) will swap 0s and 1s
VERBATIM
static double muladd (void* vv) {
  int i,n;
  double *x,mul,add;
  n = vector_instance_px(vv, &x);
  mul = *getarg(1);
  add = *getarg(2);
  for (i=0; i<n; i++) x[i]=x[i]*mul+add;
  return x[0];
}
ENDVERBATIM

:* v1.binfind(num) looks at sorted list to see if contains num
VERBATIM
static double binfind (void* vv) {
  int i, n, lt, rt, mid;
  double *x,num;
  n = vector_instance_px(vv, &x);
  num = *getarg(1);
  lt=0; rt=n-1;
  while (lt <= rt) {
    mid = (lt+rt)/2;
    if (num>x[mid]) lt=mid+1; else if (num<x[mid]) rt=mid-1; else return (double)mid;
  }
  return -1;
}
ENDVERBATIM

:* v1.uniq() returns number of unique values in vec
: v1.uniq(v2) -- v2 has the uniq values
: v1.uniq(List) L.o(0) has the uniq values; .o(1) has counts
: v1.uniq(List,1) L.o(1) has the uniq values with preserved order
VERBATIM
static double uniq (void* vv) {
  int i, j, k, n, cnt, ny, nz, flag, lt, rt, mid, res;
  double *x, *y, *z, lastx, num;
  void* voi[2]; Object* ob; char *ix;
  n = vector_instance_px(vv, &x);
  flag=ny=nz=0;
  if (n==0) {printf("vecst:uniq WARNA empty input vector\n"); return 0;}
  if (ifarg(1)) {
    ny=openvec(1,&y);
    if (ny==-1) { // list
      ob= *hoc_objgetarg(1);
      ny=list_vector_px3(ob, 0, &y, &voi[0]);
      nz=list_vector_px3(ob,1,&z,&voi[1]);
      if (nz==0) z=vector_newsize(voi[1],nz=100);
    } else {
      voi[0]=vector_arg(1);   // save vector pointer
    }
    if (ny==0) y=vector_newsize(voi[0],ny=100);
  }
  if (ifarg(2)) {
    if (hoc_is_double_arg(2)) { 
      flag=*getarg(2);
      ix=(char*)ecalloc(n,sizeof(char));
      nz=0;
    } else {
      if (nz>0) {printf("ERROR: uniq(list,vec)\n"); hxe();}
      voi[1]=vector_arg(2);
      if ((nz=openvec(2,&z))==0) z=vector_newsize(voi[1],nz=100);
    }
  }
  scrset(n);
  for (i=0;i<n;i++) scr[i]=i;
  nrn_mlh_gsort(x, scr, n, cmpdfn);
  if (ny) y[0]=x[scr[0]]; 
  if (nz>0) z[0]=1.;
  for (i=1, lastx=x[scr[0]], cnt=1; i<n; i++) {
    if (x[scr[i]]>lastx+hoc_epsilon) {
      if (ny) { 
        if (cnt>=ny) y=vector_newsize(voi[0],ny*=3);
        y[cnt]=x[scr[i]]; 
      }
      if (nz>0) {
        if (cnt>=nz) z=vector_newsize(voi[1],nz*=3);
        z[cnt]=1.;
      }
      cnt++;
      lastx=x[scr[i]];
    } else if (nz>0) z[cnt-1]++;
  }
  if (ny) vector_resize(voi[0], cnt);
  if (nz>0) vector_resize(voi[1], cnt);
  if (flag) { // refill z with the unique values in proper order
    z=vector_newsize(voi[1], cnt);
    for (i=0;i<cnt;i++) ix[i]=1;
    for (i=0,j=0;i<n;i++) {
      lt=0; rt=cnt-1; res=-1; num=x[i];
      while (lt<=rt) { // look for the number in sorted y vector
        mid=(lt+rt)/2;
        if (num>y[mid]) lt=mid+1; else if (num<y[mid]) rt=mid-1; else {res=mid; break;}
      }
      if (y[res]!=num) {printf("uniq ERRC: %d %g %g\n",res,y[res],num); hxe();}
      if (ix[res]) { // haven't got this one yet
        z[j++]=num;
        ix[res]=0;
      }
      if (i%1000==0) {
        for (k=0;k<cnt;k++) if (ix[k]) break;
        if (k==cnt) break; // ix[] filled in completely so exit for loop
      }
    }
    free(ix);
  } 
  return (double)cnt;
}

// x.unq(y,z) calls uniq2() -- functionality same as uniq(List,1)
static double unq (void* vv) {
  int n, cnt; double *x, *y, *z; 
  n=vector_instance_px(vv, &x);
  y=vector_newsize(vector_arg(1),n); // all same size
  z=vector_newsize(vector_arg(2),n);
  cnt=uniq2(n,x,y,z);
  y=vector_newsize(vector_arg(1),cnt);
  z=vector_newsize(vector_arg(2),cnt);
  return (double)cnt;
}

//** uniq2() should be called with 3 double arrays and their size
int uniq2 (int n, double *x, double *y, double *z) {
  int i, j, k, cnt, lt, rt, mid, res;  double lastx, num;
  if (n==0) return 0;
  scrset(n);
  for (i=0;i<n;i++) scr[i]=i;
  nrn_mlh_gsort(x, scr, n, cmpdfn); // sort x
  y[0]=x[scr[0]]; // first value
  for (i=1, lastx=x[scr[0]], cnt=1; i<n; i++) {
    if (x[scr[i]]>lastx+hoc_epsilon) {
      y[cnt]=x[scr[i]]; 
      cnt++;
      lastx=x[scr[i]];
    }
  }
  for (i=0;i<cnt;i++) scr[i]=1; // markers for cnt unique values in y
  // places uniq num in y into z in order from original redund x
  for (i=0,j=0;i<n;i++) { // go through all the x values
    lt=0; rt=cnt-1; res=-1; num=x[i]; // num is x value
    while (lt<=rt) { // look for num in sorted y vector -- binary search
      mid=(lt+rt)/2;
      if (num>y[mid]) lt=mid+1; else if (num<y[mid]) rt=mid-1; else {res=mid; break;}
    }
    if (y[res]!=num) {printf("uniq2 ERRC: %d %g %g\n",res,y[res],num); hxe();}
    if (scr[res]) { // haven't got this one yet
      z[j++]=num;
      scr[res]=0; // mark that one as being taken care of
    }
    if (i%10*cnt==0) { // check if we're done every few iterations
      for (k=0;k<cnt;k++) if (scr[k]) break; // still some that haven't been found
      if (k==cnt) break; // scr[] cleared completely so finished
    }
  } 
  return cnt;
}

// v1.nqsvt() for nqs vt iterator
static double nqsvt (void* vv) {
  int i, j, n, flag, cols;
  double *col, *fcd, *ind, *vvo[100];
  Object *fcdo, *vl, *obo;
  Symbol* s; char *proc;
  if ((cols=vector_instance_px(vv, &col))>100) {printf("nqsvt ERRD only 100 cols\n"); hxe();}
  proc = gargstr(1);
  if (!(s=hoc_lookup(proc))) {printf("nqsvt ERRA: proc %s not found\n",proc); hxe();}
  fcdo=*hoc_objgetarg(2);
  vector_arg_px(3, &fcd);
  vl=*hoc_objgetarg(4);
  if (ifarg(5)) {vector_arg_px(5, &ind); flag=1;} else flag=0;
  n=list_vector_px(vl,(int)col[0],&vvo[0]);
  for (i=1; i<cols; i++) if ((j=list_vector_px(vl,(int)col[i],&vvo[i]))!=n) {
    printf("nqvt ERRB irreg cols %d %d %d\n",i,n,j); hxe(); }
  if (flag) { // selected only -- need to write
  } else for (i=0; i<n; i++) {
    for (j=0; j<cols; j++) {
      if (fcd[(int)col[j]]==0) {  
        hoc_pushx(vvo[j][i]);
      } else if (fcd[(int)col[j]]==1) {
        obo=ivoc_list_item(fcdo, (int)vvo[j][i]);
        hoc_pushobj(&obo);
      } else { printf("nqvt ERRC unhandled type: %g\n",fcd[j]); hxe(); }
    }
    hoc_pushx((double)i);
    hoc_call_func(s, cols+1);
  }
  return (double)n;
}

// openvec() will pick up and open up a single vector but also will look for a list
int openvec (int arg, double **y) {
  int max; void* vv;
  Object* ob;
  ob =   *hoc_objgetarg(arg);
  if (! ISVEC(ob)) return -1;
  vector_arg_px(arg, y);
  vv=vector_arg(arg);
  max=vector_buffer_size(vv);
  vector_resize(vv, max);
  if (max==0) printf("openvec(): 0 size vec\n");
  return max;
}

// vector_newsize() will also increase size of vector
double *vector_newsize (void* vv, int n) {
  vector_resize(vv,n);
  return vector_vec(vv);
}
ENDVERBATIM

:* v1.rnd([flag]) rounds off to nearest integer, with flag==1 rounds down
VERBATIM
static double rnd (void* vv) {
  int i, n, flag;
  double *x;
  flag=(ifarg(1)?(int)*getarg(1):0);
  n = vector_instance_px(vv, &x);
  if (flag) {for (i=0; i<n; i++) x[i]=floor(x[i]);
  } else     for (i=0; i<n; i++) x[i]=floor(x[i]+0.5);
  return (double)i;
}
ENDVERBATIM

:* v1.pop() removes last entry and shortens vector
VERBATIM
static double pop (void* vv) {
  int n;
  double *x;
  n = vector_instance_px(vv, &x);
  if (n==0) {printf("vec.pop ERR: empty vec\n");hxe();}
  vector_resize(vv,n-1);
  return x[n-1];
}
ENDVERBATIM

PROCEDURE Expo (x) {
  TABLE RES FROM -20 TO 20 WITH 5000
  RES = exp(x)
}

FUNCTION EXP (x) {
  if (x>20 || x<-20) { printf("EXP(%g) called with OOB value [-20,20]\n",x) 
    EXP=ERR 
  } else {
    Expo(x)
    EXP=RES
  }
}

FUNCTION SUMEXP () {
  VERBATIM
  double i,min,max,step,sum;
  if (ifarg(2)) { min=*getarg(1); max=*getarg(2); step=ifarg(3)?*getarg(3):1.;
  } else { max=*getarg(1); min=0.; step=1.; }
  if (max>20. || min<-20.) { 
    printf("SUMEXP() called with OOB value: %g %g [-20,20]\n",min,max);
    sum=ERR;
  } else for (i=min,sum=0;i<=max+hoc_epsilon;i+=step) {
    Expo(i);
    sum+=RES;
  }
  _lSUMEXP=sum;
  ENDVERBATIM
}

:* dest.smgs(src,low,high,step,var)
:  rewrite of v.sumgauss() in nrn5.3::ivoc/ivocvect.cpp:1078
:  NEEDS DEBUGGING -- see drline.hoc:smgs() 
VERBATIM
static double smgs (void* vv) {	
  int i, j, nx, xv, nsum, points, maxsz;
  double *x, *sum;
  double  low , high , step , var , svar , scale , arg;

  nsum = vector_instance_px(vv, &sum);
  nx = vector_arg_px(1,&x);
  low = *getarg(2);
  high = *getarg(3);
  step = *getarg(4);
  var = *getarg(5);

  points = (int)((high-low)/step+hoc_epsilon);
  if (nsum!=points) { 
    maxsz=vector_buffer_size(vv);
    if (points<=maxsz) {
      nsum=points;  vector_resize(vv, nsum); 
    } else {
      printf("%d > %d :: ",points,maxsz);
      hoc_execerror("Vector max capacity too small in smgs ", 0);
    }
  }

  svar = -2.*var*var/step/step;
  scale = 1./sqrt(2.*M_PI)/var;

  for (j=0; j<points;j++) sum[j] = 0.;
  for (i=0;i<nx;i++) {
    xv = (int)((x[i]-low)/step + 0.5);
    for (j=xv; j<points && (arg=(j-xv)*(j-xv)/svar)>-20;j++) {
      Expo(arg);
      sum[j] += RES;
    }
    for (j=xv-1; j>=0 && (arg=(j-xv)*(j-xv)/svar)>-20;j--) {
      Expo(arg);
      sum[j] += RES;
    }
  }
  for (j=0; j<points;j++) sum[j] *= scale;
  return svar;
}
ENDVERBATIM

:* dest.smsy(tvec,CVLV_VEC,tstop[,dt,del])
:  sum CVLV_VEC starting at each point given in tvec with optional delay
:  used for summing up syn potentials
VERBATIM
static double smsy (void* vv) {	
  int i, j, k, nx, nc, nsum, points, maxsz;
  double *x, *sum, *c;
  double del,tstop,mdt;

  if (! ifarg(1)) { printf("dest.smsy(tvec,CVLV_VEC,tstop[,dt,del])\n"); return -1.; }

  del=0.; mdt=0.2;
  nsum = vector_instance_px(vv, &sum);
  nx = vector_arg_px(1,&x);
  nc = vector_arg_px(2,&c);
  tstop = *getarg(3);
  if (ifarg(4)) mdt = *getarg(4);
  if (ifarg(5)) del = *getarg(5);

  points=(int)(tstop/mdt+hoc_epsilon);
  if (nsum!=points) { 
    maxsz=vector_buffer_size(vv);
    if (points<=maxsz) {
      vector_resize(vv, points); points=nsum; 
    } else {
      printf("%d > %d :: ",points,maxsz);
      hoc_execerror("Dest vector too small in smsy ", 0);
    }
  }

  // don't zero out dest vec
  for (i=0;i<nx;i++) for (j=0,k=(x[i]+del)/mdt;j<nc && k<nsum;j++,k++) sum[k] += c[j];
  return points;
}
ENDVERBATIM

:* int.vrdh(FILE,veclist,code)
: vector read header will read the headers from vecs saved with vread()
: needs to be generalized so reads code as well, also should do BYTESWAP
VERBATIM 
static double vrdh (void* vv) {	
  int code, i, num, n[2], maxsz; size_t r;
  double *x;
  FILE* f;

  num = vector_instance_px(vv, &x);
  maxsz=vector_buffer_size(vv);
  f =     hoc_obj_file_arg(1);
  num = (int)*getarg(2); // number of vectors to look for

  if (maxsz<2*num){printf("vrdh ERR0 need %d room in vec\n",2*num);hxe();}
  vector_resize(vv, 2*num);

  for (i=0;i<num;i++) { 
    r=fread(&n,sizeof(int),2,f); // n[1] is type
    if (n[1]!=3){printf("vrdh ERRA code 3 only implemented %d:%d\n",i,n[1]);hxe();}
    x[2*i]=(double)n[0]; // size
    x[2*i+1]=(double)n[1];
    fseek(f,(long)n[1],SEEK_CUR);
  }
  return (double)num;
}
ENDVERBATIM

:* rdmany(FILE,{veclist or vec},code[,num])
VERBATIM
static double rdmany (void* vv) {	
  int code, i, j, ni, vsz, ny, nv, num, cnt, n[2], sz, hd, vflag, iflag, last;
  Object* ob; size_t r;
  double *vvo[100], sf[2], *ind, *y;
  FILE* f;

  vflag=iflag=0;
  ni = vector_instance_px(vv, &ind);
  f =     hoc_obj_file_arg(1);
  ob =   *hoc_objgetarg(2);
  if (ifarg(3)) cnt=(int)*getarg(3); else { cnt=ni; iflag=1; }
  if (strncmp(hoc_object_name(ob),"Vector",6)==0) vflag=1;
  i=2*sizeof(int) + 2*sizeof(double); // size of header with scaling
  j=2*sizeof(int);  // size of header without scaling
  r=fread(&n,sizeof(int),2,f);
  vsz=n[0]; code=n[1];
  fseek(f,(long)-2*sizeof(int),SEEK_CUR);  // go back
  if (DEBUG_VECST) printf("rdmanyDBA: %ld %d %d\n",ftell(f),vsz,code);
  switch (code) {
    // case 1:sz=1; hd=i; break; // char
    case 2:sz=2; hd=i; break; // short
    case 3:sz=4; hd=j; break; // float
    case 4:sz=8; hd=j; break; // double
    // case 5:sz=4; hd=i; break; // int
    default: hoc_execerror("rdmany ERRE: code not recognized", 0);
  }
  if (vflag) {
    ny = vector_arg_px(2, &y);
    num= cnt;
    if (vsz*cnt!=ny) {
      printf("rdmany ERRD: wrong size vec: %d statt (%d*%d) %d\n",ny,vsz,cnt,vsz*cnt); hxe();}
  } else {
    num = ivoc_list_count(ob);
    if (num>100) hoc_execerror("rdmany ERRA: can only handle 100 vectors", 0);
    if (num!=cnt) {printf("rdmany ERRB: %d != %d",num,cnt); hxe();}
    for (i=0;i<num;i++) { 
      nv = list_vector_px(ob, i, &vvo[i]);
      if (vsz!=nv){printf("rdmany ERRC: Vectors must all be same size %d %d %d\n",i,vsz,nv);hxe();}
    }
  }
  if (vsz*sz>bufsz) { 
    if (scrsz>0) { free(scr); scr=(unsigned int *)NULL; }
    scrsz=vsz+10;
    scr=(unsigned int *)ecalloc(scrsz, sz);
    bufsz=scrsz*sz; // number of chars available
  }
  if (code==2) {
    unsigned short *xs;
    xs=(unsigned short *)scr;
    for (last=-1,i=0;i<num;i++) {
      if (iflag) {  // iflag // "i flag" not "if lag"
        fseek(f,(long)((int)ind[i]-last-1)*(hd+vsz*sizeof(short)),SEEK_CUR); 
        if (DEBUG_VECST) printf("rdmanyDBB %ld ",ftell(f));
        last=(int)ind[i]; 
      }
      r=fread(&n,sizeof(int),2,f);
      r=fread(&sf,sizeof(double),2,f);
      if (n[0]!=vsz){printf("rdmany ERRA vec(%d) %d vs %d\n",iflag?(int)ind[i]:i,vsz,n[0]);hxe();}
      if (n[1]!=code){printf("rdmany ERRB code mismatch %d %d\n",n[1],code);hxe();}
      r=fread(xs,sizeof(short),n[0],f);
      for (j=0;j<vsz;j++) if (vflag) {
            y[i*vsz+j]=(double)(xs[j]/sf[0] + sf[1]);
      } else vvo[i][j]=(double)(xs[j]/sf[0] + sf[1]);
    }
  } else if (code==3) {
    float *xs;
    xs=(float *)scr;
    for (last=-1,i=0;i<num;i++) {
      if (iflag) { 
        fseek(f,(long)((int)ind[i]-last-1)*(hd+vsz*sizeof(float)),SEEK_CUR); 
        last=(int)ind[i]; 
      }
      if (DEBUG_VECST) printf("rdmanyDBC:%ld ",ftell(f));
      r=fread(&n,sizeof(int),2,f);
      if (n[0]!=vsz){printf("rdmany ERRA vec(%d) %d vs %d\n",iflag?(int)ind[i]:i,vsz,n[0]);hxe();}
      if (n[1]!=code){printf("rdmany ERRB code mismatch %d %d\n",n[1],code);hxe();}
      r=fread(xs,sizeof(float),n[0],f);
      for (j=0;j<n[0];j++) if (vflag) {
            y[i*vsz+j]=(double)xs[j];
      } else vvo[i][j]=(double)xs[j];
    }
  } else if (code==4) {
    double *xs;
    xs=(double *)scr;
    for (last=-1,i=0;i<num;i++) {
      if (iflag) { 
        fseek(f,(long)((int)ind[i]-last-1)*(hd+vsz*sizeof(double)),SEEK_CUR); 
        last=(int)ind[i]; 
      }
      if (DEBUG_VECST) printf("rdmanyDBD %ld ",ftell(f));
      r=fread(&n,sizeof(int),2,f);
      if (n[0]!=vsz){printf("rdmany ERRA vec(%d) %d vs %d\n",iflag?(int)ind[i]:i,vsz,n[0]);hxe();}
      if (n[1]!=code){printf("rdmany ERRB code mismatch %d %d\n",n[1],code);hxe();}
      r=fread(xs,sizeof(double),n[0],f); // should just read directly into final array
      for (j=0;j<n[0];j++) if (vflag) y[i*vsz+j]=xs[j]; else vvo[i][j]=xs[j];
    }
  } else printf("rdmany() code %d not implemented\n",code);
  return (double)num;
}
ENDVERBATIM

:* rdfile(FILE,{veclist or vec})
: should check speed for reading in and then later picking up individual vec
: would set up internal global pointers *vvo, *vnq but not copy in till needed
: also would want global size,type,scale,offset -- put all in a struct
VERBATIM
static double rdfile (void* vv) {	
  int i, j, k, ni, vsz, ty, ny, nv, num, cnt, n[2], hd, vflag;
  void* vnq[10000]; size_t r;
  size_t sz;
  char* xc; int *xi; float *xf; double *xd; void* xv; unsigned short* xus;
  Object* ob;
  double *vvo[10000], sf[2], *ind, *y;
  FILE* f;

  vflag=0;
  ni = vector_instance_px(vv, &ind);
  f =     hoc_obj_file_arg(1);
  ob =   *hoc_objgetarg(2);
  if (strncmp(hoc_object_name(ob),"Vector",6)==0) vflag=1;

  fseek(f,0,SEEK_END); sz=(int)ftell(f); rewind(f); // get size
  if (DEBUG_VECST) printf("Size %d\n",sz);
  if (sz>scrsz*sizeof(int)) { 
    if (scrsz>0) { free(scr); scr=(unsigned int *)NULL; }
    scr=(unsigned int *)ecalloc(1, sz);
    scrsz=sz/sizeof(int); // number of chars available
  }

  xc=(char *)scr;
  r=fread(xc,(size_t)sz,1,f);

  if (vflag) {
    ny = vector_arg_px(2, &y);
  } else {
    num = ivoc_list_count(ob);
    if (num>10000) { printf("rdfile ERRA: can only handle 10000 vectors"); hxe();}
    for (i=0;i<num;i++) { 
      nv = list_vector_px3(ob, i, &vvo[i], &vnq[i]);
      if (i==0) vsz=nv;
      if (vsz!=nv){printf("rdfile ERRC: Vectors must all be same size %d %d %d\n",i,vsz,nv);hxe();}
    }
  }
  for (i=0,k=0,cnt=0;i<sz;cnt++) { // increment i from within loop
    xi=(int*) (xc+i);
    vsz=xi[0];
    ty= xi[1]; i+=(2*sizeof(int)); // picked up 2 ints
    if (vsz<=0 || ty<1 || ty>5) {
      printf("rdfile ERRB: bad size/type: %d/%d in vec# %d\n",vsz,ty,cnt); hxe();}
    if (DEBUG_VECST) printf("%d:%d:%d ",i,ty,vsz);
    if (vflag) { // vector
      if (k+vsz>=ny) {
        printf("rdfile ERRC: No more room in vec: %d %d %d %d\n",ny,k+vsz,cnt,ty); hxe(); }
    } else { // a list
      if (cnt>=num) {
        printf("rdfile ERRD: out of vecs: %d %d %d\n",num,cnt,ty); hxe(); }
      if (vsz>nv) {
        printf("rdfile ERRE: No more room in vec: %d %d %d %d\n",nv,vsz,cnt,ty); hxe(); }
    }
    if (ty==3) { // float must be recast
      xf=(float*)(xc+i);
      if (vflag) {
        for (j=0;j<vsz;j++) y[k+j]=(double)xf[j];
        k+=vsz;
      } else { 
        for (j=0;j<vsz;j++) vvo[cnt][j]=(double)xf[j];
        vector_resize(vnq[cnt],vsz);
      }
      i+=(vsz*sizeof(float));
    } else if (ty==4) { // double is just a memcpy
      xv=(void*)(xc+i);
      if (vflag) {
        memcpy((void*)(y+k),xv,(size_t)(vsz*sizeof(double)));
        k+=vsz;
      } else {
        memcpy((void*)(&vvo[cnt][0]),xv,(size_t)(vsz*sizeof(double)));
        vector_resize(vnq[cnt],vsz);
      }
      i+=(vsz*sizeof(double));
    } else if (ty==2) { // short must be shifted and scaled
      xd =(double *)(xc+i); i+=2*sizeof(double);
      for (j=0;j<2;j++) sf[j]=xd[j];
      xus=(unsigned short*)(xc+i);
      if (vflag) {
        for (j=0;j<vsz;j++) y[k+j]=((double)xus[j])/sf[0] + sf[1];
        k+=vsz;
      } else { 
        for (j=0;j<vsz;j++) vvo[cnt][j]=((double)xus[j])/sf[0] + sf[1];
        vector_resize(vnq[cnt],vsz);
      }
      i+=(vsz*sizeof(short));
    } else printf("rdfile() type %d not implemented\n",ty);
  }
  if (vflag) vector_resize(vector_arg(2), k);
  if (scrsz>1e7) { free(scr); scr=(unsigned int *)NULL; scrsz=0; }
  return (double)num;
}
ENDVERBATIM

:* PROCEDURE install_vecst()
PROCEDURE install_vecst () {
  if (VECST_INSTALLED==1) {
    printf("$Id: vecst.mod,v 1.499 2011/07/22 22:16:48 billl Exp $\n")
  } else {
  VECST_INSTALLED=1
  VERBATIM {
  int i,j; 
  install_vector_method("indset", indset);
  install_vector_method("mkind", mkind);
  install_vector_method("circ", circ);
  install_vector_method("thresh", thresh);
  install_vector_method("triplet", triplet);
  install_vector_method("onoff", onoff);
  install_vector_method("bpeval", bpeval);
  install_vector_method("w", w);
  install_vector_method("whi", whi);
  install_vector_method("sedit", sedit);
  install_vector_method("xing", xing);
  install_vector_method("scxing", scxing);
  install_vector_method("cvlv", cvlv);
  install_vector_method("sccvlv", sccvlv);
  install_vector_method("scl", scl);
  install_vector_method("revec", revec);
  install_vector_method("has", has);
  install_vector_method("intrp", intrp);
  install_vector_method("xzero", xzero);
  install_vector_method("peak", peak);
  install_vector_method("negwrap", negwrap);
  install_vector_method("sw", sw);
  install_vector_method("ismono", ismono);
  install_vector_method("count", count);
  install_vector_method("muladd", muladd);
  install_vector_method("binfind", binfind);
  install_vector_method("unq", unq);
  install_vector_method("uniq", uniq);
  install_vector_method("rnd", rnd);
  install_vector_method("fewind", fewind);
  install_vector_method("findx", findx);
  install_vector_method("lma", lma);
  install_vector_method("sindx", sindx);
  install_vector_method("sindv", sindv);
  install_vector_method("nind", nind);
  install_vector_method("keyind", keyind);
  install_vector_method("slct", slct);
  install_vector_method("slor", slor);
  install_vector_method("insct", insct);
  install_vector_method("linsct", linsct);
  install_vector_method("cull", cull);
  install_vector_method("redundout", redundout);
  install_vector_method("mredundout", mredundout);
  install_vector_method("d2v", d2v);
  install_vector_method("v2d", v2d);
  install_vector_method("v2p", v2p);
  install_vector_method("l2p", l2p);
  install_vector_method("fetch", fetch);
  install_vector_method("covar", covar);
  install_vector_method("ixsort", ixsort);
  install_vector_method("vlxpose", vlxpose);
  install_vector_method("b2v", b2v);
  install_vector_method("iwr", iwr);
  install_vector_method("ird", ird);
  install_vector_method("smgs", smgs);
  install_vector_method("smsy", smsy);
  install_vector_method("ident", ident);
  install_vector_method("lcat", lcat);
  install_vector_method("snap", snap);
  install_vector_method("fread2", fread2);
  install_vector_method("vfill", vfill);
  install_vector_method("vrdh", vrdh);
  install_vector_method("mkcode", mkcode);
  install_vector_method("uncode", uncode);
  install_vector_method("sumabs", sumabs);
  install_vector_method("inv", inv);
  install_vector_method("join", join);
  install_vector_method("slone", slone);
  install_vector_method("pop", pop);
  install_vector_method("rdmany", rdmany);
  install_vector_method("rdfile", rdfile);
  install_vector_method("samp", samp);
  install_vector_method("nearest", nearest);
  install_vector_method("nearall", nearall);
  install_vector_method("approx", approx);
  install_vector_method("nqsvt", nqsvt);
  install_vector_method("roton", roton);
  for (i=0,j=5;i<=5;i++,j--) sc[i]=pow(2,10*j);
  }
  ENDVERBATIM
  }
}

:* isojt(OB1,EXAMPLE_OBJ) return whether OB1 is an instance of EXAMPLE_OBJ
FUNCTION isojt () {
  VERBATIM {
  Object *ob1, *ob2;
  ob1 = *hoc_objgetarg(1); ob2 = *hoc_objgetarg(2);
  if (!ob1) if (!ob2) return 1; else return 0;
  if (!ob2 || ob1->template != ob2->template) {
    return 0;
  }
  return 1;
  }
  ENDVERBATIM
}

: isojn(OB1,NAME) return whether OB1 is an instance of EXAMPLE_OBJ
FUNCTION isojn () {
  VERBATIM {
  Object *ob1; char* name;
  ob1 = *hoc_objgetarg(1); name = gargstr(2);
  if (strncmp(hoc_object_name(ob1),name,3)==0) _lisojn=1.; else _lisojn=0.;
  }
  ENDVERBATIM
}

: ojtnum(OBJ) returns object number
: returns internal number of object, eg if vec[3] is Vector[432] returns 432
FUNCTION ojtnum () {
  VERBATIM {
  Object *ob1; char name[50]; int ii;
  ob1 = *hoc_objgetarg(1);
  if (!ob1) return -1;
  if (ifarg(2)) {
    strncpy(name, hoc_object_name(ob1),50);
    for (ii=strlen(name);ii>1;ii--) if (name[ii]==91) {name[ii]=0; break;} // 91 is [
    hoc_assign_str(hoc_pgargstr(2),name);
  }
  return (double)ob1->index;
  }
  ENDVERBATIM
}

: eqojt(OB1,OB2) return whether OB1 and OB2 point to same object
FUNCTION eqojt () {
  VERBATIM {
  Object *ob1, *ob2;
  ob1 = *hoc_objgetarg(1); ob2 = *hoc_objgetarg(2);
  if (ob1 && ob2 && ob1==ob2) {
    return 1;
  }
  return 0;
  }
  ENDVERBATIM
}

:* byteswap(FILE)
FUNCTION byteswap () {
  VERBATIM {
  int n[2]; size_t r;
  double ret;
  FILE* f;
  BYTEHEADER

  f =     hoc_obj_file_arg(1);
  r=fread(&n,sizeof(int),2,f);
  if (n[1] < 1 || n[1] > 5) {
    BYTESWAP_FLAG = 1;
    ret = 1.; 
  } else ret = 0.;
  BYTESWAP(n[1],int)
  if (n[1] < 1 || n[1] > 5) { 
    printf("byteswap: Something wrong with location sampled: %d\n",n[1]);
    ret = -1.;
  }
  fseek(f,-2*sizeof(int),SEEK_CUR); // go back to where we started
  return ret;
  }
  ENDVERBATIM
}


: mkcodf(val1,val2,val3,val4,val5) stuff 5 vals<=999 into a single double
FUNCTION mkcodf () {
  VERBATIM {
  int i;
  double x,a;
  if (ifarg(6)) {printf("mkcodf() ERR: can only encode 5 values\n"); hxe();}
  for (x=0.,i=1;i<=5;i++) { 
    a=(ifarg(i))?*getarg(i):0.0;  
    if (a<0. || a>=sc[4] || floor(a+0.5)!=a) {
      printf("mkcodf restricted to integers %g [0,%g]\n",a,sc[4]-1);hxe(); }
    x+=a*sc[i];
  }
  return x;
  }
  ENDVERBATIM
}

: uncodf(code,i) returns field i (1-5) from code
FUNCTION uncodf () {
  VERBATIM {
  int i;
  double x,ret, *ptr;
  x=*getarg(1);
  if (hoc_is_double_arg(2)) {
    i=(int)*getarg(2);
    if (i<1||i>5) {printf("2nd arg must be field# 1-5 (%d)\n",i); hxe();}
    UNCODE(x,i,ret);
    return ret;
  } else {
    for (i=2;i<=6;i++) if (ifarg(i)) {
      ptr = hoc_pgetarg(i);
      UNCODE(x,i-1,*ptr);
    } else break;
    return *ptr;
  }
  }
  ENDVERBATIM
}

: recodf(i,code,new) replaces field i (1-5) from code with new
FUNCTION recodf () {
  VERBATIM {
  int i;
  double x, y, old;
  i=(int)chkarg(1,1.,5.); x=*getarg(2); y=chkarg(3,0.,sc[4]-1);
  UNCODE(x,i,old);
  return x + sc[i]*(y-old);
  }
  ENDVERBATIM
}

: flor(val)
FUNCTION flor () {
  VERBATIM {
  return floor(*getarg(1));
  }
  ENDVERBATIM
}

: ceilg(val)
FUNCTION ceilg () {
  VERBATIM {
  return ceil(*getarg(1));
  }
  ENDVERBATIM
}

: MINxy(val1,val2)
FUNCTION MINxy () {
  VERBATIM {
  return MIN(*getarg(1),*getarg(2));
  }
  ENDVERBATIM
}

: MAXxy(val1,val2)
FUNCTION MAXxy () {
  VERBATIM {
  return MAX(*getarg(1),*getarg(2));
  }
  ENDVERBATIM
}

:* PROCEDURE fspitchar
PROCEDURE fspitchar(c) {
VERBATIM
{	
  FILE* f;
  f = hoc_obj_file_arg(2);
  fprintf(f, "%c", (int)_lc);
}
ENDVERBATIM
}

:* PROCEDURE fgchar
FUNCTION fgchar() {
VERBATIM
{	
  FILE* f;
  f = hoc_obj_file_arg(1);
  _lfgchar = (double)fgetc(f);
}
ENDVERBATIM
}

:* FUNCTION Str2Num takes a string arg and returns the # as a double
FUNCTION Str2Num () {
VERBATIM
{
  double d;
  char* c;
  c = gargstr(1);
  d = atof(c);
  return d;
}
ENDVERBATIM
}

:* FUNCTION vlsz() resize all the vectors in a list
FUNCTION vlsz () {
VERBATIM
{	
  int i,j,c,n; double *x, sz, fill; void *vv;
  ListVec* pL; Object* obl;
  pL = AllocListVec(obl=*hoc_objgetarg(1));
  sz=*getarg(2);
  if (ifarg(3)) fill=*getarg(3); else fill=OK;
  c=pL->isz;     // list length
  for (i=0;i<c;i++) {
    pL->pv[i]=list_vector_resize(obl, i, (int)sz);
    if (fill!=OK) for (j=0;j<(int)sz;j++) pL->pv[i][j]=fill;
  }
  FreeListVec(&pL);
  _lvlsz = (double)sz*c;
}
ENDVERBATIM
}

VERBATIM
void FreeListVec(ListVec** pp) {
  ListVec* p = *pp;
  if(p->pv){
    free(p->pv);
    p->pv=0;
  }
  if(p->plen){
    free(p->plen);
    p->plen=0;
  }
  free(p);
  *pp=0;
}

ListVec* AllocListVec (Object* p) {
  int i, iSz; ListVec* pList;  Object* obv;
  if(!IsList(p)){printf("AllocListVec ERRA: arg must be list object!\n"); hxe();}
  pList = (ListVec*)malloc(sizeof(ListVec));
  if(!pList) hxe();
  pList->pL=p; pList->isz=0;  pList->pv=0;  pList->plen=0;
  iSz = pList->isz = ivoc_list_count(p);
  if(iSz < 1) return pList;
  pList->plen = (unsigned int*)malloc(sizeof(int)*iSz);
  if(!pList->plen){printf("AllocListVec ERRB: Out of memory!\n"); hxe();}
  pList->pbuflen = (unsigned int*)malloc(sizeof(int)*iSz);
  pList->pv = (double**)malloc(sizeof(double*)*iSz);
  if(!pList->pv){free(pList->plen); printf("AllocListVec ERRC: Out of memory!\n"); hxe();}
  for(i=0;i<pList->isz;i++) {
    obv = ivoc_list_item(p,i);
    pList->pv[i]=vector_vec(obv->u.this_pointer);
    pList->plen[i]=vector_capacity(obv->u.this_pointer);
    pList->pbuflen[i]=vector_buffer_size(obv->u.this_pointer);;
  }
  return pList;
}

// Allocate a list vec that is indexed
ListVec* AllocILV (Object* p, int nx, double *x) {
  int i, j, iSz, ilc; ListVec* pList; Object* obv;
  if(!IsList(p)){printf("AllocILV ERRA: arg must be list object!\n"); hxe();}
  pList = (ListVec*)malloc(sizeof(ListVec));
  if(!pList) hxe();
  pList->pL=p; iSz=pList->isz=nx; pList->pv=0;  pList->plen=0;
  ilc=ivoc_list_count(p);
  if(iSz<1) return pList;
  pList->plen = (unsigned int*)malloc(sizeof(int)*iSz);
  if(!pList->plen){printf("AllocILV ERRB: Out of memory!\n"); hxe();}
  pList->pbuflen = (unsigned int*)malloc(sizeof(int)*iSz);
  pList->pv = (double**)malloc(sizeof(double*)*iSz);
  if(!pList->pv){free(pList->plen); printf("AllocILV ERRC: Out of memory!\n"); hxe();}
  for(i=0;i<iSz;i++){
    if ((j=(int)x[i])>=ilc){printf("AllocILV ERRD: index OOB: %d>=%d\n",j,ilc); hxe();}
    obv = ivoc_list_item(p,j);
    pList->pv[i]=vector_vec(obv->u.this_pointer);
    pList->plen[i]=vector_capacity(obv->u.this_pointer);
    pList->pbuflen[i]=vector_buffer_size(obv->u.this_pointer);;
  }
  return pList;
}

void ListVecResize (ListVec* p,int newsz) {
  int i,j; Object* obv;
  for(i=0;i<p->isz;i++){
    obv = ivoc_list_item(p->pL, i);
    p->pv[i]=vector_newsize(obv->u.this_pointer,newsz);
    p->plen[i]=newsz;
  }
}

void FillListVec (ListVec* p,double dval) {
  int i,j;
  for(i=0;i<p->isz;i++){
    for(j=0;j<p->plen[i];j++){
      p->pv[i][j]=dval;
    }
  }
}

int IsObj (Object* p,char* s){
  if(!p) return 0;
  if(!s || !strlen(s)) return 0;
  return !strncmp(hoc_object_name(p),s,strlen(s));
}
int IsVector (Object* p){ return IsObj(p,"Vector"); }
int IsList (Object* p){return IsObj(p,"List"); }

int** getint2D(int rows,int cols) {
  int **pp,*pool,*curPtr; int i;
  pp = (int**) malloc(sizeof(int*)*rows);
  if(!pp) { printf("ERR: out of memory!\n"); return 0x0; }
  pool = (int*) malloc(sizeof(int)*rows*cols);
  if(!pool) { printf("ERR: out of memory!\n"); free(pp); return 0x0; }
  curPtr = pool;
  for(i = 0; i < rows; i++) {
    pp[i] = curPtr;
    curPtr += cols;
  }
  return pp;
}

void freeint2D(int*** ppp,int rows) {
  int** pp;
  pp = *ppp;
  free(pp[0]);
  free(pp);
  *ppp = 0;
}

double** getdouble2D(int rows,int cols) {
  double **pp,*pool,*curPtr; int i;
  pp = (double**) malloc(sizeof(double*)*rows);
  if(!pp) { printf("ERR: out of memory!\n"); return 0x0; }
  pool = (double*) malloc(sizeof(double)*rows*cols);
  if(!pool) { printf("ERR: out of memory!\n"); free(pp); return 0x0; }
  curPtr = pool;
  for(i = 0; i < rows; i++) {
    pp[i] = curPtr;
    curPtr += cols;
  }
  return pp;
}

void freedouble2D(double*** ppp,int rows) {
  double** pp;
  pp = *ppp;
  free(pp[0]);
  free(pp);
  *ppp = 0;
}

ENDVERBATIM
