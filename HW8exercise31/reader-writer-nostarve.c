#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "common_threads.h"

//
// Your code goes in the structure and functions below
//

typedef struct __rwlock_t {
    sem_t readEntry;   // Control reader entry (prevent new readers when writer waits)
    sem_t writelock;   // Writer's exclusive lock
    sem_t lock;        // Protect readers counter
    int readers;       // Number of active readers
} rwlock_t;


void rwlock_init(rwlock_t *rw) {
    rw->readers = 0;
    Sem_init(&rw->readEntry, 1);  // Entry gate open
    Sem_init(&rw->lock, 1);       // Mutex for readers counter
    Sem_init(&rw->writelock, 1);  // Binary semaphore for writer
}

void rwlock_acquire_readlock(rwlock_t *rw) {
    Sem_wait(&rw->readEntry);  // Pass through entry (may be blocked by writer)
    Sem_wait(&rw->lock);
    rw->readers++;
    if (rw->readers == 1) {    // First reader
        Sem_wait(&rw->writelock);  // Block writers
    }
    Sem_post(&rw->lock);
    Sem_post(&rw->readEntry);  // Leave entry gate
}

void rwlock_release_readlock(rwlock_t *rw) {
    Sem_wait(&rw->lock);
    rw->readers--;
    if (rw->readers == 0) {    // Last reader
        Sem_post(&rw->writelock);  // Allow writer
    }
    Sem_post(&rw->lock);
}

void rwlock_acquire_writelock(rwlock_t *rw) {
    Sem_wait(&rw->readEntry);    // Close entry gate (block new readers)
    Sem_wait(&rw->writelock);    // Wait for existing readers to finish
    Sem_post(&rw->readEntry);    // Reopen gate (we have writelock now)
}

void rwlock_release_writelock(rwlock_t *rw) {
    Sem_post(&rw->writelock);  // Release write lock
}

//
// Don't change the code below (just use it!)
// 

int loops;
int value = 0;

rwlock_t lock;

void *reader(void *arg) {
    int i;
    for (i = 0; i < loops; i++) {
	rwlock_acquire_readlock(&lock);
	printf("read %d\n", value);
	rwlock_release_readlock(&lock);
    }
    return NULL;
}

void *writer(void *arg) {
    int i;
    for (i = 0; i < loops; i++) {
	rwlock_acquire_writelock(&lock);
	value++;
	printf("write %d\n", value);
	rwlock_release_writelock(&lock);
    }
    return NULL;
}

int main(int argc, char *argv[]) {
    assert(argc == 4);
    int num_readers = atoi(argv[1]);
    int num_writers = atoi(argv[2]);
    loops = atoi(argv[3]);

    pthread_t pr[num_readers], pw[num_writers];

    rwlock_init(&lock);

    printf("begin\n");

    int i;
    for (i = 0; i < num_readers; i++)
	Pthread_create(&pr[i], NULL, reader, NULL);
    for (i = 0; i < num_writers; i++)
	Pthread_create(&pw[i], NULL, writer, NULL);

    for (i = 0; i < num_readers; i++)
	Pthread_join(pr[i], NULL);
    for (i = 0; i < num_writers; i++)
	Pthread_join(pw[i], NULL);

    printf("end: value %d\n", value);

    return 0;
}

