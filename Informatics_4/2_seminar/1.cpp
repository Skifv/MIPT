#include <iostream> 
using namespace std; 
 
bool is_simple(int n)
{
    if (n == 1) 
    {
        return false;
    }
    for (int i = 2; i * i <= n + 1; i++)
    {
        if (n % i == 0)
        {
            return false;
        }
    }
    return true;
} 
 
int main () { 
    int n; 
    cin >> n; 
    for (int i = 1; i <= n; i++) 
        if ( is_simple(i) ) 
            cout <<i <<' '; 
    cout <<endl; 
    return 0; 
} 