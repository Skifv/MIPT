#include <iostream>

int main() 
{
    int n = 0;

    std::cin >> n;

    if (n <= 0)
    {
        std::cout << "Error\n";
    }
    else if (n > 0)
    {
        for (int i = 1; i <= n; i++)
        {
            for (int j = 0; j < i; j++)
            {
                std::cout << '+';
            }
            std::cout << '\n';   
        }
    }

    return 0;
}