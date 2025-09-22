#include <stdio.h>
#include <sys/time.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/wait.h>

int main() {
    int pipe1[2], pipe2[2];  // Two pipes
    pid_t pid;
    struct timeval start, end;
    char byte = 1;
    int iterations = 10000;
    long time_diff;
    double time_per_switch;
    
    // Create two pipes
    if (pipe(pipe1) < 0 || pipe(pipe2) < 0) {
        perror("pipe");
        exit(1);
    }
    
    printf("Measuring context switch cost...\n");
    printf("Running %d context switch tests\n", iterations);
    
    pid = fork();
    if (pid < 0) {
        perror("fork");
        exit(1);
    }
    
    if (pid == 0) {
        // Child process
        for (int i = 0; i < iterations; i++) {
            read(pipe1[0], &byte, 1);   // Read from pipe1
            write(pipe2[1], &byte, 1);  // Write to pipe2
        }
        exit(0);
    } else {
        // Parent process
        // Start timing
        gettimeofday(&start, NULL);
        
        for (int i = 0; i < iterations; i++) {
            write(pipe1[1], &byte, 1);  // Write to pipe1
            read(pipe2[0], &byte, 1);   // Read from pipe2
        }
        
        // End timing
        gettimeofday(&end, NULL);
        
        // Wait for child process to finish
        wait(NULL);
        
        // Calculate time difference (in microseconds)
        time_diff = (end.tv_sec - start.tv_sec) * 1000000 + 
                    (end.tv_usec - start.tv_usec);
        
        // Each round trip = 2 context switches, so divide by 2
        time_per_switch = (double)time_diff / (iterations * 2);
        
        printf("Total time: %ld microseconds\n", time_diff);
        printf("Average time per context switch: %.2f microseconds\n", time_per_switch);
    }
    
    return 0;
}