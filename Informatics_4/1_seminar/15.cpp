#include <iostream>

bool is_exist(char c, const char * arr, int n)
{
    for (int i = 0; i < n; i++)
    {
        if (c == arr[i])
        {
            return true;
        }
    }

    return false;
}

int main() {
    int count = 0;
    char c = '@';

    while(true)
    {
        std::cin >> c;
        if (c == '@')
        {
            break;
        }
        else if (is_exist(c, "0123456789", 10))
        {
            count++;
        }
    }

    std::cout << count;

    return 0;
}

