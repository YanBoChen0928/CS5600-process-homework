#include <stdio.h>
#include <sys/time.h>
#include <unistd.h>
#include <stdlib.h>

int main() {
    struct timeval start, end;
    int iterations = 100000;  // Number of test iterations
    long time_diff;
    double time_per_call;
    
    printf("Measuring system call cost...\n");
    printf("Running %d read() system calls\n", iterations);
    
    // Start timing
    gettimeofday(&start, NULL);
    
    // Execute many system calls
    for (int i = 0; i < iterations; i++) {
        read(0, NULL, 0);  // 0-byte read system call
    }
    
    // End timing
    gettimeofday(&end, NULL);
    
    // Calculate time difference (in microseconds)
    time_diff = (end.tv_sec - start.tv_sec) * 1000000 + 
                (end.tv_usec - start.tv_usec);
    
    // Calculate average time per system call
    time_per_call = (double)time_diff / iterations;
    
    printf("Total time: %ld microseconds\n", time_diff);
    printf("Average time per system call: %.2f microseconds\n", time_per_call);
    
    return 0;
}