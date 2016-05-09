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
#define C _p[0]
#define k _p[1]
#define vr _p[2]
#define vt _p[3]
#define vpeak _p[4]
#define a _p[5]
#define b _p[6]
#define c _p[7]
#define d _p[8]
#define Iin _p[9]
#define celltype _p[10]
#define alive _p[11]
#define cellid _p[12]
#define i _p[13]
#define u _p[14]
#define delta _p[15]
#define t0 _p[16]
#define derivtype _p[17]
#define _g _p[18]
#define _tsav _p[19]
#define _nd_area  *_ppvar[0]._pval
 
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
 /* external NEURON variables */
 /* declaration of user functions */
 static double _hoc_derivfunc();
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
 "derivfunc", _hoc_derivfunc,
 0, 0
};
#define derivfunc derivfunc_Izhi2007b
 extern double derivfunc( );
 /* declare global and static user variables */
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 0,0,0
};
 static HocParmUnits _hoc_parm_units[] = {
 "vr", "mV",
 "vt", "mV",
 "vpeak", "mV",
 "i", "nA",
 "u", "mV",
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
 static void nrn_cur(_NrnThread*, _Memb_list*, int);
static void  nrn_jacob(_NrnThread*, _Memb_list*, int);
 
#define _watch_array _ppvar + 3 
 static void _hoc_destroy_pnt(_vptr) void* _vptr; {
   Prop* _prop = ((Point_process*)_vptr)->_prop;
   if (_prop) { _nrn_free_watch(_prop->dparam, 3, 8);}
   destroy_point_process(_vptr);
}
 /* connect range variables in _p that hoc is supposed to know about */
 static const char *_mechanism[] = {
 "6.2.0",
"Izhi2007b",
 "C",
 "k",
 "vr",
 "vt",
 "vpeak",
 "a",
 "b",
 "c",
 "d",
 "Iin",
 "celltype",
 "alive",
 "cellid",
 0,
 "i",
 "u",
 "delta",
 "t0",
 "derivtype",
 0,
 0,
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
 	_p = nrn_prop_data_alloc(_mechtype, 20, _prop);
 	/*initialize range parameters*/
 	C = 100;
 	k = 0.7;
 	vr = -60;
 	vt = -40;
 	vpeak = 35;
 	a = 0.03;
 	b = -2;
 	c = -50;
 	d = 100;
 	Iin = 0;
 	celltype = 1;
 	alive = 1;
 	cellid = -1;
  }
 	_prop->param = _p;
 	_prop->param_size = 20;
  if (!nrn_point_prop_) {
 	_ppvar = nrn_prop_datum_alloc(_mechtype, 11, _prop);
  }
 	_prop->dparam = _ppvar;
 	/*connect ionic variables to this model*/
 
}
 static void _initlists();
 
#define _tqitem &(_ppvar[2]._pvoid)
 static void _net_receive(Point_process*, double*, double);
 extern Symbol* hoc_lookup(const char*);
