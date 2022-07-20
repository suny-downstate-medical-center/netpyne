: $Id: stats.mod,v 1.227 2012/09/07 14:25:41 samn Exp $
 
:* COMMENT
COMMENT
randwd   randomly chooses n bits to set to 1
hamming  v.hamming(v1) is hamming distance between 2 vecs
flipbits v.flipbits(scratch,num) flips num rand chosen bits
flipbalbits v.flipbalbits(scratch,num) balanced flipping
vpr      v.vpr prints out vector as 1 (x[i]>0) or 0 (x[i]<=0)
fac      not vec related - returns factorial
logfac   not vec related - returns log factorial
vseed    set some C level randomizer seeds
slope(num) does a linear regression to find the slope, assuming num=timestep of vector
vslope(v2) does a linear regression to find the slope, assuming num=timestep of vector
stats(num,[out]) does a linear regression, assuming num=timestep of vector
vstats(v2,[out]) does a linear regression, using v2 as the x-coords
setrnd(v,flag) does set rand using 1:rand, 2:drand48
v.hash(list)  // make a hash out values in vecs in list
v.unnan([nan_value,][inf_value])  // remove nan's and inf's from a vector
ENDCOMMENT

NEURON {
  SUFFIX stats
  GLOBAL  INSTALLED,DBL_MAX,seed,kmeasure,verbose,self_ok_combi,hretval,flag,transpose,newline
}

PARAMETER {
  : BVBASE = 0. : defined in vecst.mod
  DBL_MAX=10e12
  INSTALLED=0
  kmeasure=0
  verbose=0
  self_ok_combi=0
  hretval=0
  transpose=0
  newline=90
  flag=0 : flag can be used by any of the routines for different things
}

ASSIGNED { seed }

VERBATIM
#include "misc.h"
#define MIN_MERGESORT_LIST_SIZE    32

union dblint {
  int i[2];
  double d;
};

static u_int32_t ilow=0;  
static u_int32_t ihigh=0; // same as ihigh in (/usr/site/nrniv/nrn/src/ivoc/ivocrand.cpp:75)
static double *x1x, *y1y, *z1z;
static void vprpr();

static int compare_ul(const void* l1, const void* l2) {
  int retval;
  unsigned long d;
  d = (*((const unsigned long*) l1)) - (*((const unsigned long*) l2));
  if(d==0) return 1;
  if(d < 0) return -1;
  return 0;
}

ENDVERBATIM
 
:* v1.slope(num) does a linear regression to find the slope, assuming num=timestep of vector

VERBATIM
static double slope(void* vv) {
	int i, n;
	double *x, *y;
        double timestep, sigxy, sigx, sigy, sigx2;
	/* how to get the instance data */
	n = vector_instance_px(vv, &y);

        if(ifarg(1)) { 
          timestep = *getarg(1); 
        } else { printf("You must supply a timestep\n"); return 0; }

        sigxy= sigx= sigy= sigx2=0; // initialize these

        x = (double *) malloc(sizeof(double)*n);
        for(i=0; i<n; i++) {
          x[i] = timestep*i;
          sigxy += x[i] * y[i];
          sigx  += x[i];
          sigy  += y[i];
          sigx2 += x[i]*x[i];
        }
        free(x);
        return (n*sigxy - sigx*sigy)/(n*sigx2 - sigx*sigx);
}
ENDVERBATIM

:* v1.moment(v2) stores moments:
VERBATIM
static double moment (void* vv) {
  int i, j, n, fl;
  double *mdata, *y;
  double ave,adev,sdev,svar,skew,curt,s,p;
  n = vector_instance_px(vv, &mdata);
  fl=0;
  if (n<=1) {printf("n must be at least 2 in stats:moment()"); hxe();}
  if(ifarg(1)) {
    if (hoc_is_object_arg(1)) {
      y=vector_newsize(vector_arg(1), 6); fl=1;
    } else { 
      printf("vec.moment(ovec) stores in ovec: ave,adev,sdev,svar,skew,kurt\n");
      return 0;
    }
  }
  for (j=0,s=0;j<n;j++) s+=mdata[j];
  ave=s/n; adev=svar=skew=curt=0.0;
  for (j=0;j<n;j++) { adev+=fabs(s=mdata[j]-ave); svar+=(p=s*s); skew+=(p*=s); curt+=(p*=s); }
  adev/=n;  svar/=(n-1);  sdev=sqrt(svar);
  if (svar) {
    skew /= (n*svar*sdev);
    curt= curt/(n*svar*svar)-3.0;
  } else {printf("No skew/kurtosis when variance = 0 (in stats::moment())\n"); hxe();}
  if (fl) {y[0]=ave; y[1]=adev; y[2]=sdev; y[3]=svar; y[4]=skew; y[5]=curt;}
  return curt;
}
ENDVERBATIM

:* v1.vslope(v2) does a linear regression, using v2 as the x-coords
VERBATIM
static double vslope (void* vv) {
	int i, n;
	double *x, *y;
        double timestep, sigxy, sigx, sigy, sigx2;
	/* how to get the instance data */
	n = vector_instance_px(vv, &y);

        if(ifarg(1)) {
          if(vector_arg_px(1, &x) != n ) {
            hoc_execerror("Vector size doesn't match.", 0); 
          }
          sigxy= sigx= sigy= sigx2=0; // initialize these

          for(i=0; i<n; i++) {
            sigxy += x[i] * y[i];
            sigx  += x[i];
            sigy  += y[i];
            sigx2 += x[i]*x[i];
          }
        }         
        return (n*sigxy - sigx*sigy)/(n*sigx2 - sigx*sigx);
}
ENDVERBATIM

VERBATIM
//computes mean,max squared error of data points
//off a line model with m=slope , b=y_intercept
//x is independent variable
//y is dependent variable
//n is # of data points
//meansqerr is output
//maxsqerr is output
double getsqerr(double* x,double* y,double m,double b,int n,double* meansqerr,double* maxsqerr){
  int i; double val;
  if(!n){
    return -1.0;
  }
  val=0.0;
  *meansqerr=0.0;
  *maxsqerr=0.0;
  for(i=0;i<n;i++){
    val = y[i] - (m*x[i]+b);
    val = val*val;
    if(val>*maxsqerr) *maxsqerr = val;
    *meansqerr += val;
  }
  *meansqerr=*meansqerr/(double)n;
  return *meansqerr;
}
ENDVERBATIM
 
:* v1.stats(num) does a linear regression, assuming num=timestep of vector
VERBATIM
static double stats(void* vv) {
	int i, n;
	double *x, *y, *out;
        double timestep, sigxy, sigx, sigy, sigx2, sigy2;
        double r, m, b, dmeansqerr,dmaxsqerr;
	/* how to get the instance data */
	n = vector_instance_px(vv, &y);

        if(ifarg(1)) { 
          timestep = *getarg(1); 
        } else { printf("You must supply a timestep\n"); return 0; }

        sigxy= sigx= sigy= sigx2=sigy2= 0; // initialize these

        x = (double *) malloc(sizeof(double)*n);
        for(i=0; i<n; i++) {
          x[i] = timestep*i;
          sigxy += x[i] * y[i];
          sigx  += x[i];
          sigy  += y[i];
          sigx2 += x[i]*x[i];
          sigy2 += y[i]*y[i];
        }
        m = (n*sigxy - sigx*sigy)/(n*sigx2 - sigx*sigx);
        b = (sigy*sigx2 - sigx*sigxy)/(n*sigx2 - sigx*sigx);
        r = (n*sigxy - sigx*sigy)/(sqrt(n*sigx2-sigx*sigx) * sqrt(n*sigy2-sigy*sigy));
        getsqerr(x,y,m,b,n,&dmeansqerr,&dmaxsqerr); //mean,max squared error
        if(ifarg(2)){ //save results to output
          out=vector_newsize(vector_arg(2),5);
          out[0]=m; out[1]=b; out[2]=r; out[3]=dmeansqerr; out[4]=dmaxsqerr;
        } else {
          printf("Examined %d data points\n", n);
          printf("slope     = %f\n", m);
          printf("intercept = %f\n", b);
          printf("R         = %f\n", r);
          printf("R-squared = %f\n", r*r);
          printf("MeanSQErr = %f\n",dmeansqerr);
          printf("MaxSQErr  = %f\n",dmaxsqerr);
        }
        free(x);
        return 1;
}

typedef struct pcorst_ {
  int pidse[2];
  double* X;
  double* Y;
  double sigx;
  double sigy;
  double sigx2;
  double sigy2;
  double sigxy;
} pcorst;

void* PCorrelTHFunc(void *arg) {
  pcorst* p;
  int i;
  double *X,*Y;
  p=(pcorst*)arg;
//  X=&p->X[p->pidse[0]]; Y=&p->Y[p->pidse[1]];
  X = p->X; Y = p->Y;
  p->sigx=p->sigy=p->sigxy=p->sigx2=p->sigy2=0.0;
  for(i=p->pidse[0]; i<p->pidse[1]; i++) {
//    p->sigxy += *X * *Y; 
//    p->sigx  += *X; 
//    p->sigy  += *Y;
//    p->sigx2 += *X * *X; 
//    p->sigy2 += *Y * *Y; 
//    X++; Y++;
    p->sigxy += X[i] * Y[i];
    p->sigx += X[i];
    p->sigy += Y[i];
    p->sigx2 += X[i] * X[i];
    p->sigy2 += Y[i] * Y[i];
  }  
  return NULL;
}

/* v1.pcorrels2(v2) does a Pearson correlation*/
#if defined(t)
static double pcorrelsmt(double *x, double* y, int n,int nth) {
  int i,nperth,idx,rc;
  double sigxy, sigx, sigy, sigx2, sigy2, ret;
  pcorst** pp;
  pthread_t* pth;
  pthread_attr_t attr;
  ret=sigxy=sigx=sigy=sigx2=sigy2=0.0; // initialize these
  nperth = n / nth;
  //allocate thread args
  pp = (pcorst**)malloc(sizeof(pcorst*)*nth);
  idx=0; 
  for(i=0;i<nth;i++) {
    pp[i] = (pcorst*)calloc(1,sizeof(pcorst));
    pp[i]->X = x;
    pp[i]->Y = y;    
    pp[i]->pidse[0] = idx;
    pp[i]->pidse[1] = idx + nperth;
    idx += nperth;
  }
  i--;  if(pp[i]->pidse[1] < n ||
           pp[i]->pidse[1] > n) pp[i]->pidse[1] = n; //make sure all values used
  //allocate thread IDs
  pth=(pthread_t*)malloc(sizeof(pthread_t)*nth);
  pthread_attr_init(&attr);
  pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_JOINABLE);
  //start threads
  for(i=0;i<nth;i++) if((rc=pthread_create(&pth[i], NULL, PCorrelTHFunc, (void*)pp[i]))) {
    printf("pcorrelsmt ERRA: couldn't create thread : %d!\n",rc);
    goto PCMTFREE;
  }
  pthread_attr_destroy(&attr);
  //wait for them to finish
  for(i=0;i<nth;i++) if((rc=pthread_join(pth[i], NULL))) {
    printf("pcorrelsmt ERRB: couldn't join thread : %d!\n",rc);
    goto PCMTFREE;
  }
  //put together the results
  for(i=0;i<nth;i++) {
    sigx += pp[i]->sigx;
    sigy += pp[i]->sigy;
    sigxy += pp[i]->sigxy;
    sigx2 += pp[i]->sigx2;
    sigy2 += pp[i]->sigy2;
  }
  sigxy -= (sigx * sigy) / n;
  sigx2 -= (sigx * sigx) / n;
  sigy2 -= (sigy * sigy) / n;
  if(sigx2 <= 0) goto PCMTFREE;
  if(sigy2 <= 0) goto PCMTFREE;
  ret = sigxy / sqrt(sigx2*sigy2);
PCMTFREE:
  //free memory
  for(i=0;i<nth;i++) free(pp[i]);
  free(pp);
  free(pth);
  return ret; // return results
}
#endif

/* v1.pcorrels2(v2) does a Pearson correlation*/
static double pcorrels2 (double *x, double* y, int n) {
  int i;
  double sigxy, sigx, sigy, sigx2, sigy2;
  sigxy=sigx=sigy=sigx2=sigy2=0.0; // initialize these
  for(i=0; i<n; i++) {
    sigxy += x[i] * y[i];
    sigx  += x[i];
    sigy  += y[i];
    sigx2 += x[i]*x[i];
    sigy2 += y[i]*y[i];
  }
  sigxy -= (sigx * sigy) / n;
  sigx2 -= (sigx * sigx) / n;
  sigy2 -= (sigy * sigy) / n;
  if(sigx2 <= 0) return 0;
  if(sigy2 <= 0) return 0;
  sigxy = sigxy / sqrt(sigx2*sigy2);
  return sigxy;
}

