// 1. UNINITIALIZED READ
// Reading from memory that was allocated but never initialized
#include <stdio.h>
#include <stdlib.h>

void uninitialized_read() {
    printf("=== 1. UNINITIALIZED READ ===\n");
    int *ptr = (int *)malloc(sizeof(int));
    // BUG: Never initialized the memory, but trying to read from it
    printf("Uninitialized value: %d\n", *ptr);  // Undefined behavior
    free(ptr);
}

// 2. MEMORY LEAK
// Allocating memory but forgetting to free it
void memory_leak() {
    printf("=== 2. MEMORY LEAK ===\n");
    for (int i = 0; i < 100; i++) {
        int *ptr = (int *)malloc(sizeof(int));
        *ptr = i;
        // BUG: Never calling free(ptr) - memory is leaked
        printf("Allocated memory for value: %d\n", *ptr);
    }
    // All 100 allocations are leaked!
}

// 3. DOUBLE FREE
// Calling free() twice on the same pointer
void double_free() {
    printf("=== 3. DOUBLE FREE ===\n");
    int *ptr = (int *)malloc(sizeof(int));
    *ptr = 42;
    printf("Value: %d\n", *ptr);
    
    free(ptr);  // First free - OK
    // BUG: Calling free again on the same pointer
    free(ptr);  // Second free - UNDEFINED BEHAVIOR
}

// 4. DANGLING POINTER
// Using a pointer after the memory it points to has been freed
void dangling_pointer() {
    printf("=== 4. DANGLING POINTER ===\n");
    int *ptr = (int *)malloc(sizeof(int));
    *ptr = 100;
    printf("Before free: %d\n", *ptr);
    
    free(ptr);  // Memory is freed
    
    // BUG: Using pointer after freeing the memory it points to
    printf("After free (dangling pointer): %d\n", *ptr);  // Undefined behavior
    *ptr = 200;  // Even worse - writing to freed memory!
}

// 5. INVALID FREE
// Calling free() on a pointer that wasn't returned by malloc
void invalid_free() {
    printf("=== 5. INVALID FREE ===\n");
    int *ptr = (int *)malloc(10 * sizeof(int));
    int *middle = ptr + 5;  // Pointer to middle of allocated array
    
    // BUG: Trying to free a pointer that wasn't returned by malloc
    free(middle);  // INVALID - can only free what malloc returned
    free(ptr);     // This would be correct, but may crash after invalid free
}

// 6. BONUS MEMORY ERRORS
void bonus_memory_errors() {
    printf("=== 6. BONUS MEMORY ERRORS ===\n");
    
    // Buffer overflow - writing past allocated memory
    char *str = (char *)malloc(5);
    strcpy(str, "Hello World!");  // BUG: String is longer than allocated space
    printf("Buffer overflow string: %s\n", str);
    
    // Forgetting to allocate memory
    char *dst;  // BUG: Never allocated memory for dst
    char *src = "Hello";
    // strcpy(dst, src);  // Would cause segmentation fault
    
    // Using wrong size in allocation
    char *wrong_size = (char *)malloc(strlen("Hello"));  // BUG: Forgot +1 for null terminator
    strcpy(wrong_size, "Hello");  // Overwrites one byte past allocation
    
    free(str);
    free(wrong_size);
}

int main() {
    printf("Demonstrating Common Memory Errors\n");
    printf("===================================\n\n");
    
    // WARNING: These functions contain intentional bugs!
    // Some may crash your program or produce undefined behavior
    
    uninitialized_read();
    printf("\n");
    
    memory_leak();
    printf("\n");
    
    // CAREFUL: The following may crash your program
    // Uncomment one at a time to test with valgrind
    
    // double_free();
    // dangling_pointer();
    // invalid_free();
    // bonus_memory_errors();
    
    return 0;
}

/*
COMPILATION AND TESTING:
========================

1. Compile with debugging info:
   gcc -g -o memory_errors memory_errors.c

2. Run with valgrind to detect errors:
   valgrind --leak-check=yes --track-origins=yes ./memory_errors

3. Test each error individually by uncommenting in main()

EXPECTED VALGRIND OUTPUT:
========================
- Uninitialized read: "Conditional jump or move depends on uninitialised value(s)"
- Memory leak: "definitely lost: X bytes in Y blocks"
- Double free: "Invalid free() / delete / delete[] / realloc()"
- Dangling pointer: "Invalid read/write of size X"
- Invalid free: "Invalid free() / delete / delete[] / realloc()"
- Buffer overflow: "Invalid write of size X"

LEARNING OBJECTIVES:
===================
1. Understand how each type of memory error manifests
2. Learn to use valgrind to detect these errors
3. Practice writing bug-free memory management code
4. Connect theory from OSTEP Chapter 14 to practical examples
*/