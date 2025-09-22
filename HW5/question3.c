#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main() {
    int pid = fork();
    
    if (pid == 0) {
        // Child process
        printf("hello\n");
    } else {
        // Parent process  
        sleep(1);  // Let Parent wait for 1 second to ensure Child runs first (but not real wait)
        printf("goodbye\n");
    }
    
    return 0;
}