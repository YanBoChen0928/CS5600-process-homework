#include <stdlib.h>

int main(void) {
    int *x = malloc(100 * sizeof(int));  // allocate 100 integers
    (void)x;                             // silence unused-variable warning
    return 0;                            // forget to free(x)
}