static double pcorrel (void* vv) {
 int i, n;
  double *x, *y;
  n = vector_instance_px(vv, &x);
  if ((i=vector_arg_px(1, &y)) != n ) {printf("pcorrelsERRA: %d %d\n",n,i); hxe();}
  if(ifarg(2)) {
#if defined(t)
    return pcorrelsmt(x,y,n,(int)*getarg(2));
#else
    printf("using NEURON version 6; pcorrelsmt() not compiled\n"); 
    return 0.0;
#endif
  } else {
    return pcorrels2(x,y,n);
  }
}

ENDVERBATIM



: based on python scipy code in stats.py in pearsonr function
: get the probability of null hypothesis (that correlation(pearson,spearman,etc.) btwn variables == 0.0)
: $1 == sample size (n)
: $2 == correlation coefficient (r) , -1.0 <= r <= 1.0
FUNCTION rpval () {
  VERBATIM
  double n , r, df , TINY , ts , mpval;
  n = *getarg(1);
  r = *getarg(2);
  if( r < -1.0 || r > 1.0 ){
    printf("ppval ERRA: r=%g must be : -1.0 <= r <= 1.0\n",r);
    return -1.0;
  }
  if( n < 3 ){
    printf("ppval ERRB: n too small, can't calc probability on samples with < 3 values!\n");
    return -1.0;
  }
  df = n-2; // degres of freedom
  // Use a small floating point value to prevent divide-by-zero nonsense
  // fixme: TINY is probably not the right value and this is probably not 
  // the way to be robust. The scheme used in spearmanr is probably better.
  TINY = 1.0e-20;
  ts = r*sqrt(df/((1.0-r+TINY)*(1.0+r+TINY)));
  mpval = betai(0.5*df,0.5,df/(df+ts*ts));
  return mpval;
  ENDVERBATIM
}

VERBATIM


static const double* sortdata = NULL; /* used in the quicksort algorithm */

/* Helper function for sort. Previously, this was a nested function under
 * sort, which is not allowed under ANSI C.
 */
static
int compare(const void* a, const void* b)
{ const int i1 = *(const int*)a;
  const int i2 = *(const int*)b;
  const double term1 = sortdata[i1];
  const double term2 = sortdata[i2];
  if (term1 < term2) return -1;
  if (term1 > term2) return +1;
  return 0;
}

void csort (int n, const double mdata[], int index[])
/* Sets up an index table given the data, such that mdata[index[]] is in
 * increasing order. Sorting is done on the indices; the array mdata
 * is unchanged.
 */
{ int i;
  sortdata = mdata;
  for (i = 0; i < n; i++) index[i] = i;
  qsort(index, n, sizeof(int), compare);
}

static double* getrank (int n, double mdata[])
/* Calculates the ranks of the elements in the array mdata. Two elements with
 * the same value get the same rank, equal to the average of the ranks had the
 * elements different values. The ranks are returned as a newly allocated
 * array that should be freed by the calling routine. If getrank fails due to
 * a memory allocation error, it returns NULL.
 */
{ int i;
  double* rank;
  int* index;
  rank = malloc(n*sizeof(double));
  if (!rank) return NULL;
  index = malloc(n*sizeof(int));
  if (!index)
  { free(rank);
    return NULL;
  }
  /* Call csort to get an index table */
  csort (n, mdata, index);
  /* Build a rank table */
  for (i = 0; i < n; i++) rank[index[i]] = i;
  /* Fix for equal ranks */
  i = 0;
  while (i < n)
  { int m;
    double value = mdata[index[i]];
    int j = i + 1;
    while (j < n && mdata[index[j]] == value) j++;
    m = j - i; /* number of equal ranks found */
    value = rank[index[i]] + (m-1)/2.;
    for (j = i; j < i + m; j++) rank[index[j]] = value;
    i += m;
  }
  free (index);
  return rank;
}

/*
The spearman routine calculates the Spearman rank correlation between two vectors. 
n      (input) int The number of elements in a data vector
data1  (input) double array -- the first vector
data2  (input) double array -- the second vector
*/
static double spearman(int n, double* data1, double* data2)
{ int i;
  int m = 0;
  double* rank1;
  double* rank2;
  double result = 0.;
  double denom1 = 0.;
  double denom2 = 0.;
  double avgrank;
  double* tdata1;
  double* tdata2;
  tdata1 = malloc(n*sizeof(double));
  if(!tdata1) return 0.0; /* Memory allocation error */
  tdata2 = malloc(n*sizeof(double));
  if(!tdata2) /* Memory allocation error */
  { free(tdata1);
    return 0.0;
  }
  for (i = 0; i < n; i++)
  { tdata1[m] = data1[i];
    tdata2[m] = data2[i];
    m++;
  }
  if (m==0) return 0;
  rank1 = getrank(m, tdata1);
  free(tdata1);
  if(!rank1) return 0.0; /* Memory allocation error */
  rank2 = getrank(m, tdata2);
  free(tdata2);
  if(!rank2) /* Memory allocation error */
  { free(rank1);
    return 0.0;
  }
  avgrank = 0.5*(m-1); /* Average rank */
  for (i = 0; i < m; i++)
  { const double value1 = rank1[i];
    const double value2 = rank2[i];
    result += value1 * value2;
    denom1 += value1 * value1;
    denom2 += value2 * value2;
  }
  /* Note: denom1 and denom2 cannot be calculated directly from the number
   * of elements. If two elements have the same rank, the squared sum of
   * their ranks will change.
   */
  free(rank1);
  free(rank2);
  result /= m;
  denom1 /= m;
  denom2 /= m;
  result -= avgrank * avgrank;
  denom1 -= avgrank * avgrank;
  denom2 -= avgrank * avgrank;
  if (denom1 <= 0) return 0; /* include '<' to deal with roundoff errors */
  if (denom2 <= 0) return 0; /* include '<' to deal with roundoff errors */
  result = result / sqrt(denom1*denom2);
  return result;
}

static double scorrel(void* vv) {
  int i, n;
  double *x, *y;
  n = vector_instance_px(vv, &x);
  if ((i=vector_arg_px(1, &y)) != n ) {printf("scorrelERRA: %d %d\n",n,i); hxe();}
  return spearman(n,x,y);
}

//* Kendall's correlation routines 
//** Erfcc() Returns the complementary error function erfc(x) with fractional error
//    everywhere less than 1.2 x 10^-7.
// from place.mod, is that from numerical recipes??
double Erfcc (double x) {
  double	mt,z,ans;
  z=fabs(x);
  mt=1.0/(1.0+0.5*z);
  ans=mt*exp(-z*z-1.26551223+mt*(1.00002368+mt*(0.37409196+mt*(0.09678418+\
      mt*(-0.18628806+mt*(0.27886807+mt*(-1.13520398+mt*(1.48851587+\
      mt*(-0.82215223+mt*0.17087277)))))))));
  return x >= 0.0 ? ans : 2.0-ans;
}

//** Rktau() R version of kendall tau, doesnt have huge memory footprint
//function returns kendall's tau
double Rktau (double* x, double* y, int n){
  int i,j; double c,vx,vy,sx,sy,var,z,tau;
  c = vx = vy = 0.0;
  for(i = 0; i < n; i++) {
    for(j = 0; j < i; j++) {
      sx = (x[i] - x[j]);
      sx = ((sx > 0) ? 1 : ((sx == 0)? 0 : -1));
      sy = (y[i] - y[j]);
      sy = ((sy > 0) ? 1 : ((sy == 0)? 0 : -1));
      vx += sx * sx;
      vy += sy * sy;
      c += sx * sy;
    }
  }  
  if(vx>0 && vy>0) {    
    tau = c / sqrt(vx*vy); 
    return tau;
  }
  return 0.;
}

//** vec1.kcorrel(vec2,[fast version -- useful for large arrays, vec of size 1 holding p-value])
// kendall's tau correlation
static double kcorrel (void* vv) {
  int i, n;
  double *x, *y, *prob, *i1d, *i2d, *ps, var, z, tau;
  n = vector_instance_px(vv, &x);
  if ((i=vector_arg_px(1, &y)) != n ) {printf("kcorrel ERRA: %d %d\n",n,i); hxe();}
  if(ifarg(2) && *getarg(2)) {
    i1d=dcrset(n*3); i2d=&i1d[n]; ps=&i2d[n]; tau=kcorfast(x,y,i1d,i2d,n,ps);
  } else {
    tau = Rktau(x,y,n); 
  }
  if(!(ifarg(3) && vector_arg_px(3,&prob))) prob = 0x0; //does user want to store p-value?
  if(prob) { //get p-value
    var = (4.0 * n + 10.0) / (9.0 * n * (n - 1.0));
    z = tau / sqrt(var);
    *prob = Erfcc(fabs(z)/1.4142136); //when prob small, chance of tau having its value by chance is small
  }
  return tau;
}

//** mycompare() comparison function for qsort -- sorts in ascending order
static int mycompare (const void* a, const void* b)
{ double d1,d2;
  d1 = *(double*)a;
  d2 = *(double*)b;
  if (d1 < d2) return -1;
  if (d1 > d2) return +1;
  return 0;
}

//** mergesort_array()
// recursive mergesort -- sorts a by splitting into sublists, sorting, and recombining    
void mergesort_array (double a[], int size, double temp[],unsigned long* swapcount) {
  int i1, i2, i, tempi, j, vv;
  double *right,*left;
  if(size<=1) return; //base case -- 1 element is sorted by definition
  if (0 && size <MIN_MERGESORT_LIST_SIZE){//can use insertion sort for small arrays -- but first need to put in swapcount incs
    /* Use insertion sort */
    for (i=0; i < size; i++) {
      vv = a[i];
      for (j = i - 1; j >= 0; j--) {
        if (a[j] <= vv) break;
        a[j + 1] = a[j];
      }
      a[j + 1] = vv;
    }
    return;
  }  
  mergesort_array(a, size/2, temp,swapcount);                 //sort left half
  mergesort_array(a + size/2, size - size/2, temp,swapcount); //sort right half
  //merge halves together
  i=tempi=0;  i1 = size/2; i2 = size - size/2;
  left = a; right = &a[size/2];
  while(i1>0 && i2>0) { 
    if(*right < *left) {
      *swapcount += i1; 
      temp[i] = *right++;
      i2--;
    } else {
      temp[i] = *left++;
      i1--;
    }
    i++;
  }
  if(i2>0) { 
    while(i2-->=0 && i<size) temp[i++] = *right++; //copy leftovers from right side
  } else {
    while(i1-->=0 && i<size) temp[i++] = *left++; //copy leftovers from left side
  }
  memcpy(a, temp, size*sizeof(double));//copy sorted results to a
}

//** qsort2() parallel sort
//parallel sort of p1in,p2in by sorting in lockstep. output into p1out,p2out.
//note that only p1out will be in ascending order on termination.
int qsort2 (double *p1in, double* p2in, int n,double* p1out,double* p2out) {
  int i;
  scr=scrset(n);
  for (i=0;i<n;i++) scr[i]=i;
  nrn_mlh_gsort(p1in, scr, n, cmpdfn);
  for (i=0;i<n;i++) {
    p1out[i]=p1in[scr[i]];
    p2out[i]=p2in[scr[i]];
  }
  return 1;
}

//** getMs() used in kcorfast to count # of ties
unsigned long getMs (double* data,int n) {  //Assumes data is sorted.
  unsigned long Ms, tieCount;
  int i;
  Ms = tieCount = 0;
  for(i=1;i<n;i++) {
    if(data[i] == data[i-1]) {
      tieCount++;
    } else if(tieCount) {
      Ms += (tieCount*(tieCount+1))/2;
      tieCount = 0;
    }
  }
  if(tieCount) {
    Ms += (tieCount*(tieCount+1)) / 2;
  }
  return Ms;
}

