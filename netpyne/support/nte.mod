: $Id: infot.mod,v 1.161 2010/08/19 20:02:27 samn Exp $ 

NEURON {
  SUFFIX nte
  GLOBAL installed,beg,end
  GLOBAL verbose
  GLOBAL MINEXP,MAXEXP,MINLOG2,MAXLOG2,count,cutoff,binmin,binmax
}

PARAMETER {
  installed = 0
  verbose = 0.5
  useslice = 0 : whether to look @ beg,end variables for vector slices
  beg = 0 : for doing vector slices from [beg,end)
  end = 0
  MINEXP=-20
  MAXEXP=20
  MINLOG2=0.001
  MAXLOG2=32
  count=0
  cutoff=0.2 : ignore hist pairs that are not similar
  binmin=0 : ignore hists not filling out this % of the entries
  binmax=0 : ignore hists filling out more than this % of the entries
  KTProb=0 : use Krichevsky-Trofimov probability estimates p(n)=(n+.5)/(N+.5*jmax)
}

VERBATIM
// misc.h copied here
// $Id: misc.h,v 1.38 2011/11/02 15:26:48 billl Exp $

#include <stdlib.h>
#include <math.h>
#include <limits.h> /* contains LONG_MAX */
#include <time.h>
#include <sys/time.h> 
#include <values.h>
#include <pthread.h>

#if !defined(t)
  #define _pval pval
#endif

typedef struct LISTVEC {
  int isz;
  Object* pL;
  double** pv;
  unsigned int* plen;
  unsigned int* pbuflen;
} ListVec;

typedef struct BVEC {
 int size;
 int bufsize;
 short *x;
 Object* o;
} bvec;

#define BYTEHEADER int _II__;  char *_IN__; char _OUT__[16]; int BYTESWAP_FLAG=0;
#define BYTESWAP(_X__,_TYPE__) \
    if (BYTESWAP_FLAG == 1) { \
  _IN__ = (char *) &(_X__); \
  for (_II__=0;_II__<sizeof(_TYPE__);_II__++) { \
    _OUT__[_II__] = _IN__[sizeof(_TYPE__)-_II__-1]; } \
  (_X__) = *((_TYPE__ *) &_OUT__); \
    }

#define UNCODE(_X_,_J_,_Y_) {(_Y_)=floor((_X_)/sc[(_J_)])/sc[4]; \
                             (_Y_)=floor(sc[4]*((_Y_)-floor(_Y_))+0.5);}
#define MIN(X,Y) ((X) < (Y) ? (X) : (Y))
#define MAX(X,Y) ((X) > (Y) ? (X) : (Y))

//square root of 2 * PI
#define SQRT2PI 2.5066282746310002416
//ln(2), base e log of 2
#define LG2 0.69314718055994530941723212145818
#define VRRY 200
#define ISVEC(_OB__) (strncmp(hoc_object_name(_OB__),"Vector",6)==0)
#define dmaxuint 4294967295. // for 32 bits

// Andre Fentons cast designations
typedef unsigned char ui1;  /* one byte unsigned integer */
typedef char    si1;  /* one byte signed integer */
typedef unsigned short  ui2;  /* two byte unsigned integer */
typedef short   si2;  /* two byte signed integer */
typedef unsigned int  ui4;  /* four byte unsigned integer */ 
typedef int   si4;  /* four byte signed integer */ 
typedef float   sf4;  /* four byte signed floating point number */ 
typedef double    sf8;  /* eight byte signed floating point number */ 

extern double ERR,GET,SET,OK,NOP,ALL,NEG,POS,CHK,NOZ,GTH,GTE,LTH,LTE,EQU;
extern double EQV,EQW,EQX,NEQ,SEQ,RXP,IBE,EBI,IBI,EBE;

extern double *vector_newsize();
extern unsigned int  dcrsz;
extern double       *dcr;
extern double       *dcrset(int);
extern unsigned int  scrsz;
extern unsigned int *scr;
extern unsigned int *scrset(int);
extern unsigned int  iscrsz;
extern int *iscr;
extern int *iscrset(int);
extern double BVBASE;
extern double* hoc_pgetarg();
extern void hoc_notify_iv();
extern double hoc_call_func(Symbol*, int narg);
extern FILE* hoc_obj_file_arg(int narg);
extern Object** hoc_objgetarg();
char *gargstr();
char** hoc_pgargstr();
extern void vector_resize();
extern int vector_instance_px();
extern void* vector_arg();
extern double* vector_vec();
extern int vector_buffer_size(void*);
extern double hoc_epsilon;
extern int stoprun;
extern void set_seed();
extern void dshuffle(double* x,int nx);
extern void mcell_ran4_init(u_int32_t);
extern double mcell_ran4(u_int32_t *idx1, double *x, unsigned int n, double range);
extern int nrn_mlh_gsort();
extern int ivoc_list_count(Object*);
extern Object* ivoc_list_item(Object*, int);
extern int list_vector_px2();
extern int hoc_is_double_arg(int narg);
extern int hoc_is_str_arg(int narg);
extern int hoc_is_object_arg(int narg);
extern int hoc_is_pdouble_arg(int narg);
extern Symbol *hoc_get_symbol(char *);
extern Symbol *hoc_lookup(const char*);
extern Point_process* ob2pntproc(Object*);

