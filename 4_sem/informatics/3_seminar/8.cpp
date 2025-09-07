#include <iostream>
using namespace std;

struct Vector {
 int x, y, z;
};

Vector sum(Vector a, Vector b)
{
    Vector res;
    res.x = a.x + b.x;
    res.y = a.y + b.y;
    res.z = a.z + b.z;
    return res;
}

const int N = 10;
int main()
{
 Vector res = {0, 0, 0};
 for (int i=0; i<N; i++)
 {
 Vector tmp;
 cin >>tmp.x >>tmp.y >>tmp.z;
 res = sum(res, tmp);
 }
 cout <<res.x <<" " <<res.y <<" " <<res.z <<endl;
 return 0;
}
