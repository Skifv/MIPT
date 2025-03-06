#include <iostream> 
using namespace std; 
 
char leveling(char c)
{
    if (c >= 'A' && c <= 'Z')
        return c - ('A' - 'a'); 
    else 
        return c;
}
 
int main() 
{ 
    char c; 
    do 
    { 
        cin.get(c); 
        cout <<leveling(c); 
    } while (c != '\n'); 
    return 0; 
} 