: $Id: samnutils.mod,v 1.42 2012/08/31 02:34:30 samn Exp $  


NEURON {
  SUFFIX sn
  GLOBAL INSTALLED,EUCLIDEAN,SQDIFF,CITYBLOCK
}

PARAMETER {
  INSTALLED=0
  EUCLIDEAN=0
  SQDIFF=1
  CITYBLOCK=2
}

VERBATIM
#include "misc.h"
double DMIN(double d1,double d2){
  return d1 < d2 ? d1 : d2;
}

int IMIN(int i1,int i2){
  return i1 < i2 ? i1 : i2;
}

static double multall(void* vv){
  double* pv, dval=0.0;
  int n = vector_instance_px(vv,&pv) , idx = 0;
  if(n<1){
    printf("multall ERRA: vector size < 1!\n");
    return 0.0;
  }
  dval=pv[0];
  for(idx=1;idx<n;idx++) dval*=pv[idx]; 
  return dval;
}


//this = output of 1.0s and 0.0s by OR'ing input
//arg1 = vec1 of 1.0s and 0.0s
//arg2 = vec2 of 1.0s and 0.0s
static double V_OR(void* vv){
  double* pV1,*pV2,*pV3;
  int n = vector_instance_px(vv,&pV1);

  if(vector_arg_px(1,&pV2)!=n || vector_arg_px(2,&pV3)!=n){
    printf("V_OR ERRA: vecs must have same size %d!",n);
    return 0.0;
  }

  int i;
  for(i=0;i<n;i++){
    pV1[i] = (pV2[i] || pV3[i]) ? 1.0 : 0.0;
  }

  return 1.0;
}

// moving average smoothing
//  vec.smooth(vecout, smooth size)
static double smooth (void* vv) {
  int i, j, k, winsz, sz;
  double s, cnt;
  double* pV1,*pV2;
  if(!ifarg(1)) { printf("vec.smooth(vecout, smooth size)\n"); return 0.0; }
  sz = vector_instance_px(vv,&pV1);
  if(vector_arg_px(1,&pV2)!=sz) {
    printf("smooth ERRA: vecs must have same size %d!",sz);
    return 0.0;
  }
  if( (winsz = (int) *getarg(2)) < 1) {
    printf("smooth ERRB: winsz must be >= 1: %d\n",winsz);
    return 0.0;
  }
  for(i=0;i<winsz;i++) pV2[i]=pV1[i];
  cnt = winsz;
  i = 0;
  j = winsz - 1;
  s = 0.0;
  for(k=i;k<=j;k++) s += pV1[k];
  while(j < sz) {
    pV2[j] = s / cnt;
    s -= pV1[i];
    i++;
    j++;
    s += pV1[j];
  }
  return 1.0;
}

static double poscount(void* vv){
  double* pV;
  int iSz = vector_instance_px(vv,&pV) , i = 0, iCount = 0;
  for(i=0;i<iSz;i++) if(pV[i]>0.0) iCount++;
  return (double)iCount;
}

//this = output spike times
//arg1 = input voltage
//arg2 = voltage threshold for spike
//arg3 = min interspike time - uses dt for calculating time
//arg4 = dt - optional
static double GetSpikeTimes(void* vv) {
  double* pVolt , *pSpikeTimes;
  int n = vector_instance_px(vv, &pSpikeTimes);

  int tmp = vector_arg_px(1,&pVolt);

  if(tmp!=n){
    printf("GetSpikeTimes ERRA: output times vec has diff size %d %d\n",n,tmp);
    return 0.0;
  }  

  double dThresh = *getarg(2);
  double dMinTime = *getarg(3);
  double dDipThresh = 1.5 * dThresh;
  double loc_dt = ifarg(4)?*getarg(4):dt;

  if(0) printf("dt = %f\n",dt);

  int i , iSpikes = 0;

  for( i = 0; i < n; i++){
    double dVal = pVolt[i];

    if(dVal >= dThresh) { //is v > threshold?
      if(iSpikes > 0) { //make sure at least $4 time has passed
        if(loc_dt*i - pSpikeTimes[iSpikes-1] < dMinTime) {
          continue;
        }
      }

      while( i + 1 < n ) { //get peak of spike
        if( pVolt[i] > pVolt[i+1] ) {
          break;
        }
        i++;
      }
      pSpikeTimes[iSpikes++] = loc_dt * i;//store spike location

      while( i < n ) { //must dip down sufficiently
        if(pVolt[i] <= dDipThresh) {
          break;
        }
        i++;
      }
    }
  }

  vector_resize(vv, iSpikes); // set to # of spikes

  return (double) iSpikes;
}

