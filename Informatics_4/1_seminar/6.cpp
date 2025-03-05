#include <iostream>

int main() 
{
    long long int n = 0;
    long long int n_factorial = 1;
    std::cin >> n;
    if (n < 0)
    {
        std::cout << "Error\n";
    }
    else if (n > 1)
    {
        for (long long int i = 2; i <= n; i++)
        {
            n_factorial *= i;
        }
    }

    std::cout << n_factorial << "\n";
    return 0;
}