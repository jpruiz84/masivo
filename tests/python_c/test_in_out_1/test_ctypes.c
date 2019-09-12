#include <stdio.h>

int sum(int num_numbers, int *numbers) {
    int i;
    int sum = 0;
    for (i = 0; i < num_numbers; i++) {
        sum += numbers[i];
    }
    numbers[0] = 100;
    return sum;
}