static double countdbl(double* p,int iStartIDX,int iEndIDX,double dval) {
  int idx = iStartIDX, iCount = 0;
  for(;idx<=iEndIDX;idx++) if(p[idx]==dval) iCount++;
  return iCount;
}
ENDVERBATIM


FUNCTION MeanCutDist(){
  VERBATIM
  double* p1, *p2, *p3;

  int n = vector_arg_px(1,&p1);
  if(n != vector_arg_px(2,&p2) || n != vector_arg_px(3,&p3)){
    printf("MeanCutDist ERRA: vecs must be same size!\n");
    return -1.0;
  }

  int i , iCount = 0;

  double dSum = 0.0 , dVal = 0.0;

  for(i=0;i<n;i++){
    if(p3[i]) continue;
    dVal = p1[i] - p2[i];
    dVal *= dVal;
    dSum += dVal;
    iCount++;
  }

  if(iCount > 0){
    dSum /= (double) iCount;
    return dSum;
  }

  printf("MeanCutDist WARNINGA: no sums taken\n ");

  return -1.0;

  ENDVERBATIM
}

FUNCTION LDist(){
  VERBATIM

  Object* pList1 = *hoc_objgetarg(1);
  Object* pList2 = *hoc_objgetarg(2);

  if(!IsList(pList1) || !IsList(pList2)){
    printf("LDist ERRA: Arg 1 & 2 must be Lists!\n");
    return -1.0;
  }

  int iListSz1 = ivoc_list_count(pList1),
      iListSz2 = ivoc_list_count(pList2);

  if(iListSz1 != iListSz2 || iListSz1 < 1){
    printf("LDist ERRB: Lists must have same > 0 size %d %d\n",iListSz1,iListSz2);
    return -1.0;
  }

  double** ppVecs1, **ppVecs2;

  ppVecs1 = (double**) malloc(sizeof(double*)*iListSz1);
  ppVecs2 = (double**) malloc(sizeof(double*)*iListSz2); 

  if(!ppVecs1 || !ppVecs2){
    printf("LDist ERRRC: out of memory!\n");
    if(ppVecs1) free(ppVecs1);
    if(ppVecs2) free(ppVecs2);
    return -1.0;
  }

  int iVecSz1 = list_vector_px(pList1,0,&ppVecs1[0]);
  int iVecSz2 = list_vector_px(pList2,0,&ppVecs2[0]);

  if(iVecSz1 != iVecSz2){
    free(ppVecs1); free(ppVecs2);
    printf("LDist ERRD: vectors must have same size %d %d!\n",iVecSz1,iVecSz2);
    return -1.0;
  }

  int i;

  for(i=1;i<iListSz1;i++){
    int iTmp1 = list_vector_px(pList1,i,&ppVecs1[i]);
    int iTmp2 = list_vector_px(pList2,i,&ppVecs2[i]);
    if(iTmp1 != iVecSz1 || iTmp2 != iVecSz1){
      free(ppVecs1); free(ppVecs2);
      printf("LDist ERRD: vectors must have same size %d %d %d \n",iVecSz1,iTmp1,iTmp2);
      return -1.0;
    }
  }

  int j; double dDist = 0.0; double dVal = 0.0; double dSum = 0.0;
  int iType = 0;

  if(ifarg(3)) iType = *getarg(3);
  
  if(iType == EUCLIDEAN){ //euclidean
    for(i=0;i<iVecSz1;i++){ 
      dSum = 0.0;
      for(j=0;j<iListSz1;j++){
        dVal = ppVecs1[j][i]-ppVecs2[j][i];
        dVal *= dVal;
        dSum += dVal;
      }
      dDist += sqrt(dSum);
    }
  } else if(iType == SQDIFF){ //squared diff
    for(i=0;i<iVecSz1;i++){
      dSum = 0.0;
      for(j=0;j<iListSz1;j++){
        dVal = ppVecs1[j][i]-ppVecs2[j][i];
        dVal *= dVal;
        dSum += dVal;
      }
      dDist += dSum;
    }   
  } else if(iType == CITYBLOCK){ //city block (abs diff)
    for(i=0;i<iVecSz1;i++){
      dSum = 0.0;
      for(j=0;j<iListSz1;j++){
        dVal = ppVecs1[j][i]-ppVecs2[j][i];
        dSum += dVal >= 0.0 ? dVal : -dVal;
      }
      dDist += dSum;
    }
  } else {
    printf("LDist ERRE: invalid distance type %d!\n",iType);
    return -1.0;
  }

  free(ppVecs1);
  free(ppVecs2);

  return dDist;

  ENDVERBATIM
}

