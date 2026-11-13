#include <stdio.h>
#include <string.h>
#include <ring_iphone/ripl.h>
static size_t answer(uint8_t *o, uint32_t uid, const char *app, const char *title, const char *msg, uint16_t ml, const char *date){
 size_t n=0; const char *s[4]={app,title,msg,date}; static const uint8_t ids[4]={0,1,3,5};
 o[n++]=0; for(int k=0;k<4;k++) o[n++]=(uid>>(8*k))&255;
 for(int i=0;i<4;i++){uint16_t l=(i==2)?ml:strlen(s[i]); o[n++]=ids[i]; o[n++]=l&255; o[n++]=l>>8; memcpy(&o[n],s[i],l); n+=l;} return n;}
int main(){ uint8_t st2[40], good[200], all[400]; struct ripl_ds d;
 size_t m=answer(st2,7,"","","",0,""); size_t ng=answer(good,5,"good.app","Good","good message",12,"20261111T220546");
 memcpy(all,st2,m); memcpy(all+m,good,ng); ripl_ds_start(&d,5);
 for(size_t k=0;k<m+ng;k++){ int rr=ripl_ds_feed(&d,all+k,1); if(0)printf("byte %zu=%02x -> state %d attr %d hdr_n %d rr=%d\n",k,all[k],d.state,d.attr,d.hdr_n,rr); if(rr<0)break;} int r=0; printf("m=%zu ng=%zu r=%d state=%d msg='%s'\n",m,ng,r,d.state,d.msg); return 0;}
