#include <stdio.h>
#include <string.h>

int arr[7][7] = {
    {0, 1, 2, 3, 4, 5, 6},
    {1, 4, 0, 2, 6, 3, 5},
    {2, 0, 3, 5, 1, 6, 4},
    {3, 2, 5, 6, 0, 4, 1},
    {4, 6, 1, 0, 5, 2, 3},
    {5, 3, 6, 4, 2, 1, 0},
    {6, 5, 4, 1, 3, 0, 2}
};

struct ECC 
{
    int arr[7][7];
    int key;
    int (*calculate)(struct ECC *, int);
};

int ECC_calculate(struct ECC * user, int m)
{   
    int res = m;
    int N = user->key;

    for (int i = 1; i < N; i++)
    {
        res = user->arr[res][m];
    }

    return res;
}

int main(void)
{
    struct ECC A, B;
    memcpy(A.arr, arr, sizeof(arr)); // Копируем массив
    memcpy(B.arr, arr, sizeof(arr)); // Копируем еще раз

    A.calculate = ECC_calculate;
    B.calculate = ECC_calculate;

    A.key = 3;       // генерируются случайно
    B.key = 4;

    int m = 1;       // обменялись между A и B
    int mA = A.calculate(&A, m);
    int mB = B.calculate(&B, m);

    printf("m: %d\n", m);
    printf("mA: %d\n", mA);
    printf("mB: %d\n", mB);

    /* Произошел обмен mA и mB */

    int AmB = A.calculate(&A, mB);
    int BmA = B.calculate(&B, mA);

    // должны быть равны
    printf("AmB: %d\n", AmB);
    printf("BmA: %d\n", BmA);  

    return 0;
}
