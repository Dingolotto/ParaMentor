#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    long n = argc > 1 ? atol(argv[1]) : 50000000;
    double suma = 0.0;
    for (long i = 0; i < n; i++)
        suma += 1.0 / (double)(i + 1);
    printf("%.10f\n", suma);
    return 0;
}