extern char* hoc_object_name(Object*);
extern int cmpdfn();
extern int openvec(int, double **);
int list_vector_px();
double *list_vector_resize();
static void hxe() { hoc_execerror("",0); }
extern void FreeListVec(ListVec** pp);
extern ListVec* AllocListVec(Object* p);
extern ListVec* AllocILV(Object*, int, double *);
void FillListVec(ListVec* p,double dval);
void ListVecResize(ListVec* p,int newsz);
extern short *nrn_artcell_qindex_;
extern double nrn_event_queue_stats(double*);
extern void clear_event_queue();

static double sc[6];
static FILE*  testout;

//* in vecst.mod
extern int** getint2D(int rows,int cols);
extern void freeint2D(int*** ppp,int rows);
extern double** getdouble2D(int rows,int cols);
extern void freedouble2D(double*** ppp,int rows);
extern double ismono1 (double *x, int n, int flag);

//* in stats.mod
double kcorfast(double* input1, double* input2, double* i1d , double* i2d,int n,double* ps);
double Rktau (double* x, double* y, int n); // R version
double kcorfast (double* input1, double* input2, double* i1d , double* i2d,int n,double* ps);

// end of misc.h


// from vecst.mod: Maintain parallel int vector to avoid slowness of repeated casts 
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

// end of from vecst.mod


// from stats.mod
static u_int32_t ilow=0;  
static u_int32_t ihigh=0;

//shuffle array of unsigned ints
void ishuffle(int* x,int nx) {
  int n,k,temp; double y[1];
  for (n=nx;n>1;) {
    mcell_ran4(&ihigh, y, 1, n);
    n--;
    k=(int)y[0]; // random int(n) // 0 <= k < n.
    temp = x[n];
    x[n] = x[k];
    x[k] = temp;
  }  
}

// end of stats.mod

static const double* ITsortdata = NULL; /* used in the quicksort algorithm */
static double tetrospks2(), pdfpr(), tetrospks3();
static int dbxi[10];


double log2d ( double d ) {
  return log(d) / LG2;
}

// for debugging -- print out a pdf
static double pdfpr (double* pdf,int szp,int dim, char* name) {
  double x,ds; int i,j,k,l,m,cnt,*nonzero;
  ds=0.; 
  printf("Contents of PDF %s\n",name);
  if (dim>2) { // may also use for higher dims if ever both with these
    nonzero=(int *)calloc(szp,sizeof(int));
    for(k=0,cnt=0;k<szp;k++) { // top dim
      for(l=0;l<szp;l++) for (m=0;m<szp;m++) if (pdf[k*szp*szp+l*szp+m]>0.) cnt++;
      if (cnt>0) nonzero[k]=1; // will need to print this slice
    }
  }
  if (dim==1) {
    for(m=0;m<szp;m++) { printf("%g ",pdf[m]); ds+=pdf[m]; }
  } else if (dim==2) {
    for(l=0;l<szp;l++) { 
      for(m=0;m<szp;m++) { printf("%g ",pdf[l*szp+m]); ds+=pdf[l*szp+m]; }
      printf("\n");
    }
  } else { // dim==3
    for (k=0;k<szp;k++) if (nonzero[k]==1) { 
      printf("\tSlice #%d:\n",k); 
      for(l=0;l<szp;l++) { 
        for(m=0;m<szp;m++) { printf("%g ",(x=pdf[k*szp*szp+l*szp+m])); ds+=x; }
        printf("\n");
      }
    }
  }
  printf("ds (%s) = %g\n",name,ds);
  return 0.0;
}


//* X1spikecounts.tentropspks(X2spikecounts,[outputvec,numshuffles,X3spikecounts])
// computes the transfer entropy of X1 -> X2, values in vecs must be discrete & non-negative
// output vec will store 0) transfer entropy, 1) H(X2F|X2P) , X2's entropy conditioned on its past
// can be used to calculate the normalized transfer entropy (NTE), which is
// (TE - TEShuffled)/H(X2F|X2P) and is in range 0,1 inclusive
// when X3spikecounts is present, calculated transfer entropy
// of X1spikecounts,X2spikecounts onto X3spikecounts
static double tentropspks (void* vv) {
  double *X1,*X2,*XO,*X3; int szX1,szX2,szXO,shuf,szX3;
  szX1 = vector_instance_px(vv,&X1);
  if((szX2=vector_arg_px(1,&X2))!=szX1) {
    printf("tentropspks ERRA: X1,X2 must have same size (%d,%d)\n",szX1,szX2); return -1.0; }
  szXO=ifarg(2)?vector_arg_px(2,&XO):0;
  shuf=ifarg(3)?((int)*getarg(3)):0;
  szX3=ifarg(4)?vector_arg_px(4,&X3):0;
  if(szX3) tetrospks3(X1,X2,X3,XO,szX1,szXO,shuf);
  else return tetrospks2(X1,X2,XO,szX1,szXO,shuf);
}