//** kcorfast()
// O(n logn) version of kendall's tau, based on Knight 1966 paper and David Simcha's D
//  implementation
// i1d,i2d,ps are scratch arrays that have same size as input1,input2
double kcorfast (double* input1, double* input2, double* i1d , double* i2d,int n,double* ps) {
    int i;
    unsigned long nPair, N, m1, m2, tieCount, swapCount;
    long s;
    double denom1,denom2;
    m1 = m2 = 0; N = n;
    nPair = N * ( N - 1 ) / 2; //total # of pairs
    qsort2(input1,input2,n,i1d,i2d); //parallel sort by input1
    s = nPair; 

    if(verbose>2) printf("nPair=%lu\n",nPair);
    if(verbose>3){printf("i1d after qsort2: "); for(i=0;i<n;i++) printf("%g ",i1d[i]); printf("\n");
                  printf("i2d after qsort2: "); for(i=0;i<n;i++) printf("%g ",i2d[i]); printf("\n");}
    tieCount = 0;
    for(i=1;i<n;i++) {
        if(i1d[i] == i1d[i-1]) {
            tieCount++;
        } else if(tieCount > 0) {
            qsort(&i2d[i-tieCount-1],tieCount+1,sizeof(double),mycompare);
            m1 += tieCount * (tieCount + 1) / 2;
            s += getMs(&i2d[i-tieCount-1],tieCount+1);
            tieCount = 0;
        }
    }
    if(verbose>2) printf("tieCount=%lu\n",tieCount);
    if(tieCount > 0) {
        qsort(&i2d[n-tieCount-1],tieCount+1,sizeof(double),mycompare);
        m1 += tieCount * (tieCount + 1) / 2;
        s += getMs(&i2d[n-tieCount-1],tieCount+1);
    }
    if(verbose>2) printf("tieCount=%lu\n",tieCount);
    swapCount = 0;

    mergesort_array(i2d,n,ps,&swapCount); //sort input2 & count # of swaps to get into sorted order
    if(verbose>3) { printf("i2d after mergesort: "); for(i=0;i<n;i++) printf("%g ",ps[i]); printf("\n"); }
    if(verbose>2) printf("swapCount=%lu\n",swapCount);

    m2 = getMs(i2d,n); if(verbose>2) printf("s=%lu m1=%lu m2=%lu\n",s,m1,m2);
    s -= (m1 + m2) + 2 * swapCount; 
    denom1=nPair-m1; denom2=nPair-m2; if(verbose>2) printf("s=%lu d1=%g d2=%g\n",s,denom1,denom2);
    if(denom1>0. && denom2>0.) return s / sqrt(denom1*denom2); else return 0.;
}
//root mean square of vector's elements
static double rms (void* vv) {
  int i,n;
  double *x,sum;
  if(!(n=vector_instance_px(vv, &x))) {printf("rms ERRA: 0 sized vector!\n"); hxe();}
  sum=0.0;
  for(i=0;i<n;i++) sum += x[i]*x[i];
  sum/=(double)n;
  if(sum>0.) return sqrt(sum); else return 0.0;
}

//cumulative sum of vector's elements
static double cumsum (void* vv) {
  int i,n;
  double *x,*y;
  if(!(n=vector_instance_px(vv, &x))) {printf("cumsum ERRA: 0 sized vector!\n"); hxe();}
  if(vector_arg_px(1, &y) != n) {printf("cumsum ERRB: output vec size needs size of %d\n",n); hxe();}
  memcpy(y,x,sizeof(double)*n);
  for(i=1;i<n;i++) y[i] += y[i-1];
  return 1.0;
}

ENDVERBATIM
 
:* vec.unnan() will reset nans, infs, neginfs to selected values -- default 0,0,0
VERBATIM
static double unnan (void *vv) {
  int i,nx,cnt; double newnan,newinf,neginf;
  union dblint xx;
  double *x;
  newnan=newinf=neginf=0;
  nx = vector_instance_px(vv, &x);
  if (ifarg(1)) newinf=newnan=*getarg(1);
  if (ifarg(2)) newinf=*getarg(2);
  if (ifarg(3)) neginf=*getarg(3);
  for (i=0,cnt=0;i<nx;i++) { 
    xx.d=x[i];
    if (xx.i[0]==0x0 && xx.i[1]==0xfff80000) {x[i]=newnan; cnt++;}
    if (xx.i[0]==0x0 && xx.i[1]==0x7ff00000) {x[i]=newinf; cnt++;}
    if (xx.i[0]==0x0 && xx.i[1]==0xfff00000) {x[i]=neginf; cnt++;}
  }
  return (double)cnt;
}
ENDVERBATIM

:* v1.vstats(v2) does a linear regression, using v2 as the x-coords
VERBATIM
static double vstats(void* vv) {
	int i, n;
	double *x, *y, *out;
        double sigxy, sigx, sigy, sigx2, sigy2;
        double r, m, b, dmeansqerr,dmaxsqerr;
	/* how to get the instance data */
	n = vector_instance_px(vv, &y);

        if(ifarg(1)) {
          if(vector_arg_px(1, &x) != n ) {
            hoc_execerror("Vector size doesn't match.", 0); 
          }
          sigxy= sigx= sigy= sigx2=sigy2=0; // initialize these

          for(i=0; i<n; i++) {
            sigxy += x[i] * y[i];
            sigx  += x[i];
            sigy  += y[i];
            sigx2 += x[i]*x[i];
            sigy2 += y[i]*y[i];
          }
          m = (n*sigxy - sigx*sigy)/(n*sigx2 - sigx*sigx);
          b = (sigy*sigx2 - sigx*sigxy)/(n*sigx2 - sigx*sigx);
          r = (n*sigxy - sigx*sigy)/(sqrt(n*sigx2-sigx*sigx) * sqrt(n*sigy2-sigy*sigy));
          getsqerr(x,y,m,b,n,&dmeansqerr,&dmaxsqerr);//mean,max squared error
          if(ifarg(2)){ //save results to output
            out=vector_newsize(vector_arg(2),5);
            out[0]=m; out[1]=b; out[2]=r; out[3]=dmeansqerr; out[4]=dmaxsqerr;
          } else {
            printf("Examined %d data points\n", n);
            printf("slope     = %f\n", m);
            printf("intercept = %f\n", b);
            printf("R         = %f\n", r);
            printf("R-squared = %f\n", r*r);
            printf("MeanSQErr = %f\n",dmeansqerr);
            printf("MaxSQErr  = %f\n",dmaxsqerr);
          }
          return 1;
        } else {
          printf("You must supply an x vector\n");
          return 0;
        }
}
ENDVERBATIM

:* v1.randwd(num[,v2]) will randomly flip num bits from BVBASE to 1
: does v1.fill(BVBASE); optionally fill v2 with the indices
VERBATIM
static double randwd(void* vv) {
	int i, ii, jj, nx, ny, flip, flag;
	double* x, *y;
	/* how to get the instance data */
	nx = vector_instance_px(vv, &x);
        flip = (int) *getarg(1);
        if (ifarg(2)) { /* write a diff vector to z */
          flag = 1; ny = vector_arg_px(2, &y);
          if (ny!=flip) { hoc_execerror("Opt vector must be size for # of flips", 0); }
        } else { flag = 0; }
        if (flip>=nx) { hoc_execerror("# of flips exceeds (or ==) vector size", 0); }
	for (i=0; i < nx; i++) { x[i] = BVBASE; }
	for (i=0,jj=0; i < flip; i++) { /* flip these bits */
	  ii = (int) ((nx+1)*drand48());
	  if (x[ii]==BVBASE) {
	    x[ii] = 1.; 
            if (flag) { y[jj] = ii; jj++; }
	  } else {
	    i--;
	  }
	}
	return flip;
}
ENDVERBATIM
 
:* v1.hash(veclist)
VERBATIM
static double hash (void* vv) {
  int i, j, nx, nv[VRRY], num, vfl; 
  union dblint xx;
  Object* ob;
  double *x, *vvo[VRRY], big, y, prod;
  nx = vector_instance_px(vv, &x);
  if (ifarg(1)) {
    vfl=0;
    ob=*hoc_objgetarg(1); 
    num = ivoc_list_count(ob);
    if (num>VRRY) {printf("vecst:hash ERR: can only handle %d vecs: %d\n",VRRY,num); hxe();}
    for (i=0;i<num;i++) { nv[i] = list_vector_px(ob, i, &vvo[i]);
      if (nx!=nv[i]) { printf("vecst:hash ERR %d %d %d\n",i,nx,nv[i]);hxe();}}
  } else {
    vfl=1; num=nx; nx=1; // outer loop will go only once
  }
  big=pow(DBL_MAX,1./(double)num); // base biggest # on nth root of num of values being used
  for (i=0;i<nx;i++) {
    for (j=0,prod=1;j<num;j++) {
      if (vfl) {  xx.d=x[j];       // break the double up into 2 unsigned ints
      } else   {  xx.d=vvo[j][i]; }
      if (xx.i[0]==0) { xx.i[0]=xx.i[1]; xx.i[0]<<=4; } // high order bits may be 0
      if (xx.i[1]==0) { xx.i[1]=xx.i[0]; xx.i[1]<<=4; } // low order bits unlikely 0
      mcell_ran4_init(xx.i[1]);
      mcell_ran4(&xx.i[0], &y, 1, big); // generate a pseudorand number based on these
      prod*=y;  // keep multiplying these out
    }
    if (! vfl) x[i]=prod; else return prod; // just return the 1 value
  }
  return (double)nx;
}
ENDVERBATIM

:* v1.smash(veclist,base)
: smash squeezes a set of numbers into a single double by considering them as digits
: in base base -- x[i]+=vvo[i][j]*wt; where wt is base^i
: note that handles transpose -- ie can smash on (transpose==1) or across each vec in a veclist
VERBATIM
static double smash (void* vv) {
  int i, j, nx, nv[VRRY], num; 
  Object* ob;
  double *x, *vvo[VRRY], wt, wtj;
  nx = vector_instance_px(vv, &x);
  ob=*hoc_objgetarg(1); 
  if (ifarg(2)) wtj=*getarg(2); else wtj=10.;
  num = ivoc_list_count(ob);
  if (num>VRRY) {printf("vecst:smash ERRA: can only handle %d vecs: %d\n",VRRY,num); hxe();}
  if (transpose) if (nx!=num) { printf("vecst:smash ERRB %d %d %d\n",i,nx,nv[i]);hxe(); }
  for (i=0;i<num;i++) { 
    nv[i] = list_vector_px(ob, i, &vvo[i]);
    if (!transpose) if (nx!=nv[i]) { printf("vecst:smash ERRB %d %d %d\n",i,nx,nv[i]);hxe(); }
  }
  if (transpose) { 
    for (i=0;i<num;i++) { // num==nx: each vector indiviudally
      for (j=0,x[i]=0,wt=1;j<nv[i];j++,wt*=wtj) x[i]+=vvo[i][j]*wt;
    }
  } else for (i=0;i<nx;i++) {
    for (j=0,x[i]=0,wt=1;j<num;j++,wt*=wtj) x[i]+=vvo[j][i]*wt;
  }
  return (double)nx;
}
ENDVERBATIM

:* v1.smash1([wtjump,mod])
:  similar to smash() but operates on a single vector; also cycles every (optional) 'mod' 
:  iterations to reset the weighting back to 1; presumably mod and base (wtjump) should
:  have no shared factors
VERBATIM
static double smash1 (void* vv) {
  int i, j, nx, nv[VRRY], num, mod; 
  double *x, wt, wtj, res;
  nx = vector_instance_px(vv, &x);
  if (ifarg(1)) wtj=*getarg(1); else wtj=10.;
  if (ifarg(2)) mod=(int)*getarg(2); else mod=0;
  for (j=0,res=0,wt=1;j<nx;j++,wt*=wtj) {
    res+=x[j]*wt;
    if (mod && j%mod==0) wt=1;
  }
  return res;
}
ENDVERBATIM

:* v1.dpro(veclist[,step,gap]) -- another hashing function?
VERBATIM 
static double dpro (void* vv) {
  int i, j, nx, nv[VRRY], num, step, gap; 
  Object* ob;
  double *x, *vvo[VRRY], wt;
  nx = vector_instance_px(vv, &x);
  ob=*hoc_objgetarg(1); 
  if (ifarg(2)) step=(int)*getarg(2); else step=1;
  if (ifarg(3)) gap=(int)*getarg(3); else gap=1;
  num = ivoc_list_count(ob);
  if (num>VRRY) {printf("stats:dpro ERR: can only handle %d vecs: %d\n",VRRY,num); hxe();}
  for (i=0;i<num;i++) { 
    nv[i] = list_vector_px(ob, i, &vvo[i]);
    if (nx!=nv[i]) { printf("stats:dpro ERR %d %d %d\n",i,nx,nv[i]);hxe(); }
  }
  for (i=0;i<nx;i+=step) {
    for (j=0,x[i]=0,wt=1;j<num;j++) {
      x[i]+=vvo[j][i]*wt;
    }
  }
  return (double)nx;
}
ENDVERBATIM

