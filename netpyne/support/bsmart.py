"""
This file contains all the function definitions necessary for running spectral
Granger causality. It is based on Mingzhou Ding's Matlab code package BSMART,
available from www.brain-smart.org.

Typical usage is as follows:
from bsmart import pwcausalr
F,pp,cohe,Fx2y,Fy2x,Fxy=pwcausalr(x,ntrls,npts,p,fs,freq);

Outputs:
	F is the frequency vector for the remaining quantities
	pp is the spectral power
	cohe is the coherence
	Fx2y is the causality of channel X to channel Y
	Fy2x is the causality of channel Y to channel X
	Fxy is the "instantaneous" causality (cohe-Fx2y-Fy2x I think)
Inputs:
	x is the data for at least two channels, e.g. a 2x8000 array consisting of two LFP time series
	ntrls is the number of trials (whatever that means -- just leave it at 1)
	npts is the number of points in the data (in this example, 8000)
	p is the order of the polynomial fit (e.g. 10 for a smooth fit, 20 for a less smooth fit)
	fs is the sampling rate (e.g. 200 Hz)
	freq is the maximum frequency to calculate (e.g. fs/2=100, which will return 0:100 Hz)

The other two functions (armorf and spectrum_AR) can also be called directly, but
more typically they are used by pwcausalr in intermediate calculations. Note that the 
sampling rate of the returned quantities is calculated as fs/2.

To calculate the power spectrum powspec of a single time series x over the frequency range 0:freq, 
use the following (NB: now accessible via "from spectrum import ar")
from bsmart import armorf, spectrum_AR
[A,Z,tmp]=armorf(x,ntrls,npts,p) # Calculate autoregressive fit
for i in range(freq+1): # Loop over frequencies
    [S,H]=spectrum_AR(A,Z,p,i,fs) # Calculate spectrum
    powspec[i]=abs(S**2) # Calculate and store power

In either case (pwcausalr or spectrum_AR), the smoothness of the spectra is determined by the
polynomial order p. Larger values of p give less-smooth spectra.

Version: 2011feb11 by Cliff Kerr (cliffk@neurosim.downstate.edu)
"""

# ARMORF -- AR parameter estimation via LWR method modified by Morf. 
#
#   X is a matrix whose every row is one variable's time series 
#   ntrls is the number of realizations, npts is the length of every realization 
#   If the time series are stationary long, just let ntrls=1, npts=length(x) 
# 
#   A = ARMORF(X,NR,NL,ORDER) returns the polynomial coefficients A corresponding to 
#   the AR model estimate of matrix X using Morf's method. 
#   ORDER is the order of the AR model. 
# 
#   [A,E] = ARMORF(...) returns the final prediction error E (the variance 
#   estimate of the white noise input to the AR model). 
# 
#   [A,E,K] = ARMORF(...) returns the vector K of reflection coefficients (parcor coefficients). 
# 
#   Ref: M. Morf, etal, Recursive Multichannel Maximum Entropy Spectral Estimation, 
#              IEEE trans. GeoSci. Elec., 1978, Vol.GE-16, No.2, pp85-94. 
#        S. Haykin, Nonlinear Methods of Spectral Analysis, 2nd Ed. 
#              Springer-Verlag, 1983, Chapter 2 

def timefreq(x,fs=200):
    """
    TIMEFREQ
    
    This function takes the time series and the sampling rate and calculates the
    total number of points, the maximum frequency, the minimum (or change in)
    frequency, and the vector of frequency points F.
    
    Version: 2011may04
    """
    from numpy import size, shape, arange, append
    
    maxfreq=float(fs)/2.0 # Maximum frequency
    minfreq=float(fs)/float(size(x,0)) # Minimum and delta frequency -- simply the inverse of the length of the recording in seconds
    F=arange(minfreq,maxfreq+minfreq,minfreq) # Create frequencies evenly spaced from 0:minfreq:maxfreq
    F=append(0,F) # Add zero-frequency component
    
    return F


def ckchol(M):
    """
    CKCHOL
    
    This function computes the Cholesky decomposition of the matrix if it's
    positive-definite; else it returns the identity matrix. It was written
    to handle the "matrix must be positive definite" error in linalg.cholesky.
    
    Version: 2011may03
    """
    from numpy import linalg, matrix, eye, size

    try: # First, try the Cholesky decomposition
        output=linalg.cholesky(M)
    except: # If not, just return garbage
        print 'WARNING: Cholesky failed, so returning (invalid) identity matrix!'    
        output=matrix(eye(size(M,0)))
    
    return output
    