//** entropxfgxpd - get conditional entropy of X future given its past: H(XF|XP)
// H(XF|XP)=-sum(p(XF,XP)*log(p(XF|XP)))=-sum(p(XF,XP)*log(p(XF,XP)/p(XP)))
// XF = future value of X, XP = past value of X
double entropxfgxpd (double* pXP, double* pXFXP,int minv,int maxv,int szp) {
  static double tmp[4];
  int k,l;
  //*** normalize on unshuffled with H(X2F|X2P); NB only X1 is being shuffled anyway:
  for(tmp[0]=0.,k=minv;k<=maxv;k++) for(l=minv;l<=maxv;l++) {
    tmp[1]=pXP[l];  tmp[2]=pXFXP[k*szp+l]; 
    if(tmp[1]>0. && tmp[2]>0.) { tmp[3] = tmp[2]/tmp[1]; 
      if (usetable && tmp[3]>=MINLOG2 && tmp[3]<=MAXLOG2) {
        tmp[0] -=tmp[2]*_n_LOG2(tmp[3]);
      } else {  tmp[0] -=tmp[2]*  log2d(tmp[3]); if (usetable&&verbose>0.4) { 
          printf("WARNA:%g outside of [%g,%g] TABLE\n",tmp[3],MINLOG2,MAXLOG2); }}}}
  return tmp[0];        
}

//** entropxfgxp - get conditional entropy of X future given its past: H(XF|XP)
// Vector has elements of X
static double entropxfgxp (void* vv) {
  double *x,*pXP,*pXFXP,dret;
  int sz,minv,maxv,cnt,i,j,szp,*X;
  sz = vector_instance_px(vv,&x);
  cnt=0;
  X=scrset(sz);
  minv=1e9; maxv=-1e9;
  for (i=0;i<sz;i++) { 
    X[i]=(int)x[i]; 
    if (X[i]>0) cnt++;   
    if (X[i]>maxv) maxv=X[i];  if (X[i]<minv) minv=X[i]; 
  }  
  if (minv<0) {
    printf("entropxfgxp ERRA: minimum value must be >= 0:%d\n",minv);hxe();}  
  szp = maxv + 1;
  pXFXP = (double*) calloc(szp*szp,sizeof(double));
  pXP = (double*) calloc(szp,sizeof(double));
  for(i=1;i<sz;i++) pXP[ X[i-1] ]++; // calculate XP
  for(i=minv;i<=maxv;i++) pXP[i] /= (sz-1);
  if (verbose>2) pdfpr(pXP,szp,1,"pXP");
  for(i=0;i<sz-1;i++) pXFXP[ X[i+1]*szp + X[i] ]++; // X future, X past
  for(i=minv;i<=maxv;i++) for(j=minv;j<=maxv;j++) pXFXP[i*szp+j]/=(sz-1);
  if (verbose>3) pdfpr(pXFXP,szp,2,"pXFXP");
  dret = entropxfgxpd(pXP,pXFXP,minv,maxv,szp);
  free(pXP); free(pXFXP);
  return dret;
}

//** entropx2fgx2px1p - get conditional entropy of X2 future given its past and X1's past:H(X2F|X2P,X1P)
// H(X2F|X2P,X1P) = -sum( p(X2F,X2P,X1P) * log( p(X2F,X2P,X1P) / p(X2P,X1P) ) )
double entropx2fgx2px1pd (double* pX2FX2PX1P, double* pX2PX1P, int minv1, int maxv1, int minv2, int maxv2, int szp) {
  static double tmp[4];
  double ent = 0.0;
  int l,k,m;
  for(l=minv2;l<=maxv2;l++) for(k=minv2;k<=maxv2;k++) for(m=minv1;m<=maxv1;m++) {  
    tmp[0]=pX2FX2PX1P[k*szp*szp+l*szp+m]; tmp[1]=pX2PX1P[l*szp+m];
    if (tmp[0]>1e-9 && tmp[1]>1e-9) {
      tmp[2] = tmp[0] / tmp[1];
      if (usetable && tmp[2]>=MINLOG2 && tmp[2]<=MAXLOG2) {
        ent -= tmp[0]*_n_LOG2(tmp[2]);
      } else {    ent -= tmp[0] * log2d(tmp[2]);
        if (usetable&&verbose>0.4) {
          printf("WARNB:%g outside of [%g,%g] TABLE (",tmp[2],MINLOG2,MAXLOG2) ; 
          printf("%g, %g, %g)\n",tmp[0],tmp[1],tmp[2]); }
      }
      if(verbose>2){printf("tmp0=%g, tmp1=%g, tmp2=%g\n",tmp[0],tmp[1],tmp[2]);
        printf("l2d:%g\n",log2d(tmp[2])); printf("ent:%g\n",ent); }
    }
  }
  return ent;
}

