/* Created by Language version: 6.2.0 */
/* NOT VECTORIZED */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "scoplib_ansi.h"
#undef PI
#define nil 0
#include "md1redef.h"
#include "section.h"
#include "nrniv_mf.h"
#include "md2redef.h"
 
#if METHOD3
extern int _method3;
#endif

#if !NRNGPU
#undef exp
#define exp hoc_Exp
extern double hoc_Exp(double);
#endif
 
#define _threadargscomma_ /**/
#define _threadargs_ /**/
 
#define _threadargsprotocomma_ /**/
#define _threadargsproto_ /**/
 	/*SUPPRESS 761*/
	/*SUPPRESS 762*/
	/*SUPPRESS 763*/
	/*SUPPRESS 765*/
	 extern double *getarg();
 static double *_p; static Datum *_ppvar;
 
#define t nrn_threads->_t
#define dt nrn_threads->_dt
#define tauhebb _p[0]
#define tauanti _p[1]
#define hebbwt _p[2]
#define antiwt _p[3]
#define RLwindhebb _p[4]
#define RLwindanti _p[5]
#define useRLexp _p[6]
#define RLlenhebb _p[7]
#define RLlenanti _p[8]
#define RLhebbwt _p[9]
#define RLantiwt _p[10]
#define wmax _p[11]
#define softthresh _p[12]
#define STDPon _p[13]
#define RLon _p[14]
#define verbose _p[15]
#define tlastpre _p[16]
#define tlastpost _p[17]
#define tlasthebbelig _p[18]
#define tlastantielig _p[19]
#define interval _p[20]
#define deltaw _p[21]
#define newweight _p[22]
#define _tsav _p[23]
#define _nd_area  *_ppvar[0]._pval
#define synweight	*_ppvar[2]._pval
#define _p_synweight	_ppvar[2]._pval
 
#if MAC
#if !defined(v)
#define v _mlhv
#endif
#if !defined(h)
#define h _mlhh
#endif
#endif
 
#if defined(__cplusplus)
extern "C" {
#endif
 static int hoc_nrnpointerindex =  2;
 /* external NEURON variables */
 /* declaration of user functions */
 static double _hoc_antiRL();
 static double _hoc_adjustweight();
 static double _hoc_hebbRL();
 static double _hoc_reward_punish();
 static double _hoc_softthreshold();
 static int _mechtype;
extern void _nrn_cacheloop_reg(int, int);
extern void hoc_register_prop_size(int, int, int);
extern void hoc_register_limits(int, HocParmLimits*);
extern void hoc_register_units(int, HocParmUnits*);
extern void nrn_promote(Prop*, int, int);
extern Memb_func* memb_func;
 extern Prop* nrn_point_prop_;
 static int _pointtype;
 static void* _hoc_create_pnt(_ho) Object* _ho; { void* create_point_process();
 return create_point_process(_pointtype, _ho);
}
 static void _hoc_destroy_pnt();
 static double _hoc_loc_pnt(_vptr) void* _vptr; {double loc_point_process();
 return loc_point_process(_pointtype, _vptr);
}
 static double _hoc_has_loc(_vptr) void* _vptr; {double has_loc_point();
 return has_loc_point(_vptr);
}
 static double _hoc_get_loc_pnt(_vptr)void* _vptr; {
 double get_loc_point_process(); return (get_loc_point_process(_vptr));
}
 extern void _nrn_setdata_reg(int, void(*)(Prop*));
 static void _setdata(Prop* _prop) {
 _p = _prop->param; _ppvar = _prop->dparam;
 }
 static void _hoc_setdata(void* _vptr) { Prop* _prop;
 _prop = ((Point_process*)_vptr)->_prop;
   _setdata(_prop);
 }
 /* connect user functions to hoc names */
 static VoidFunc hoc_intfunc[] = {
 0,0
};
 static Member_func _member_func[] = {
 "loc", _hoc_loc_pnt,
 "has_loc", _hoc_has_loc,
 "get_loc", _hoc_get_loc_pnt,
 "antiRL", _hoc_antiRL,
 "adjustweight", _hoc_adjustweight,
 "hebbRL", _hoc_hebbRL,
 "reward_punish", _hoc_reward_punish,
 "softthreshold", _hoc_softthreshold,
 0, 0
};
#define antiRL antiRL_STDP
#define hebbRL hebbRL_STDP
#define softthreshold softthreshold_STDP
 extern double antiRL( );
 extern double hebbRL( );
 extern double softthreshold( double );
 /* declare global and static user variables */
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 0,0,0
};
 static HocParmUnits _hoc_parm_units[] = {
 "tauhebb", "ms",
 "tauanti", "ms",
 "RLwindhebb", "ms",
 "RLwindanti", "ms",
 "RLlenhebb", "ms",
 "RLlenanti", "ms",
 "tlastpre", "ms",
 "tlastpost", "ms",
 "tlasthebbelig", "ms",
 "tlastantielig", "ms",
 "interval", "ms",
 0,0
};
 static double v = 0;
 /* connect global user variables to hoc */
 static DoubScal hoc_scdoub[] = {
 0,0
};
 static DoubVec hoc_vdoub[] = {
 0,0,0
};
 static double _sav_indep;
 static void nrn_alloc(Prop*);