def armorf(x,ntrls,npts,p):
    from scipy import shape, array, matrix, zeros, disp, concatenate, eye, dstack
    from numpy import linalg # for inverse and Cholesky factorization;
    import numpy as np
    inv=linalg.inv; # Make name consistent with Matlab
    
    # Initialization 
    x=matrix(x)
    [L,N]=shape(x);      # L is the number of channels, N is the npts*ntrls 
    R0=R0f=R0b=pf=pb=pfb=ap=bp=En=matrix(zeros((L,L,1)));    # covariance matrix at 0, 
        
    # calculate the covariance matrix? 
    for i in range(ntrls):
       En=En+x[:,i*npts:(i+1)*npts]*x[:,i*npts:(i+1)*npts].H; 
       ap=ap+x[:,i*npts+1:(i+1)*npts]*x[:,i*npts+1:(i+1)*npts].H;         
       bp=bp+x[:,i*npts:(i+1)*npts-1]*x[:,i*npts:(i+1)*npts-1].H; 
        
    ap = inv((ckchol(ap/ntrls*(npts-1)).T).H); 
    bp = inv((ckchol(bp/ntrls*(npts-1)).T).H); 
        
    for i in range(ntrls): 
       efp = ap*x[:,i*npts+1:(i+1)*npts]; 
       ebp = bp*x[:,i*npts:(i+1)*npts-1]; 
       pf = pf + efp*efp.H; 
       pb = pb + ebp*ebp.H; 
       pfb = pfb + efp*ebp.H; 
  
    En = (ckchol(En/N).T).H;       # Covariance of the noise 
    
    # Initial output variables
    tmp=[]
    for i in range(L): tmp.append([]) # In Matlab, coeff=[], and anything can be appended to that.
    coeff = matrix(tmp);#  Coefficient matrices of the AR model 
    kr = matrix(tmp);  # reflection coefficients 
    aparr=array(ap) # Convert AP matrix to an array, so it can be dstacked
    bparr=array(bp)
    
    for m in range(p): 
      # Calculate the next order reflection (parcor) coefficient 
      ck = inv((ckchol(pf).T).H)*pfb*inv(ckchol(pb).T);  
      kr=concatenate((kr,ck),1); 
      # Update the forward and backward prediction errors 
      ef = eye(L)- ck*ck.H; 
      eb = eye(L)- ck.H*ck; 
        
      # Update the prediction error 
      En = En*(ckchol(ef).T).H;
      E = (ef+eb)/2;

      # Update the coefficients of the forward and backward prediction errors 
      Z=zeros((L,L)) # Make it easier to define this
      aparr=dstack((aparr,Z))
      bparr=dstack((bparr,Z))
      pf = pb = pfb = Z
      # Do some variable juggling to handle Python's array/matrix limitations
      a=b=zeros((L,L,0))

      for i in range(m+2):  
          tmpap1=matrix(aparr[:,:,i]) # Need to convert back to matrix to perform operations
          tmpbp1=matrix(bparr[:,:,i])
          tmpap2=matrix(aparr[:,:,m+1-i])
          tmpbp2=matrix(bparr[:,:,m+1-i])
          tmpa = inv((ckchol(ef).T).H)*(tmpap1-ck*tmpbp2); 
          tmpb = inv((ckchol(eb).T).H)*(tmpbp1-ck.H*tmpap2); 
          a=dstack((a,array(tmpa)))
          b=dstack((b,array(tmpb)))

      for k in range(ntrls):
          efp = zeros((L,npts-m-2)); 
          ebp = zeros((L,npts-m-2)); 
          for i in range(m+2): 
              k1=m+2-i+k*npts; 
              k2=npts-i+k*npts; 
              efp = efp+matrix(a[:,:,i])*matrix(x[:,k1:k2]); 
              ebp = ebp+matrix(b[:,:,m+1-i])*matrix(x[:,k1-1:k2-1]); 
          pf = pf + efp*efp.H; 
          pb = pb + ebp*ebp.H; 
          pfb = pfb + efp*ebp.H; 

      aparr = a; 
      bparr = b; 
    
    for j in range(p):
       coeff = concatenate((coeff,inv(matrix(a[:,:,0]))*matrix(a[:,:,j+1])),1); 

    return coeff, En*En.H, kr
    

#Port of spectrum_AR.m
# Version: 2010jan18

def spectrum_AR(A,Z,M,f,fs): # Get the spectrum in one specific frequency-f
    from scipy import eye, size, exp, pi, real, disp
    from numpy import linalg; inv=linalg.inv
    N = size(Z,0); H = eye(N,N); # identity matrix
    for m in range(M):
        H = H + A[:,m*N:(m+1)*N]*exp(-1j*(m+1)*2*pi*f/fs);   # Multiply f in the exponent by sampling interval (=1/fs). See Richard Shiavi
        
    H = inv(H);
    S = H*Z*H.H/fs;
    
    return S,H
    


