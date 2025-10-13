#include <stdlib.h>

int main(void) {
    int *data = malloc(100 * sizeof(int));  // allocate space for 100 integers
    data[100] = 0;                          // ❌ invalid index: should be 0–99
    free(data);
    return 0;
}
