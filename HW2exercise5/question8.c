#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    int pipefd[2];
    pid_t pid1, pid2;
    
    // Create a pipe
    if (pipe(pipefd) == -1) {
        perror("pipe");
        exit(EXIT_FAILURE);
    }
    
    // First child process: ls
    pid1 = fork();
    if (pid1 == 0) {
        // Child 1: redirect stdout to pipe write end
        dup2(pipefd[1], STDOUT_FILENO);
        close(pipefd[0]); // Don't need read end
        close(pipefd[1]); // Already dup2'd, can close
        execlp("ls", "ls", NULL);
        perror("execlp ls");
        exit(EXIT_FAILURE);
    }
    
    // Second child process: grep txt
    pid2 = fork();
    if (pid2 == 0) {
        // Child 2: redirect stdin to pipe read end
        dup2(pipefd[0], STDIN_FILENO);
        close(pipefd[1]); // Don't need write end
        close(pipefd[0]); // Already dup2'd, can close
        execlp("grep", "grep", "txt", NULL);
        perror("execlp grep");
        exit(EXIT_FAILURE);
    }
    
    // Parent process: close pipe, wait for children to finish
    close(pipefd[0]);
    close(pipefd[1]);
    waitpid(pid1, NULL, 0);
    waitpid(pid2, NULL, 0);
    
    return 0;
}