#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    int n = argc > 1 ? atoi(argv[1]) : 600;
    double *A = malloc(sizeof(double) * n * n);
    double *B = malloc(sizeof(double) * n * n);
    double *C = calloc((size_t)n * n, sizeof(double));
    for (int i = 0; i < n * n; i++) {
        A[i] = (i % 7) * 0.5;
        B[i] = (i % 11) * 0.25;
    }
    for (int i = 0; i < n; i++)
        for (int k = 0; k < n; k++)
            for (int j = 0; j < n; j++)
                C[i * n + j] += A[i * n + k] * B[k * n + j];
    double traza = 0.0;
    for (int i = 0; i < n; i++) traza += C[i * n + i];
    printf("%.6f %.6f\n", traza, C[(n / 2) * n + n / 3]);
    free(A); free(B); free(C);
    return 0;
}
