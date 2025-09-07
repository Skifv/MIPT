#include <iostream>
#include <vector>

int main () 
{
    int n = 0;
    std::cin >> n;

    std::vector<long long int> natural(n, 1);

    natural[0] = 2;
    int p = 1;

    for (long long int i = 2; natural[n-1] == 1; i++)
    {
        bool is_prime = true;
        for (int j = 0; j < p; j++)
        {
            if (i % natural[j] == 0)
            {
                is_prime = false;
                break;
            }
        }

        is_prime ? (natural[p++] = i) : 1;
    }

    std::cout << natural[n-1] << "\n";

    return 0;
}