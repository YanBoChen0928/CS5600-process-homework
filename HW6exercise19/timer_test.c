#include <stdio.h>
#include <sys/time.h>

int main() {
    struct timeval start, end;
    long elapsed_usec;
    int samples = 100;
    long min_diff = 1000000;  // Start with 1 second
    
    printf("Testing gettimeofday() precision...\n\n");
    
    // Test 1: Measure minimum detectable time
    for (int i = 0; i < samples; i++) {
        gettimeofday(&start, NULL);
        gettimeofday(&end, NULL);
        
        elapsed_usec = (end.tv_sec - start.tv_sec) * 1000000L + 
                       (end.tv_usec - start.tv_usec);
        
        if (elapsed_usec > 0 && elapsed_usec < min_diff) {
            min_diff = elapsed_usec;
        }
    }
    
    printf("Minimum detectable time: %ld microseconds\n", min_diff);
    printf("This is approximately: %ld nanoseconds\n\n", min_diff * 1000);
    
    // Test 2: How many iterations needed for reliable measurement
    printf("For TLB measurement (5-70 ns per access):\n");
    long target_time_us = 10000;  // Target: 10ms for reliable measurement
    long single_access_ns = 50;   // Assume ~50ns average
    
    long iterations = (target_time_us * 1000) / single_access_ns;
    printf("Recommended iterations: %ld\n", iterations);
    printf("This gives ~%.1f ms total time\n", (iterations * single_access_ns) / 1000000.0);
    
    return 0;
}