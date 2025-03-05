#include <iostream>

int main() 
{
    int count = 0;

    while (true)
    {
        char c;
        std::cin >> c;
        
        switch (c)
        {
            case '0': 
            {
                continue;
            }
            case '1':
            {
                count++;
                continue;
            }
            default:
            {
                break;
            }
        }

        break;
    }

    std::cout << count << "\n";

    return 0;
}