// memory-user.c
// Allocate and continuously access a given amount of memory.

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: %s <memory_in_MB> [duration_in_seconds]\n", argv[0]);
        return 1;
    }

    int megabytes = atoi(argv[1]);
    int duration = (argc >= 3) ? atoi(argv[2]) : -1;  // -1 = run forever
    if (megabytes <= 0) {
        fprintf(stderr, "Error: memory size must be positive\n");
        return 1;
    }

    size_t bytes = (size_t)megabytes * 1024 * 1024;
    char *array = malloc(bytes);
    if (!array) {
        perror("malloc");
        return 1;
    }

    printf("Using %d MB of memory...\n", megabytes);

    int seconds = 0;
    while (1) {
        // Touch each byte to ensure physical allocation
        for (size_t i = 0; i < bytes; i++) {
            array[i] = (char)(i % 256);
        }

        sleep(1);
        seconds++;
        if (duration > 0 && seconds >= duration) break;
    }

    free(array);
    printf("Done. Freed %d MB.\n", megabytes);
    return 0;
}