: G = SpikeTrainCoinc(targ_vec,model_vec,time_bin_size,stim_dur)
: spike train coincidence measure from 
: http://citeseer.ist.psu.edu/cache/papers/cs/15812/http:zSzzSzdiwww.epfl.chzSzlamizSzteamzSzgerstnerzSzPUBLICATIONSzSzKistler97.pdf/kistler96reduction.pdf
:
FUNCTION SpikeTrainCoinc(){
  VERBATIM

  double* pVec1, *pVec2;
  int iSz1 = vector_arg_px(1,&pVec1);
  int iSz2 = vector_arg_px(2,&pVec2);

  double dErr = -666.0;

  if(!pVec1 || !pVec2){
    printf("SpikeTrainCoinc ERRA: Can't get vec args 1 & 2!\n");
    return dErr;
  }

  if(iSz1 == 0 && iSz2 == 0){
    printf("SpikeTrainCoinc WARNA: both spike trains size of 0\n");
    return 0.0;
  }

  double dBinSize = *getarg(3);
  if(dBinSize <= 0.0){
    printf("SpikeTrainCoinc ERRB: bin size must be > 0.0!\n");
    return dErr;
  }

  double dStimDur = *getarg(4);
  if(dStimDur <= 0.0){
    printf("SpikeTrainCoinc ERRC: stim dur must be > 0.0!\n");
    return dErr;
  }

  double dNumBins = dStimDur / dBinSize; //K

  int i = 0 , j = 0;

  int iCoinc = 0; //

  double dThresh = 2.0;

  for(i=0;i<iSz1;i++){
    for(j=0;j<iSz2;j++){
      if( fabs(pVec1[i]-pVec2[i]) <= dThresh){
        iCoinc++;
        break;
      }
    }
  }

  double dN = 1.0 - ( (double) iSz1) / dNumBins;
         dN = 1.0 / dN;

  double dRandCoinc = (iSz1 * iSz2) / dNumBins; // avg coinc from poisson spike train <Ncoinc> 

  return dN * ((((double)iCoinc) - dRandCoinc) / ((iSz1+iSz2)/2.0));

  ENDVERBATIM
}

