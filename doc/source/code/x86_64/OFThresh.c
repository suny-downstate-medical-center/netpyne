/* Created by Language version: 6.2.0 */
/* VECTORIZED */
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
 
#define _threadargscomma_ _p, _ppvar, _thread, _nt,
#define _threadargs_ _p, _ppvar, _thread, _nt
 
#define _threadargsprotocomma_ double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt,
#define _threadargsproto_ double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt
 	/*SUPPRESS 761*/
	/*SUPPRESS 762*/
	/*SUPPRESS 763*/
	/*SUPPRESS 765*/
	 extern double *getarg();
 /* Thread safe. No static _p or _ppvar. */
 
#define t _nt->_t
#define dt _nt->_dt
#define gkbase _p[0]
#define taugka _p[1]
#define spkht _p[2]
#define tauk _p[3]
#define ek _p[4]
#define vth _p[5]
#define refrac _p[6]
#define verbose _p[7]
#define apdur _p[8]
#define gkinc _p[9]
#define tauvtha _p[10]
#define vthinc _p[11]
#define gna _p[12]
#define ena _p[13]
#define ina _p[14]
#define ik _p[15]
#define i _p[16]
#define gnamax _p[17]
#define gkmin _p[18]
#define inrefrac _p[19]
#define gk _p[20]
#define vthadapt _p[21]
#define gkadapt _p[22]
#define iother _p[23]
#define Dgk _p[24]
#define Dvthadapt _p[25]
#define Dgkadapt _p[26]
#define v _p[27]
#define _g _p[28]
#define _tsav _p[29]
#define _nd_area  *_ppvar[0]._pval
#define _ion_iother	*_ppvar[2]._pval
#define _ion_diotherdv	*_ppvar[3]._pval
 
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
 static int hoc_nrnpointerindex =  -1;
 static Datum* _extcall_thread;
 static Prop* _extcall_prop;
 /* external NEURON variables */
 /* declaration of user functions */
 static double _hoc_fflag();
 static double _hoc_iassign();
 static double _hoc_version();
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
 _extcall_prop = _prop;
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
 "fflag", _hoc_fflag,
 "iassign", _hoc_iassign,
 "version", _hoc_version,
 0, 0
};
#define fflag fflag_OFTH
 extern double fflag( _threadargsproto_ );
 /* declare global and static user variables */
#define checkref checkref_OFTH
 double checkref = 1;
#define kadapt kadapt_OFTH
 double kadapt = 0.007;
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 0,0,0
};
 static HocParmUnits _hoc_parm_units[] = {
 "kadapt_OFTH", "uS",
 "gkbase", "uS",
 "taugka", "ms",
 "spkht", "mV",
 "tauk", "ms",
 "ek", "mV",
 "vth", "mV",
 "refrac", "ms",
 "apdur", "ms",
 "gkinc", "uS",
 "tauvtha", "ms",
 "gna", "uS",
 "ena", "mV",
 "ina", "nA",
 "ik", "nA",
 "i", "nA",
 "gnamax", "uS",
 "gkmin", "uS",
 0,0
};
 static double delta_t = 0.01;
 static double gkadapt0 = 0;
 static double gk0 = 0;
 static double vthadapt0 = 0;
 /* connect global user variables to hoc */
 static DoubScal hoc_scdoub[] = {
 "kadapt_OFTH", &kadapt_OFTH,
 "checkref_OFTH", &checkref_OFTH,
 0,0
};
 static DoubVec hoc_vdoub[] = {
 0,0,0
};
 static double _sav_indep;
 static void nrn_alloc(Prop*);
static void  nrn_init(_NrnThread*, _Memb_list*, int);
static void nrn_state(_NrnThread*, _Memb_list*, int);
 static void nrn_cur(_NrnThread*, _Memb_list*, int);
static void  nrn_jacob(_NrnThread*, _Memb_list*, int);
 
#define _watch_array _ppvar + 5 
 static void _hoc_destroy_pnt(_vptr) void* _vptr; {
   Prop* _prop = ((Point_process*)_vptr)->_prop;
   if (_prop) { _nrn_free_watch(_prop->dparam, 5, 2);}
   destroy_point_process(_vptr);
}
 
