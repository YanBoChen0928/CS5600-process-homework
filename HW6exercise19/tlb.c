#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <unistd.h>
#include <sched.h>

// Pin current thread to a specific CPU core (Linux)
void pin_to_core(int core_id) {
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(core_id, &set);
    if (sched_setaffinity(0, sizeof(set), &set) == -1) {
        perror("sched_setaffinity failed");
    }
}

int main(int argc, char *argv[]) {
    // Pin to core 0 immediately
    pin_to_core(0);
    
    // Check arguments
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <num_pages> <num_trials>\n", argv[0]);
        return 1;
    }
    
    int NUMPAGES = atoi(argv[1]);
    int trials = atoi(argv[2]);
    int PAGESIZE = getpagesize();  // Typically 4096 bytes
    
    // Allocate array
    int jump = PAGESIZE / sizeof(int);  // Number of ints per page
    int array_size = NUMPAGES * jump;
    int *a = (int *)malloc(array_size * sizeof(int));
    
    if (a == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }
    
    // Initialize array to avoid demand zeroing overhead
    for (int i = 0; i < array_size; i += jump) {
        a[i] = 0;
    }
    
    struct timeval start, end;
    
    // Start timing
    gettimeofday(&start, NULL);
    
    // Main measurement loop
    for (int t = 0; t < trials; t++) {
        for (int i = 0; i < NUMPAGES * jump; i += jump) {
            a[i] += 1;  // Access one int per page
        }
    }
    
    // End timing
    gettimeofday(&end, NULL);
    
    // Calculate elapsed time in microseconds
    long elapsed_usec = (end.tv_sec - start.tv_sec) * 1000000L + 
                        (end.tv_usec - start.tv_usec);
    
    // Convert to nanoseconds per access (use double to avoid overflow)
    double total_accesses = (double)trials * (double)NUMPAGES;
    double ns_per_access = (elapsed_usec * 1000.0) / total_accesses;
    
    printf("%d %.2f\n", NUMPAGES, ns_per_access);
    
    free(a);
    return 0;
}