static void  nrn_init(_NrnThread*, _Memb_list*, int);
static void nrn_state(_NrnThread*, _Memb_list*, int);
 static void _hoc_destroy_pnt(_vptr) void* _vptr; {
   destroy_point_process(_vptr);
}
 /* connect range variables in _p that hoc is supposed to know about */
 static const char *_mechanism[] = {
 "6.2.0",
"STDP",
 "tauhebb",
 "tauanti",
 "hebbwt",
 "antiwt",
 "RLwindhebb",
 "RLwindanti",
 "useRLexp",
 "RLlenhebb",
 "RLlenanti",
 "RLhebbwt",
 "RLantiwt",
 "wmax",
 "softthresh",
 "STDPon",
 "RLon",
 "verbose",
 0,
 "tlastpre",
 "tlastpost",
 "tlasthebbelig",
 "tlastantielig",
 "interval",
 "deltaw",
 "newweight",
 0,
 0,
 "synweight",
 0};
 
extern Prop* need_memb(Symbol*);

static void nrn_alloc(Prop* _prop) {
	Prop *prop_ion;
	double *_p; Datum *_ppvar;
  if (nrn_point_prop_) {
	_prop->_alloc_seq = nrn_point_prop_->_alloc_seq;
	_p = nrn_point_prop_->param;
	_ppvar = nrn_point_prop_->dparam;
 }else{
 	_p = nrn_prop_data_alloc(_mechtype, 24, _prop);
 	/*initialize range parameters*/
 	tauhebb = 10;
 	tauanti = 10;
 	hebbwt = 1;
 	antiwt = -1;
 	RLwindhebb = 10;
 	RLwindanti = 10;
 	useRLexp = 0;
 	RLlenhebb = 100;
 	RLlenanti = 100;
 	RLhebbwt = 1;
 	RLantiwt = -1;
 	wmax = 15;
 	softthresh = 0;
 	STDPon = 1;
 	RLon = 1;
 	verbose = 0;
  }
 	_prop->param = _p;
 	_prop->param_size = 24;
  if (!nrn_point_prop_) {
 	_ppvar = nrn_prop_datum_alloc(_mechtype, 4, _prop);
  }
 	_prop->dparam = _ppvar;
 	/*connect ionic variables to this model*/
 
}
 static void _initlists();
 
#define _tqitem &(_ppvar[3]._pvoid)
 static void _net_receive(Point_process*, double*, double);
 extern Symbol* hoc_lookup(const char*);
