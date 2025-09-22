#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    int x = 100;
    
    printf("Before fork: x = %d (PID: %d)\n", x, getpid());
    
    int pid = fork();
    
    if (pid < 0) {
        fprintf(stderr, "Fork failed\n");
        exit(1);
    } else if (pid == 0) {
        // Child process
        printf("Child initial: x = %d (PID: %d)\n", x, getpid());
        x = 200;
        printf("Child changed: x = %d (PID: %d)\n", x, getpid());
    } else {
        // Parent process
        wait(NULL);
        printf("Parent initial: x = %d (PID: %d)\n", x, getpid());
        x = 300;
        printf("Parent changed: x = %d (PID: %d)\n", x, getpid());
    }
    
    return 0;
}