static int _ode_count(int);
static void _ode_map(int, double**, double**, double*, Datum*, double*, int);
static void _ode_spec(_NrnThread*, _Memb_list*, int);
static void _ode_matsol(_NrnThread*, _Memb_list*, int);
 
#define _cvode_ieq _ppvar[7]._i
 /* connect range variables in _p that hoc is supposed to know about */
 static const char *_mechanism[] = {
 "6.2.0",
"OFTH",
 "gkbase",
 "taugka",
 "spkht",
 "tauk",
 "ek",
 "vth",
 "refrac",
 "verbose",
 "apdur",
 "gkinc",
 "tauvtha",
 "vthinc",
 "gna",
 "ena",
 "ina",
 "ik",
 "i",
 "gnamax",
 "gkmin",
 0,
 "inrefrac",
 0,
 "gk",
 "vthadapt",
 "gkadapt",
 0,
 0};
 static Symbol* _other_sym;
 
extern Prop* need_memb(Symbol*);

static void nrn_alloc(Prop* _prop) {
	Prop *prop_ion;
	double *_p; Datum *_ppvar;
  if (nrn_point_prop_) {
	_prop->_alloc_seq = nrn_point_prop_->_alloc_seq;
	_p = nrn_point_prop_->param;
	_ppvar = nrn_point_prop_->dparam;
 }else{
 	_p = nrn_prop_data_alloc(_mechtype, 30, _prop);
 	/*initialize range parameters*/
 	gkbase = 0.06;
 	taugka = 100;
 	spkht = 55;
 	tauk = 2.3;
 	ek = -70;
 	vth = -40;
 	refrac = 2.7;
 	verbose = 0;
 	apdur = 0.9;
 	gkinc = 0.006;
 	tauvtha = 1;
 	vthinc = 0;
 	gna = 0;
 	ena = 55;
 	ina = 0;
 	ik = 0;
 	i = 0;
 	gnamax = 0.3;
 	gkmin = 1e-05;
  }
 	_prop->param = _p;
 	_prop->param_size = 30;
  if (!nrn_point_prop_) {
 	_ppvar = nrn_prop_datum_alloc(_mechtype, 8, _prop);
  }
 	_prop->dparam = _ppvar;
 	/*connect ionic variables to this model*/
 prop_ion = need_memb(_other_sym);
 	_ppvar[2]._pval = &prop_ion->param[3]; /* iother */
 	_ppvar[3]._pval = &prop_ion->param[4]; /* _ion_diotherdv */
 
}
 static void _initlists();
  /* some states have an absolute tolerance */
 static Symbol** _atollist;
 static HocStateTolerance _hoc_state_tol[] = {
 0,0
};
 
#define _tqitem &(_ppvar[4]._pvoid)
 static void _net_receive(Point_process*, double*, double);
 static void _update_ion_pointer(Datum*);
 extern Symbol* hoc_lookup(const char*);
