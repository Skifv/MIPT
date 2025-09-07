#include <iostream> 
#include <string>
#include <vector>
#include <cmath>
using namespace std; 


 
unsigned int get_a_hexadecimal()
{
    unsigned int res = 0;
    char c;
    vector<char> hex;

    do
    {
        c = getchar();
        if (c == '\n' || c == ' ')
        {
            break;
        }
        else if (!((c >= '0' && c <= '9') || (c >= 'A' && c <= 'F')))
        {
            return 0;
        }

        hex.push_back(c);
        
    } while (true);

    for (int i = hex.size() - 1; i >= 0; i--)
    {
        if (hex[i] >= '0' && hex[i] <= '9')
        {
            res += (hex[i] - '0') * pow(16, hex.size() - 1 - i);
        }
        else if (hex[i] >= 'A' && hex[i] <= 'F')
        {
            res += (hex[i] - 'A' + 10) * pow(16, hex.size() - 1 - i);
        }
    }
    
    return res;
}
 
int main() 
{ 
    cout <<get_a_hexadecimal() <<endl; 
    return 0; 
} 