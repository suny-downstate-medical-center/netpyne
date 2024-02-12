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
typedef	unsigned char	ui1;	/* one byte unsigned integer */
typedef	char		si1;	/* one byte signed integer */
typedef unsigned short	ui2;	/* two byte unsigned integer */
typedef short		si2;	/* two byte signed integer */
typedef unsigned int	ui4;	/* four byte unsigned integer */ 
typedef int		si4;	/* four byte signed integer */ 
typedef float		sf4;	/* four byte signed floating point number */ 
typedef double		sf8;	/* eight byte signed floating point number */ 

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