FUNCTION StupidCopy(){
  VERBATIM
  double* pDest,*pSrc;
  int iSz1 = vector_arg_px(1,&pDest);
  int iSz2 = vector_arg_px(2,&pSrc);
  int iSrcStart = *getarg(3);
  int iSrcEnd = *getarg(4);
  int i,j = 0;
  for(i=iSrcStart;i<iSrcEnd;i++,j++){
    pDest[j] = pSrc[i];
  }
  return 1.0;
  ENDVERBATIM
}

: cost = SpikeTrainEditDist(spiketrain1, spiketrain2 [, move_cost, delete/insert_cost])
FUNCTION SpikeTrainEditDist(){
  VERBATIM
  double* pVec1=0x0, *pVec2=0x0;
  int iSz1 = vector_arg_px(1,&pVec1);
  int iSz2 = vector_arg_px(2,&pVec2);
  if(!pVec1 || !pVec2){
    printf("SpikeTrainEditDist ERRA: Can't get vec args 1 & 2!\n");
    return -1.0;
  }
  double dMoveCost = ifarg(3) ? *getarg(3) : 0.1;
  if(dMoveCost < 0.0){
    printf("SpikeTrainEditDist ERRB: move cost must be >= 0!\n");
    return -1.0;
  }
  double dDelCost = ifarg(4) ? *getarg(4) : 1.0;
  if(dDelCost < 0.0){
    printf("SpikeTrainEditDist ERRC: delete cost must be >= 0!\n");
    return -1.0;
  }  

  if(dMoveCost == 0.0) return fabs(iSz1-iSz2) * dDelCost;
  else if(dMoveCost >= 9e24) return (double)(iSz1 + iSz2) * dDelCost;

  if(iSz1 < 1) return (double)(iSz2 * dDelCost);
  else if(iSz2 < 1) return (double)(iSz1 * dDelCost);

  double** dtab = (double**) malloc(sizeof(double*) * (iSz1+1));
  if(!dtab){
    printf("SpikeTrainEditDist ERRD: out of memory!\n");
    return -1.0;
  }
  int row,col;
  for(row = 0; row < iSz1 + 1; row += 1){
    dtab[row] = (double*) malloc(sizeof(double)*(iSz2+1));
    if(!dtab[row]){
      printf("SpikeTrainEditDist ERRE: out of memory!\n");
      int trow;
      for(trow=0;trow<row;trow++) free(dtab[trow]);
      free(dtab);
      return -1.0;
    }
    memset(dtab[row],0,sizeof(double)*(iSz2+1));
  }
  for(row = 0; row < iSz1 + 1; row += 1) dtab[row][0] = (double)(row * dDelCost);

  for(col = 0; col < iSz2 + 1; col += 1)  dtab[0][col] = (double)(col * dDelCost);

  for( row = 1; row < iSz1 + 1; row += 1){
    for(col = 1; col < iSz2 + 1; col += 1){
      dtab[row][col]= DMIN(  DMIN(dtab[row-1][col]+dDelCost,dtab[row][col-1]+dDelCost),     /* deletion/insertion cost */
                                              dtab[row-1][col-1]+dMoveCost*fabs(pVec1[row-1]-pVec2[col-1])); /* move cost */
    }
  }
  double dTotalCost = dtab[iSz1][iSz2];
  for(row=0;row<iSz1+1;row++) free(dtab[row]);
  free(dtab);
  return dTotalCost;
  ENDVERBATIM
}

PROCEDURE install() {
 if(INSTALLED==1){
:   printf("Already installed $Id: samnutils.mod,v 1.42 2012/08/31 02:34:30 samn Exp $ \n")
 } else {
 INSTALLED=1
 VERBATIM
 install_vector_method("GetSpikeTimes" ,GetSpikeTimes);
 install_vector_method("V_OR",V_OR);
 install_vector_method("poscount" ,poscount);
 install_vector_method("multall" ,multall);
 install_vector_method("smooth",smooth);
 ENDVERBATIM
 : printf("Installed $Id: samnutils.mod,v 1.42 2012/08/31 02:34:30 samn Exp $ \n")
 }
}