//** entropx3fgx1px2px3p - get conditional entropy of X3 future given its past and X1,X2's past:H(X3F|X1P,X2P,X3P)
// H(X3F|X1P,X2P,X3P) =  -sum( p(X3F,X1P,X2P,X3P) * log( p(X3F,X1P,X2P,X3P) / p(X1P,X2P,X3P) )
double entropx3fgx1px2px3pd (double* pX3FX1PX2PX3P, double* pX1PX2PX3P, 
                            int minv1, int maxv1, int minv2, int maxv2, int minv3, int maxv3, int szp) {
  static double tmp[4];
  double ent = 0.0;
  int l,k,m,n;
  for(l=minv3;l<=maxv3;l++) for(k=minv1;k<=maxv1;k++) for(m=minv2;m<=maxv2;m++) for(n=minv3;n<=maxv3;n++) {  
    tmp[0]=pX3FX1PX2PX3P[l*szp*szp*szp+k*szp*szp+m*szp+n]; tmp[1]=pX1PX2PX3P[k*szp*szp+m*szp+n];
    if (tmp[0]>1e-9 && tmp[1]>1e-9) {
      tmp[2] = tmp[0] / tmp[1];
      if (usetable && tmp[2]>=MINLOG2 && tmp[2]<=MAXLOG2) {
        ent -= tmp[0]*_n_LOG2(tmp[2]);
      } else {    ent -= tmp[0] * log2d(tmp[2]);
        if (usetable&&verbose>0.4) {
          printf("WARNB:%g outside of [%g,%g] TABLE (",tmp[2],MINLOG2,MAXLOG2) ; 
          printf("%g, %g, %g)\n",tmp[0],tmp[1],tmp[2]); }
      }
      if(verbose>2){printf("tmp0=%g, tmp1=%g, tmp2=%g\n",tmp[0],tmp[1],tmp[2]);
        printf("l2d:%g\n",log2d(tmp[2])); printf("ent:%g\n",ent); }
    }
  }
  return ent;
}

// count # of non-zero elements in a pdf
double pdfnz (double* pdf, int szp, int dim) {
  double x,ds,cnt; int i,j,k,l,m,n;
  cnt = 0.0;
  if(dim==1) {
    for(m=0;m<szp;m++) if(pdf[m]>0.0) cnt+=1.0;
  } else if(dim==2) {
    for(l=0;l<szp;l++) for(m=0;m<szp;m++) if(pdf[l*szp+m]>0.0) cnt+=1.0;
  } else if(dim==3) {
    for(k=0;k<szp;k++) for(l=0;l<szp;l++) for(m=0;m<szp;m++) if(pdf[k*szp*szp+l*szp+m]>0.0) cnt+=1.0;
  } else if(dim==4) {
    for(k=0;k<szp;k++) for(l=0;l<szp;l++) for(m=0;m<szp;m++) for(n=0;n<szp;n++) {
      if(pdf[k*szp*szp*szp+l*szp*szp+m*szp+n]>0.0) cnt+=1.0; }
  } else {
    printf("pdfnz WARNA: invalid dim=%d for pdf!\n",dim);
  }
  return cnt;
}

