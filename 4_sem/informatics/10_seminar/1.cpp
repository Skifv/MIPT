#include <iostream>
#include <string>

using namespace std;

template<typename T>
T get_min_value(const T& a, const T& b)
{
    return a <= b ? a : b;
}


int main() 
{
    int a = 5;
    int b = 4;
    string s1 = "abc";
    string s2 = "zxc";
    cout << "Min int: " << get_min_value(a, b) << endl;
    cout << "Min string: " << get_min_value(s1, s2) << endl;
    return 0;
}