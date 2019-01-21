: $Id: misc.mod,v 1.24 2011/10/14 15:00:26 samn Exp $

COMMENT
Misc. routines:
sassign() // assign a string from system
dassign()// assign a double
nokill() // chatch SIGHUP
prtime() // gives date/time
fspitchar(c,file) // sends single char to a file
spitchar(c)       // sends single char to stdout: eg c=1 => ^A
file_exist(file) // returns 1 if filename exists
hocgetc(file) // get single char from a file

  Note that with a SUFFIX equal to "nothing" these functions do not
have a suffix in hoc.  Thus to call sassign() in hoc use simply type
"sassign()" <- without the quotes.

    file_exist(filename)
        - returns 1 if filename exists

    sassign()  (string assign, written by Bill Lytton)
        - This routine is used to set a string in Hoc to something that has
          been returned by a system call.  sassign("name","shell_call ...")
          will produce a file called "sassign" in the cwd that will contain
          a hoc call that sets string 'name' to the result of shell_call 
          which should be a string.
        
    dassign()  (double assign, written and used by Bill Lytton)
        - This routine is used to set a variable in Hoc to something that has
          been returned by a system call.  sassign("name","shell_call ...")
          will produce a file called "dassign" in the cwd that will contain
          a hoc call that sets variable 'name' to the result of shell_call 
          which should be a number.

ENDCOMMENT
                           
INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
    SUFFIX nothing
}

VERBATIM
#include <unistd.h>     /* F_OK     */
#include <errno.h>      /* errno    */
#include <signal.h>
#include <sys/types.h>         /* MUST REMEMBER THIS */
#include <time.h>
#include <stdio.h>
#include <limits.h>
extern int hoc_is_tempobj(int narg);
ENDVERBATIM

:* FUNCTION file_exist()
FUNCTION file_exist() {
VERBATIM
    /* Returns TRUE if file exists, if file not exist the need to reset
       errno else will get a nrnoc error.  Seems to be a problem even
       if I don't include <errno.h> */

    char *gargstr(), *filename;

    filename = gargstr(1);

    if (*filename && !access(filename, F_OK)) {
        _lfile_exist = 1;

    } else {
        /* Errno set to 2 when file not found */
        errno = 0;

        _lfile_exist = 0;
    }
ENDVERBATIM
}

FUNCTION istmpobj () {
VERBATIM
  _listmpobj=hoc_is_tempobj_arg(1);
ENDVERBATIM  
}

:* PROCEDURE sassign()
FUNCTION sassign() {
VERBATIM
    FILE *pipein;
    char string[BUFSIZ], **strname, *syscall;
    char** hoc_pgargstr();

    strname = hoc_pgargstr(1);
    syscall = gargstr(2);

    if( !(pipein = popen(syscall, "r"))) {
        fprintf(stderr,"System call failed\n");
        return 0; 
    }
    
    if (fgets(string,BUFSIZ,pipein) == NULL) {
        fprintf(stderr,"System call did not return a string\n");
        pclose(pipein); return 0;
    }

    /*  assign_hoc_str(strname, string, 0); */
    hoc_assign_str(strname, string);

    pclose(pipein);
    errno = 0;
    return 0;
ENDVERBATIM
}

:* PROCEDURE dassign() 
FUNCTION dassign() {
VERBATIM
    FILE *pipein, *outfile;
    char *strname, *syscall;
    double num;

    strname = gargstr(1);
    syscall = gargstr(2);

    if ( !(outfile = fopen("dassign","w"))) {
        fprintf(stderr,"Can't open output file dassign\n");
        return 0; 
    }

    if( !(pipein = popen(syscall, "r"))) {
        fprintf(stderr,"System call failed\n");
        fclose(outfile); return 0; 
    }
    
    if (fscanf(pipein,"%lf",&num) != 1) {
        fprintf(stderr,"System call did not return a number\n");
        fclose(outfile); pclose(pipein); return 0; 
    }

    fprintf(outfile,"%s=%g\n",strname,num);
    fprintf(outfile,"system(\"rm dassign\")\n");

    fclose(outfile); pclose(pipein);
    errno = 0;
    return 0;
ENDVERBATIM
}

:* PROCEDURE nokill() 
: nohup
PROCEDURE nokill() {
VERBATIM
  signal(SIGHUP, SIG_IGN);
ENDVERBATIM
}

:* FUNCTION prtime()
FUNCTION prtime () {
VERBATIM
_lprtime = clock();
ENDVERBATIM
}

:* FUNCTION now ()
FUNCTION now () {
VERBATIM
  _lnow = time((time_t*)0);
  _lnow -= (12784) * 24*60*60; // time from the Epoch to 01/01/05
ENDVERBATIM
}

:* FUNCTION sleepfor (seconds[,nanoseconds])
: returns 0 on success, -1 on failure, nanosecond arg should be < 1 second
FUNCTION sleepfor (sec) {
VERBATIM
  struct timespec ts;
  ts.tv_sec = (time_t)_lsec;
  ts.tv_nsec = ifarg(2)?(long)*getarg(2):(long)0;
  return (double) nanosleep(&ts,(struct timespec*)0);
ENDVERBATIM
}

:* PROCEDURE spitchar
PROCEDURE spitchar(c) {
VERBATIM
{	
  printf("%c", (int)_lc);
}
ENDVERBATIM
}

:* PROCEDURE spitchar
VERBATIM
static char *pmlc;
ENDVERBATIM

PROCEDURE mymalloc(sz) {
VERBATIM
{ 
  size_t x,y;
  x=(size_t)_lsz;
  pmlc=(char *)malloc(x);
  printf("Did %ld: %x\n",x,pmlc);
  y=(unsigned int)_lsz-1;
  pmlc[y]=(char)97;
  printf("WRITE/READ 'a': "); 
  printf("%c\n",pmlc[y]);
  if (ifarg(2)) free(pmlc); else printf("Use unmalloc() to free memory\n");
}
ENDVERBATIM
}

PROCEDURE unmalloc() {
VERBATIM
  free(pmlc);
ENDVERBATIM
}

:* FUNCTION hocgetc
FUNCTION hocgetc() {
VERBATIM
{	
  FILE* f, *hoc_obj_file_arg();
  f = hoc_obj_file_arg(1);
  _lhocgetc = (double)getc(f);
}
ENDVERBATIM
}

PROCEDURE pwd() {
  VERBATIM
  {char cwd[1000],cmd[1200];
  getcwd(cwd, 1000);
  sprintf(cmd, "execute1(\"strdef cwd\")\n");         hoc_oc(cmd);
  sprintf(cmd, "execute1(\"cwd=\\\"%s\\\"\")\n",cwd); hoc_oc(cmd);
  }
  ENDVERBATIM
}