//** tetrospks3() -- another helper function for tentrospks()
// calculates H(X3F|X3P) - H(X3F|X1P,X2P,X3P)
// H(X3F|X1P,X2P,X3P) =  -sum( p(X3F,X1P,X2P,X3P) * log( p(X3F,X1P,X2P,X3P) / p(X1P,X2P,X3P) )
// H(X3F|X3P) = -sum( p(X3F,X3P) * log(p(X3F,X3P) / p(X3P) ) )
//
// pX3FX3P , pX3P, pX3FX1PX2PX3P,  pX1PX2PX3P
//
static double tetrospks3 (double* X1d,double* X2d,double* X3d,double* XO,int szX1,int szXO,int shuf) {
 
  double *pX3FX3P , *pX3P, *pX3FX1PX2PX3P, *pX1PX2PX3P, te, ds, tmp[5], mout[200], mean, norm, teout;
  double cnt1,cnt2,cnt3,jmax,N; 
  int i,j,k,l,m,n,sz,szp,*X1,*X2,*X3,minv1,maxv1,minv2,maxv2,minv3,maxv3;

  if (shuf>200) {printf("tetrospks3 INTERR nshuf (%d) >200\n",shuf); hxe();}
  if(useslice) { // if doing a slice of the vector
    if (end>0.0 && end<=szX1) szX1=(int)end; 
    printf("WARNING: using newly modified useslice capability\n");
  } else end=beg=0;
  sz=szX1-(int)beg; // max index
  X1=iscrset(sz*3); X2=X1+sz; X3=X1+2*sz;// move into integer arrays
  if(verbose>3) printf("X1:%p , X2:%p, X3:%p:%p\n",X1,X2,X3);
  minv1=minv2=minv3=INT_MAX; maxv1=maxv2=maxv3=INT_MIN; cnt1=cnt2=cnt3=0;
  for (i=0;i<sz;i++) { 
    X1[i]=(int)X1d[i+(int)beg]; X2[i]=(int)X2d[i+(int)beg]; X3[i]=(int)X3d[i+(int)beg];
    if (X1[i]>0) cnt1++; if (X2[i]>0) cnt2++; if(X3[i]>0) cnt3++;
    if (X1[i]>maxv1) maxv1=X1[i];  if (X1[i]<minv1) minv1=X1[i]; 
    if (X2[i]>maxv2) maxv2=X2[i];  if (X2[i]<minv2) minv2=X2[i]; 
    if (X3[i]>maxv3) maxv3=X3[i];  if (X3[i]<minv3) minv3=X3[i]; 
  }
  if (minv1<0 || minv2<0 || minv3<0) {
    printf("tetrospks3 ERRB: minimum value must be >= 0:%d,%d,%d\n",minv1,minv2,minv3);hxe();}
  count+=1;
  if (minv1==maxv1 || minv2==maxv2 || minv3==maxv3) { // no variation return 0,1
    if(verbose>0) printf("tetrospks3 WARN0: #1:%d,%d,#2:%d,%d,#3:%d,%d)\n",minv1,maxv1,minv2,maxv2,minv3,maxv3);
    for (i=0;i<szXO;i++) XO[i]=0.0; if(szXO>=4+shuf)XO[shuf+3]=1.0; return 0.; }
  szp=(maxv1>maxv2)?(maxv1+1):(maxv2+1); if(maxv3+1>szp) szp=maxv3+1;
  if(verbose>1){printf("minv1:%d,maxv1:%d,cnt1:%g\n",minv1,maxv1,cnt1);
                printf("minv2:%d,maxv2:%d,cnt2:%g\n",minv2,maxv2,cnt2);
                printf("minv3:%d,maxv3:%d,cnt3:%g\n",minv3,maxv3,cnt3);}
  pX3P = (double*) calloc(szp,sizeof(double));
  pX3FX3P = (double*) calloc(szp*szp,sizeof(double));
  pX1PX2PX3P = (double*) calloc(szp*szp*szp,sizeof(double));
  pX3FX1PX2PX3P = (double*) calloc(szp*szp*szp*szp,sizeof(double));

  // only need to do the X3 stuff once since only shuffle X1
  for(k=1;k<sz;k++) pX3P[ X3[k-1] ]++; // calculate X3P -- only once
  if(KTProb) { jmax=pdfnz(pX3P,szp,1); for(k=minv3;k<=maxv3;k++) if(pX3P[k]>0.0) {
      pX3P[k] = (0.5+pX3P[k]) / ( sz-1.0 + 0.5*jmax );}
  } else for(k=minv3;k<=maxv3;k++) pX3P[k] /= (sz-1);

  if (verbose>2) pdfpr(pX3P,szp,1,"pX3P");

  for(k=0;k<sz-1;k++) pX3FX3P[ X3[k+1]*szp + X3[k] ]++; // X3 future, X3 past

  if(KTProb) { jmax=pdfnz(pX3FX3P,szp,2); 
    for(k=minv3;k<=maxv3;k++) for(l=minv3;l<=maxv3;l++) if(pX3FX3P[k*szp+l]>0.0){
      pX3FX3P[k*szp+l] = (pX3FX3P[k*szp+l]+0.5) / ( sz-1.0 + 0.5*jmax ); }
  } else for(k=minv3;k<=maxv3;k++) for(l=minv3;l<=maxv3;l++) pX3FX3P[k*szp+l]/=(sz-1);
  if (verbose>3) pdfpr(pX3FX3P,szp,2,"pX3FX3P");

  //*** normalize on unshuffled with H(X3F|X3P); NB only X1,X2 is being shuffled anyway:

  norm=entropxfgxpd(pX3P,pX3FX3P,minv3,maxv3,szp);               

  if (verbose>2) printf("H(X3F|X3P)=%g\n",norm);

  for (j=0,mean=0.;j<=shuf;j++) {

    //*** create X1 requiring pdfs: pX2PX1P, pX2FX2PX1P
    if (j>0) { ishuffle(X1,sz); ishuffle(X2,sz); // shuffle and then reset pdfs 
      memset(pX1PX2PX3P,0,sizeof(double)*szp*szp*szp); 
      memset(pX3FX1PX2PX3P,0,sizeof(double)*szp*szp*szp*szp); }
    for(l=1;l<sz;l++) pX1PX2PX3P[ X1[l-1]*szp*szp +X2[l-1]*szp + X3[l-1] ]++;  // X1 past, X2 past, X3 past
    if(KTProb) {jmax=pdfnz(pX1PX2PX3P,szp,3); 
      for(l=minv1;l<=maxv1;l++) for(m=minv2;m<=maxv2;m++) for(n=minv3;n<=maxv3;n++) if(pX1PX2PX3P[l*szp*szp+m*szp+n]>0.0){
        pX1PX2PX3P[l*szp*szp+m*szp+n] = ( pX1PX2PX3P[l*szp*szp+m*szp+n] + 0.5 ) / ( sz-1.0 + 0.5*jmax ); }
    } else for(l=minv1;l<=maxv1;l++) for(m=minv2;m<=maxv2;m++) for(n=minv3;n<=maxv3;n++) pX1PX2PX3P[l*szp*szp+m*szp+n]/=(sz-1);
    if (verbose>3) pdfpr(pX1PX2PX3P,szp,3,"pX1PX2PX3P");

    //*** init X3 future, X1 past, X2 past
    for(k=0;k<sz-1;k++) pX3FX1PX2PX3P[ X3[k+1]*szp*szp*szp + X1[k]*szp*szp + X2[k]*szp + X3[k] ]++; 
    if(KTProb){jmax=pdfnz(pX3FX1PX2PX3P,szp,4);
      for(k=minv3;k<=maxv3;k++)for(l=minv1;l<=maxv1;l++)for(m=minv2;m<=maxv2;m++)for(n=minv3;n<=maxv3;n++){
        if(pX3FX1PX2PX3P[k*szp*szp*szp+l*szp*szp+m*szp+n]>0.0){
          pX3FX1PX2PX3P[k*szp*szp*szp+l*szp*szp+m*szp+n]=(pX3FX1PX2PX3P[k*szp*szp*szp+l*szp*szp+m*szp+n]+0.5)/(sz-1.0 + 0.5*jmax);}}
    } else for(k=minv3;k<=maxv3;k++) for(l=minv1;l<=maxv1;l++) for(m=minv2;m<=maxv2;m++) for(n=minv3;n<=maxv3;n++) {
      pX3FX1PX2PX3P[k*szp*szp*szp+l*szp*szp+m*szp+n]/=(sz-1);  }
    if (verbose>3) pdfpr(pX3FX1PX2PX3P,szp,4,"pX3FX1PX2PX3P");

    //*** calculate log2
    te = norm - entropx3fgx1px2px3pd(pX3FX1PX2PX3P,pX1PX2PX3P,minv1,maxv1,minv2,maxv2,minv3,maxv3,szp);
    if (j>0) {mean+=te; mout[j-1]=te;} else teout=te; // saving these for now -- don't need to
  }
  if (shuf>0) mean/=shuf;
  if (szXO>0) XO[0]=teout; if (szXO>1) XO[1]=norm; if (szXO>2) XO[2]=mean;
  if (szXO>=3+shuf) for (i=0;i<shuf;i++) XO[i+3]=mout[i];
  if (szXO>=4+shuf && shuf>0) { //get p-value, low means unlikely te due to chance
    cnt1 = 0.0; 
    for(i=0;i<shuf;i++) if(teout < XO[i+3]) {cnt1+=1.0; if(verbose>2)printf("teout:%g, XO[%d]=%g\n",teout,i+3,XO[i+3]);}
    XO[shuf+3] = cnt1 / (double)shuf;
    if(verbose>2) printf("cnt1=%g, shuf=%d, XO[%d]=%g\n",cnt1,shuf,shuf+3,XO[shuf+3]);
  }
  if(verbose>2) printf("te=%g\n",te);
  free(pX3P); free(pX3FX3P); free(pX1PX2PX3P); free(pX3FX1PX2PX3P);
  return (teout-mean)/norm;
}

