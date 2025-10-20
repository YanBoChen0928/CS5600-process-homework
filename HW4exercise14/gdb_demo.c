#include <stdio.h>
#include <stdlib.h>

// Function 3: This will cause a crash
int divide_numbers(int a, int b) {
    printf("  [divide_numbers] Dividing %d by %d\n", a, b);
    int result = a / b;  // If b=0, this will crash!
    return result;
}

// Function 2: Calls divide_numbers
int calculate(int x, int y) {
    printf(" [calculate] x=%d, y=%d\n", x, y);
    int result = divide_numbers(x, y);
    printf(" [calculate] Result = %d\n", result);
    return result;
}

// Function 1: Main function
int main(void) {
    printf("[main] Program starting...\n");
    
    int a = 10;
    int b = 2;
    printf("[main] First calculation: %d / %d\n", a, b);
    int result1 = calculate(a, b);
    printf("[main] Result1 = %d\n", result1);
    
    int c = 20;
    int d = 0;  // Danger! This is zero!
    printf("[main] Second calculation: %d / %d\n", c, d);
    int result2 = calculate(c, d);  // This will crash!
    printf("[main] Result2 = %d\n", result2);
    
    printf("[main] Program ending...\n");
    return 0;
}
