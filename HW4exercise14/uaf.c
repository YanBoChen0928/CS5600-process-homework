#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int *arr = malloc(10 * sizeof(int));  // allocate space for 10 integers
    arr[0] = 42;                          // assign a value
    free(arr);                            // free the allocated memory
    printf("%d\n", arr[0]);               // ❌ use after free
    return 0;
}