:* v1.setrnd(flag) performs setrand()
: note that seed is kept as a global so that it can be easily set from hoc
: to repeat a sequence
: flag: 1 rand(); 2 drand48(); 3 scop_random(); 4 mcell_ran4(); 5 integers via mcell_ran4()
: v1.setrnd(4[,MAX_VAL DEFAULT=1, SEED])
: v1.setrnd(4,vec[,step,seed]) // find location of vec value >= randvar and mul by step
: v1.setrnd(4.5,min,max[,seed]) // [min,max)
: v1.setrnd(5[,n,seed]) -- integers [0,100) or [0,n]
: v1.setrnd(5[,min,max,seed]) -- integers [min,max] -- if seed=0 it's not reset
: v1.setrnd(5,ind[,seed]) -- random values from ind
: v1.setrnd(6) -- unique integers as follows:
: v1.setrnd(6,min,max[,seed]) -- unique in [min,max]
: v1.setrnd(6,min,max,exclude_vec[,seed]) -- unique in [min,max] excluding values in exclude_vec
VERBATIM
static double setrnd (void* vv) {
  int flag, i,j,k,n,cnt; unsigned int nx, nx1, nex, lt, rt, mid;
  double *x, y, *ex, *ex2, min, max, dfl, tmp, step, num;
  unsigned long value;
  value=1;
  nx = vector_instance_px(vv, &x);
  flag = (int)(dfl=*getarg(1));
  if (flag==1) {
    for (i=0; i < nx; i++) x[i] = (double)rand()/RAND_MAX; 
  }  else if (flag==2) {
    for (i=0; i < nx; i++) x[i] = drand48(); 
  } else if (flag==3) { // scop_random()'s cheap and dirty rand
    unsigned long a = 2147437301, c = 453816981, m = ~0;
    value = (unsigned long) seed;
    for (i=0; i < nx; i++) {
      value = a * value + c;
      x[i] = (fabs((double) value / (double) m));
    }
    seed=(double)value;
  } else if (flag==4) { // mcell_ran4() doubles
    ex=0x0; i=2;
    if (ifarg(i)) {
      if (hoc_is_object_arg(i)) {
        nex=vector_arg_px(i++,&ex); // vector to look in
        step=ifarg(i)?*getarg(i):1.0;
        max=1.0; i++;
      } else {
	if (dfl==4.5 || ifarg(4)) { // flag 4.5 resolves ambiguity of arg3 max or seed
	  min=*getarg(i++); 
	  max=*getarg(i++)-min; 
	  dfl=4.5;
	} else {
	  max=*getarg(i++);
	}
      }
    } else max=1.0; // default
    if (ifarg(i)) { y=*getarg(i++); if (y) ihigh=(unsigned int)y; } // look for seed
    if (max==0) { for (i=0;i<nx;i++) x[i]=0.;
    } else mcell_ran4(&ihigh, x, nx, max);
    if (dfl==4.5) for (i=0;i<nx;i++) x[i]+=min;
    if (ex) for (i=0;i<nx;i++) { // go through all the ex values
      num=x[i]; lt=0; rt=nex-1;
      while (lt<=rt) { // binary search
        mid=(lt+rt)/2;
        if (num>ex[mid]) { 
          if (num<ex[mid+1]) break; // looking for in-between not ==
          lt=mid+1;
        } else if (num<ex[mid]) rt=mid-1;
      }
      x[i]=step*mid;
    }
    return (double)ihigh;
  } else if (flag==5) { // nx integers from [0,n)
    n=100; ex=0x0;
    if (ifarg(2)) {
      if (hoc_is_object_arg(2)) {
        n=vector_arg_px(2,&ex); // vector to sample from
      } else {
        n=(int)*getarg(2);
      }
    }
    i=3; // next arg
    if (dfl==5.5 || ifarg(4)) { max=*getarg(3); min=n; n=max-min+1; dfl=5.5; i=4; }
    if (ifarg(i)) { y=*getarg(i); if (y) ihigh=(unsigned int)y; }
    if (n<=1) { for (i=0;i<nx;i++) x[i]=0.0;
    } else mcell_ran4(&ihigh, x, nx, (double)n);
    if (dfl==5.5)  { for (i=0;i<nx;i++) x[i]=min+floor(x[i]);
    } else if (ex) { for (i=0;i<nx;i++) x[i]=  ex[(int)x[i]];
    } else           for (i=0;i<nx;i++) x[i]=    floor(x[i]);
    return (double)ihigh;
  } else if (flag==6) { // n uniq integers from a to b
    min=*getarg(2); max=*getarg(3); i=4; nex=0;
    if (ifarg(i+1)) {
      nex=vector_arg_px(i, &ex); // exclude list
      ihigh=(unsigned int)(*getarg(i+1));
    } else if (ifarg(i)) {
      if (hoc_is_object_arg(i)) { nex=vector_arg_px(i, &ex); // exclude list
      } else { ihigh=(unsigned int)(*getarg(i)); }
    } 
    // pick up err when ex[] contains values that are not in [min,max]
    if (nex>1) { // sort the exclude vector
      scrset(nex);
      x1x = (double *)realloc(x1x,sizeof(double)*nx*4);
      for (i=0;i<nex;i++) scr[i]=i;
      nrn_mlh_gsort(ex, scr, nex, cmpdfn);
      for (i=0;i<nex;i++) x1x[i]=ex[scr[i]];
      for (i=0;i<nex;i++) ex[i]=x1x[i];
    }
    for (j=0;j<nex;j++) if (ex[j]>max || ex[j]<min || (j>0 && ex[j]<=ex[j-1])) {
      printf("%g in exclusion list -- out of range [%g,%g] or a repeat\n",ex[j],min,max);hxe();} 
    if (max-min+1-nex==nx) { 
      for (i=min,k=0;i<=max;i++) {
        y=(double)i;
        for (j=0;j<nex && ex[j]!=y;j++) {} // look for the value in the exclude vec
        if (j==nex) x[k++]=y; // look for next one
      }
      dshuffle(x,nx);
      return (double)nx;
    } else if (max-min+1-nex<nx) {
      printf("setrnd ERR6A incompatible: min=%g max=%g; %d vs %g\n",min,max,nx,max-min+1-nex); 
      hxe();
    }
    cnt=0; nx1=nx; 
    while (cnt<nx && nx1<=256*nx) {
      nx1*=4; // leave what should be plenty of room
      x1x = (double *)realloc(x1x,sizeof(double)*nx1);
      y1y = (double *)realloc(y1y,sizeof(double)*nx1);
      z1z = (double *)realloc(z1z,sizeof(double)*nx1);
      mcell_ran4(&ihigh, x1x, nx1, max-min+1-nex);
      for (i=0;i<nx1;i++) x1x[i]=floor(x1x[i])+min;
      cnt=uniq2(nx1,x1x,y1y,z1z);
    }
    if (nex) { // have correct # of uniq values but must shift some of them up
      // any value thats >= to an excluded value must shift by # its >= to
      for (i=0;i<nx;i++) {
        for (j=0,k=0;j<nex;j++) if (z1z[i]+k>=ex[j]) k++; // will move it up by k
        x[i]=z1z[i]+k;
      }
    } else  for (i=0;i<nx;i++) x[i]=z1z[i];
  }
  return nx;
}
ENDVERBATIM
 


:* v1.hamming(v2[,v3]) compares v1 and v2 for matches, v3 gives diff vector
VERBATIM
static double hamming (void* vv) {
  int i, nx, ny, nz, prflag;
  double* x, *y, *z,sum;
  sum = 0.;
  nx = vector_instance_px(vv, &x);
  ny = vector_arg_px(1, &y);
  if (ifarg(2)) { // write a diff vector to z
    prflag = 1; nz = vector_arg_px(2, &z);
  } else { prflag = 0; }
  if (nx!=ny || (prflag && nx!=nz)) {
    hoc_execerror("Vectors must be same size", 0);
  }
  for (i=0; i < nx; ++i) {
    if (x[i] != y[i]) { sum++; 
      if (prflag) { z[i] = 1.; }
    } else if (prflag) { z[i] = 0.; }
  }
  return sum;
}
ENDVERBATIM

:* vec.combi(prix,prixe,poix,poixe,prv,pov,perc) // appends presyn,postsyn values to prv,pov
:* vec.combi(prindv,poindv,prv,pov,perc) 
:  self_ok_combi_stats flag defaults to 0 -- allows shortcut (soc shortcut) if set to 1 in hoc
:  does combinadics
VERBATIM
static double combi (void* vv) {
  int i,j,k,m,n,prix,prixe,poix,poixe,prn,pon,s,vfl,tot,soc; 
  double perc, *v1, *v2, *vpr, *vpo, *vec; void *v1v, *v2v;
  int nx,cnt,nx1,nvec,nv1,nv2;
  nx=nvec = vector_instance_px(vv, &vec);
  if (ifarg(7)) vfl=0; else vfl=1; 
  nv1 = vector_arg_px((vfl?3:5), &v1); v1v=vector_arg((vfl?3:5)); 
  nv2 = vector_arg_px((vfl?4:6), &v2); v2v=vector_arg((vfl?4:6)); 
  perc = *getarg(vfl?5:7);
  if (nv1!=nv2) {printf("stats:combi()ERRA out vec size discrep: %d,%d\n",nv1,nv2); hxe();}
  if (vfl) {
    prn = vector_arg_px(1, &vpr);
    pon = vector_arg_px(2, &vpo);
  } else {
    prix=(int)*getarg(1); prixe=(int)*getarg(2); poix=(int)*getarg(3); poixe=(int)*getarg(4);
    prn=prixe-prix+1; pon=poixe-poix+1;
  } 
  if (prn<=0 || pon<=0) {printf("stats:combi()ERRB %d,%d\n",prn,pon); hxe();}
  soc=(int)self_ok_combi;
  if (soc) tot=prn*pon; else { // else count non-self_connects -- soc shortcut
    if (vfl){for(i=0,tot=0;   i<prn;   i++) for (j=0;j<pon;j++) if (vpr[i]!=vpo[j]) tot++;
    } else  for (i=prix,tot=0;i<=prixe;i++) for (j=poix;j<=poixe;j++) if (i!=j)     tot++;
  }
  // fractional perc is % else # of edges desired
  if (perc<1) s=(int)floor(perc*(double)tot+0.5); else s=(int)perc; 
  // soc shortcut -- set self_ok_combi before call when sets are disjoint and s=1
  if (soc && s==1) { // don't need to go through this rigamarole just choose 1 from A,1 from B
    vec=vector_newsize(vv,1); v1=vector_newsize(v1v,nv1+1); v2=vector_newsize(v2v,nv2+1);
    mcell_ran4(&ihigh, vec, 1, prn);
    if (vfl) v1[nv1]=vpr[(int)vec[0]]; else v1[nv1]=prix+floor(vec[0]);
    mcell_ran4(&ihigh, vec, 1, pon);    
    if (vfl) v2[nv2]=vpo[(int)vec[0]]; else v2[nv2]=poix+floor(vec[0]);    
    return 1.0; // note that vec will not contain the combi#
  }
  vec=vector_newsize(vv,s); // vec.resize(s)
  if (tot==s) { for (i=0;i<s;i++) vec[i]=(double)i; // all values
  } else { // vec.setrnd(6,0,tot-1) -- find s unique integers in [0,tot)
    cnt=0; nx1=10*s;
    while (cnt<s && nx1<=640*nx) {
      nx1*=4; // leave what should be plenty of room
      x1x = (double *)realloc(x1x,sizeof(double)*nx1);
      y1y = (double *)realloc(y1y,sizeof(double)*nx1);
      z1z = (double *)realloc(z1z,sizeof(double)*nx1);
      mcell_ran4(&ihigh, x1x, nx1, tot);
      for (i=0;i<nx1;i++) x1x[i]=floor(x1x[i]);
      cnt=uniq2(nx1,x1x,y1y,z1z);
    }
    for (i=0;i<s;i++) vec[i]=z1z[i];
  }
  v1=vector_newsize(v1v,nv1+s); v2=vector_newsize(v2v,nv2+s);
  // vec.sort() // not done but would make it easier to see what's going on
  for (i=0,m=nv1,n=-1;i<prn;i++) for (j=0;j<pon;j++) { // thru all pre, all post
    if (vfl) {if (soc || (vpr[i]!=vpo[j])) n++; else continue; // make sure no self connect
    } else   {if (soc || (prix+i!=poix+j)) n++; else continue; }
    for (k=0;k<s;k++) if (vec[k]==(double)n) { // look for this one among rand values in vec
      if (vfl) {v1[m]=vpr[i]; v2[m]=vpo[j];    // found -- use the pre,post values associated 
      } else   {v1[m]=prix+i; v2[m]=poix+j;   }//          with combi # 'n'
      m++;     
      break;
    }
  }
  return (double)s;
}
ENDVERBATIM

