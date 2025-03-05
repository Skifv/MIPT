#include <iostream>

int gcd(int a, int b) 
{
    if (b == 0)
    {
        return a;
    }
    else
    {
        return gcd(b, a % b);
    }
}

int LCM(int a, int b) 
{
    return a * b / gcd(a, b);
}

int main() 
{
    int a, b, c;
    std::cin >> a >> b >> c;
    std::cout << LCM(LCM(a, b), c) << std::endl;
    return 0;
}