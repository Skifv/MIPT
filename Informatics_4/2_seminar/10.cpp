#include <iostream> 
using namespace std; 
 
char unleveling(char c); 
char get_a_letter(); 
//------------------------------------------------------------- 
char unleveling(char c) 
{ 
    if (c >= 'a' && c <= 'z') 
        c += 'A' - 'a'; 
    return c; 
} 

char get_a_letter()
{
    char c;
    cin >>c;
    while (!( (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ) )
    {
        cin >>c;
    }
    
    return c;
}
 
int main() 
{ 
    for (int i = 0; i < 10; i++) 
        cout <<unleveling(get_a_letter()); 
    cout <<endl; 
    return 0; 
} 