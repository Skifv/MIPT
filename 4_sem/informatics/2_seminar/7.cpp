#include <iostream> 
using namespace std; 
 
unsigned int sum_of_numbers(unsigned long long int n); 
unsigned long long int nonacci(unsigned int n); 
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

unsigned long long int nonacci(unsigned int n)
{
    unsigned long long int F0 = 0,
                           F1 = 0,
                           F2 = 0,
                           F3 = 0,
                           F4 = 0,
                           F5 = 0,
                           F6 = 0,
                           F7 = 0,
                           F8 = 1;

    if (n < 8)
    {
        return F0;
    }
    else if (n == 8)
    {
        return F8;
    }
    else 
    {
        for (unsigned int i = 9; i <= n; i++)
        {
            unsigned long long int Fi = F0 + F1 + F2 + F3 + F4 + F5 + F6 + F7 + F8;

            F0 = F1;
            F1 = F2;
            F2 = F3;
            F3 = F4;
            F4 = F5;
            F5 = F6;
            F6 = F7;
            F7 = F8;
            F8 = Fi;
        }
    }

    return F8;
}

int main() 
{  
    unsigned int n; 
    cin >>n; 
    cout <<sum_of_numbers(nonacci(n)) <<endl; 
    return 0; 
} 