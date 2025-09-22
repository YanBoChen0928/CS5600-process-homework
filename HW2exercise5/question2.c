#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <sys/wait.h>

int main() {
    // Open file before fork
    int fd = open("test_file.txt", O_CREAT | O_WRONLY | O_TRUNC, 0644);
    
    int pid = fork();
    
    if (pid == 0) {
        // Child process
        char child_msg[] = "Child writes this\n";
        write(fd, child_msg, strlen(child_msg));
    } else {
        // Parent process
        char parent_msg[] = "Parent writes this\n";
        write(fd, parent_msg, strlen(parent_msg));
        wait(NULL);
    }
    
    close(fd);
    return 0;
}