#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include "common_threads.h"

// TODO: Declare two semaphores
sem_t sem_a;  // Thread A signals "I'm here"
sem_t sem_b;  // Thread B signals "I'm here"

void *thread_a(void *arg) {
    printf("Thread A: doing work before rendezvous\n");
    
    // TODO: Signal that A has arrived
    Sem_post(&sem_a);
    
    // TODO: Wait for B to arrive
    Sem_wait(&sem_b);
    
    printf("Thread A: continuing after rendezvous\n");
    return NULL;
}

void *thread_b(void *arg) {
    printf("Thread B: doing work before rendezvous\n");
    
    // TODO: Signal that B has arrived
    Sem_post(&sem_b);
    
    // TODO: Wait for A to arrive  
    Sem_wait(&sem_a);
    
    printf("Thread B: continuing after rendezvous\n");
    return NULL;
}

int main() {
    pthread_t a, b;
    
    // TODO: Initialize both semaphores to 0
    Sem_init(&sem_a, 0);
    Sem_init(&sem_b, 0);
    
    Pthread_create(&a, NULL, thread_a, NULL);
    Pthread_create(&b, NULL, thread_b, NULL);
    
    Pthread_join(a, NULL);
    Pthread_join(b, NULL);
    
    printf("Both threads completed!\n");
    return 0;
}