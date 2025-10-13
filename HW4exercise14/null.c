#include <stdio.h>

int main(void) {
    int *ptr = NULL;
    *ptr = 42;   // This line will cause a segmentation fault
    return 0;
}
