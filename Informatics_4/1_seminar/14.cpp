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
            if (digits[i] == 1)
            {
                std::cout << "1";
            }
        }
        for (int i = digits.size() - 1; i >= 0; i--)
        {
            if (digits[i] == 0)
            {
                std::cout << "0";
            }
        }

    }


    return 0;
}