//** tetrospks2() -- helper function for tentrospks()
// sum( p(X2F, X2P, X1P) * log( p(X2F, X2P, X1P) * p(X2P) / ( p(X2P, X1P) * p(X2F, X2P) ) ) )
    // H(X2F|X2P)=-sum(p(X2F,X2P)*log(p(X2F|X2P)))=-sum(p(X2F,X2P)*log(p(X2F,X2P)/p(X2P)))
    // calculate p(X2F,X2P) and p(X2P), so can just sum up their entropy
    // tmp[0] will store the conditional entropy below
static double tetrospks2 (double* X1d,double* X2d,double* XO,int szX1,int szXO,int shuf) {
  double *pX2P,*pX2FX2PX1P,*pX2PX1P,*pX2FX2P,te,ds,tmp[5],mout[200],mean,norm,teout;
  double cnt1,cnt2,jmax,N; int i,j,k,l,m,sz,szp,*X1,*X2,minv1,maxv1,minv2,maxv2;
  if (shuf>200) {printf("tetrospks2 INTERR nshuf (%d) >200\n",shuf); hxe();}
  if(useslice) { // if doing a slice of the vector
    if (end>0.0 && end<=szX1) szX1=(int)end; 
    printf("WARNING: using newly modified useslice capability\n");
  } else end=beg=0;
  sz=szX1-(int)beg; // max index
  X1=iscrset(sz*2); X2=X1+sz; // move into integer arrays
  if(verbose>3) printf("X1:%p , X2:%p\n",X1,X2);
  minv1=minv2=INT_MAX; maxv1=maxv2=INT_MIN; cnt1=cnt2=0;
  if(verbose>2) printf("before: minv1=%d ,maxv1=%d, minv2=%d, maxv2=%d\n",minv1,maxv1,minv2,maxv2);
  for (i=0;i<sz;i++) { 
    X1[i]=(int)X1d[i+(int)beg]; X2[i]=(int)X2d[i+(int)beg];
    if (X1[i]>0) cnt1++;           if (X2[i]>0) cnt2++; 
    if (X1[i]>maxv1) maxv1=X1[i];  if (X1[i]<minv1) minv1=X1[i]; 
    if (X2[i]>maxv2) maxv2=X2[i];  if (X2[i]<minv2) minv2=X2[i]; 
  }
  if(verbose>2) printf("after: minv1=%d ,maxv1=%d, minv2=%d, maxv2=%d\n",minv1,maxv1,minv2,maxv2);
  if (minv1<0 || minv2<0) {
    printf("tentropspks ERRB: minimum value must be >= 0:%d,%d\n",minv1,minv2);hxe();}
  if (binmin) { 
    cnt1/=sz; cnt2/=sz; // ignore if not enough of the windows are filled
    if (cnt1<binmin) return -11.; else if (cnt2<binmin) return -12.;
    if (binmax) if (cnt1>binmax) return -11.; else if (cnt2>binmax) return -12.;
    if (abs(cnt1-cnt2)>cutoff) return -13.;
  }
  if(verbose>2)printf("tentropspks:minv1=%d,maxv1=%d,minv2=%d,maxv2=%d\n",minv1,maxv1,minv2,maxv2);
  count+=1;
  if (minv1==maxv1 || minv2==maxv2) { // no variation return 0,1
    if(verbose>0) printf("tentropspk WARN0: #1:%d,%d,#2:%d,%d)\n",minv1,maxv1,minv2,maxv2);
    for (i=0;i<szXO;i++) XO[i]=0.0; if(szXO>=4+shuf)XO[shuf+3]=1.0; return 0.; }
  szp=(maxv1>maxv2)?(maxv1+1):(maxv2+1);
  pX2P = (double*) calloc(szp,sizeof(double));
  pX2PX1P = (double*) calloc(szp*szp,sizeof(double));
  pX2FX2P = (double*) calloc(szp*szp,sizeof(double));
  pX2FX2PX1P = (double*) calloc(szp*szp*szp,sizeof(double));
  // only need to do the X2 stuff once since only shuffle X1
  for(k=1;k<sz;k++) pX2P[ X2[k-1] ]++; // calculate X2P -- only once
  if(KTProb) { jmax=pdfnz(pX2P,szp,1); for(k=minv2;k<=maxv2;k++) if(pX2P[k]>0.0) {
      pX2P[k] = (0.5+pX2P[k]) / ( sz-1.0 + 0.5*jmax );}
  } else for(k=minv2;k<=maxv2;k++) pX2P[k] /= (sz-1);
  if (verbose>2) pdfpr(pX2P,szp,1,"pX2P");
  for(k=0;k<sz-1;k++) pX2FX2P[ X2[k+1]*szp + X2[k] ]++; // X2 future, X2 past
  if(KTProb) { jmax=pdfnz(pX2FX2P,szp,2); 
    for(k=minv2;k<=maxv2;k++) for(l=minv2;l<=maxv2;l++) if(pX2FX2P[k*szp+l]>0.0){
      pX2FX2P[k*szp+l] = (pX2FX2P[k*szp+l]+0.5) / ( sz-1.0 + 0.5*jmax ); }
  } else for(k=minv2;k<=maxv2;k++) for(l=minv2;l<=maxv2;l++) pX2FX2P[k*szp+l]/=(sz-1);
  if (verbose>3) pdfpr(pX2FX2P,szp,2,"pX2FX2P");
  //*** normalize on unshuffled with H(X2F|X2P); NB only X1 is being shuffled anyway:
  norm=entropxfgxpd(pX2P,pX2FX2P,minv2,maxv2,szp);               
  if (verbose>2) printf("H(X2F|X2P)=%g\n",tmp[0]);
  for (j=0,mean=0.;j<=shuf;j++) {
    //*** create X1 requiring pdfs: pX2PX1P, pX2FX2PX1P
    if (j>0) { ishuffle(X1,sz); // shuffle and then reset pdfs 
      memset(pX2PX1P,0,sizeof(double)*szp*szp); 
      memset(pX2FX2PX1P,0,sizeof(double)*szp*szp*szp);    }
    for(l=1;l<sz;l++) pX2PX1P[ X2[l-1]*szp + X1[l-1] ]++;  // X2 past, X1 past
    if(KTProb) {jmax=pdfnz(pX2PX1P,szp,2); 
      for(l=minv2;l<=maxv2;l++) for(m=minv1;m<=maxv1;m++) if(pX2PX1P[l*szp+m]>0.0){
        pX2PX1P[l*szp+m] = ( pX2PX1P[l*szp+m] + 0.5 ) / ( sz-1.0 + 0.5*jmax ); }
    } else for(l=minv2;l<=maxv2;l++) for(m=minv1;m<=maxv1;m++) pX2PX1P[l*szp+m]/=(sz-1);
    if (verbose>3) pdfpr(pX2PX1P,szp,2,"pX2PX1P");
    //*** init X2 future, X2 past, X1 past
    for(k=0;k<sz-1;k++) pX2FX2PX1P[ X2[k+1]*szp*szp + X2[k]*szp + X1[k] ]++; 
    if(KTProb){jmax=pdfnz(pX2FX2PX1P,szp,3);
      for(k=minv2;k<=maxv2;k++)for(l=minv2;l<=maxv2;l++)for(m=minv1;m<=maxv1;m++){
        if(pX2FX2PX1P[k*szp*szp+l*szp+m]>0.0){
          pX2FX2PX1P[k*szp*szp+l*szp+m]=(pX2FX2PX1P[k*szp*szp+l*szp+m]+0.5)/(sz-1.0 + 0.5*jmax);}}
    } else for(k=minv2;k<=maxv2;k++) for(l=minv2;l<=maxv2;l++) for(m=minv1;m<=maxv1;m++) {
      pX2FX2PX1P[k*szp*szp+l*szp+m]/=(sz-1);  }
    if (verbose>3) pdfpr(pX2FX2PX1P,szp,3,"pX2FX2PX1P");
    //*** calculate log2
    te = norm - entropx2fgx2px1pd(pX2FX2PX1P,pX2PX1P,minv1,maxv1,minv2,maxv2,szp);
    if (j>0) {mean+=te; mout[j-1]=te;} else teout=te; // saving these for now -- don't need to
  }
  if (shuf>0) mean/=shuf;
  if (szXO>0) XO[0]=teout; if (szXO>1) XO[1]=norm; if (szXO>2) XO[2]=mean;
  if (szXO>=3+shuf) for (i=0;i<shuf;i++) XO[i+3]=mout[i];
  if (szXO>=4+shuf && shuf>0) { //get p-value, low means unlikely te due to chance
    cnt1 = 0.0; 
    for(i=0;i<shuf;i++) if(teout < XO[i+3]) {cnt1+=1.0; if(verbose>2)printf("teout:%g, XO[%d]=%g\n",teout,i+3,XO[i+3]);}
    XO[shuf+3] = cnt1 / (double)shuf;
    if(verbose>2) printf("cnt1=%g, shuf=%d, XO[%d]=%g\n",cnt1,shuf,shuf+3,XO[shuf+3]);
  }
  if(verbose>2) printf("te=%g\n",te);
  free(pX2FX2P); free(pX2PX1P); free(pX2P); free(pX2FX2PX1P);
  return (teout-mean)/norm;
}


ENDVERBATIM


FUNCTION EXP (x) {
 TABLE DEPEND MINEXP,MAXEXP FROM MINEXP TO MAXEXP WITH 50000
 EXP = exp(x)
}

FUNCTION LOG2 (x) {
 TABLE DEPEND MINLOG2,MAXLOG2 FROM MINLOG2 TO MAXLOG2 WITH 50000
 LOG2 = log(x)/LG2
}

PROCEDURE install () {
  if (installed==1) {
    printf("infot.mod version %s\n","$Id: infot.mod,v 1.161 2010/08/19 20:02:27 samn Exp $")
  } else {
    installed = 1
    VERBATIM
    _check_LOG2(); _check_EXP();
    install_vector_method("tentropspks",tentropspks);
    ENDVERBATIM
  }
}