extern void _nrn_thread_reg(int, int, void(*f)(Datum*));
extern void _nrn_thread_table_reg(int, void(*)(double*, Datum*, Datum*, _NrnThread*, int));
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void _cvode_abstol( Symbol**, double*, int);

 void _stdp_reg() {
	int _vectorized = 0;
  _initlists();
 	_pointtype = point_register_mech(_mechanism,
	 nrn_alloc,(void*)0, (void*)0, (void*)0, nrn_init,
	 hoc_nrnpointerindex, 0,
	 _hoc_create_pnt, _hoc_destroy_pnt, _member_func);
 _mechtype = nrn_get_mechtype(_mechanism[1]);
     _nrn_setdata_reg(_mechtype, _setdata);
  hoc_register_prop_size(_mechtype, 24, 4);
 pnt_receive[_mechtype] = _net_receive;
 pnt_receive_size[_mechtype] = 1;
 	hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 STDP C:/Users/campb/OneDrive/Documents/GitHub/compscaling/sim_netpyne/mod/stdp.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
static int _reset;
static char *modelname = "";

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static void _modl_cleanup(){ _match_recurse=1;}
static int adjustweight(double);
static int reward_punish(double);
 
static void _net_receive (_pnt, _args, _lflag) Point_process* _pnt; double* _args; double _lflag; 
{    _p = _pnt->_prop->param; _ppvar = _pnt->_prop->dparam;
  if (_tsav > t){ extern char* hoc_object_name(); hoc_execerror(hoc_object_name(_pnt->ob), ":Event arrived out of order. Must call ParallelContext.set_maxstep AFTER assigning minimum NetCon.delay");}
 _tsav = t;   if (_lflag == 1. ) {*(_tqitem) = 0;}
 {
   deltaw = 0.0 ;
   if ( ( _lflag  == - 1.0 )  && ( tlastpre  != t - 1.0 ) ) {
     _args[0] = 0.0 ;
     deltaw = hebbwt * exp ( - interval / tauhebb ) ;
     if ( softthresh  == 1.0 ) {
       deltaw = softthreshold ( _threadargscomma_ deltaw ) ;
       }
     if ( verbose > 0.0 ) {
       printf ( "Hebbian STDP event: t = %f ms; deltaw = %f\n" , t , deltaw ) ;
       }
     }
   else if ( ( _lflag  == 1.0 )  && ( tlastpost  != t - 1.0 ) ) {
     _args[0] = 0.0 ;
     deltaw = antiwt * exp ( interval / tauanti ) ;
     if ( softthresh  == 1.0 ) {
       deltaw = softthreshold ( _threadargscomma_ deltaw ) ;
       }
     if ( verbose > 0.0 ) {
       printf ( "anti-Hebbian STDP event: t = %f ms; deltaw = %f\n" , t , deltaw ) ;
       }
     }
   if ( _args[0] >= 0.0 ) {
     interval = tlastpost - t ;
     if ( ( tlastpost > - 1.0 )  && ( interval > 1.0 ) ) {
       if ( STDPon  == 1.0 ) {
         net_send ( _tqitem, _args, _pnt, t +  1.0 , 1.0 ) ;
         }
       if ( ( RLon  == 1.0 )  && ( - interval <= RLwindanti ) ) {
         tlastantielig = t ;
         }
       }
     tlastpre = t ;
     }
   else {
     interval = t - tlastpre ;
     if ( ( tlastpre > - 1.0 )  && ( interval > 1.0 ) ) {
       if ( STDPon  == 1.0 ) {
         net_send ( _tqitem, _args, _pnt, t +  1.0 , - 1.0 ) ;
         }
       if ( ( RLon  == 1.0 )  && ( interval <= RLwindhebb ) ) {
         tlasthebbelig = t ;
         }
       }
     tlastpost = t ;
     }
   adjustweight ( _threadargscomma_ deltaw ) ;
   } }
 
static int  reward_punish (  double _lreinf ) {
   if ( RLon  == 1.0 ) {
     deltaw = 0.0 ;
     deltaw = deltaw + _lreinf * hebbRL ( _threadargs_ ) ;
     deltaw = deltaw + _lreinf * antiRL ( _threadargs_ ) ;
     if ( softthresh  == 1.0 ) {
       deltaw = softthreshold ( _threadargscomma_ deltaw ) ;
       }
     adjustweight ( _threadargscomma_ deltaw ) ;
     if ( verbose > 0.0 ) {
       printf ( "RL event: t = %f ms; deltaw = %f\n" , t , deltaw ) ;
       }
     }
    return 0; }
 
static double _hoc_reward_punish(void* _vptr) {
 double _r;
    _hoc_setdata(_vptr);
 _r = 1.;
 reward_punish (  *getarg(1) );
 return(_r);
}
 
double hebbRL (  ) {
   double _lhebbRL;
 if ( ( RLon  == 0.0 )  || ( tlasthebbelig < 0.0 ) ) {
     _lhebbRL = 0.0 ;
     }
   else if ( useRLexp  == 0.0 ) {
     if ( t - tlasthebbelig <= RLlenhebb ) {
       _lhebbRL = RLhebbwt ;
       }
     else {
       _lhebbRL = 0.0 ;
       }
     }
   else {
     _lhebbRL = RLhebbwt * exp ( ( tlasthebbelig - t ) / RLlenhebb ) ;
     }
   
return _lhebbRL;
 }
 
static double _hoc_hebbRL(void* _vptr) {
 double _r;
    _hoc_setdata(_vptr);
 _r =  hebbRL (  );
 return(_r);
}
 
double antiRL (  ) {
   double _lantiRL;
 if ( ( RLon  == 0.0 )  || ( tlastantielig < 0.0 ) ) {
     _lantiRL = 0.0 ;
     }
   else if ( useRLexp  == 0.0 ) {
     if ( t - tlastantielig <= RLlenanti ) {
       _lantiRL = RLantiwt ;
       }
     else {
       _lantiRL = 0.0 ;
       }
     }
   else {
     _lantiRL = RLantiwt * exp ( ( tlastantielig - t ) / RLlenanti ) ;
     }
   
return _lantiRL;
 }
 
static double _hoc_antiRL(void* _vptr) {
 double _r;
    _hoc_setdata(_vptr);
 _r =  antiRL (  );
 return(_r);
}
 
double softthreshold (  double _lrawwc ) {
   double _lsoftthreshold;
 if ( _lrawwc >= 0.0 ) {
     _lsoftthreshold = _lrawwc * ( 1.0 - synweight / wmax ) ;
     }
   else {
     _lsoftthreshold = _lrawwc * synweight / wmax ;
     }
   
return _lsoftthreshold;
 }
 
static double _hoc_softthreshold(void* _vptr) {
 double _r;
    _hoc_setdata(_vptr);
 _r =  softthreshold (  *getarg(1) );
 return(_r);
}
 
static int  adjustweight (  double _lwc ) {
   synweight = synweight + _lwc ;
   if ( synweight > wmax ) {
     synweight = wmax ;
     }
   if ( synweight < 0.0 ) {
     synweight = 0.0 ;
     }
    return 0; }
 
static double _hoc_adjustweight(void* _vptr) {
 double _r;
    _hoc_setdata(_vptr);
 _r = 1.;
 adjustweight (  *getarg(1) );
 return(_r);
}

static void initmodel() {
  int _i; double _save;_ninits++;
{
 {
   tlastpre = - 1.0 ;
   tlastpost = - 1.0 ;
   tlasthebbelig = - 1.0 ;
   tlastantielig = - 1.0 ;
   interval = 0.0 ;
   deltaw = 0.0 ;
   newweight = 0.0 ;
   }

}
}

static void nrn_init(_NrnThread* _nt, _Memb_list* _ml, int _type){
Node *_nd; double _v; int* _ni; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
 _tsav = -1e20;
#if CACHEVEC
  if (use_cachevec) {
    _v = VEC_V(_ni[_iml]);
  }else
#endif
  {
    _nd = _ml->_nodelist[_iml];
    _v = NODEV(_nd);
  }
 v = _v;
 initmodel();
}}

static double _nrn_current(double _v){double _current=0.;v=_v;{
} return _current;
}

static void nrn_state(_NrnThread* _nt, _Memb_list* _ml, int _type){
 double _break, _save;
Node *_nd; double _v; int* _ni; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
 _nd = _ml->_nodelist[_iml];
#if CACHEVEC
  if (use_cachevec) {
    _v = VEC_V(_ni[_iml]);
  }else
#endif
  {
    _nd = _ml->_nodelist[_iml];
    _v = NODEV(_nd);
  }
 _break = t + .5*dt; _save = t;
 v=_v;
{
}}

}

static void terminal(){}

static void _initlists() {
 int _i; static int _first = 1;
  if (!_first) return;
_first = 0;
}
