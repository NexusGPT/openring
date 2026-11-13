#include <stdio.h>
#include <string.h>
#include <ring_iphone/ripl.h>
static size_t answer(uint8_t *o, uint32_t uid, const char *app, const char *title, const char *msg, uint16_t ml, const char *date){
 size_t n=0; const char *s[4]={app,title,msg,date}; static const uint8_t ids[4]={0,1,3,5};
 o[n++]=0; for(int k=0;k<4;k++) o[n++]=(uid>>(8*k))&255;
 for(int i=0;i<4;i++){uint16_t l=(i==2)?ml:strlen(s[i]); o[n++]=ids[i]; o[n++]=l&255; o[n++]=l>>8; memcpy(&o[n],s[i],l); n+=l;} return n;}
int main(){ uint8_t st[40],good[100],all[200]; struct ripl_ds d;
 size_t ns=answer(st,7,"","","",0,""); size_t ng=answer(good,0,"good.app","Good","good message",12,"20261111T220546");
 memcpy(all,st,ns); memcpy(all+ns,good,ng); ripl_ds_start(&d,0);
 int r=ripl_ds_feed(&d,all,ns+ng); printf("r=%d state=%d msg='%s' title='%s'\n",r,d.state,d.msg,d.title); return 0;}
