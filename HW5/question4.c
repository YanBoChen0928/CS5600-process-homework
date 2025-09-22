#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    printf("Testing different exec() variants:\n\n");
    
    // Test execl()
    printf("1. Testing execl():\n");
    int pid1 = fork();
    if (pid1 == 0) {
        execl("/bin/ls", "ls", "-l", NULL);
    } else {
        wait(NULL);
    }
    
    printf("\n2. Testing execlp():\n");
    int pid2 = fork();
    if (pid2 == 0) {
        execlp("ls", "ls", "-l", NULL);  // No need for /bin
    } else {
        wait(NULL);
    }
    
    printf("\n3. Testing execv():\n");
    int pid3 = fork();
    if (pid3 == 0) {
        char *args[] = {"ls", "-l", NULL};
        execv("/bin/ls", args);
    } else {
        wait(NULL);
    }
    
    printf("\n4. Testing execvp():\n");
    int pid4 = fork();
    if (pid4 == 0) {
        char *args[] = {"ls", "-l", NULL};
        execvp("ls", args);  // No need for /bin
    } else {
        wait(NULL);
    }
    
    printf("\nAll exec() variants tested!\n");
    return 0;
}