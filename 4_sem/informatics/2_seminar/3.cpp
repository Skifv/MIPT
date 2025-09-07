#include <iostream> 
using namespace std; 
 
unsigned int sum_of_numbers(unsigned int n)
{
    if (n == 0)
        return 0;
    else
        return n % 10 + sum_of_numbers(n / 10);
}
 
int main() 
{ 
    unsigned int n; 
    cin >>n; 
    cout <<sum_of_numbers(n) <<endl; 
    return 0; 
} 