extern void _nrn_thread_reg(int, int, void(*f)(Datum*));
extern void _nrn_thread_table_reg(int, void(*)(double*, Datum*, Datum*, _NrnThread*, int));
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void _cvode_abstol( Symbol**, double*, int);

 void _OFThresh_reg() {
	int _vectorized = 1;
  _initlists();
 	ion_reg("other", 1.0);
 	_other_sym = hoc_lookup("other_ion");
 	_pointtype = point_register_mech(_mechanism,
	 nrn_alloc,nrn_cur, nrn_jacob, nrn_state, nrn_init,
	 hoc_nrnpointerindex, 1,
	 _hoc_create_pnt, _hoc_destroy_pnt, _member_func);
 _mechtype = nrn_get_mechtype(_mechanism[1]);
     _nrn_setdata_reg(_mechtype, _setdata);
     _nrn_thread_reg(_mechtype, 2, _update_ion_pointer);
  hoc_register_prop_size(_mechtype, 30, 8);
 	hoc_register_cvode(_mechtype, _ode_count, _ode_map, _ode_spec, _ode_matsol);
 	hoc_register_tolerance(_mechtype, _hoc_state_tol, &_atollist);
 add_nrn_has_net_event(_mechtype);
 pnt_receive[_mechtype] = _net_receive;
 pnt_receive_size[_mechtype] = 1;
 	hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 OFTH /u/salvadord/Documents/ISB/Work/netpyne_doc/source/code/x86_64/OFThresh.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
static int _reset;
static char *modelname = "OF Threshold Spiking";

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static void _modl_cleanup(){ _match_recurse=1;}
static int iassign(_threadargsproto_);
static int version(_threadargsproto_);
 
static int _ode_spec1(_threadargsproto_);
/*static int _ode_matsol1(_threadargsproto_);*/
 static int _slist1[3], _dlist1[3];
 static int states(_threadargsproto_);
 
/*CVODE*/
 static int _ode_spec1 (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {int _reset = 0; {
   Dgk = - gk / tauk ;
   Dgkadapt = ( gkbase - gkadapt ) / taugka ;
   Dvthadapt = ( vth - vthadapt ) / tauvtha ;
   }
 return _reset;
}
 static int _ode_matsol1 (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
 Dgk = Dgk  / (1. - dt*( ( - 1.0 ) / tauk )) ;
 Dgkadapt = Dgkadapt  / (1. - dt*( ( ( ( - 1.0 ) ) ) / taugka )) ;
 Dvthadapt = Dvthadapt  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tauvtha )) ;
 return 0;
}
 /*END CVODE*/
 static int states (double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) { {
    gk = gk + (1. - exp(dt*(( - 1.0 ) / tauk)))*(- ( 0.0 ) / ( ( - 1.0 ) / tauk ) - gk) ;
    gkadapt = gkadapt + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / taugka)))*(- ( ( ( gkbase ) ) / taugka ) / ( ( ( ( - 1.0) ) ) / taugka ) - gkadapt) ;
    vthadapt = vthadapt + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tauvtha)))*(- ( ( ( vth ) ) / tauvtha ) / ( ( ( ( - 1.0) ) ) / tauvtha ) - vthadapt) ;
   }
  return 0;
}
 
static int  iassign ( _threadargsproto_ ) {
   ik = gk * ( v - ek ) ;
   ina = gna * ( v - ena ) ;
   i = ik + ina ;
   iother = i ;
    return 0; }
 
static double _hoc_iassign(void* _vptr) {
 double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   _p = ((Point_process*)_vptr)->_prop->param;
  _ppvar = ((Point_process*)_vptr)->_prop->dparam;
  _thread = _extcall_thread;
  _nt = (_NrnThread*)((Point_process*)_vptr)->_vnt;
 _r = 1.;
 iassign ( _p, _ppvar, _thread, _nt );
 return(_r);
}
 
static double _watch1_cond(_pnt) Point_process* _pnt; {
 	double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
	_thread= (Datum*)0; _nt = (_NrnThread*)_pnt->_vnt;
 	_p = _pnt->_prop->param; _ppvar = _pnt->_prop->dparam;
	v = NODEV(_pnt->node);
	return  ( v ) - ( vthadapt ) ;
}
 
static void _net_receive (_pnt, _args, _lflag) Point_process* _pnt; double* _args; double _lflag; 
{  double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   int _watch_rm = 0;
   _thread = (Datum*)0; _nt = (_NrnThread*)_pnt->_vnt;   _p = _pnt->_prop->param; _ppvar = _pnt->_prop->dparam;
  if (_tsav > t){ extern char* hoc_object_name(); hoc_execerror(hoc_object_name(_pnt->ob), ":Event arrived out of order. Must call ParallelContext.set_maxstep AFTER assigning minimum NetCon.delay");}
 _tsav = t;  v = NODEV(_pnt->node);
   if (_lflag == 1. ) {*(_tqitem) = 0;}
 {
   if ( _lflag  == 1.0 ) {
       _nrn_watch_activate(_watch_array, _watch1_cond, 1, _pnt, _watch_rm++, 2.0);
 }
   else if ( _lflag  == 2.0  &&  ! inrefrac ) {
     net_event ( _pnt, t ) ;
     net_send ( _tqitem, _args, _pnt, t +  apdur , 3.0 ) ;
     net_send ( _tqitem, _args, _pnt, t +  refrac , 4.0 ) ;
     inrefrac = 1.0 ;
     gkadapt = gkadapt + gkinc ;
     vthadapt = vthadapt + vthinc ;
     gna = gnamax ;
     if ( verbose ) {
       printf ( "spike at t=%g\n" , t ) ;
       }
     }
   else if ( _lflag  == 3.0 ) {
     gk = gkadapt ;
     gna = 0.0 ;
     if ( verbose ) {
       printf ( "end of action potential @ t = %g\n" , t ) ;
       }
     }
   else if ( _lflag  == 4.0 ) {
     inrefrac = 0.0 ;
     if ( verbose ) {
       printf ( "refrac over @ t = %g\n" , t ) ;
       }
     if ( checkref  && v > vthadapt ) {
       net_send ( _tqitem, _args, _pnt, t +  0.0 , 2.0 ) ;
       }
     }
   else if ( _lflag  == 0.0  && _args[0] > 0.0 ) {
     net_event ( _pnt, t ) ;
     }
   else if ( _lflag  == 2.0  && inrefrac  && verbose ) {
     printf ( "in refrac @ t = %g, no spike\n" , t ) ;
     }
   } 
 NODEV(_pnt->node) = v;
 }
 