VERBATIM

//shuffle array of doubles
void dshuffle (double* x,int nx) {
  int n,k; double temp,y[1];
  for (n=nx;n>1;) {
    mcell_ran4(&ihigh, y, 1, n);
    n--;
    k=(int)y[0]; // random int(n) // 0 <= k < n.
    temp = x[n];
    x[n] = x[k];
    x[k] = temp;
  }  
}

//shuffle array of unsigned ints
void uishuffle(unsigned int* x,int nx) {
  int n,k; unsigned int temp; double y[1];
  for (n=nx;n>1;) {
    mcell_ran4(&ihigh, y, 1, n);
    n--;
    k=(int)y[0]; // random int(n) // 0 <= k < n.
    temp = x[n];
    x[n] = x[k];
    x[k] = temp;
  }  
}

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

unsigned long choose (int n, int k) {
  int i,delta;
  unsigned long ret;
  //assert ((n >= 0) && (k >= 0));
  if (n < k) return 0;
  if (n==k)  return 1;
  if (k < n - k) {
    delta = n - k;
  } else {
    delta = k;
    k = n - k;
  }
  ret = delta + 1;
  for (i = 2; i <= k; ++i)
    ret = (ret * (delta + i)) / i;
  return ret;
}

// computes combinadic given combination vector
unsigned long syncci (int nn,int kk,int* ccvv) {
  unsigned long c = 0;
  while ((kk > 0) && (*ccvv >= kk)) {
    c += choose (*ccvv++, kk--);
  }
  return c;
}


// computes combinadic given combination vector
unsigned long syncc (int nn,int kk,double* ccvv) {
  unsigned long c = 0;
  while ((kk > 0) && (*ccvv >= kk)) {
    c += choose (*ccvv++, kk--);
  }
  return c;
}

// computes combination vector given combinadic
void synccv (int nn,int kk,int cc,double* ccvv) {
  unsigned long n_k;
  while (--nn >= 0) {
    n_k = choose (nn, kk);
    if (cc >= n_k) {
      cc -= n_k;
      *ccvv++ = nn;
      --kk;
    }
  }
}

ENDVERBATIM

: returns the # of combinations for choosing k from a set of n
: combs(n,k)
FUNCTION combs () {
  VERBATIM
  unsigned int n,k;
  n=(unsigned int)*getarg(1);
  k=(unsigned int)*getarg(2);
  return choose(n,k);
  ENDVERBATIM
}

:* vec.comb(nn,kk,cc)
:  returns combination indexed by cc, from selecting kk elements from set of nn elements
:  element ids are from 0..nn-1
VERBATIM
static double comb (void* vv) {
  double* x;
  int nn,kk,cc,sz,i;
  sz=vector_instance_px(vv,&x);
  nn=(int)*getarg(1);
  kk=(int)*getarg(2);
  cc=(int)*getarg(3);
  if(sz<kk){
    printf("comb ERRA: output vec sz must be >= %d , is %d!\n",kk,sz);
    return 0.0;
  }
  memset(x,0,sizeof(double)*kk);
  synccv(nn,kk,cc,x);
  vector_resize(vv,kk);
  return 1.0;
}
ENDVERBATIM

:* vec.combid(nn,kk)
:  returns combination index corresponding to data in vector
:  indices from selecting kk elements from set of nn elements
:  element ids are from 0..nn-1
VERBATIM
static double combid (void* vv) {
  double* x;
  int nn,kk,sz,i;
  sz=vector_instance_px(vv,&x);
  nn=(int)*getarg(1);
  kk=(int)*getarg(2);
  if(sz<kk){
    printf("comb ERRA: input vec sz must be >= %d , is %d!\n",kk,sz);
    return 0.0;
  }
  return syncc(nn,kk,x);
}
ENDVERBATIM

VERBATIM
int findlong (unsigned long* p,unsigned long val,int istart,int iend) {
  int i;
  for(i=istart;i<=iend;i++) if(p[i]==val) return 1; 
  return 0;
}

ENDVERBATIM

:* rsampsig(vIN0,vIN1,prc,"vhfmeasure","compfunc",vhsout,[onesided,nocmbchk,inorder])
:  vIN0 - elements of group 0
:  vIN1 - elements of group 1
:  prc - fraction of subsets to measure with "vhfmeasure" , or total # of combinations to test iff prc > 1.0
:  "vhfmeasure" - hoc function that takes 1 vector as arg and returns a double, must set hretval_stats
:  to the return value so can be read from here
:  "compfunc" - hoc function that takes 2 doubles as args & returns 1 iff a boolean condition is satisfied, must set
:  hretval_stats to return value so can be read from here
:  vhsout - vector used in hocmeasure , must have size >= vIN0.size + vIN1.size
:  onesided - optional, use one sided p-value or two-sided (default = 1) , onsided==0 means use two-sided
:  nocmbchk - skip combination ID check, useful for groups with large size ( > 30000 ) , to avoid overflow, def=1 == skip combination ID check
:  returns -1.0 on error
VERBATIM
static double rsampsig(void* vv){
  int n0,n1,na,nn,kk,cc,i,j,*pm,szthis,onesided,nocmbchk,bti,*pids;
  unsigned long nruncombs,nallcombs,*pcombids;
  double *g0,*g1,*ga,prc,*g0t,*g1t,dmobs,dm0,dm1,*phso,nmatch,*pthis,dret;
  void* vhso; //vector * for changing size at end
  Symbol* pHocVecFunc,*pHocCompFunc; //hoc function pointers
  dret=-1.0;
  g0t=g1t=NULL; pm=pids=NULL; pcombids=NULL;//init arrays to null
  szthis=vector_instance_px(vv, &pthis); //size of calling vector
  n0=vector_arg_px(1,&g0);//group 0 size
  n1=vector_arg_px(2,&g1);//group 1 size
  na=n0+n1;//total # of elements
  prc=*getarg(3);//% of combinations to try, or total # of combinations to try iff > 1.0
  if(!(pHocVecFunc=hoc_lookup(gargstr(4)))){
    printf("rsampsig ERRA: couldn't find hoc vec func %s\n",gargstr(4));
    goto CLEANRSAMPSIG;
  }
  if(!(pHocCompFunc=hoc_lookup(gargstr(5)))){
    printf("rsampsig ERRB: couldn't find hoc comp func %s\n",gargstr(5));
    goto CLEANRSAMPSIG;
  }
  if(vector_arg_px(6,&phso)<na){ //pointer to hoc stats output used in hocmeasure
    printf("rsampsig ERRC: arg 6 must have size >= %d!\n",na);
    goto CLEANRSAMPSIG;
  }
  if(prc<=0.0) {
    printf("rsampsig ERRD: invalid value for arg 3, must be > 0.0!\n");
    goto CLEANRSAMPSIG;
  }
  vhso=vector_arg(6);//get vector arg for resize
  ga=(double*)malloc(sizeof(double)*na);//all elements
  memcpy(ga,g0,sizeof(double)*n0);//copy elements of group 0 to ga
  memcpy(ga+n0,g1,sizeof(double)*n1);//append elements of group 1 to ga
  //form nruncombs combinations, select elements into groups, and compare measure on groups
  g0t=(double*)malloc(sizeof(double)*n0);//temp storage for group 0
  g1t=(double*)malloc(sizeof(double)*n1);//temp storage for group 1
  if(n0<n1) kk=n0; else kk=n1;//select kk using smaller group
  if(verbose>1) printf("choose(%d,%d)=%ld\n",na,kk,choose(na,kk));
  nallcombs=choose(na,kk);//all possible combinations selecting kk elements from a set of size na
  nruncombs=prc>1.0?prc:prc*nallcombs; nmatch=0.0;//# of combinations to run
  if(szthis<nruncombs){
    printf("rsampsig ERRE: vector size (%d) < nruncombs (%ld)!\n",szthis,nruncombs);
    goto CLEANRSAMPSIG;
  }
  onesided=ifarg(7)?(int)*getarg(7):1;
  nocmbchk=ifarg(8)?(int)*getarg(8):1;
  pids=(int*)malloc(sizeof(int)*na); //ids to be shuffled
  for(i=0;i<na;i++) pids[i]=i; //initialize ids in order
  pcombids=(unsigned long*)malloc(sizeof(unsigned long)*nruncombs); //combination ids that were used
  if(verbose>1) printf("na=%d , kk=%d, n0=%d, n1=%d\n",na,kk,n0,n1);
  if(verbose>1) printf("nruncombs = %ld\n",nruncombs);
  if(verbose>2) pm=(int*)malloc(sizeof(int)*na);
  for(i=0;i<nruncombs;i++) {    
    do { //get the combination index - only selecting first kk elements
      ishuffle(pids,na);//shuffle the ids randomly
      pcombids[i] = syncci(na , kk, pids);
    } while(!nocmbchk && i-1>0 && findlong(pcombids,pcombids[i],0,i-1)); //make sure pcombids[i] wasnt used yet
    if(verbose) if(i%100==0) { printf("."); fflush(stdout); }
    for(j=0;j<n0;j++) *g0t++=ga[*pids++]; //first n0 elements indexed by pid go into g0t
    for(;j<na;j++)    *g1t++=ga[*pids++]; //next n1 elements indexed by pid go into g1t
    g0t-=n0; g1t-=n1; pids-=na; //reset pointers (from increments on 2 lines above)
    if(verbose>2){ for(j=0;j<n0;j++) pm[pids[j]]=0; for(;j<na;j++) pm[pids[j]]=1;  printf("pm: ");
      for(j=0;j<40;j++) printf("%d",pm[j]); printf("\n"); }//print out bit-array of element ids
    //compare measures between
    vector_resize(vhso, n0); memcpy(phso,g0t,sizeof(double)*n0); 
    hoc_call_func(pHocVecFunc,0); dm0 = hretval; //get measure on group 0
    vector_resize(vhso, n1); memcpy(phso,g1t,sizeof(double)*n1); 
    hoc_call_func(pHocVecFunc,0); dm1 = hretval; //get measure on group 1
    hoc_pushx(dm0); hoc_pushx(dm1); hoc_call_func(pHocCompFunc,2); //call comparison function
    pthis[i]=onesided?hretval:fabs(hretval); //save value from comparison function
  }
  vector_resize(vv,nruncombs);//resize calling vec
  //get comparison function value for original data groups
  vector_resize(vhso,n0); memcpy(phso,g0,sizeof(double)*n0); 
  hoc_call_func(pHocVecFunc,0); dm0 = hretval; //get measure on original group 0
  vector_resize(vhso,n1); memcpy(phso,g1,sizeof(double)*n1); 
  hoc_call_func(pHocVecFunc,0); dm1 = hretval; //get measure on original group 1
  hoc_pushx(dm0); hoc_pushx(dm1); hoc_call_func(pHocCompFunc,2); //call comparison function
  dmobs = onesided?hretval:fabs(hretval); // "observed" value of statistic  
  //count # times rand comparison values > observed test statistic, to get p-value
  for(i=0;i<nruncombs;i++) if(pthis[i] > dmobs) nmatch++;    
  dret=nmatch/(double)nruncombs;//this output value doesnt mean anything yet
CLEANRSAMPSIG: //free memory and return
  if(ga) free(ga); if(g0t) free(g0t); if(g1t) free(g1t); if(pm) free(pm);
  if(pcombids) free(pcombids); if(pids) free(pids);
  return dret;
}
ENDVERBATIM


