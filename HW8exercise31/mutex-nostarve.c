#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <semaphore.h>
#include "common_threads.h"

#define MAX_THREADS 10

typedef struct __ns_mutex_t {
    sem_t room;           // Control entry to queueing room
    sem_t mutex;          // Protect shared variables
    sem_t queue[MAX_THREADS];  // One semaphore per thread position
    int ticket;           // Next ticket number
    int turn;             // Current turn number
} ns_mutex_t;

void ns_mutex_init(ns_mutex_t *m) {
    Sem_init(&m->room, 1);   // One thread at a time in room
    Sem_init(&m->mutex, 1);  // Protect ticket/turn
    for (int i = 0; i < MAX_THREADS; i++) {
        Sem_init(&m->queue[i], 0);  // All waiting initially
    }
    m->ticket = 0;
    m->turn = 0;
    Sem_post(&m->queue[0]);  // First thread can enter
}

void ns_mutex_acquire(ns_mutex_t *m) {
    Sem_wait(&m->room);      // Enter queueing room
    Sem_wait(&m->mutex);
    int my_ticket = m->ticket++;  // Get ticket number
    Sem_post(&m->mutex);
    
    Sem_wait(&m->queue[my_ticket % MAX_THREADS]);  // Wait for my turn
    Sem_post(&m->room);      // Leave queueing room
}

void ns_mutex_release(ns_mutex_t *m) {
    Sem_wait(&m->mutex);
    m->turn++;               // Next turn
    Sem_post(&m->queue[m->turn % MAX_THREADS]);  // Wake next thread
    Sem_post(&m->mutex);
}

ns_mutex_t lock;
int counter = 0;

void *worker(void *arg) {
    int id = *(int *)arg;
    for (int i = 0; i < 3; i++) {
        ns_mutex_acquire(&lock);
        printf("Thread %d: acquired lock (counter=%d)\n", id, counter);
        counter++;
        sleep(1);  // Simulate work
        printf("Thread %d: releasing lock (counter=%d)\n", id, counter);
        ns_mutex_release(&lock);
    }
    return NULL;
}

int main(int argc, char *argv[]) {
    printf("parent: begin\n");
    
    ns_mutex_init(&lock);
    
    pthread_t threads[5];
    int ids[5];
    
    for (int i = 0; i < 5; i++) {
        ids[i] = i;
        Pthread_create(&threads[i], NULL, worker, &ids[i]);
    }
    
    for (int i = 0; i < 5; i++) {
        Pthread_join(threads[i], NULL);
    }
    
    printf("parent: end (final counter=%d)\n", counter);
    return 0;
}

