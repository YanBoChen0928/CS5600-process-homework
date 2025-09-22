#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    printf("Before fork\n");
    
    int pid = fork();
    
    if (pid == 0) {
        // Child process
        printf("Child: I'm running\n");
        sleep(2);  // Child takes some time
        printf("Child: I'm done\n");
        
        // Test wait() in child
        int child_wait_result = wait(NULL);
        printf("Child: wait() returned %d\n", child_wait_result);
        
    } else {
        // Parent process
        printf("Parent: waiting for child\n");
        // int wait_result = wait(NULL); // for question 5
        int wait_result = waitpid(pid, NULL, 0); // for question 6
        printf("Parent: wait() returned %d\n", wait_result);
        printf("Parent: child finished\n");
    }
    
    return 0;
}