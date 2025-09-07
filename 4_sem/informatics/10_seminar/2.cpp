#include <iostream>

using namespace std;

template<typename T>
bool check_them(T& x, T& y, T& z)
{
    return x == y && y == z;
}


struct student 
{
    std::string name;
    std::string id_number_string;
};

bool operator==(const student& a, const student& b)
{
    return a.id_number_string == b.id_number_string;
}


int main()
{
    student a = {"Andy", "1234 123123"};
    student b = {"Andrew", "1234 123123"};
    student c = {"Andy", "1234123123"};
    cout << boolalpha << "Check result is: " << check_them(a, b, c) << endl;
    return 0;
}