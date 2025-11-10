#include <stdio.h>
#include <pthread.h>
#include <semaphore.h>
#include "common_threads.h"

typedef struct _rwlock_t {
    sem_t writelock;   // Writer's exclusive lock
    sem_t lock;        // Protect readers counter
    int readers;       // Number of active readers
} rwlock_t;

void rwlock_init(rwlock_t *rw) {
    rw->readers = 0;
    Sem_init(&rw->lock, 1);       // Mutex for readers
    Sem_init(&rw->writelock, 1);  // Binary semaphore for writer
}

void rwlock_acquire_readlock(rwlock_t *rw) {
    Sem_wait(&rw->lock);
    rw->readers++;
    if (rw->readers == 1) {  // First reader
        Sem_wait(&rw->writelock);  // Block writers
    }
    Sem_post(&rw->lock);
}

void rwlock_release_readlock(rwlock_t *rw) {
    Sem_wait(&rw->lock);
    rw->readers--;
    if (rw->readers == 0) {  // Last reader
        Sem_post(&rw->writelock);  // Allow writers
    }
    Sem_post(&rw->lock);
}

void rwlock_acquire_writelock(rwlock_t *rw) {
    Sem_wait(&rw->writelock);  // Exclusive access
}

void rwlock_release_writelock(rwlock_t *rw) {
    Sem_post(&rw->writelock);
}

// Test code
rwlock_t rwlock;
int shared_data = 0;

void *reader(void *arg) {
    int id = *(int *)arg;
    for (int i = 0; i < 3; i++) {
        rwlock_acquire_readlock(&rwlock);
        printf("Reader %d: read %d\n", id, shared_data);
        sleep(1);
        rwlock_release_readlock(&rwlock);
    }
    return NULL;
}

void *writer(void *arg) {
    int id = *(int *)arg;
    for (int i = 0; i < 2; i++) {
        rwlock_acquire_writelock(&rwlock);
        shared_data++;
        printf("Writer %d: wrote %d\n", id, shared_data);
        sleep(2);
        rwlock_release_writelock(&rwlock);
    }
    return NULL;
}

int main() {
    pthread_t readers[3], writers[2];
    int ids[5] = {0, 1, 2, 3, 4};
    
    rwlock_init(&rwlock);
    
    for (int i = 0; i < 3; i++)
        Pthread_create(&readers[i], NULL, reader, &ids[i]);
    for (int i = 0; i < 2; i++)
        Pthread_create(&writers[i], NULL, writer, &ids[i+3]);
    
    for (int i = 0; i < 3; i++)
        Pthread_join(readers[i], NULL);
    for (int i = 0; i < 2; i++)
        Pthread_join(writers[i], NULL);
    
    return 0;
}