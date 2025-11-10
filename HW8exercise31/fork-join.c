#include <stdio.h>
#include <unistd.h>
#include <pthread.h>
#include "common_threads.h"

sem_t s; 

void *child(void *arg) {
    printf("child\n");
    sleep(1);         // Add sleep(1) to ensure it is working
    Sem_post(&s);     // Signal parent: child is done
    return NULL;
}

int main(int argc, char *argv[]) {
    pthread_t p;
    printf("parent: begin\n");
    Sem_init(&s, 0);                      // Initialize semaphore to 0
    Pthread_create(&p, NULL, child, NULL);
    Sem_wait(&s);                         // Wait for child to finish
    printf("parent: end\n");
    return 0;
}