VERBATIM
// rantran(index_vec1,value_vec1[,index_vec2,value_vec2,...])
// index_vec can be replaced with a step which gives regular pointers or base values
// in presence of a step value can be eg 10 for 0..9 [or 10.3 for 0,3,6,9 -- not implemented]
// rantran() translates a random index vec through a series of mappings from a value onto 
// one or more possible values: eg rand col indices to rand minicols within that col to 
// rand cell within the minicol to rand locations on the cell dend
static double rantran (void* vv) {
  int i,j,ix,ixe,ixvn,nvn,rvn,na,xj;
  double *ixv, *nv, *x, y[1], ixn,step,indx;
  rvn=vector_instance_px(vv, &x);
  for (na=1;ifarg(na);na++); na--; // count args
  for (i=1;i<na;i+=2) {
    if (hoc_is_object_arg(i)) {
      step=-1;
      ixvn=vector_arg_px(i,&ixv);// ixv[] are indices for nv
      nvn=vector_arg_px(i+1, &nv); // nv are the possible new values
    } else { // can simply calculate the rand vals
      step=*getarg(i);
      indx=*getarg(i+1);
      if (indx>1.) { 
        x1x = (double *)realloc(x1x,sizeof(double)*rvn); 
        mcell_ran4(&ihigh, x1x, rvn, indx);
      }
    }
    for (j=0;j<rvn;j++) { 
      if (step>-1) { // step in by xi[type] and then augment by random val
        x[j]=step + x[j]*indx + ((indx>1.)?(floor(x1x[j])):0.0);
      } else {
        xj=(int)x[j]; // prior level index
        ix=(int)ixv[xj]; ixn=ixv[xj+1]-ix; // possible next level indices; pick 1 in [ix,ixe]
        if (ixn==1.) {
          x[j]=nv[ix];
        } else {
          mcell_ran4(&ihigh, y, 1, ixn);  // pick 1 rand value [0,ix)
          x[j]=nv[(int)y[0]+ix];
        }
      }
    }      
  }
  return (double)rvn; // number of substitutions performed
}
ENDVERBATIM

:* vec.shuffle() Fisher-Yates shuffle (from wikipedia)
: pointlessly extended to augment the vector n-fold (used for cell projections in columns)
: makes more sense to just have a parallel random vector of intra-columnar indices
VERBATIM
static double shuffle (void* vv) {
  int i,j,k,n,nx,augfac; double *x, y[1], temp, augstep;
  nx=vector_instance_px(vv, &x);
  if (ifarg(1)) {
    augfac=(int)*getarg(1);
    if (ifarg(2)) augstep=*getarg(2); else augstep=1.0/augfac;
    x=vector_newsize(vv,nx*augfac);
    for (i=1;i<augfac;i++) for (j=0;j<nx;j++) x[i*nx+j]=x[j]+i*augstep;
    nx*=augfac;
  }
  dshuffle(x,nx);
  return (double)nx;
}
ENDVERBATIM

:* v1.distance(v2) euclidean distance
VERBATIM
static double distance (void* vv) {
  int i, nx, ny;
  double* x, *y, sum;
  sum = 0.;
  nx = vector_instance_px(vv, &x);
  ny = vector_arg_px(1, &y);
  if (nx!=ny) {printf("Vectors must be same size %d %d\n",nx,ny); hxe();}
  for (i=0; i<nx; i++) sum+=(x[i]-y[i])*(x[i]-y[i]); 
  return sqrt(sum);
}
ENDVERBATIM

:* v1.ndprd(v2) normalized dot prod distance (cos of angle)
VERBATIM
static double ndprd (void* vv) {
  int i, nx, ny;
  double* x, *y, sum, sumx, sumy;
  nx = vector_instance_px(vv, &x);
  ny = vector_arg_px(1, &y);
  if (nx!=ny) {printf("Vectors must be same size %d %d\n",nx,ny); hxe();}
  for (i=0, sum=0., sumx=0., sumy=0.; i<nx; i++) {
    sum+=x[i]*y[i]; sumx+=x[i]*x[i]; sumy+=y[i]*y[i]; 
  }
  if (ifarg(2)) { return sum/sqrt(sumx)/sqrt(sumy);                   // cos of angle
  } else {        return acos(sum/sqrt(sumx)/sqrt(sumy))*180./M_PI; } // angle in degrees
}
ENDVERBATIM

:* v1.flipbits(scratch,num) flips num bits
: uses scratch vector of same size as v1 to make sure doesn't flip same bit twice
VERBATIM
static double flipbits (void* vv) {	
  int i, j, nx, ny, flip, ii;
  double *x, *y;
  nx = vector_instance_px(vv, &x);
  ny = vector_arg_px(1, &y);
  flip = (int)*getarg(2);
  if (ny<nx) {hoc_execerror("flipbits:Scratch vector must adequate size", 0);}
  mcell_ran4(&ihigh, y, (unsigned int)ny, (double)nx); // indices to flip
  for (i=0,j=0; i<flip && j<ny; j++) { // flip these bits
    ii=(int)y[j];
    if        (x[ii]==BVBASE) { x[ii]= 1e9; i++;  // mark location 
    } else if (x[ii]==1)      { x[ii]=-1e9; i++; }
  }
  j=i;
  for (i=0; i<nx; i++) if (x[i]==1e9) x[i]=1; else if (x[i]==-1e9) x[i]=BVBASE;
  return (double)j;
}
ENDVERBATIM
 
:* v1.flipbalbits(scratch,num) flips num bits making sure to balance every 1
: flip with a 0 flip to preserve initial power
: uses scratch vector of same size as v1 to make sure doesn't flip same bit twice
VERBATIM
static double flipbalbits(void* vv) {	
	int i, nx, ny, flip, ii, next;
	double* x, *y;

	nx = vector_instance_px(vv, &x);
	ny = vector_arg_px(1, &y);
        flip = (int)*getarg(2);
	if (nx != ny) {
	  hoc_execerror("Scratch vector must be same size", 0);
	}
	for (i=0; i<nx; i++) { y[i]=x[i]; } /* copy */
        next = 1; /* start with 1 */
	for (i=0; i < flip;) { /* flip these bits */
	  ii = (int) ((nx+1)*drand48());
	  if (x[ii]==y[ii] && y[ii]==next) { /* hasn't been touched */
	    next=x[ii]=((x[ii]==1.)?BVBASE:1.);
            i++;
	  }
	}
	return flip;
}
ENDVERBATIM
 
:* v1.vpr([BASE]) prints out neatly in binary -- optional arg allows base 10,16,64
: generally prints out 1 char per entry
VERBATIM
static double vpr (void* vv) {
  int i, nx, flag, min,max;
  double* x; char c;
  FILE* f;
  nx = vector_instance_px(vv, &x);
  min=0; max=nx;
  if (ifarg(3)) {min=(int)*getarg(2); max=(int)*getarg(3)+1;} else if (ifarg(2)) {
    max=(int)*getarg(2)+1; } // inclusive slice
  if (min<0 || max>nx) {printf("stats vpr ERRA OOB: %d %d\n",min,max); hxe();}
  if (ifarg(1)) { 
    if (hoc_is_double_arg(1)) {
      flag=(int) *getarg(1);
      if (flag==2) { // binary which is default
        for (i=min; i<max; i++) printf("%d",(x[i]>BVBASE)?1:0);
      } else if (flag==0) {
        for (i=min; i<max; i++) printf("%s%d%s",x[i]>=10?"|":"",(int)x[i],x[i]>=10?"|":"");
      } else if (flag==-1) { 
        for (i=min; i<max; i++) printf("%04.2f|",x[i]);
      } else {
        for (i=min; i<max; i++) vprpr(x[i],flag);
      }
      if (!ifarg(2)) printf("\n"); else printf(" ");
    } else {
      f = hoc_obj_file_arg(1);
      for (i=min; i<max; i++) {
        if (x[i]>BVBASE) { fprintf(f,"%d",1); 
        } else { fprintf(f,"%d",0); }
      }
      fprintf(f,"\n");
    }
  } else {
    for (i=min; i<max; i++) printf("%d",(x[i]>BVBASE)?1:0);
    printf("\n");
  }
  return 1.;
}
ENDVERBATIM

:* v1.vpr2(v2,[BASE]) prints out 2 vectors using = where same -- optional arg allows base 10,16,64
: use VERBOSE to adjust printing verbose=1 for no spaces; verbose=2 no spaces and abbrev 00->_
VERBATIM
static double vpr2 (void* vv) {
  int i, flag, n, nx, ny, colc, base, min,max, fl2;
  double *x, *y, cnt, ign; char c;
  nx = vector_instance_px(vv, &x);
  cnt=min=0; max=nx;
  ny = vector_arg_px(1, &y);
  if (nx!=ny) {printf("vpr2 diff sizes %d %d\n",nx,ny); hxe();}
  base=(int)*getarg(2);
  flag=(ifarg(3)?(int)*getarg(3):2);
  for (i=min,fl2=0,colc=0; i<max; i++) {
    if (flag>0 && x[i]==BVBASE && y[i]==BVBASE) {
      if (!fl2) {printf(" _ "); colc+=3;}
      fl2=1; 
    } else { 
      fl2=0; colc++;
      vprpr(x[i],base);
      if (colc>(int)newline){printf("\n    "); colc=0;}
    }
  }
  printf("\n");
  for (i=min,fl2=0,colc=0; i<max; i++) {
    if (flag>0 && x[i]==BVBASE && y[i]==BVBASE) {
      if (!fl2) {printf(" _ "); colc+=3;} 
      fl2=1; 
    } else { fl2=0;
      vprpr(y[i],base);
      colc++;
      if (colc>(int)newline){printf("\n    ",colc); colc=0;}
    }
  }
  printf("\n");
  if (flag==1) { 
    for (i=min,n=0,fl2=0,colc=0; i<max; i++) {
      if (x[i]==BVBASE && y[i]==BVBASE) { 
        fl2=1; n++;
      } else { 
        if (fl2) {printf(" %2d ",n); colc+=3;} else {printf(" "); colc++;}
        n=fl2=0; 
      }
      if (colc>(int)newline){printf("\n    ",colc); colc=0;}
    }
    printf("\n");
  }
}

static void vprpr (double x, int base) {
  int xx;
  xx=(int)x;
  if (base==0)  {    printf("%5.2f",x);
  } else if (xx>=base && base!=0) { printf("+");
  } else if (base==64) { // base 64
    if (xx<16) {  printf("%x",xx);    // 0-f   0-15
    } else if (xx<36) {  printf("%c",xx+87); // g-z  16-35
    } else if (xx<62) {  printf("%c",xx+29); // A-Z  36-61
    } else if (xx<63) { printf("@");                // @    62
    } else if (xx<64) { printf("=");                // =    63   
    } else printf("ERROR");
  } else if (base==10) {    printf("%d",xx);
  } else if (base==16) {    printf("%x",xx);
  }
}
ENDVERBATIM

:* v1.bin(targ,invl[min,max]) place counts for each interval
:* v1.bin(list,invl[min,max]) using NQS("count","index") for easy sorting
: like .hist() but doesn't throw away values <min or >max
: note that optional max denotes the start of an interval not end
VERBATIM
static double bin (void* vv) {	
  int i, j, nx, maxsz, lfl;
  double* x, *y, *ix, invl, min, max, maxf, jj;
  Object* ob;
  void* voi[2];

  min=0; max=1e9; maxf=-1e9;
  nx = vector_instance_px(vv, &x);
  ob =   *hoc_objgetarg(1);
  if (strncmp(hoc_object_name(ob),"Vector",6)==0) { lfl=0; // lfl is list flag
    if ((maxsz=openvec(1, &y))==0) hxe();
    voi[0]=vector_arg(1);
  } else { // list of 2
    lfl=1;
    maxsz = list_vector_px3(ob, 0, &y, &voi[0]);
    if (maxsz!=(i=list_vector_px3(ob,1,&ix,&voi[1]))){printf("binERRA %d %d\n",maxsz,i); hxe();}
  }
  invl = *getarg(2);
  if (ifarg(4)) {min=*getarg(3); max=*getarg(4);
  } else if (ifarg(3)) max=*getarg(3);
  for (j=0; j<maxsz; j++) y[j]=0.;
  for (i=0; i<nx; i++) {
    if (x[i]>=max) {        y[(j=(int)(jj=(max-min)/invl))]++;
    } else if (x[i]<=min) { y[(j=0)]++; jj=0.;
    } else {
      if (x[i]>maxf) maxf=x[i]; // max found
      j=(int)(jj=(x[i]-min)/invl);
      if (j>maxsz-1) {printf("bin ERRB OOB: %d>%d\n",j,maxsz-1); hxe();}
      y[j]++;
    }
    if (lfl) ix[j]=jj+min;
  }
  maxsz=(max==1e9)?(int)(maxf/invl+1):(int)((max-min)/invl+1);
  vector_resize(voi[0], maxsz);
  if (lfl) vector_resize(voi[1], maxsz);
  return (double)maxsz;
}
ENDVERBATIM

