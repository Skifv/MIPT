#include <iostream>

int main() {
    int n = 0;
    int max = 0;
    int tmp = 0;

    std::cin >> n;
    
    for (int i = 0; i < n; i++)
    {
        std::cin >> tmp;
        if (tmp > max)
        {
            max = tmp;
        }
    }
    
    std::cout << max << "\n";
    return 0;
}
