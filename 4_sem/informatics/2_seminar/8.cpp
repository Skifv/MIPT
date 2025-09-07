#include <iostream> 
using namespace std; 
 
bool is_a_number(char c)
{
    const char * arr = "0123456789";

    for (int i = 0; i < 10; i++)
    {
        if (c == arr[i])
        {
            return true;
        }
    }

    return false;
}
 
int main() 
{ 
    char c; 
    unsigned int sum = 0; 
    do 
    { 
        cin >>c; 
        if (is_a_number(c)) 
            sum += c - '0'; 
    } while (c != '$'); 
    cout <<sum <<endl; 
    return 0; 
} 