:* ind.ihist(vec,list,tmin,tmax,binsz,[,ioff]) does binning for individual indices
: into list -- ioff gives an offset such that index N maps to list.o(0)
: normally used for a raster pair of cell indices (ind) and spike time (tvec)
: eg  nq=new NQS(#cells)
:     ind.ihist(tvec,nq.vl,tmin,tmax,100)
VERBATIM
static double ihist (void* vv) {
  unsigned int i, j, k, n, nx, c;
  double *x, *tv, ioff, min, max, nbin, binsz; 
  ListVec* pL; Object* obl;
  nx = vector_instance_px(vv, &x); // vector of indices
  i = vector_arg_px(1, &tv); // vector of times
  if (i!=nx) {printf("vecst:ihist()ERR0: diff size %d %d\n",nx,i); hxe();}
  if (!flag && !ismono1(tv,nx,1)){
    printf("vecst:ihist()ERR0A: set flag_stats for non-monotonic time vec\n",nx,i); hxe();}
  pL = AllocListVec(obl=*hoc_objgetarg(2));
  min=*getarg(3); max=*getarg(4); binsz=*getarg(5); 
  if (binsz<=0) {printf("stats:ihist()ERR0B: binsz must be >0 (%g)\n",binsz); hxe();}
  nbin=floor((max-min)/binsz);
  max=min+binsz*nbin; // new max
  if (verbose) printf("%g-%g in %g bins of %g\n",min,max,nbin,binsz);
  if (ifarg(6)) ioff=*getarg(6); else ioff=0.;
  if (pL->isz<2) {printf("stats:ihist()ERRA: %d\n",pL->isz); FreeListVec(&pL); hxe();}
  c=pL->isz;     // number of columns (list length)
  // pL->pv[i][j] -- i goes through the list and j goes through each vector
  for (i=0;i<c;i++) {
    pL->pv[i]=list_vector_resize(obl, i, (int)nbin);
    for (j=0;j<(int)nbin;j++) pL->pv[i][j]=0.;
  }
  i=n=0;
  if (!flag) for (;i<nx; i++) if (tv[i]>=min) break; // tvec sorted so can move forward to begin
  for (;i<nx; i++) { // read through the parallel index and time vectors
    if (flag) { // default is flag==0: tvec sorted so can return
      if (tv[i]>=max || tv[i]<min) continue;
    } else if (tv[i]>=max) break;
    k=(int)(x[i]-ioff); // which cell index
    if (k>=c || k<0) continue; // ignore outside of index range
    j=(int)((tv[i]-min)/binsz); // which time bin
    // if(j>=nbin||j<0){printf("INTERR %d %d %d %g %g %g %g\n",k,c,j,nbin,tv[i],min,binsz);hxe();}
    pL->pv[k][j]++;
    n++;
  }
  flag=0;
  FreeListVec(&pL);
  return (double)n;
}
ENDVERBATIM

:* vec.irate(vhist,binsz) - sets contents of vec to instantaneous rate using inverse
: of interspike intervals
VERBATIM
static double irate (void* vv) {
  unsigned int i, j, n, nx;
  double *prate,*phist,binsz,t1,t2;
  nx = vector_arg_px(1, &phist);
  vector_resize(vv,nx);
  vector_instance_px(vv, &prate);
  binsz = *getarg(2);
  for(i=0;i<nx;i++) {
    prate[i]=0.;
    if(phist[i]>0) {
      t1=t2=i;
      prate[i]=phist[i]*1e3/binsz;
      i++;
      break;
    }
  }
  for(;i<nx;i++) {
    prate[i]=0.;
    if(phist[i]>0) {
      t2=i;
      prate[i]=phist[i]*1e3/binsz;
      break;
    }
  }
  if(verbose>1) if(t1==t2) printf("t1==t2!\n");
  for(i=t1;i<t2;i++) prate[i] = 1e3 / (binsz*(t2-t1));
  i++;
  for(;i<nx;i++) {
    if(phist[i]>0) { 
      prate[i] = phist[i]*1e3/binsz;
      t1=t2; t2=i;      
      if(verbose>2) printf("t1 %g t2 %g\n",t1,t2);
    } else {
      if(verbose>1) if(t1==t2) printf("t1==t2!\n");
      prate[i] = 1e3 / (binsz*(t2-t1));
    }
  }
  return 1.0;
}

//* dlvar(p,sz) -- calculates the local variation in interspike interval stored in p.
// p should have all positive numbers. for poisson interspike intervals, dlvar will return 1.
// for regular interspike intervals, dlvar will return 0. 
double dlvar (double* p, int sz) {
  int i; double s,n,d;
  s=0.0;
  for(i=0;i<sz-1;i++) {
    n = p[i]-p[i+1];
    n = n*n;
    d = p[i]+p[i+1];
    d = d*d;
    s += 3*n/d;
  }
  return s / (double) (sz-1.0);
}
//* visi.lvar() -- returns local variation in interspike interval stored in visi
static double lvar (void* vv) {
  double *x; int sz;
  if((sz=vector_instance_px(vv,&x))<2) {
    fprintf(stderr,"lvar WARNA: vector size must be >= 2, returning 0!\n");
    return 0.0;
  }
  return dlvar(x,sz);
}
ENDVERBATIM

VERBATIM
//cholesky decomposition from numerical recipies chapter 2.9
//Given a positive-dfinite symmetric matrix a[1..n][1..n], this routine constructs its Cholesky
//decomposition, A = L * LT . On input, only the upper triangle of a need be given; it is not
//modified. The Cholesky factor L is returned in the lower triangle of a, except for its diagonal
//elements which are returned in p[1..n]
int choldc(double **a, int n, double p[])
{
  int i,j,k;
  double sum;  
  for (i=0;i<n;i++) {
    for (j=i;j<n;j++) {
      for (sum=a[i][j],k=i-1;k>=0;k--) sum -= a[i][k]*a[j][k]; 
      if (i == j) {
        if (sum <= 0.0) return 0;
        p[i]=sqrt(sum);
      } else a[j][i]=sum/p[i];
    }
  }
  return 1;
}
ENDVERBATIM

: mktscor(pearson r-value,list of time-series)
: each time-series should be normally distributed
: upon return, the values will be changed and each pair of time-series will be correlated with pcorrel = ~r
: same method as here http://comisef.wikidot.com/tutorial:correlation
FUNCTION mktscor () {
VERBATIM
  double dret,*ptmp,**cF,**Y,**X,**cFT,r;
  ListVec *pTS;
  int i,j,k,nrows,ncols,nrcf;
  dret=0.0;
  pTS=0x0; ptmp=0x0; cF=cFT=0x0; X=Y=0x0;
  r = *getarg(1);
  pTS = AllocListVec(*hoc_objgetarg(2));
  nrows=pTS->plen[0]; ncols=pTS->isz;
  X = getdouble2D(nrows,ncols);
  for(i=0;i<ncols;i++) for(j=0;j<nrows;j++) X[j][i] = pTS->pv[i][j];
  nrcf=ncols;
  cF = getdouble2D(nrcf,nrcf);
  for(i=0;i<ncols;i++) for(j=0;j<=i;j++) if(j==i) cF[i][j]=1; else cF[i][j]=cF[j][i]=r;
  ptmp = (double*)calloc(ncols,sizeof(double));
  if(!choldc(cF,ncols,ptmp)) { printf("mktscor ERRA: arg must be positive definite!\n"); goto MKTSCORFREE; }
  for(i=0;i<ncols;i++) for(j=1;j<ncols;j++) if(j>i) cF[i][j]=0.0; else if(j==i) cF[i][j]=ptmp[i];
  cFT = getdouble2D(nrcf,nrcf);
  for(i=0;i<nrcf;i++) for(j=0;j<nrcf;j++) cFT[i][j] = cF[j][i];
  if(verbose){
    printf("\n\ncholsky decomp:\n");
    for(i=0;i<nrcf;i++) { for(j=0;j<nrcf;j++) printf("%g ",cFT[i][j]); printf("\n"); } printf("\n");
  }
  Y = getdouble2D(nrows,ncols);   //Y = X * cFT
  for(i=0;i<nrows;i++) for(j=0;j<ncols;j++) for(k=0;k<nrcf;k++) Y[i][j] += X[i][k] * cFT[k][j];//mat-mult.
  for(i=0;i<nrows;i++) for(j=0;j<ncols;j++) pTS->pv[j][i]=Y[i][j];
MKTSCORFREE:
  dret=1.0;
  if(pTS) FreeListVec(&pTS);
  if(ptmp) free(ptmp);
  if(cF) freedouble2D(&cF,nrcf);
  if(cFT) freedouble2D(&cFT,nrcf);
  if(Y) freedouble2D(&Y,nrows);
  if(X) freedouble2D(&X,nrows);
  return dret;
ENDVERBATIM
}

:* PROCEDURE install_stats()
PROCEDURE install () {
  if (INSTALLED==1) {
    printf("$Id: stats.mod,v 1.227 2012/09/07 14:25:41 samn Exp $")
  } else {
  INSTALLED=1
VERBATIM
  x1x=y1y=z1z=0x0;
  ihigh=1;
  install_vector_method("slope", slope);
  install_vector_method("moment", moment);
  install_vector_method("vslope", vslope);
  install_vector_method("stats", stats);
  install_vector_method("pcorrel", pcorrel);
  install_vector_method("scorrel",scorrel);
  install_vector_method("kcorrel",kcorrel);
  install_vector_method("rms",rms);
  install_vector_method("vstats", vstats);
  install_vector_method("randwd", randwd);
  install_vector_method("hamming", hamming);
  install_vector_method("flipbits", flipbits);
  install_vector_method("flipbalbits", flipbalbits);
  install_vector_method("vpr", vpr);
  install_vector_method("vpr2", vpr2);
  install_vector_method("bin", bin);
  install_vector_method("ihist", ihist);
  install_vector_method("setrnd", setrnd);
  install_vector_method("rantran", rantran);
  install_vector_method("distance", distance);
  install_vector_method("ndprd", ndprd);
  install_vector_method("hash", hash);
  install_vector_method("smash", smash);
  install_vector_method("smash1", smash1);
  install_vector_method("dpro", dpro);
  install_vector_method("unnan", unnan);
  install_vector_method("combi", combi);
  install_vector_method("shuffle", shuffle);
  install_vector_method("comb", comb);
  install_vector_method("combid", combid);
  install_vector_method("rsampsig",rsampsig);
  install_vector_method("irate",irate);
  install_vector_method("cumsum",cumsum);
  install_vector_method("lvar",lvar);
ENDVERBATIM
  }
}

PROCEDURE prhash (x) {
VERBATIM {
  long unsigned int xx;
  xx=*(long unsigned int*)(&_lx);
  printf("%16lx\n",xx);
}
ENDVERBATIM
}

:* fac (n) 
: from numerical recipes p.214
FUNCTION fac (n) {
VERBATIM {
    static int ntop=4;
    static double a[101]={1.,1.,2.,6.,24.};
    static double cof[6]={76.18009173,-86.50532033,24.01409822,
      -1.231739516,0.120858003e-2,-0.536382e-5};
    int j,n;
    n = (int)_ln;
    if (n<0) { hoc_execerror("No negative numbers ", 0); }
    if (n>100) { /* gamma function */
      double x,tmp,ser;
      x = _ln;
      tmp=x+5.5;
      tmp -= (x+0.5)*log(tmp);
      ser=1.0;
      for (j=0;j<=5;j++) {
        x += 1.0;
        ser += cof[j]/x;
      }
      return exp(-tmp+log(2.50662827465*ser));
    } else {
      while (ntop<n) {
        j=ntop++;
        a[ntop]=a[j]*ntop;
      }
    return a[n];
    }
}
ENDVERBATIM
}
 
:* logfac (n)
: from numerical recipes p.214
FUNCTION logfac (n) {
VERBATIM {
    static int ntop=4;
    static double a[101]={1.,1.,2.,6.,24.};
    static double cof[6]={76.18009173,-86.50532033,24.01409822,
      -1.231739516,0.120858003e-2,-0.536382e-5};
    int j,n;
    n = (int)_ln;
    if (n<0) { hoc_execerror("No negative numbers ", 0); }
    if (n>100) { /* gamma function */
      double x,tmp,ser;
      x = _ln;
      tmp=x+5.5;
      tmp -= (x+0.5)*log(tmp);
      ser=1.0;
      for (j=0;j<=5;j++) {
        x += 1.0;
        ser += cof[j]/x;
      }
      return (-tmp+log(2.50662827465*ser));
    } else {
      while (ntop<n) {
        j=ntop++;
        a[ntop]=a[j]*ntop;
      }
    return log(a[n]);
    }
}
ENDVERBATIM
}

VERBATIM
unsigned int hashseed2 (int na, double* x) {
  int i; union dblint xx; double y, big;
  big=pow(DBL_MAX,1./(double)(na+1)); // base biggest # on nth root of num of values being used
  ihigh=1;
  for (i=0;i<na;i++) {
    if (x[i]==0.0) continue;
    xx.d=x[i];
    if (xx.i[0]==0) { xx.i[0]=xx.i[1]; xx.i[0]<<=4; } // high order bits may be 0
    if (xx.i[1]==0) { xx.i[1]=xx.i[0]; xx.i[1]<<=4; } // low order bits unlikely 0
    xx.i[0]+=(i+1); xx.i[1]+=(i+1); // so different for different order args
    mcell_ran4_init(xx.i[1]);
    mcell_ran4(&xx.i[0], &y, 1, big); // generate a pseudorand number based on these
    while (y>UINT_MAX) y/=1e9; // UINT_MAX is 4.294967e+09
    ihigh*=(unsigned int)y;  // keep multiplying these out
  }
  return ihigh; // global
}
ENDVERBATIM

FUNCTION hashseed () {
  VERBATIM
  int i,na,nb,sf=0; double *x=0;
  if (hoc_is_double_arg(2)) {
    for (na=1;ifarg(na);na++); 
    na--;
    if (na==1) nb=2; else nb=na;
    x = (double *) malloc(sizeof(double)*nb);
    for (i=1;i<=na;i++) x[i-1]=*getarg(i);
    if (na==1) x[1]=x[0]*x[0]+13; // so can get something
    sf=1;//should free
  } else {
    nb=(int)*getarg(1);
    x=hoc_pgetarg(2);
  } 
  hashseed2(nb,x);
  if(sf) free(x); //only free if malloc'd
  _lhashseed=(double)ihigh;
  ENDVERBATIM
}

: unable to get the drand here to recognize the same fseed used in rand
FUNCTION vseed () {
  VERBATIM
#ifdef WIN32
  if (ifarg(1)) seed=*getarg(1); else {
    printf("TIME ACCESS NOT PRESENT IN WINDOWS\n");
    hxe();
  }
  srand48((unsigned)seed);
  set_seed(seed);
  return seed;
#else
  struct  timeval tp;
  // struct  timezone tzp;
  // if (ifarg(1)) seed=*getarg(1); else {
  //   gettimeofday(&tp,&tzp);
  //   seed=tp.tv_usec;
  // }
  srand48((unsigned)seed);
  set_seed(seed);
  srandom(seed);
  ihigh=(unsigned int)seed;
  return seed;
#endif
  ENDVERBATIM
}

: mc4seed() sets 'low' bits for mccell_ran4() 
: opt 2nd arg ihigh is 'high' bits; see (/usr/site/nrniv/nrn/src/ivoc/ivocrand.cpp:85) u_int32_t ihigh_, orig_, ilow_
FUNCTION mc4seed () {
  VERBATIM
  double x; u_int32_t idx; unsigned int y;
  if (!ifarg(1)) {
    printf("low:%d high:%d\n",(unsigned int)ilow,(unsigned int)ihigh);
    return (double)ihigh;
  } else {
    // u_int32_t idx=(u_int32_t) chkarg(1, 0., 4294967295.);
    x = *getarg(1);
    if (x>dmaxuint) {y=(unsigned int)x%4294967296; printf("Warning truncating %20.0f to %d (ilow)\n",x,y);x=y;}
    ilow = idx = (u_int32_t)x;
    mcell_ran4_init(idx);
  }
  if (ifarg(2)) {
    x = *getarg(2);
    if (x>dmaxuint) {y=(unsigned int)x%4294967296; printf("Warning truncating %20.0f to %d (ihigh)\n",x,y);x=y;}
    ihigh=(u_int32_t) x;
  }
  return (double)ihigh;
  ENDVERBATIM
}


: from Numerical Recipes in C
FUNCTION gammln (xx) {
  VERBATIM {
    double x,tmp,ser;
    static double cof[6]={76.18009173,-86.50532033,24.01409822,-1.231739516,0.120858003e-2,-0.536382e-5};
    int j;
    x=_lxx-1.0;
    tmp=x+5.5;
    tmp -= (x+0.5)*log(tmp);
    ser=1.0;
    for (j=0;j<=5;j++) {
      x += 1.0;
      ser += cof[j]/x;
    }
    return -tmp+log(2.50662827465*ser);
  }
  ENDVERBATIM
}

FUNCTION betai(a,b,x) {
VERBATIM {
  double bt;
  double gammln(),betacf();

  if (_lx < 0.0 || _lx > 1.0) {printf("Bad x in routine BETAI\n"); hxe();}
  if (_lx == 0.0 || _lx == 1.0) bt=0.0;
  else
  bt=exp(gammln(_la+_lb)-gammln(_la)-gammln(_lb)+_la*log(_lx)+_lb*log(1.0-_lx));
  if (_lx < (_la+1.0)/(_la+_lb+2.0))
  return bt*betacf(_la,_lb,_lx)/_la;
  else
  return 1.0-bt*betacf(_lb,_la,1.0-_lx)/_lb;
 }
ENDVERBATIM
}

VERBATIM
#define ITMAX 100
#define EPS 3.0e-7
ENDVERBATIM

FUNCTION betacf(a,b,x) {
VERBATIM {
  double qap,qam,qab,em,tem,d;
  double bz,bm=1.0,bp,bpp;
  double az=1.0,am=1.0,ap,app,aold;
  int m;
  void nrerror();

  qab=_la+_lb;
  qap=_la+1.0;
  qam=_la-1.0;
  bz=1.0-qab*_lx/qap;
  for (m=1;m<=ITMAX;m++) {
    em=(double) m;
    tem=em+em;
    d=em*(_lb-em)*_lx/((qam+tem)*(_la+tem));
    ap=az+d*am;
    bp=bz+d*bm;
    d = -(_la+em)*(qab+em)*_lx/((qap+tem)*(_la+tem));
    app=ap+d*az;
    bpp=bp+d*bz;
    aold=az;
    am=ap/bpp;
    bm=bp/bpp;
    az=app/bpp;
    bz=1.0;
    if (fabs(az-aold) < (EPS*fabs(az))) return az;
  }
  printf("a or b too big, or ITMAX too small in BETACF"); return -1.;
}
ENDVERBATIM
}

FUNCTION symval() {
VERBATIM {
  Symbol *sym;
  sym = hoc_get_symbol(* hoc_pgargstr(1));
  // should do type check eg sym->type == VAR
  return *(hoc_objectdata[sym->u.oboff]._pval); // is this ._pval safe??
 }
ENDVERBATIM
}

:* tval(r,N) , computes t-statistic , r == pearson correlation coefficient, N == size of sample
FUNCTION tstat() {
  VERBATIM
  double r = fabs(*getarg(1));
  double N = *getarg(2);
  if(N < 2) { printf("tstat ERRA: N must be > 2!\n"); return -1; }
  return r * sqrt(N-2.)/sqrt(1.0-(r*r));
  ENDVERBATIM
}

FUNCTION tdistrib() {
  VERBATIM
  double gammln();
  double x = *getarg(1);
  double dof = *getarg(2);
  double res = (gammln( (dof+1.0) / 2.0 )  / gammln( dof / 2.0 ) );
  double pi = 3.14159265358979323846;
  res *= (1.0 / sqrt( dof * pi ) );
  res *= pow((1 + x*x/dof),-1.0*((dof+1.0)/2.0));
  return res;
  ENDVERBATIM
}

: based on code from http://www.psychstat.missouristate.edu/introbook/rdist.htm
: return estimate of critical correlation coefficient (r) that >= to it would be considered significant
: at a given sample size of $1 (N) . probability of null hypothesis p < 0.05
: iff $2 == 1, probability of null hypothesis p < 0.01 ( r will then be higher )
: null hypothesis == correlation between variables , r , == 0
: this function uses a lookup table so is limited in estimates -- max sample size , N, == 1000 , but
: if your sample is bigger and your r value is also bigger, the correlation is significant because
: in general, as the sample size , N , increases, the r value above which is considered significant decreases
FUNCTION rcrit () {
  VERBATIM
  double rtbl[68][3]={//for each row: index0==N, index1==p0.05 value of r, index2==p0.01 value of r
    1 , 0.997 , 0.999 ,    2 , 0.950 , 0.990 ,    3 , 0.878 , 0.959 ,    4 , 0.811 , 0.917 ,    5 , 0.754 , 0.874 ,
    6 , 0.707 , 0.834 ,    7 , 0.666 , 0.798 ,    8 , 0.632 , 0.765 ,    9 , 0.602 , 0.735 ,    10 , 0.576 , 0.708 ,
    11 , 0.553 , 0.684 ,    12 , 0.532 , 0.661 ,    13 , 0.514 , 0.641 ,    15 , 0.482 , 0.606 ,    16 , 0.468 , 0.590 ,
    17 , 0.456 , 0.575 ,    18 , 0.444 , 0.561 ,    19 , 0.433 , 0.549 ,    20 , 0.423 , 0.537 ,    21 , 0.413 , 0.526 ,
    22 , 0.404 , 0.515 ,    23 , 0.396 , 0.505 ,    24 , 0.388 , 0.496 ,    25 , 0.331 , 0.487 ,    26 , 0.374 , 0.478 ,
    27 , 0.367 , 0.470 ,    28 , 0.361 , 0.463 ,    29 , 0.355 , 0.456 ,    30 , 0.349 , 0.449 ,    31 , 0.344 , 0.442 ,
    32 , 0.339 , 0.436 ,    33 , 0.334 , 0.430 ,    34 , 0.329 , 0.424 ,    35 , 0.325 , 0.418 ,    36 , 0.320 , 0.413 ,
    37 , 0.316 , 0.408 ,    38 , 0.312 , 0.403 ,    39 , 0.308 , 0.398 ,    40 , 0.304 , 0.393 ,    41 , 0.301 , 0.389 ,
    42 , 0.297 , 0.384 ,    43 , 0.294 , 0.380 ,    44 , 0.291 , 0.376 ,    45 , 0.288 , 0.372 ,    46 , 0.284 , 0.368 ,
    47 , 0.281 , 0.364 ,    48 , 0.279 , 0.361 ,    58 , 0.254 , 0.330 ,    63 , 0.244 , 0.317 ,    68 , 0.235 , 0.306 ,
    73 , 0.227 , 0.296 ,    78 , 0.220 , 0.286 ,    83 , 0.213 , 0.278 ,    88 , 0.207 , 0.270 ,    93 , 0.202 , 0.263 ,
    98 , 0.195 , 0.256 ,    123 , 0.170 , 0.230 ,    148 , 0.159 , 0.210 ,    173 , 0.148 , 0.194 , 
    198 , 0.138 , 0.181 ,   298 , 0.113 , 0.148 ,    398 , 0.098 , 0.128 ,    498 , 0.088 , 0.115 ,    
    598 , 0.080 , 0.105 ,   698 , 0.074 , 0.097 ,    798 , 0.070 , 0.091 ,    898 , 0.065 , 0.086 ,  
    998 , 0.062 , 0.081   
  };
  double N;
  int get99, i , tablen, df;
  N = *getarg(1); 
  get99 = ifarg(2) ? (int)*getarg(2) : 0;
  tablen = 68;

  if(N < 3){
    printf("rcrit ERRA: N must be >= 3!\n");
    return -1.0;
  }

  if( N > 998+2 ) { printf("rcrit WARNA: Using N=1000 as estimate.\n"); N = 998+2; }

  df = (int)N - 2;

  for(i=0;i<tablen;i++) if(rtbl[i][0]==df) if(get99) return rtbl[i][2]; else return rtbl[i][1];

  for(i=1;i<tablen;i++) {
    if (rtbl[i][0] > df) {
      if(get99)
        return rtbl[i-1][2] + ((rtbl[i][2] - rtbl[i-1][2])*((df - rtbl[i-1][0] )/(rtbl[i][0] - rtbl[i-1][0])));
      else 
        return rtbl[i-1][1] + ((rtbl[i][1] - rtbl[i-1][1])*((df - rtbl[i-1][0] )/(rtbl[i][0] - rtbl[i-1][0])));      
    }
  }
  return -1.0;
  ENDVERBATIM
}
