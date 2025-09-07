#include <iostream> 
using namespace std; 
 
unsigned int sum_of_numbers(unsigned long long int n); 
unsigned long long int fibonacci(unsigned int n); 
//---------------------------------------------------- 
unsigned int sum_of_numbers(unsigned long long int n) 
{ 
    unsigned int res = 0; 
    while (n) 
    { 
        res += n % 10; 
        n /= 10; 
    } 
    return res; 
} 

unsigned long long int fibonacci(unsigned int n)
{
    unsigned long long int F_1 = 0;
    unsigned long long int F_2 = 1;

    if (n == 1) 
        return F_1;
    else if (n == 2) 
        return F_2;
    else
    {
        for (unsigned int i = 3; i <= n; i++)
        {
            unsigned long long int F_i = F_2 + F_1;
            F_1 = F_2;
            F_2 = F_i;
        }
    }
    return F_2;
}

int main() 
{ 
    unsigned int n; 
    cin >>n; 
    cout <<sum_of_numbers(fibonacci(n)) <<endl; 
    return 0; 
} 