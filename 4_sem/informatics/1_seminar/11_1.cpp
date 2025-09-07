#include <iostream>

int main() {
    int n;
    std::cin >> n;

    int rows = (n-1) / 2;
    int spaces = rows;

    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < spaces; j++)
        {
            std::cout << " ";
        }
        for (int j = 0; j < 2 * i + 1; j++)
        {
            std::cout << "+";
        }

        spaces--;
        std::cout << std::endl;
    }

    for (int i = 0; i < n; i++)
    {
        std::cout << "+";
    }
    std::cout << std::endl;

    for (int i = 0; i < rows; i++)
    {
        spaces++;
        for (int j = 0; j < spaces; j++)
        {
            std::cout << " ";
        }
        for (int j = 0; j < n - 2 - 2 * i; j++)
        {
            std::cout << "+";
        }

        std::cout << std::endl;
    }

    return 0;
}