double fflag ( _threadargsproto_ ) {
   double _lfflag;
 _lfflag = 1.0 ;
   
return _lfflag;
 }
 
static double _hoc_fflag(void* _vptr) {
 double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   _p = ((Point_process*)_vptr)->_prop->param;
  _ppvar = ((Point_process*)_vptr)->_prop->dparam;
  _thread = _extcall_thread;
  _nt = (_NrnThread*)((Point_process*)_vptr)->_vnt;
 _r =  fflag ( _p, _ppvar, _thread, _nt );
 return(_r);
}
 
static int  version ( _threadargsproto_ ) {
   printf ( "$Id: OFThresh.mod,v 1.22 2010/05/04 21:32:47 billl Exp $ " ) ;
    return 0; }
 
static double _hoc_version(void* _vptr) {
 double _r;
   double* _p; Datum* _ppvar; Datum* _thread; _NrnThread* _nt;
   _p = ((Point_process*)_vptr)->_prop->param;
  _ppvar = ((Point_process*)_vptr)->_prop->dparam;
  _thread = _extcall_thread;
  _nt = (_NrnThread*)((Point_process*)_vptr)->_vnt;
 _r = 1.;
 version ( _p, _ppvar, _thread, _nt );
 return(_r);
}
 
static int _ode_count(int _type){ return 3;}
 
static void _ode_spec(_NrnThread* _nt, _Memb_list* _ml, int _type) {
   double* _p; Datum* _ppvar; Datum* _thread;
   Node* _nd; double _v; int _iml, _cntml;
  _cntml = _ml->_nodecount;
  _thread = _ml->_thread;
  for (_iml = 0; _iml < _cntml; ++_iml) {
    _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
    _nd = _ml->_nodelist[_iml];
    v = NODEV(_nd);
     _ode_spec1 (_p, _ppvar, _thread, _nt);
  }}
 
static void _ode_map(int _ieq, double** _pv, double** _pvdot, double* _pp, Datum* _ppd, double* _atol, int _type) { 
	double* _p; Datum* _ppvar;
 	int _i; _p = _pp; _ppvar = _ppd;
	_cvode_ieq = _ieq;
	for (_i=0; _i < 3; ++_i) {
		_pv[_i] = _pp + _slist1[_i];  _pvdot[_i] = _pp + _dlist1[_i];
		_cvode_abstol(_atollist, _atol, _i);
	}
 }
 
static void _ode_matsol(_NrnThread* _nt, _Memb_list* _ml, int _type) {
   double* _p; Datum* _ppvar; Datum* _thread;
   Node* _nd; double _v; int _iml, _cntml;
  _cntml = _ml->_nodecount;
  _thread = _ml->_thread;
  for (_iml = 0; _iml < _cntml; ++_iml) {
    _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
    _nd = _ml->_nodelist[_iml];
    v = NODEV(_nd);
 _ode_matsol1 (_p, _ppvar, _thread, _nt);
 }}
 extern void nrn_update_ion_pointer(Symbol*, Datum*, int, int);
 static void _update_ion_pointer(Datum* _ppvar) {
   nrn_update_ion_pointer(_other_sym, _ppvar, 2, 3);
   nrn_update_ion_pointer(_other_sym, _ppvar, 3, 4);
 }

