#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    // Print initial message
    printf("About to fork and exec\n");
    
    int pid = fork();
    
    if (pid < 0) {
        // Fork failed
        fprintf(stderr, "Fork failed\n");
        exit(1);
    } else if (pid == 0) {
        // Child process - execute ls command
        execl("/bin/ls", "ls", "-l", NULL);
        printf("This shouldn't print if exec succeeds\n");
    } else {
        // Parent process - wait for child to complete
        wait(NULL);
        printf("Child finished executing ls\n");
    }
    
    return 0;
}