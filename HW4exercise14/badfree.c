#include <stdio.h>

int main(void) {
    int *ptr = NULL;     // create a pointer and set it to NULL
    *ptr = 42;           // try to write to that pointer (will crash)
    return 0;
}