extern void _nrn_thread_reg(int, int, void(*f)(Datum*));
extern void _nrn_thread_table_reg(int, void(*)(double*, Datum*, Datum*, _NrnThread*, int));
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void _cvode_abstol( Symbol**, double*, int);

 void _izhi2007b_reg() {
	int _vectorized = 0;
  _initlists();
 	_pointtype = point_register_mech(_mechanism,
	 nrn_alloc,nrn_cur, nrn_jacob, nrn_state, nrn_init,
	 hoc_nrnpointerindex, 0,
	 _hoc_create_pnt, _hoc_destroy_pnt, _member_func);
 _mechtype = nrn_get_mechtype(_mechanism[1]);
     _nrn_setdata_reg(_mechtype, _setdata);
  hoc_register_prop_size(_mechtype, 20, 11);
 add_nrn_has_net_event(_mechtype);
 pnt_receive[_mechtype] = _net_receive;
 pnt_receive_size[_mechtype] = 1;
 	hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 Izhi2007b C:/Users/campb/OneDrive/Documents/GitHub/compscaling/sim_netpyne/mod/izhi2007b.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
static int _reset;
static char *modelname = "";

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static void _modl_cleanup(){ _match_recurse=1;}
 
double derivfunc (  ) {
   double _lderivfunc;
 if ( celltype  == 5.0  && derivtype  == 2.0 ) {
     _lderivfunc = a * ( 0.0 - u ) ;
     }
   else if ( celltype  == 5.0  && derivtype  == 1.0 ) {
     _lderivfunc = a * ( ( 0.025 * ( v - d ) * ( v - d ) * ( v - d ) ) - u ) ;
     }
   else if ( celltype  == 5.0 ) {
     
/*VERBATIM*/
    hoc_execerror("izhi2007b.mod ERRA: derivtype not set",0);
 }
   else {
     _lderivfunc = a * ( b * ( v - vr ) - u ) ;
     }
   
return _lderivfunc;
 }
 
static double _hoc_derivfunc(void* _vptr) {
 double _r;
    _hoc_setdata(_vptr);
 _r =  derivfunc (  );
 return(_r);
}
 
static double _watch1_cond(_pnt) Point_process* _pnt; {
  	_p = _pnt->_prop->param; _ppvar = _pnt->_prop->dparam;
	v = NODEV(_pnt->node);
	return  ( v ) - ( ( vpeak - 0.1 * u ) ) ;
}
 
static double _watch2_cond(_pnt) Point_process* _pnt; {
  	_p = _pnt->_prop->param; _ppvar = _pnt->_prop->dparam;
	v = NODEV(_pnt->node);
	return  ( v ) - ( ( vpeak + 0.1 * u ) ) ;
}
 
static double _watch3_cond(_pnt) Point_process* _pnt; {
  	_p = _pnt->_prop->param; _ppvar = _pnt->_prop->dparam;
	v = NODEV(_pnt->node);
	return  ( v ) - ( vpeak ) ;
}
 
static double _watch4_cond(_pnt) Point_process* _pnt; {
  	_p = _pnt->_prop->param; _ppvar = _pnt->_prop->dparam;
	v = NODEV(_pnt->node);
	return  ( v ) - ( - 65.0 ) ;
}
 
static double _watch5_cond(_pnt) Point_process* _pnt; {
  	_p = _pnt->_prop->param; _ppvar = _pnt->_prop->dparam;
	v = NODEV(_pnt->node);
	return  -( ( v ) - ( - 65.0 ) ) ;
}
 
static double _watch6_cond(_pnt) Point_process* _pnt; {
  	_p = _pnt->_prop->param; _ppvar = _pnt->_prop->dparam;
	v = NODEV(_pnt->node);
	return  ( v ) - ( d ) ;
}
 
static double _watch7_cond(_pnt) Point_process* _pnt; {
  	_p = _pnt->_prop->param; _ppvar = _pnt->_prop->dparam;
	v = NODEV(_pnt->node);
	return  -( ( v ) - ( d ) ) ;
}
 
static void _net_receive (_pnt, _args, _lflag) Point_process* _pnt; double* _args; double _lflag; 
{   int _watch_rm = 0;
    _p = _pnt->_prop->param; _ppvar = _pnt->_prop->dparam;
  if (_tsav > t){ extern char* hoc_object_name(); hoc_execerror(hoc_object_name(_pnt->ob), ":Event arrived out of order. Must call ParallelContext.set_maxstep AFTER assigning minimum NetCon.delay");}
 _tsav = t;  v = NODEV(_pnt->node);
   if (_lflag == 1. ) {*(_tqitem) = 0;}
 {
   if ( _lflag  == 1.0 ) {
     if ( celltype  == 4.0 ) {
         _nrn_watch_activate(_watch_array, _watch1_cond, 1, _pnt, _watch_rm++, 2.0);
 }
     else if ( celltype  == 6.0 ) {
         _nrn_watch_activate(_watch_array, _watch2_cond, 2, _pnt, _watch_rm++, 2.0);
 }
     else {
         _nrn_watch_activate(_watch_array, _watch3_cond, 3, _pnt, _watch_rm++, 2.0);
 }
     if ( celltype  == 6.0  || celltype  == 7.0 ) {
         _nrn_watch_activate(_watch_array, _watch4_cond, 4, _pnt, _watch_rm++, 3.0);
   _nrn_watch_activate(_watch_array, _watch5_cond, 5, _pnt, _watch_rm++, 4.0);
 }
     if ( celltype  == 5.0 ) {
         _nrn_watch_activate(_watch_array, _watch6_cond, 6, _pnt, _watch_rm++, 3.0);
   _nrn_watch_activate(_watch_array, _watch7_cond, 7, _pnt, _watch_rm++, 4.0);
 }
     v = vr ;
     }
   else if ( _lflag  == 2.0 ) {
     if ( alive ) {
       net_event ( _pnt, t ) ;
       }
     if ( celltype  == 4.0 ) {
       v = c + 0.04 * u ;
       if ( ( u + d ) < 670.0 ) {
         u = u + d ;
         }
       else {
         u = 670.0 ;
         }
       }
     else if ( celltype  == 5.0 ) {
       v = c ;
       }
     else if ( celltype  == 6.0 ) {
       v = c - 0.1 * u ;
       u = u + d ;
       }
     else {
       v = c ;
       u = u + d ;
       }
     }
   else if ( _lflag  == 3.0 ) {
     if ( celltype  == 5.0 ) {
       derivtype = 1.0 ;
       }
     else if ( celltype  == 6.0 ) {
       b = 0.0 ;
       }
     else if ( celltype  == 7.0 ) {
       b = 2.0 ;
       }
     }
   else if ( _lflag  == 4.0 ) {
     if ( celltype  == 5.0 ) {
       derivtype = 2.0 ;
       }
     else if ( celltype  == 6.0 ) {
       b = 15.0 ;
       }
     else if ( celltype  == 7.0 ) {
       b = 10.0 ;
       }
     }
   } 
 NODEV(_pnt->node) = v;
 }

static void initmodel() {
  int _i; double _save;_ninits++;
{
 {
   u = 0.2 * vr ;
   derivtype = 2.0 ;
   net_send ( _tqitem, (double*)0, _ppvar[1]._pvoid, t +  0.0 , 1.0 ) ;
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

static double _nrn_current(double _v){double _current=0.;v=_v;{ {
   delta = t - t0 ;
   if ( celltype < 5.0 ) {
     u = u + delta * a * ( b * ( v - vr ) - u ) ;
     }
   else {
     if ( celltype  == 5.0 ) {
       if ( v < d ) {
         u = u + delta * a * ( 0.0 - u ) ;
         }
       else {
         u = u + delta * a * ( ( 0.025 * ( v - d ) * ( v - d ) * ( v - d ) ) - u ) ;
         }
       }
     if ( celltype  == 6.0 ) {
       if ( v > - 65.0 ) {
         b = 0.0 ;
         }
       else {
         b = 15.0 ;
         }
       u = u + delta * a * ( b * ( v - vr ) - u ) ;
       }
     if ( celltype  == 7.0 ) {
       if ( v > - 65.0 ) {
         b = 2.0 ;
         }
       else {
         b = 10.0 ;
         }
       u = u + delta * a * ( b * ( v - vr ) - u ) ;
       }
     }
   t0 = t ;
   i = - ( k * ( v - vr ) * ( v - vt ) - u + Iin ) / C / 1000.0 ;
   }
 _current += i;

} return _current;
}

static void nrn_cur(_NrnThread* _nt, _Memb_list* _ml, int _type){
Node *_nd; int* _ni; double _rhs, _v; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
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
 _g = _nrn_current(_v + .001);
 	{ _rhs = _nrn_current(_v);
 	}
 _g = (_g - _rhs)/.001;
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

static void nrn_jacob(_NrnThread* _nt, _Memb_list* _ml, int _type){
Node *_nd; int* _ni; int _iml, _cntml;
#if CACHEVEC
    _ni = _ml->_nodeindices;
#endif
_cntml = _ml->_nodecount;
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

static void nrn_state(_NrnThread* _nt, _Memb_list* _ml, int _type){

}

static void terminal(){}

static void _initlists() {
 int _i; static int _first = 1;
  if (!_first) return;
_first = 0;
}
