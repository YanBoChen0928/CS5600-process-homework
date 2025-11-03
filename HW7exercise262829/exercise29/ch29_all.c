/* ============================================================
 * OSTEP Chapter 29: Lock-Based Concurrent Data Structures
 * Combined implementation for Q1 - Q6
 * Build: gcc -O2 -pthread -o ch29 ch29_all.c
 * ============================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <sys/time.h>
#include <stdint.h>
#include <assert.h>
#include <string.h>

// Common helpers ---------------------------------------------------------------
static inline uint64_t now_us(void) {
    struct timeval tv; gettimeofday(&tv, NULL);
    return (uint64_t)tv.tv_sec * 1000000ULL + (uint64_t)tv.tv_usec;
}
static inline double elapsed_ms(uint64_t a, uint64_t b){ return (double)(b-a)/1000.0; }

// ==============================================================================
//// ==== Q1: Timer Accuracy ====================================================
int run_q1(int samples){
    if(samples<=0) samples=100000;
    uint64_t min_delta=UINT64_MAX, zero=0, last=now_us();
    for(int i=0;i<samples;i++){
        uint64_t t=now_us();
        if(t==last){ zero++; continue; }
        if(t-last<min_delta) min_delta=t-last;
        last=t;
    }
    printf("[Q1] samples=%d zero=%llu min_nonzero_delta_us=%llu\n",
        samples,(unsigned long long)zero,(unsigned long long)(min_delta==UINT64_MAX?0:min_delta));
    return 0;
}

// ==============================================================================
//// ==== Q2: Simple Concurrent Counter (Single Lock) ===========================
typedef struct { int value; pthread_mutex_t lock; } counter_t;
void counter_init(counter_t *c){ c->value=0; pthread_mutex_init(&c->lock,NULL); }
void counter_inc(counter_t *c){ pthread_mutex_lock(&c->lock); c->value++; pthread_mutex_unlock(&c->lock); }
int counter_get(counter_t *c){ pthread_mutex_lock(&c->lock); int v=c->value; pthread_mutex_unlock(&c->lock); return v; }

typedef struct { counter_t *ctr; long iters; } q2_arg_t;
void* q2_worker(void *arg){ q2_arg_t *a=(q2_arg_t*)arg; for(long i=0;i<a->iters;i++) counter_inc(a->ctr); return NULL; }
int run_q2(int threads,long iters){
    counter_t c; counter_init(&c);
    pthread_t *t = (pthread_t*)malloc(sizeof(pthread_t)*threads);
    q2_arg_t *a = (q2_arg_t*)malloc(sizeof(q2_arg_t)*threads);
    uint64_t s=now_us();
    for(int i=0;i<threads;i++){ a[i]=(q2_arg_t){.ctr=&c,.iters=iters}; pthread_create(&t[i],NULL,q2_worker,&a[i]); }
    for(int i=0;i<threads;i++) pthread_join(t[i],NULL);
    uint64_t e=now_us();
    printf("[Q2] threads=%d total=%d time_ms=%.3f\n",threads,counter_get(&c),elapsed_ms(s,e));
    free(t); free(a);
    return 0;
}

// ==============================================================================
//// ==== Q3: Approximate Counter (Per-CPU + Global) ============================
#define MAXCPUS 128
typedef struct {
    int global; pthread_mutex_t glock;
    int local[MAXCPUS]; pthread_mutex_t llock[MAXCPUS];
    int threshold; int ncpu;
} approx_t;
void approx_init(approx_t *c,int th,int ncpu){ c->threshold=th; c->global=0; pthread_mutex_init(&c->glock,NULL); c->ncpu=ncpu>0?ncpu:4; for(int i=0;i<c->ncpu;i++){c->local[i]=0; pthread_mutex_init(&c->llock[i],NULL);} }
void approx_update(approx_t *c,int tid){int cpu=tid%c->ncpu;pthread_mutex_lock(&c->llock[cpu]);c->local[cpu]++;if(c->local[cpu]>=c->threshold){pthread_mutex_lock(&c->glock);c->global+=c->local[cpu];pthread_mutex_unlock(&c->glock);c->local[cpu]=0;}pthread_mutex_unlock(&c->llock[cpu]);}
int approx_get(approx_t *c){pthread_mutex_lock(&c->glock);int v=c->global;pthread_mutex_unlock(&c->glock);return v;}

typedef struct { approx_t *ctr; long iters; int tid; } q3_arg_t;
void* q3_worker(void *arg){ q3_arg_t *a=(q3_arg_t*)arg; for(long i=0;i<a->iters;i++) approx_update(a->ctr,a->tid); return NULL; }
int run_q3(int threads,long iters,int th){
    approx_t c; approx_init(&c,th,threads);
    pthread_t *t = (pthread_t*)malloc(sizeof(pthread_t)*threads);
    q3_arg_t *a = (q3_arg_t*)malloc(sizeof(q3_arg_t)*threads);
    uint64_t s=now_us();
    for(int i=0;i<threads;i++){a[i]=(q3_arg_t){.ctr=&c,.iters=iters,.tid=i}; pthread_create(&t[i],NULL,q3_worker,&a[i]);}
    for(int i=0;i<threads;i++) pthread_join(t[i],NULL);
    uint64_t e=now_us();
    printf("[Q3] threads=%d threshold=%d total=%d time_ms=%.3f\n",threads,th,approx_get(&c),elapsed_ms(s,e));
    free(t); free(a);
    return 0;
}

// ==============================================================================
//// ==== Q4: Linked List (Single Lock vs Hand-over-hand) =======================
typedef struct node { int key; struct node *next; pthread_mutex_t lock; } node_t;
typedef struct { node_t *head; pthread_mutex_t lock; int hoh; } list_t;
void list_init(list_t *L,int hoh){ L->head=NULL; pthread_mutex_init(&L->lock,NULL); L->hoh=hoh; }
int list_insert(list_t *L,int key){
    node_t *n=(node_t*)malloc(sizeof(node_t)); if(!n) return -1;
    n->key=key; n->next=NULL; pthread_mutex_init(&n->lock,NULL);
    if(!L->hoh){
        pthread_mutex_lock(&L->lock); n->next=L->head; L->head=n; pthread_mutex_unlock(&L->lock);
    } else {
        pthread_mutex_lock(&L->lock);
        if(L->head) pthread_mutex_lock(&L->head->lock);
        n->next=L->head; L->head=n;
        if(n->next) pthread_mutex_unlock(&n->next->lock);
        pthread_mutex_unlock(&L->lock);
    }
    return 0;
}
int list_lookup(list_t *L,int key){
    if(!L->hoh){
        int rv=-1; pthread_mutex_lock(&L->lock);
        for(node_t*c=L->head;c;c=c->next) if(c->key==key){rv=0;break;}
        pthread_mutex_unlock(&L->lock); return rv;
    } else {
        pthread_mutex_lock(&L->lock); node_t *c=L->head; if(c) pthread_mutex_lock(&c->lock); pthread_mutex_unlock(&L->lock);
        while(c){
            if(c->key==key){ pthread_mutex_unlock(&c->lock); return 0; }
            node_t*n=c->next; if(n) pthread_mutex_lock(&n->lock); pthread_mutex_unlock(&c->lock); c=n;
        }
        return -1;
    }
}
typedef struct { list_t *L; int *keys; long n; } q4_arg_t;
void* q4_worker(void*arg){ q4_arg_t*a=(q4_arg_t*)arg; for(long i=0;i<a->n;i++) list_lookup(a->L,a->keys[i]); return NULL; }
int run_q4(int threads,long ops){
    int N=threads*(int)ops; int *keys=(int*)malloc(sizeof(int)*N); for(int i=0;i<N;i++) keys[i]=i;
    list_t A,B; list_init(&A,0); list_init(&B,1);
    for(int i=0;i<N;i++){ list_insert(&A,keys[i]); list_insert(&B,keys[i]); }
    pthread_t *t = (pthread_t*)malloc(sizeof(pthread_t)*threads);
    q4_arg_t *a = (q4_arg_t*)malloc(sizeof(q4_arg_t)*threads);
    uint64_t s1=now_us();
    for(int i=0;i<threads;i++){ a[i]=(q4_arg_t){.L=&A,.keys=&keys[i*ops],.n=ops}; pthread_create(&t[i],NULL,q4_worker,&a[i]); }
    for(int i=0;i<threads;i++) pthread_join(t[i],NULL);
    uint64_t e1=now_us();
    uint64_t s2=now_us();
    for(int i=0;i<threads;i++){ a[i]=(q4_arg_t){.L=&B,.keys=&keys[i*ops],.n=ops}; pthread_create(&t[i],NULL,q4_worker,&a[i]); }
    for(int i=0;i<threads;i++) pthread_join(t[i],NULL);
    uint64_t e2=now_us();
    printf("[Q4] threads=%d ops_each=%ld single=%.3fms hoh=%.3fms\n",threads,ops,elapsed_ms(s1,e1),elapsed_ms(s2,e2));
    free(keys); free(t); free(a); return 0;
}

// ==============================================================================
//// ==== Q5 & Q6: Hash Table (Global Lock vs Per-bucket) =======================
typedef struct bucket { node_t *head; pthread_mutex_t lock; } bucket_t;
typedef struct { bucket_t *b; int nb; pthread_mutex_t glock; int per_bucket; } hash_t;
void hash_init(hash_t *H,int nb,int per){ H->nb=nb>0?nb:101; H->per_bucket=per; H->b=(bucket_t*)calloc(H->nb,sizeof(bucket_t)); for(int i=0;i<H->nb;i++) pthread_mutex_init(&H->b[i].lock,NULL); pthread_mutex_init(&H->glock,NULL); }
int hfunc(hash_t*H,int k){ return (k%H->nb+H->nb)%H->nb; }
void hash_insert(hash_t*H,int k){
    int b=hfunc(H,k); node_t*n=(node_t*)malloc(sizeof(node_t)); if(!n) return; n->key=k; pthread_mutex_init(&n->lock,NULL);
    if(!H->per_bucket){ pthread_mutex_lock(&H->glock); n->next=H->b[b].head; H->b[b].head=n; pthread_mutex_unlock(&H->glock); }
    else { pthread_mutex_lock(&H->b[b].lock); n->next=H->b[b].head; H->b[b].head=n; pthread_mutex_unlock(&H->b[b].lock); }
}
typedef struct { hash_t *H; int start; int n; } q56_arg_t;
void* q56_worker(void*arg){ q56_arg_t*a=(q56_arg_t*)arg; for(int i=0;i<a->n;i++) hash_insert(a->H,a->start+i); return NULL; }
int run_hash(int threads,int nops,int nb,int per){
    hash_t H; hash_init(&H,nb,per);
    pthread_t *t = (pthread_t*)malloc(sizeof(pthread_t)*threads);
    q56_arg_t *a = (q56_arg_t*)malloc(sizeof(q56_arg_t)*threads);
    uint64_t s=now_us();
    for(int i=0;i<threads;i++){ a[i]=(q56_arg_t){.H=&H,.start=i*nops,.n=nops}; pthread_create(&t[i],NULL,q56_worker,&a[i]); }
    for(int i=0;i<threads;i++) pthread_join(t[i],NULL);
    uint64_t e=now_us();
    printf("[%s] threads=%d ops_each=%d buckets=%d time_ms=%.3f\n", per? "Q6-per-bucket":"Q5-global", threads, nops, nb, elapsed_ms(s,e));
    free(t); free(a); return 0;
}

// ==============================================================================
//// ==== Main Dispatch =========================================================
static void usage(const char*p){
    printf("Usage: %s q1 [samples]\n"
           "       %s q2 <threads> <iters>\n"
           "       %s q3 <threads> <iters> <threshold>\n"
           "       %s q4 <threads> <ops>\n"
           "       %s q5 <threads> <ops> <buckets>\n"
           "       %s q6 <threads> <ops> <buckets>\n",p,p,p,p,p,p);
}
int main(int argc,char**argv){
    if(argc<2){ usage(argv[0]); return 1; }
    if(!strcmp(argv[1],"q1")){ return run_q1(argc>2?atoi(argv[2]):100000); }
    if(!strcmp(argv[1],"q2")){ if(argc<4){usage(argv[0]);return 1;} return run_q2(atoi(argv[2]),atol(argv[3])); }
    if(!strcmp(argv[1],"q3")){ if(argc<5){usage(argv[0]);return 1;} return run_q3(atoi(argv[2]),atol(argv[3]),atoi(argv[4])); }
    if(!strcmp(argv[1],"q4")){ if(argc<4){usage(argv[0]);return 1;} return run_q4(atoi(argv[2]),atol(argv[3])); }
    if(!strcmp(argv[1],"q5")){ if(argc<5){usage(argv[0]);return 1;} return run_hash(atoi(argv[2]),atoi(argv[3]),atoi(argv[4]),0); }
    if(!strcmp(argv[1],"q6")){ if(argc<5){usage(argv[0]);return 1;} return run_hash(atoi(argv[2]),atoi(argv[3]),atoi(argv[4]),1); }
    usage(argv[0]); return 1;
}
