: $Id: infot.mod,v 1.161 2010/08/19 20:02:27 samn Exp $ 

NEURON {
  SUFFIX infot
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
#include "misc.h"
#include <stdlib.h>
#include <math.h>
static const double* ITsortdata = NULL; /* used in the quicksort algorithm */
static double tetrospks2(), pdfpr(), tetrospks3();
static int dbxi[10];

typedef struct ITNode_ {
  int idims;
  int icount;
  int* pvals;
  struct ITNode_* pLeft;
  struct ITNode_* pRight;
} ITNode;

ITNode* allocITNode(int idims) {
  ITNode* p;
  p = calloc(1,sizeof(ITNode));
  if(!p) { printf("allocITNode: out of mem!\n"); hxe(); return 0x0; }
  p->pvals = calloc(idims,sizeof(int));
  return p;
}

void freeITNode(ITNode** pp) {
  ITNode* p;
  p = pp[0];
  free(p->pvals);
  if(p->pLeft != 0x0) freeITNode(&p->pLeft);
  if(p->pRight!= 0x0) freeITNode(&p->pRight);
  free(p);
  *pp = 0x0;
}

int compITNode(ITNode* pL,ITNode* pR) {
  int idims,i;
  idims = pL->idims;
  for(i=0;i<idims;i++) {
    if(pL->pvals[i] < pR->pvals[i]) return -1; //left < right
    if(pL->pvals[i] > pR->pvals[i]) return 1;  //left > right  
  }
  return 0; //equal
}

//find pS's value in tree rooted at pRoot and return the node, if it exists
//otherwise return 0x0
ITNode* findITNode( ITNode* pRoot, ITNode* pS ) {
  int ic;
  if(pRoot == 0x0 || pS == 0x0) return 0x0;
  ic = compITNode(pS,pRoot);
  if(ic==0) {
    return pRoot;
  } else if(ic == -1) {
    return findITNode(pRoot->pLeft,pS);
  } else return findITNode(pRoot->pRight,pS);
}

//insert pNew into tree rooted at pRoot
//pNew's count should be initialized to 1
//if pNew->pval already exists in the tree, it isnt inserted again, instead the count of the node its in is incremented by 1
//0 is returned when pNew isnt inserted, when pNew is inserted, 1 is returned
int insertITNode( ITNode* pRoot, ITNode* pNew ) {
  int ic;
  ic = compITNode(pNew,pRoot);
  if(ic == 0) {
    pRoot->icount++;
    return 0;
  }
  if(ic == -1) {
    if(pRoot->pLeft == 0x0) {
      pRoot->pLeft = pNew;
      return 1;
    } 
    return insertITNode(pRoot->pLeft,pNew);
  } else {
    if(pRoot->pRight == 0x0) {
      pRoot->pRight = pNew;
      return 1;
    }
    return insertITNode(pRoot->pRight,pNew);
  }
}

ENDVERBATIM

FUNCTION TestITree () {
  VERBATIM
  int i,j;
  ITNode *pRoot,pNew;
  return 0.0;
  ENDVERBATIM
}

VERBATIM

//* functions: getavgd() getstdevd()
double getavgd(double* p,int n) {
  int i; double sum,*pp;
  if(n<1) return 0.0;
  sum = 0.0; pp=p;
  for(i=0;i<n;i++,pp++) sum += *pp;
  return sum / (double) n;
}

double getstdevd(double* p,int n) {
  int i;
  double X,X2,*pp;
  if(n<1) return 0.;
  X=X2=0.0; pp=p;
  for(i=0;i<n;i++,pp++) {
    X2 += (*pp * *pp);
    X += *pp;
  }
  X /= (double)n;
  X2 = X2/(double)n - X*X;
  if(X2>0.) return sqrt(X2);
  return 0.;
}

double getstdevi(int* p,int n) {
  double sd,X,X2;
  int i;
  X = X2 = 0.0;
  for(i=0;i<n;i++) {
    X += p[i];
    X2 += p[i]*p[i];
  }
  X /= (double) n;
  sd = X2/n - X*X;
  if(sd>0.) return sqrt(sd);
  return 0.0;
}

double kprob1Dd (double* X,int sz,double h,double val) {
  double prob,dif,sig2,h2;
  int i;
  h2 = 2.0*h*h;
  prob = 0.0;
  for(i=0;i<sz;i++) {
    dif = val-X[i];
    dif *= dif;
    prob += exp( -dif / h2 );
  }
  prob *= (1.0 / ( (double) sz * h * SQRT2PI ) );
  return prob;
}

double kprob2D (int* X,int* Y,int sz,double sigma,double a,int x,int y) {
  double prob,dx,dy,sig2; 
  int i;
  prob = 0.0;
  sig2 = sigma * sigma;
  for(i=0;i<sz;i++) {
    dx = x - X[i];
    dy = y - Y[i];
    dx *= dx;
    dy *= dy;
    prob += exp( (-dx-dy) / sig2 );
  }
  return prob;
}

double log2d ( double d ) {
  return log(d) / LG2;
}

//* kprobstepi() kernel density PDF using step kernel
// h == bandwidth
// each row of XX is a different data-point, each column is a diff dimension
// x is the data vector who's probability is to be calculated
double kprobstepi (int** XX,int iDims,int iStartIDX,int iLen,double h,int* x) {
  double prob,dif,val,cnt;
  int i,j;
  prob = cnt = 0.0;
  for(i=iStartIDX;i<iLen;i++) { //go through data points
    dif = 0.0;
    for(j=0;j<iDims;j++) { //calc distance
      val = x[j] - XX[i][j];
      dif += val*val;
    }
    dif = h - sqrt(dif);
    if(dif > 0) prob += 1.0; //apply step function
    cnt += 1.0;
  }  
  prob = prob / cnt; 
  return prob;
}

//* kprobgaussi() kernel density PDF using gaussian kernel
// h == bandwidth
// each row of XX is a different data-point, each column is a diff dimension
// x is the data vector who's probability is to be calculated
double kprobgaussi (int** XX,int iDims,int iStartIDX,int iLen,double h,int* x) {
  double prob,dif,val,h2,hh,tp,tpn;  
  int i,j;
  tp = 2.0*3.14159265;
  tpn = pow(tp,((double)iDims)/2.0);
  h2 = h; // 2.0*h*h;
  hh = h;
//  val = h * SQRT2PI;
//  hh = 1;
//  for(i=0;i<iDims;i++) hh *= val; // get normalization term
  prob = 0.0;
  for(i=iStartIDX;i<iLen;i++) {
    dif = 0.0;
    for(j=0;j<iDims;j++) {
      val = x[j] - XX[i][j];
      dif += val*val;
    }
    prob += exp( -dif / h2 );
  }
//  prob = prob / ( tpn * iLen * hh );
  prob = prob / ( tpn * iLen );
  return prob;
}

//** getbandwidthd()
double getbandwidthd (int d,int N,double sd) {

  //uses silverman 1986 formula for optimal bandwidth, assuming data is approximately gaussian
  if(d > 1) {
    return sd*pow((4.0/(double)d+2.0),1.0/((double)d+4.0))*pow((double)N,-1.0/(d+4.0));
  } else {
    return sd * 1.06 * pow((double)N,-0.2);
  }

  //    def scotts_factor(self):
  //      return power(self.n, -1./(self.d+4))

  //   def silverman_factor(self):
  //      return power(self.n*(self.d+2.0)/4.0, -1./(self.d+4))

  return 1.;
}

//** getnormd()
int* getnormd (double* x,int sz,int nbins) {
  int* p;
  double max,min,rng,dnbins;
  int i;
  max=min=x[0];
  for(i=1;i<sz;i++) {
    if(x[i]>max) max=x[i];
    if(x[i]<min) min=x[i];
  }
  p = (int*) malloc(sizeof(int)*sz);
  rng = max - min; dnbins = nbins;
  for(i=0;i<sz;i++) {
    p[i] = (int) ((dnbins * ((double)x[i]-min)/rng) + 0.5);
    if(p[i] < 0) p[i] = 0; else if(p[i] >= nbins) p[i] = nbins - 1;
  }
  return p;
}

//** downsampavgd - downsamples pin vector taking average of chunks of size winsz
// returns results in pout , which must be allocated with size of ceil(sz/winsz)*sizeof(double)
int downsampavgd (double* pin,double* pout,int szin,int szout,int winsz) {
  double dsz,dsum;
  dsz= (double)szin/(double)winsz;  dsz = ceil(dsz);
  if(szout<dsz) return 0;
  int i,j,k,startx,endx,cnt;
  for(i=0,k=0;i<szin;i+=winsz) {
    startx=i; endx=i+winsz-1; if(endx>=szin) endx=szin-1;
    cnt=endx-startx+1; dsum=0.;
    for(j=startx;j<=endx;j++) dsum += pin[j];
    if(cnt>0) dsum /= (double) cnt;
    pout[k++] = dsum;
  }
  return 1;
}

//** chencd - changes in pin are encoded as 0:decrease,1:same,2:increase in pout
void chgencd (double* pin,double* pout,int sz) {
  double df; int i;
  if(sz<1) return;
  pout[0]=1;
  for(i=1;i<sz;i++) {
    df=pin[i]-pin[i-1];
    if(df>0) {
      pout[i]=2;
    } else if(df<0) {
      pout[i]=0;
    } else pout[i]=1;
  }
}

//** oddometerinc() increment the oddometer stored in p
int oddometerinc (int* p,int idims,int imaxval) {
  int i;
  i = 0;
  for(;i<idims;i++) {
    if(p[i] + 1 > imaxval) {
      p[i] = 0;
      continue;
    }
    p[i] += 1;
    return 1;
  }
  return 0;
}

int* doublep2intp (double* d, int sz) {
  int i;
  int* pout;
  pout = (int*) malloc(sizeof(int)*sz);
  if(!pout) { printf("doublep2intp: out of mem!\n"); hxe(); }
  for(i=0;i<sz;i++) pout[i] = (int) d[i]; 
  return pout;
}

void pri2d (int** p, int r,int c) {
  int i,j;
  for(i=0;i<r;i++) {
    for(j=0;j<c;j++) {
      printf("%d ",p[i][j]);
    }
    printf("\n");
  }
}

// 001100110011  110
//* issubint - check if pattern pat occurs in 'string' str
// sz1 is size of str, sz2 is size of pat. returns 1 iff pat found, 0 otherwise
int issubint (int* str,int sz1,int* pat,int sz2) {
  int i,j;  
  for(i=0;i+sz2<=sz1;i++) {//shift pattern against positions in str
    for(j=0;j<sz2 && str[i+j]==pat[j];j++);//check for match
    if(j==sz2) return 1;//match found, return 1
  }
  return 0;//no match found, return 0
}

//* lz76complexityd
//  LZ-76 complexity measure to estimate entropy -- x should only have 1s and 0s 
double lz76complexityd (double* x,int iLen) {
  int *px,**pdict,i,j,npat,patlen,fnd;
  if(iLen<1) return 0.0;
  px=doublep2intp(x,iLen);
  pdict=getint2D(iLen,2);//offset length
  npat=i=1; pdict[0][0]=0; pdict[0][1]=1;//first pattern of length 1
  while(i<iLen) {    
    fnd=1;
    for(patlen=1;i+patlen<iLen;patlen++) { //look for new pattern
      if(verbose>2) printf("i%d patlen%d\n",i,patlen);
      if(!(fnd=issubint(px,i,&px[i],patlen))){//pattern not a sub-string, so its a new pattern
        pdict[npat][0]=i; pdict[npat][1]=patlen; npat++; i+=patlen; if(verbose>2) printf("not found\n"); break;
      } 
    }
    if(fnd) {pdict[npat][0]=i; pdict[npat][1]=iLen-i; npat++; break;} //last pattern may appear twice
  }
  if(verbose>1) { //print input with pattern separator
    j=0; printf("found %d patterns:\n\t",npat);
    for(i=0;i<iLen;i++) {
      if(i==pdict[j][0]+pdict[j][1]){ printf("|"); j++; }
      printf("%d",px[i]);
    }  printf("\n");
    printf("pat off len:\n");
    for(i=0;i<npat;i++) printf("\t%d %d\n",pdict[i][0],pdict[i][1]);
  }
  free(px); freeint2D(&pdict,iLen);
  return log2d((double)iLen) * npat / (double)iLen;
}

//* lz76c : LZ-76 complexity measure to estimate entropy -- should only provide input consisting of 1.0 and 0.0
static double lz76c (void* vv) {
  double* x; int n;
  n = vector_instance_px(vv,&x);
  if(n<1) { printf("lz76c ERRA: 0 size vector\n"); return 0.0; }
  return lz76complexityd(x,n);
}

//* tentropd() transfer entropy of y -> x
//x=time-series 1, y=time-series 2,iLen=# of samples,nbins=# of values to discretize time-series to,
//xpast=# of past x values to use for prediction,ypast=# of past y values to use for prediction
//hval is bandwidth specified by user, if <=0.0, tentropd will select
// te = sum p(xf,xp,yp) * log(p(xf|xp,yp) / p(xf|xp))
// = sum p(xf,xp,yp) * log (  (p(xf,xp,yp)/p(xp,yp)) / ( p(xf,xp)/p(xp)) )
// = sum p(xf,xp,yp) * log ( p(xp)*p(xf,xp,yp) / ( p(xp,yp)*p(xf,xp) ) )
double tentropd (double* x,double* y,int iLen,int nbins,int xpast,int ypast,int nshuf,double* sig,double hval,int kern,double* nTE) {
  int *px,*py,jointd,i,j,k,**pjointxy,minidx,**pjointx,**ppastx,**ppastxy,*poddometer,sh,*ptmp;
  int cntjxy,cntjx,cntpx,cntpxy;
  double teout,te,teavg,testd,probjxy,probjx,probpx,probpxy;//transfer entropy,probabilities
  double hjxy,hjx,hpx,hpxy,sd,dsum,dtmp,N,ent,norm;//bandwidths,std-dev
  px=py=poddometer=0x0; pjointxy=pjointx=ppastx=ppastxy=0x0;
  dsum=0.0;
  *sig=-1e6;//init sig to neg
  *nTE = 0.0;
  sh=cntjxy=cntjx=cntpx=cntpx=0;   teavg=testd=te=teout=0.0;

  px = nbins>0 ? getnormd(x,iLen,nbins) : doublep2intp(x,iLen); //discretize x to nbins, or just copy to ints
  py = nbins>0 ? getnormd(y,iLen,nbins) : doublep2intp(y,iLen); //discretize y to nbins, or just copy to ints

  jointd = xpast + ypast + 1;//joint distribution with all x,y values

  if(verbose>1) printf("iLen%d, jointd%d, xpast%d, ypast%d\n", iLen,jointd,xpast,ypast);

  //setup distributions - not probability distributions, distributions of values
  pjointxy=getint2D(iLen,jointd+(kern==0?1:0)); if(!pjointxy) {printf("tentropd: out of mem!\n"); hxe();}
  pjointx=getint2D(iLen,xpast+1+(kern==0?1:0)); if(!pjointx)  {printf("tentropd: out of mem!\n"); hxe();}

  ptmp=kern?0x0:(int*)malloc(sizeof(int)*jointd);

  if(verbose>1) printf("jointd=%d, xpast+1=%d, iLen=%d, nbins=%d\n",jointd,xpast+1,iLen,nbins);

  if(xpast>0) ppastx=getint2D(iLen,xpast+(kern==0?1:0)); else {ppastx=0; printf("tentropd WARN: ppastx=0!\n");}
  if(xpast>0 || ypast>0) {
    ppastxy=getint2D(iLen,xpast+ypast+(kern==0?1:0));
  } else {ppastxy=0;  printf("tentropd WARN: ppastxy=0!\n");}

  minidx = xpast > ypast ? xpast : ypast;

  do {

    if(sh > 0) ishuffle(py,iLen); //shuffle y

    if(kern) { //if using kernel probabilities
      for(i=minidx;i<iLen-1;i++) { //initialize distributions
        pjointxy[i][0] = pjointx[i][0] = px[i+1]; //future x value
        k = 1;
        for(j=0;j<xpast;j++,k++) {
          pjointxy[i][k] = pjointx[i][k] = ppastx[i][k-1] = ppastxy[i][k-1] = px[i-j]; //past x values
        }
        for(j=0;j<ypast;j++,k++) {
          pjointxy[i][k] = ppastxy[i][k-1] = py[i-j]; //past y values
        }
      }
      if(sh==0){ //only calc bandwidths first time
        if(hval<=0.0){   //calc bandwidths
          sd = (getstdevi(px,iLen) + getstdevi(py,iLen)) / 2.0;
          if(verbose>1) printf("sd=%g\n",sd);
          hjxy = getbandwidthd(jointd,iLen-1-minidx+1,sd);
          hjx = getbandwidthd(1+xpast,iLen-1-minidx+1,sd);
          hpx = getbandwidthd(xpast,iLen-1-minidx+1,sd);
          hpxy = getbandwidthd(xpast+ypast,iLen-1-minidx+1,sd);
        } else hjxy=hjx=hpx=hpxy=hval;
        if(verbose>1) printf("hjxy=%g, hjx=%g, hpx=%g, hpxy=%g\n",hjxy,hjx,hpx,hpxy);
      }    
      //iterate over all values to get transfer entropy
      te=dsum=0.0;//init to 0
      for(j=minidx;j<iLen-1;j++) {
        poddometer = pjointxy[j];
        probjxy = kprobstepi(pjointxy,jointd,minidx,iLen-1,hjxy,poddometer);
        dsum += probjxy;
        probjx = kprobstepi(pjointx,xpast+1,minidx,iLen-1,hjx,poddometer);
        probpx = xpast>0?kprobstepi(ppastx,xpast,minidx,iLen-1,hpx,&poddometer[1]):1.0;
        probpxy = kprobstepi(ppastxy,xpast+ypast,minidx,iLen-1,hpxy,&poddometer[1]);    
        if(verbose>2) printf("probjxy=%g,probjx=%g,probpx=%g,probpxy=%g\n",probjxy,probjx,probpx,probpxy);
        if(probpx>1e-9 && probjxy>1e-9 && probjx>1e-9 && probpxy>1e-9) {
          dtmp = (probpx*probjxy)/(probjx*probpxy);
          if(usetable && dtmp>=MINLOG2 && dtmp<=MAXLOG2) 
           te += probjxy * _n_LOG2(dtmp);
          else
           te += probjxy * log2d(dtmp);
        }
      }
      N = ( iLen - 1 ) - minidx + 1;
      if(N > 0) dsum = dsum / (double) N;
      if(verbose>1) printf("dsum=%g\n",dsum);
    } else { //use regular counts to get probabilities

      N = ( iLen - 1 ) - minidx + 1;

      //init counts to 0. only init distribs with ONLY x first time, since ONLY y is shuffled.
      if(sh==0) cntjxy=cntjx=cntpx=cntpxy=0; else cntjxy=cntpxy=0;

      for(i=minidx;i<iLen-1;i++) { //initialize pjointxy
        ptmp[0]=px[i+1]; //future x value
        k=1;
        for(j=0;j<xpast;j++,k++) ptmp[k] = px[i-j]; //past x values
        for(j=0;j<ypast;j++,k++) ptmp[k] = py[i-j]; //past y values
        for(j=0;j<cntjxy;j++) { //search for ptmp in list
          for(k=0;k<jointd;k++) if(ptmp[k]!=pjointxy[j][k])break;
          if(k==jointd)break;//found existing one
        }
        if(j==cntjxy) { //found new one
          for(k=0;k<jointd;k++) pjointxy[cntjxy][k]=ptmp[k];
          pjointxy[cntjxy][k] = 1; //init count to 1
          cntjxy++; //inc # of unique vectors
        } else {
          pjointxy[j][jointd] += 1; //inc count
        }
      }
      if(verbose>1) {printf("cntjxy=%d\n",cntjxy);
        for(i=0;i<cntjxy;i++) {
          printf("pjointxy%d: [");
          for(j=0;j<jointd;j++) printf("%d ",pjointxy[i][j]);
          printf("] , cnt=%d, p=%g\n",pjointxy[i][jointd],pjointxy[i][jointd]/(double)N);
        }
      }
      if(sh==0) { //only init distribs with ONLY x first time, since ONLY y is shuffled.
        for(i=minidx;i<iLen-1;i++) { //initialize pjointx
          ptmp[0]=px[i+1];
          k=1;
          for(j=0;j<xpast;j++,k++) ptmp[k] = px[i-j]; //past x values
          for(j=0;j<cntjx;j++) { //search for ptmp in list
            for(k=0;k<xpast+1;k++) if(ptmp[k]!=pjointx[j][k])break;
            if(k==xpast+1)break;//found existing one
          }
          if(j==cntjx) { //found new one
            for(k=0;k<xpast+1;k++) pjointx[cntjx][k]=ptmp[k];
            pjointx[cntjx][k] = 1; //init count to 1
            cntjx++; //inc # of unique vectors
          } else {
            pjointx[j][xpast+1] += 1; //inc count
          }        
        }
        for(i=minidx;i<iLen-1;i++) { //initialize ppastx
          k=1;
          for(j=0;j<xpast;j++,k++) ptmp[k-1] = px[i-j]; //past x values  
          for(j=0;j<cntpx;j++) { //search for ptmp in list
            for(k=0;k<xpast;k++) if(ptmp[k]!=ppastx[j][k])break;
            if(k==xpast)break;//found existing one
          }
          if(j==cntpx) { //found new one
            for(k=0;k<xpast;k++) ppastx[cntpx][k]=ptmp[k];
            ppastx[cntpx][k] = 1; //init count to 1
            cntpx++; //inc # of unique vectors
          } else {
            ppastx[j][xpast] += 1; //inc count
          }                
        }
      }
      for(i=minidx;i<iLen-1;i++) { //initialize ppastxy
        k = 1;
        for(j=0;j<xpast;j++,k++) ptmp[k-1] = px[i-j]; //past x values
        for(j=0;j<ypast;j++,k++) ptmp[k-1] = py[i-j]; //past y values
        for(j=0;j<cntpxy;j++) { //search for ptmp in list
          for(k=0;k<xpast+ypast;k++) if(ptmp[k]!=ppastxy[j][k])break;
          if(k==xpast+ypast)break;//found existing one
        }
        if(j==cntpxy) { //found new one
          for(k=0;k<xpast+ypast;k++) ppastxy[cntpxy][k]=ptmp[k];
          ppastxy[cntpxy][k] = 1; //init count to 1
          cntpxy++; //inc # of unique vectors
        } else {
          ppastxy[j][xpast+ypast] += 1; //inc count
        }                        
      }
      te=dsum=0.0;//init to 0      
      if(sh==0) { //calculate H(XF|XP) once, H(XF|XP)=-sum(p(XF,XP)*log(p(XF,XP)/p(XP)))
        norm = 0.0;
        for(i=0;i<cntjx;i++) {
          probjx = pjointx[i][xpast+1]/(double)N;
          for(j=0;j<cntpx;j++) { //get probability of pastx by finding it in lookup table
            for(k=0;k<xpast;k++) { if(ppastx[j][k]!=pjointx[i][k+1]) break; }
            if(k==xpast) {
              probpx = ppastx[j][xpast]/(double)N;
              break;
            }
          }
          if(probjx > 1e-9 && probpx > 1e-9) {
            dtmp = probjx / probpx;
            if(usetable && dtmp>=MINLOG2 && dtmp<=MAXLOG2) 
              norm -= probjx * _n_LOG2(dtmp);
            else
              norm -= probjx * log2d(dtmp);            
          }
        }      
      }
      ent = 0.0;// H(XF|XP,YP) = -sum( p(XF,XP,YP) * log( p(XF,XP,YP)/p(XP,YP) ) )
      for(i=0;i<cntjxy;i++) { //calculate te. go through all pjointxy values

        probjxy = pjointxy[i][jointd]/(double)N; //direct lookup of pjointxy
        dsum += probjxy;
        
        for(j=0;j<cntpxy;j++) { //get probability of pastxy by finding it in lookup table
          for(k=0;k<xpast+ypast;k++) { if(ppastxy[j][k]!=pjointxy[i][k+1]) break; }
          if(k==xpast+ypast) {
            probpxy = ppastxy[j][xpast+ypast]/(double)N;
            break;
          }
        }
        if(verbose>1) printf("probjxy=%g,probjx=%g,probpx=%g,probpxy=%g\n",probjxy,probjx,probpx,probpxy);
        if(probjxy>1e-9 && probpxy>1e-9) {
          dtmp = probjxy / probpxy;
          if(usetable && dtmp>=MINLOG2 && dtmp<=MAXLOG2) 
            ent -= probjxy * _n_LOG2(dtmp);
          else
            ent -= probjxy * log2d(dtmp);
        }
      }
      te = norm - ent;
      if(te<0) te=0.0; //make sure no neg values. possible due to numerical issues with probabilities.
      if(verbose>1) printf("dsum=%g\n",dsum);
    }
    if(sh==0) teout=te; else {
      teavg += te;
      testd += te*te;
    }
  } while(sh++ < nshuf);

  if(nshuf>0) {
    teavg /= (double) nshuf;
    testd = testd/(double)nshuf - teavg*teavg;
    if(testd > 1e-9) *sig = (teout - teavg) / testd;
    if(verbose>0) printf("teout=%g,teavg=%g,testd=%g,sig=%g\n",teout,teavg,testd,*sig);
    *nTE = norm > 1e-9 ? (teout - teavg) / norm : (teout - teavg);
  } else *nTE=norm>1e-9?teout/norm:teout;
  if(*nTE < 0) *nTE = 0.; // clip nTE @ 0
  freeint2D(&pjointxy,iLen); freeint2D(&pjointx,iLen);   //free mem
  if(ppastx) freeint2D(&ppastx,iLen); if(ppastxy) freeint2D(&ppastxy,iLen);  
  free(px); free(py); if(ptmp) free(ptmp);
  return teout;
}

//* vx.tentrop(vy,nbins[,xpast,ypast,nshuf,vout,hval,kern]) calculates (normalized)transfer entropy of vx on vy
//nbins   : # of bins to discretize x,y to. if nbins < 1, dont discretize distrib,(i.e. for spikecounts)
//x,ypast : # of past values of x,y to use.
//nshuf   : # of shuffles to perform to calculate significance
//vout    : stores output , vout.x(0) = un-normalized transfer entropy, vout.x(1)=significance
//hval    : bandwidth - larger values means distributions smoothed more
//kern    : toggle whether to use kernel density estimation (vs plain counts)
static double tentrop (void* vv) {
  double *x,*y,hval,sig,*pout,te,nTE;
  int szx,szy,szo,nbins,xpast,ypast,nshuf,kern;
  szx = vector_instance_px(vv,&x);
  if((szy=vector_arg_px(1,&y))!=szx) {
    printf("tentrop ERRA: x,y must have same size (%d,%d)\n",szy,szy);
    return -1.0;
  } //nbins == # of discrete symbols to use for the time series
  //if < 1, dont discretize distribution (i.e. for spikecounts)
  nbins = *getarg(2);
  xpast = ifarg(3)?(int)*getarg(3):1;//# of past values of x to use
  ypast = ifarg(4)?(int)*getarg(4):2;//# of past values of y to use
  nshuf = ifarg(5)?(int)*getarg(5):0;//# of times to shuffle
  if(ifarg(6)) szo=vector_arg_px(6,&pout); else szo=0; //output vector
  hval = ifarg(7)?*getarg(7):-1.0;//single bandwidth specified by user,-1 means tentropd selects  
  kern = ifarg(8)?(int)*getarg(8):0;//use kernels or just counts?
  te = tentropd(y,x,szx,nbins,ypast,xpast,nshuf,&sig,hval,kern,&nTE);
  if(szo>0) pout[0]=te; if(szo>1) pout[1]=sig;
  return nTE;
}

//* myprvec - print the contents of a double* , prefaced by optional msg
void myprvec (double* x, int sz,char* msg) {
  int i;
  if(msg) printf("%s",msg);
  for(i=0;i<sz;i++) printf("%g ",x[i]);
  printf("\n");
}

//* vx.ntedir(vy,nbins[,xpast,ypast,nshuf,vout,hval]) calculates preferred direction of vx on vy, pxy, using tentropd
// preferred direction of vy on vx is -1 * pxy.
// preferred direction is : (ntexy-nteyx)/(ntexy+nteyx), and is bound to (-1,1) since nte is (0,1). nte has
// its lower bound set to 0 in tentropd, so its ok.
//nbins   : # of bins to discretize x,y to. if nbins < 1, dont discretize distrib,(i.e. for spikecounts)
//x,ypast : # of past values of x,y to use.
//nshuf   : # of shuffles to perform to calculate significance
//vout    : stores output , vout.x(0,1,2,3,4,5,6)=texy,sigtexy,ntexy,teyx,sigteyx,nteyx,nteprefdir
//hval    : bandwidth - larger values means distributions smoothed more
//kern    : toggle whether to use kernel density estimation (vs plain counts)
static double ntedir (void* vv) {
  double *x,*y,hval,sigxy,sigyx,*pout,texy,teyx,texyout,teyxout,prefdir;
  double ntexy,nteyx,ntexyout,nteyxout;
  int szx,szy,szo,nbins,xpast,ypast,nshuf,i,kern;
  szx = vector_instance_px(vv,&x);
  if((szy=vector_arg_px(1,&y))!=szx) {
    printf("tecause ERRA: x,y must have same size (%d,%d)\n",szx,szy);
    return -1.0;
  } 
  //nbins == # of discrete symbols to use for the time series
  //if < 1, dont discretize distribution (i.e. for spikecounts)
  nbins = *getarg(2);
  xpast = ifarg(3)?(int)*getarg(3):1;//# of past values of x to use
  ypast = ifarg(4)?(int)*getarg(4):2;//# of past values of y to use
  nshuf = ifarg(5)?(int)*getarg(5):0;//# of times to shuffle
  if(ifarg(6)) szo=vector_arg_px(6,&pout); else szo=0; //output vector
  hval = ifarg(7)?*getarg(7):-1.0;//single bandwidth specified by user,-1 means tentropd selects  
  kern = ifarg(8)?(int)*getarg(8):0;//use kernels or just counts?

  texyout = tentropd(y,x,szx,nbins,ypast,xpast,nshuf,&sigxy,hval,kern,&ntexyout); //TE_X->Y
  teyxout = tentropd(x,y,szy,nbins,ypast,xpast,nshuf,&sigyx,hval,kern,&nteyxout); //TE_Y->X

  if(verbose) printf("texyout=%g,teyxout=%g,ntexyout=%g,nteyxout=%g\n",texyout,teyxout,ntexyout,nteyxout);

  prefdir = ntexyout + nteyxout > 1e-9 ? (ntexyout - nteyxout)/(ntexyout+nteyxout) : 0;

  if(szo>0) pout[0]=texyout; if(szo>1) pout[1]=sigxy; if(szo>2) pout[2]=ntexyout;
  if(szo>3) pout[3]=teyxout; if(szo>4) pout[4]=sigyx; if(szo>5) pout[5]=nteyxout;
  if(szo>6) pout[6]=prefdir;

  return prefdir;//preferred direction
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

//*** vfrom.ntel2(vto,list1,list2,nte vector[,te vector,nshuf])
static double ntel2 (void* vv) {
  double *pfrom,*pto,*pTE,*pNTE,ret,te;
  int i,j,sz,tsz,nshuf;
  ListVec *pLFrom,*pLTo;
  ret = 0.0; // return value
  sz = vector_instance_px(vv, &pfrom);
  pTE=0x0;
  if(sz!=vector_arg_px(1, &pto) ||  sz!=vector_arg_px(4,&pNTE) || (ifarg(5) && sz!=vector_arg_px(5,&pTE)) ) {
    printf("ntel2 ERRA: arg 1,4,5 must have size of %d\n",sz); hxe();}
  nshuf = ifarg(6) ? (int)*getarg(6):30;
  pLFrom = AllocListVec(*hoc_objgetarg(2)); // list of from vectors (spike counts per time)
  pLTo = AllocListVec(*hoc_objgetarg(3)); // list of to vectors (spike counts per time)
  if(!pLFrom->isz || !pLTo->isz) { printf("ntel2 ERRB: empty list vectors\n"); goto NTEL2DOFREE; }
  tsz = pLFrom->plen[0]; // length of spike counts per time, assumes they're all the same length
  if(pTE) {
    for(i=0;i<sz;i++,pfrom++,pto++,pNTE++,pTE++) {
      *pNTE=tetrospks2(pLFrom->pv[(int)*pfrom],pLTo->pv[(int)*pto],&te,tsz,1,nshuf);
      *pTE=te;
    }
  } else {
    for(i=0,j=0;i<sz;i++,pfrom++,pto++,pNTE++) {
      *pNTE=tetrospks2(pLFrom->pv[(int)*pfrom],pLTo->pv[(int)*pto],0x0,tsz,0,nshuf);
    }
  }
  ret=1.0;
NTEL2DOFREE:
  FreeListVec(&pLFrom); FreeListVec(&pLTo);
  return ret;
}

//*** Vind0.nte(Vind1,LIST,OUTVEC or OUTLIST) // do normalization with H(X2F|X2P)
static double nte (void* vv) {
  int i, j, k, ii, jj, oi, nx, ny, omax, sz, ci, bg, flag, nshuf, szX, *x1i, *x2i, x1z, x2z;
  ListVec *pLi; Object *obi,*ob;  double *x, *y, *out, o1, o2, cnt, *vvo[3]; void *vvl;
  nx = vector_instance_px(vv, &x); // index i vector
  ny = vector_arg_px(1, &y);       // index j vectors
  pLi = AllocListVec(obi=*hoc_objgetarg(2)); // input vectors
  ob =   *hoc_objgetarg(3);
  if (ISVEC(ob)) {omax  = vector_arg_px(3, &out);} else omax=-1;
  if (ifarg(4)) nshuf=(int)*getarg(4); else nshuf=0;
  if (nshuf<=0) nshuf=0;
  if (nshuf>200) {printf("WARN: reducing # of shuffles from %d to 200\n",nshuf); nshuf=200;}
  if (omax==-1) { flag=1; // do all pairwise bidirectional
    i = ivoc_list_count(ob);
    if (i<3) {printf("nte() ERRA out list should be at least 3 (%d)\n",i); hxe();}
    for (k=0;k<3;k++) { 
      j=list_vector_px3(ob, k, &vvo[k], &vvl);
      if (k==0) omax=j; else if (omax!=j||j<10) {
        printf("nte() ERRC: too small %d %d\n",j,omax); hxe(); }
    }
  } else if (2*nx*ny==omax) { flag=4; // pairwise bidirectional with single vec output
  } else if (nx==ny && 2*nx==omax) { flag=2; // do bidirectional nx<->ny
  } else if (nx==ny && nx==omax) {   flag=3; // do unidirectional nx->ny   
  } else {printf("te_infot ERRA vector sizes are %d %d %d\n",nx,ny,omax);hxe();}
  ci=pLi->isz;
  sz=pLi->plen[0];  
  if (flag==1 || flag==4) { // all pairwise, 4 is alternative output
    x1i=(int*)calloc(nx,sizeof(int)); x2i=(int*)calloc(ny,sizeof(int)); x1z=x2z=0; 
    bg=(int)beg;
    if (binmin>0 && flag==1) {    // check ahead for ones to skip
      szX=((end>0.0 && end<=sz)?(int)end:sz) - beg;
      for (i=0;i<nx;i++)   { ii=(int)x[i];
        if (ii<0 || ii>=ci || pLi->plen[ii]!=sz) {
          printf("nte ERRC:%d imax:%d isz:%d sz0:%d\n",ii,ci,pLi->plen[ii],sz); hxe(); }
        for (j=0,cnt=0.;j<szX;j++) if (pLi->pv[ii][j+bg]>0) cnt++;
        if (cnt>(double)szX*binmin && (!binmax || cnt<(double)szX*binmax)) { 
          x1i[x1z]=ii; x1z++; }// use this one
      }
      for (i=0;i<ny;i++)   { ii=(int)y[i];
        if (ii<0 || ii>=ci || pLi->plen[ii]!=sz) {
          printf("nte ERRCa i:%d imax:%d isz:%d sz0:%d\n",ii,ci,pLi->plen[ii],sz); hxe(); }
        for (j=0,cnt=0;j<szX;j++) if (pLi->pv[ii][j+bg]>0) cnt++;
        if (cnt>szX*binmin && (!binmax || cnt<szX*binmax)) { x2i[x2z]=ii; x2z++; }
      }
    } else { // copy all of them in
      x1z=nx; x2z=ny;
      for (i=0;i<nx;i++) x1i[i]=(int)x[i]; 
      for (i=0;i<ny;i++) x2i[i]=(int)y[i]; 
    }
    if (flag==4) for (oi=0;oi<omax;oi++) out[oi]=-1;
    for (i=0,oi=0;i<x1z;i++)   { ii=x1i[i];
      for (j=0;j<x2z;j++) { jj=x2i[j]; // dbxi[0]=ii; dbxi[1]=jj;
        o1=tetrospks2(pLi->pv[ii],pLi->pv[jj],0x0,sz,0,nshuf);
        if (o1<=-10) { // don't bother doing
          if (verbose>3) printf("tentropspks IGNORING %d:%d %d:%d (%g)\n",i,ii,j,jj,o1);
          continue;
        }
        o2=tetrospks2(pLi->pv[jj],pLi->pv[ii],0x0,sz,0,nshuf);
        if (flag==1) {
          if (oi>=omax-1) { omax*=2; for (k=0;k<3;k++) vvo[k]=list_vector_resize(ob, k, omax); }
          vvo[0][oi]=ii;vvo[1][oi]=jj;vvo[2][oi]=o1;oi++;
          vvo[0][oi]=jj;vvo[1][oi]=ii;vvo[2][oi]=o2;oi++;
        } else { oi=i*ny+j;
          out[oi]=o1;      
          out[oi+nx*ny]=o2;
        }
      }
    }
    if (flag==1) for (k=0;k<3;k++) vvo[k]=list_vector_resize(ob, k, oi);
    return (double)oi;
  } else {
    for (oi=0;oi<omax;oi++) out[oi]=-1;
    for (i=0;i<nx;i++) {
      ii=(int)x[i]; jj=(int)y[i];
      if (ii==jj) { out[i]=0; // don't calculate self-self TE
        if (flag==2) out[i+nx]=0;
        continue;
      } 
      if (ii<0 || jj<0 || ii>=ci || jj>=ci || pLi->plen[ii]!=sz || pLi->plen[jj]!=sz) {
        printf("te_infot ERRC bad index or sz i:%d j:%d imax:%d isz:%d jsz:%d sz0:%d\n",\
               ii,jj,ci,pLi->plen[ii],pLi->plen[jj],sz); hxe(); }
      out[i]=tetrospks2(pLi->pv[ii],pLi->pv[jj],0x0,sz,0,nshuf);
      if (flag==2) out[i+nx]= tetrospks2(pLi->pv[jj],pLi->pv[ii],0x0,sz,0,nshuf);
    }
    return out[0];
  }
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
  if(verbose>3) printf("X1:%p , X2:%p, X3:%p, scr:%p\n",X1,X2,X3,iscr);
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
  if(verbose>3) printf("X1:%p , X2:%p, scr:%p\n",X1,X2,iscr);
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

//* other funcs
//** getbandwidth()
static double getbandwidth (void* vv) {
  double *x, sd;
  int n;
  n = vector_instance_px(vv,&x);
  sd = getstdevd(x,n);
  return getbandwidthd(1,n,sd);
}

//** v1.getdisc(v2,nbins) discretize v1 into v2 using nbins
// v2.x(i) = nbins * (v1.x(i)-v1.min)/(v1.max-v1.min) + 0.5, clamped to 0,nbins-1
static double getdisc (void* vv) {
  double *pin,*pout;
  int szin,szout,nbins,*ptmp,i;
  szin = vector_instance_px(vv,&pin);
  if((szout = vector_arg_px(1,&pout))<szin) {
    printf("getnorm ERRA: output size %d < input size %d\n",szout,szin);
    return 0.0;
  }
  nbins = (int)*getarg(2);
  if(nbins < 1) {
    printf("getnorm ERRB: nbins must be positive\n");
    return 0.0;
  }
  ptmp = getnormd(pin,szin,nbins);
  for(i=0;i<szin;i++) pout[i] = ptmp[i];
  free(ptmp);
  return 1.0;
}

//** vin.downsampavg(vout,winsz) - downsamples input vector taking average of chunks of size winsz
// returns results in vout , which must be allocated with size of ceil(sz/winsz)*sizeof(double)
static double downsampavg (void* vv) {
  double *pin,*pout,*ptmp,dsz;
  int szin,szout,winsz;
  szin=vector_instance_px(vv,&pin);
  winsz = (int)*getarg(2);
  if(winsz < 1) {
    printf("downsampavg ERRA: winsz must be positive\n");
    return 0.0;
  }
  dsz= (double)szin/(double)winsz;  dsz = ceil(dsz);
  if((szout=vector_arg_px(1,&pout))<dsz) {
    printf("downsampavg ERRB: output size %d < required size %d\n",szout,(int)dsz);
    return 0.0;
  }
  if(!downsampavgd(pin,pout,szin,szout,winsz)) {
    printf("downsampavg ERRC: output size too small\n");
    return 0.0;
  }
  vector_resize(vector_arg(1),(int)dsz);
  return 1.0;
}

//** chenc - vin.chgenc(vout) changes in vin are encoded as 0:decrease,1:same,2:increase in vout
static double chgenc (void* vv) {
  double *pin,*pout;
  int szin,szout;
  szin=vector_instance_px(vv,&pin);
  if((szout=vector_arg_px(1,&pout))!=szin) {
    printf("chgenc ERRA: output size %d < required size %d\n",szout,szin);
    return 0.0;
  }
  chgencd(pin,pout,szin);
  return 1.0;
}

//** v1.kprob1D(bandwidth,value) , return probability estimate of value using 1D kernel density
//estimation with gaussian kernel using bandwidth as kernel width
static double kprob1D (void* vv) {
  double *x,val,h;
  int n;
  n = vector_instance_px(vv,&x);  h = *getarg(1);  val = *getarg(2);
  return kprob1Dd(x,n,h,val);
}

//** ITcompare() Helper function for sort. Previously, this was a nested function under
// sort, which is not allowed under ANSI C.
static int ITcompare(const void* a, const void* b)
{ const int i1 = *(const int*)a;
  const int i2 = *(const int*)b;
  const double term1 = ITsortdata[i1];
  const double term2 = ITsortdata[i2];
  if (term1 < term2) return -1;
  if (term1 > term2) return +1;
  return 0;
}

//** ITcsort()
void ITcsort (int n, const double mdata[], int index[])
/* Sets up an index table given the data, such that mdata[index[]] is in
  increasing order. Sorting is done on the indices; the array mdata
  is unchanged.
     */
{ int i;
  ITsortdata = mdata;
  for (i = 0; i < n; i++) index[i] = i;
  qsort(index, n, sizeof(int), ITcompare);
}

//** ITgetrank()
static double* ITgetrank (int n, double mdata[])
// Calculates the ranks of the elements in the array mdata. Two elements with
// the same value get the same rank, equal to the average of the ranks had the
// elements different values. The ranks are returned as a newly allocated
// array that should be freed by the calling routine. If getrank fails due to
// a memory allocation error, it returns NULL.
{ int i;
  double* rank;
  int* index;
  rank = calloc(n,sizeof(double));
  if (!rank) return NULL;
  index = calloc(n,sizeof(int));
  if (!index)
  { free(rank);
    return NULL;
  }
  /* Call ITcsort to get an index table */
  ITcsort (n, mdata, index);
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


//* mutinfbd()
static double mutinfbd(double* x,double* y,int sz,int nbins) {
  double *xr,*yr,*px,*py,**pxy,ret,dinf;
  int i,j,idx,idy;
  ret=-1.0;
  xr=yr=px=py=NULL; pxy=NULL;
  if(verbose>0) printf("sz=%d, nbins=%d\n",sz,nbins);
  if(!(xr=ITgetrank(sz,x))) { printf("mutinfb ERRB: out of memory\n"); goto MUTEND; }
  if(!(yr=ITgetrank(sz,y))) { printf("mutinfb ERRB: out of memory\n"); goto MUTEND; }
  if(verbose>0) { printf("xr: "); for(i=0;i<sz;i++) printf("%g ",xr[i]); printf("\n");
                  printf("yr: "); for(i=0;i<sz;i++) printf("%g ",yr[i]); printf("\n");}
  if(!(px=(double*)calloc(nbins,sizeof(double)))){printf("mutinfb ERRB: out of memory\n"); goto MUTEND;}
  if(!(py=(double*)calloc(nbins,sizeof(double)))){printf("mutinfb ERRB: out of memory\n"); goto MUTEND;}
  if(!(pxy=getdouble2D(nbins,nbins))){printf("mutinfb ERRB: out of memory\n"); goto MUTEND;}
  for(i=0;i<sz;i++) { //initialize counts
    idy = (int) nbins * ( yr[i] / (sz-1) ); if(idy>=nbins) idy = nbins-1;
    idx = (int) nbins * ( xr[i] / (sz-1) ); if(idx>=nbins) idx = nbins-1;
    px[idx]++; py[idy]++; pxy[idy][idx]++;
  }
  if(verbose>0) { //print counts
    printf("px: "); for(i=0;i<nbins;i++) printf("%.2f ",px[i]); printf("\n");
    printf("py: "); for(i=0;i<nbins;i++) printf("%.2f ",py[i]); printf("\n");
    printf("pxy: \n");
    for(i=0;i<nbins;i++) { for(j=0;j<nbins;j++) printf("%.2f ",pxy[i][j]); printf("\n"); }
  }
  dinf=0.0;
  for(idy=0;idy<nbins;idy++) { //calc mutual info
    if(py[idy]==0.0) continue;
    for(idx=0;idx<nbins;idx++) {
      if(px[idx]==0.0 || pxy[idy][idx]==0.0) continue;
      dinf += pxy[idy][idx] * log2d( pxy[idy][idx] / ( px[idx] * py[idy] ) );
    }
  }
  if(verbose>0) printf("A: dinf = %g\n",dinf);
  dinf = dinf / (double) sz;
  if(verbose>0) printf("B: dinf = %g\n",dinf);
  dinf += log2d(sz);
  if(verbose>0) printf("C: dinf = %g\n",dinf);
  ret = dinf;
MUTEND:
  if(xr) free(xr); if(yr) free(yr);  if(px) free(px); if(py) free(py);
  if(pxy) freedouble2D(&pxy,nbins);
  return ret;
}

//** v1.mutinfb(v2,nbins) - get mutual information using nbins, return -1 on error
static double mutinfb (void* v) {
  double *x,*y;
  int sz,nbins,tmp;
  sz = vector_instance_px(v,&x);
  if((tmp=vector_arg_px(1,&y))!=sz) {
    printf("mutinfb ERRA: x,y must have same sizes : %d %d\n",sz,tmp);
    return -1.0;
  }
  nbins = ifarg(2) ? (int) *getarg(2) : 10;
  return mutinfbd(x,y,sz,nbins);
}

double entropspksd (double* x,int sz) {
  double *px,ret,dinf,size;
  int i,*X,maxv,minv,cnt,err;
  if(sz<1) {printf("entropspks ERR0: min size must be > 0!\n"); return -1.0;}
  size=(double)sz;
  ret=-1.0; err=0;
  px=NULL; 
  minv=1000000000; maxv=-1000000000;
  X=scrset(sz*2); // move into integer arrays
  cnt=0;
  for (i=0;i<sz;i++) { 
    X[i]=(int)x[i]; 
    if (X[i]>0) cnt++;  
    if (X[i]>maxv) maxv=X[i];  if (X[i]<minv) minv=X[i]; 
  }
  if (minv<0){printf("entropb ERRB: minimum value must be >= 0:%d\n",minv);hxe();}
  if(!(px=(double*)calloc(maxv+1,sizeof(double)))){
    printf("entropb ERRB: out of memory\n"); err=1; goto ENTEND;}
  for(i=0;i<sz;i++) px[X[i]] += 1.0; //initialize counts
  for(i=minv;i<=maxv;i++) px[i]/=size;
  if(verbose>1) {printf("px: "); for(i=minv;i<=maxv;i++) printf("%.2f ",px[i]); printf("\n");}
  dinf=0.0;
  if(usetable) {
    for(i=minv;i<=maxv;i++) if(px[i]>0.) {
      if(px[i]>=MINLOG2&&px[i]<=MAXLOG2) dinf -= px[i]*_n_LOG2(px[i]); else {
                                         dinf -= px[i]*  log2d(px[i]); }
    }
  } else for(i=minv;i<=maxv;i++) if(px[i]>0.) dinf -= px[i] * log2d(px[i]);
  ret = dinf;
ENTEND:
  if(px) free(px);
  if (err) hxe();
  return ret;
}

static double entropspks (void* v) {
  double *x;
  int sz;
  sz = vector_instance_px(v,&x);
  return entropspksd(x,sz);
}

static double mxentropd (double* m, int rows, int cols, int tsz) {
  int lsz,i,j,*pcnts,x,y,tdx,yy,xx,ntiles,*ptmp;   double dent,p,d;
  lsz=1; ntiles=0; dent=0.0;
  for(i=0;i<tsz*tsz;i++) lsz*=2;
  if(verbose>=1) printf("# of tile patterns: %d\n",lsz);
  ptmp=verbose>=1?(int*)calloc(sizeof(int),tsz*tsz):0x0;
  pcnts = (int*) calloc(sizeof(int),lsz);
  for(y=0;y<rows-tsz;y++) {
    for(x=0;x<cols-tsz;x++) {
      tdx=0; i=1; j=0;
      for(yy=y;yy<y+tsz;yy++) {
        for(xx=x;xx<x+tsz;xx++) {
          d = m[yy*cols+xx]; // value in matrix
          if(ptmp) ptmp[j]=(int)d; // for debugging
          if(d) tdx += i;
          i *= 2; j+=1;
        }
      }
      pcnts[tdx]++; ntiles+=1;
      if(ptmp) {
        for(j=0;j<tsz*tsz;j++) printf("%d",ptmp[j]);
        printf("\tidx:%d\n",tdx); 
      }
    }
  }
  for(i=0;i<lsz;i++) {
    if(verbose>=1) printf("pcnts[%d]=%d\n",i,pcnts[i]);
    if(pcnts[i]) {
      p = (double) pcnts[i] / (double) ntiles;
      dent -= p*log2d(p);
    }
  }
  free(pcnts); if(ptmp) free(ptmp);
  return dent;
}

// v.mxentrop(nrows,tilesize) - v is treated as a matrix with row-major order, it should only have 0s and 1s. the
// function will calculate the entropy of the tiles in the matrix. if tilesize is 2, then it will take 2x2
// tiles. each pattern will be a symbol. it will count # of occurrences of each symbol & get entropy
static double mxentrop (void* v) {
  double* m;
  int sz,rows,cols,tsz;
  sz = vector_instance_px(v,&m);
  rows = (int)*getarg(1);
  cols = sz/rows;
  tsz = (int)*getarg(2);
  return mxentropd(m,rows,cols,tsz);
}

ENDVERBATIM

:* test functions and install 
FUNCTION testoddometer () {
  VERBATIM
  int *po,i;
  po = (int*) calloc(4,sizeof(int));
  do {
    for(i=0;i<4;i++) printf("%d",po[i]);
    printf("\n");
  } while(oddometerinc(po,4,9));
  free(po);
  return 1.0;
  ENDVERBATIM
}

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
    install_vector_method("tentrop",tentrop);
    install_vector_method("ntedir",ntedir);
    install_vector_method("getbandwidth",getbandwidth);
    install_vector_method("getdisc",getdisc);
    install_vector_method("downsampavg",downsampavg);
    install_vector_method("chgenc",chgenc);
    install_vector_method("kprob1D",kprob1D);
    install_vector_method("mutinfb",mutinfb);
    install_vector_method("tentropspks",tentropspks);
    install_vector_method("nte",nte);
    install_vector_method("ntel2",ntel2);
    install_vector_method("entropspks",entropspks);
    install_vector_method("entropxfgxp",entropxfgxp);
    install_vector_method("lz76c",lz76c);
    install_vector_method("mxentrop",mxentrop);
    ENDVERBATIM
  }
}
