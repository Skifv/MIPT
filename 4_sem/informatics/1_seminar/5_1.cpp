#include <iostream>

int main() {
    int n = 0, m = 0;
    std::cin >> n >> m;
    
    for (int j = 0; j < m; j++)
    {
        std::cout << '+';
    }
    std::cout << '\n';

    for (int i = 1; i < n - 1; i++)
    {
        std::cout << '+';
        for (int j = 1; j < m - 1; j++)
        {
            std::cout << ' ';
        }
        std::cout << '+';
        std::cout << '\n';
    }

    for (int j = 0; j < m; j++)
    {
        std::cout << '+';
    }
    std::cout << '\n';

    return 0;
}