static void initmodel(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt) {
  int _i; double _save;{
  gkadapt = gkadapt0;
  gk = gk0;
  vthadapt = vthadapt0;
 {
   net_send ( _tqitem, (double*)0, _ppvar[1]._pvoid, t +  0.0 , 1.0 ) ;
   gk = 0.0 ;
   gkadapt = gkbase ;
   vthadapt = vth ;
   gna = 0.0 ;
   ina = 0.0 ;
   ik = 0.0 ;
   i = 0.0 ;
   iother = 0.0 ;
   inrefrac = 0.0 ;
   }
 
}
}

static void nrn_init(_NrnThread* _nt, _Memb_list* _ml, int _type){
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; double _v; int* _ni; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
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
 initmodel(_p, _ppvar, _thread, _nt);
 }}

static double _nrn_current(double* _p, Datum* _ppvar, Datum* _thread, _NrnThread* _nt, double _v){double _current=0.;v=_v;{ {
   if ( gk < gkmin ) {
     gk = gkmin ;
     }
   if ( gkadapt < gkbase ) {
     gkadapt = gkbase ;
     }
   if ( vthadapt < vth ) {
     vthadapt = vth ;
     }
   iassign ( _threadargs_ ) ;
   }
 _current += iother;

} return _current;
}

static void nrn_cur(_NrnThread* _nt, _Memb_list* _ml, int _type) {
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; int* _ni; double _rhs, _v; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml]; _ppvar = _ml->_pdata[_iml];
#if CACHEVEC
  if (use_cachevec) {
    _v = VEC_V(_ni[_iml]);
  }else
#endif
  {
    _nd = _ml->_nodelist[_iml];
    _v = NODEV(_nd);
  }
 _g = _nrn_current(_p, _ppvar, _thread, _nt, _v + .001);
 	{ double _diother;
  _diother = iother;
 _rhs = _nrn_current(_p, _ppvar, _thread, _nt, _v);
  _ion_diotherdv += (_diother - iother)/.001 * 1.e2/ (_nd_area);
 	}
 _g = (_g - _rhs)/.001;
  _ion_iother += iother * 1.e2/ (_nd_area);
 _g *=  1.e2/(_nd_area);
 _rhs *= 1.e2/(_nd_area);
#if CACHEVEC
  if (use_cachevec) {
	VEC_RHS(_ni[_iml]) -= _rhs;
  }else
#endif
  {
	NODERHS(_nd) -= _rhs;
  }
 
}}

static void nrn_jacob(_NrnThread* _nt, _Memb_list* _ml, int _type) {
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; int* _ni; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
for (_iml = 0; _iml < _cntml; ++_iml) {
 _p = _ml->_data[_iml];
#if CACHEVEC
  if (use_cachevec) {
	VEC_D(_ni[_iml]) += _g;
  }else
#endif
  {
     _nd = _ml->_nodelist[_iml];
	NODED(_nd) += _g;
  }
 
}}

static void nrn_state(_NrnThread* _nt, _Memb_list* _ml, int _type) {
 double _break, _save;
double* _p; Datum* _ppvar; Datum* _thread;
Node *_nd; double _v; int* _ni; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
_thread = _ml->_thread;
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
 { {
 for (; t < _break; t += dt) {
   states(_p, _ppvar, _thread, _nt);
  
}}
 t = _save;
 } }}

}

static void terminal(){}

static void _initlists(){
 double _x; double* _p = &_x;
 int _i; static int _first = 1;
  if (!_first) return;
 _slist1[0] = &(gk) - _p;  _dlist1[0] = &(Dgk) - _p;
 _slist1[1] = &(gkadapt) - _p;  _dlist1[1] = &(Dgkadapt) - _p;
 _slist1[2] = &(vthadapt) - _p;  _dlist1[2] = &(Dvthadapt) - _p;
_first = 0;
}

#if defined(__cplusplus)
} /* extern "C" */
#endif
