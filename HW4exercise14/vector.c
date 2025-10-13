#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int *data;      // pointer to the array
    int size;       // current number of elements
    int capacity;   // total allocated capacity
} Vector;

// initialize the vector
void init(Vector *v) {
    v->size = 0;
    v->capacity = 2;
    v->data = malloc(v->capacity * sizeof(int));
}

// add an element (auto expand if full)
void push(Vector *v, int value) {
    if (v->size == v->capacity) {
        v->capacity *= 2;
        v->data = realloc(v->data, v->capacity * sizeof(int));
    }
    v->data[v->size++] = value;
}

// free the memory
void destroy(Vector *v) {
    free(v->data);
    v->data = NULL;
    v->size = 0;
    v->capacity = 0;
}

int main(void) {
    Vector v;
    init(&v);

    for (int i = 0; i < 10; i++) {
        push(&v, i * 10);
    }

    for (int i = 0; i < v.size; i++) {
        printf("%d ", v.data[i]);
    }
    printf("\n");

    destroy(&v);
    return 0;
}