# Using Geweke's method to compute the causality between any two channels 
# 
#   x is a two dimentional matrix whose each row is one variable's time series 
#   Nr is the number of realizations, 
#   Nl is the length of every realization 
#      If the time series have one ralization and are stationary long, just let Nr=1, Nl=length(x) 
#   porder is the order of AR model 
#   fs is sampling frequency 
#   freq is a vector of frequencies of interest, usually freq=0:fs/2 
#       CK: WRONG!! freq must be a scalar, else the for loop doesn't work.
# 
#   Fx2y is the causality measure from x to y 
#   Fy2x is causality from y to x 
#   Fxy is instantaneous causality between x and y 
#        the order of Fx2y/Fy2x is 1 to 2:L, 2 to 3:L,....,L-1 to L.  That is, 
#        1st column: 1&2; 2nd: 1&3; ...; (L-1)th: 1&L; ...; (L(L-1))th: (L-1)&L. 

# revised Jan. 2006 by Yonghong Chen 
# Note: remove the ensemble mean before using this code 

def pwcausalr(x,Nr,Nl,porder,fs,freq=0): # Note: freq determines whether the frequency points are calculated or chosen
    from pylab import size, shape, real, log, conj, zeros, arange, disp, array
    from numpy import linalg; det=linalg.det
    import numpy as np # Just for "sum"; can't remember what's wrong with pylab's sum
    [L,N] = shape(x); #L is the number of channels, N is the total points in every channel 
     
    if freq==0: F=timefreq(x[0,:],fs) # Define the frequency points
    else: F=array(range(0,freq+1)) # Or just pick them
    npts=size(F,0)
    # Initialize arrays
    maxindex=np.sum(arange(1,L))
    pp=zeros((L,npts))
    # Had these all defined on one line, and stupidly they STAY linked!!
    cohe=zeros((maxindex,npts))
    Fy2x=zeros((maxindex,npts))
    Fx2y=zeros((maxindex,npts))
    Fxy=zeros((maxindex,npts))
    index = 0;

    for i in range(1,L):
        for j in range(i+1,L+1):
            y=zeros((2,N)) # Initialize y
            index = index + 1; 
            y[0,:] = x[i-1,:]; 
            y[1,:] = x[j-1,:];   
            A2,Z2,tmp = armorf(y,Nr,Nl,porder); #fitting a model on every possible pair 
            eyx = Z2[1,1] - Z2[0,1]**2/Z2[0,0]; #corrected covariance 
            exy = Z2[0,0] - Z2[1,0]**2/Z2[1,1]; 
            f_ind = 0; 
            for f in F:
                f_ind = f_ind + 1; 
                S2,H2 = spectrum_AR(A2,Z2,porder,f,fs); 
                pp[i-1,f_ind-1] = abs(S2[0,0]*2);      # revised 
                if (i==L-1) & (j==L):
                    pp[j-1,f_ind-1] = abs(S2[1,1]*2);  # revised 
                cohe[index-1,f_ind-1] = real(abs(S2[0,1])**2 / S2[0,0]/S2[1,1]);   
                Fy2x[index-1,f_ind-1] = log(abs(S2[0,0])/abs(S2[0,0]-(H2[0,1]*eyx*conj(H2[0,1]))/fs)); #Geweke's original measure 
                Fx2y[index-1,f_ind-1] = log(abs(S2[1,1])/abs(S2[1,1]-(H2[1,0]*exy*conj(H2[1,0]))/fs)); 
                Fxy[index-1,f_ind-1] = log(abs(S2[0,0]-(H2[0,1]*eyx*conj(H2[0,1]))/fs)*abs(S2[1,1]-(H2[1,0]*exy*conj(H2[1,0]))/fs)/abs(det(S2))); 
                
    return F,pp,cohe,Fx2y,Fy2x,Fxy







def granger(vec1,vec2,order=10,rate=200,maxfreq=0):
    """
    GRANGER
    
    Provide a simple way of calculating the key quantities.
    
    Usage:
        F,pp,cohe,Fx2y,Fy2x,Fxy=granger(vec1,vec2,order,rate,maxfreq)
    where:
        F is a 1xN vector of frequencies
        pp is a 2xN array of power spectra
        cohe is the coherence between vec1 and vec2
        Fx2y is the causality from vec1->vec2
        Fy2x is the causality from vec2->vec1
        Fxy is non-directional causality (cohe-Fx2y-Fy2x)
        
        vec1 is a time series of length N
        vec2 is another time series of length N
        rate is the sampling rate, in Hz
        maxfreq is the maximum frequency to be returned, in Hz
    
    Version: 2011jul18
    """
    from bsmart import timefreq, pwcausalr
    from scipy import array, size
    
    if maxfreq==0: F=timefreq(vec1,rate) # Define the frequency points
    else: F=array(range(0,maxfreq+1)) # Or just pick them
    npts=size(F,0)
    
    data=array([vec1,vec2])
    F,pp,cohe,Fx2y,Fy2x,Fxy=pwcausalr(data,1,npts,order,rate,maxfreq)
    return F,pp[0,:],cohe[0,:],Fx2y[0,:],Fy2x[0,:],Fxy[0,:]
