#include <stdlib.h>

int main(void) {
    int *arr = malloc(100 * sizeof(int));  // allocate 100 integers
    free(arr + 50);                        // ❌ invalid free: not the original pointer
    free(arr);                             // even this may crash afterward
    return 0;
}
