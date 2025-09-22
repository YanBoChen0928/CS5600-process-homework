#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    printf("Before fork\n");
    
    int pid = fork();
    
    if (pid == 0) {
        // Child process
        printf("Child: before closing stdout\n");
        
        close(STDOUT_FILENO);  // Close standard output
        
        printf("Child: after closing stdout - can you see this?\n");
        
    } else {
        // Parent process
        wait(NULL);
        printf("Parent: child finished\n");
    }
    
    return 0;
}