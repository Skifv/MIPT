#include <iostream>
#include <vector>

int main() 
{
    int n = -1;
    std::cin >> n;

    if (n < 0)
    {
        std::cout << "Error\n";
    }
    else 
    {
        std::vector <int> digits;

        while (n > 0)
        {
            digits.push_back(n % 2);
            n /= 2;
        }

        for (int i = digits.size() - 1; i >= 0; i--)
        {
            std::cout << digits[i];
        }
    }


    return 0;
}