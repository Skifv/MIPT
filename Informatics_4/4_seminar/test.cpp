#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <sstream>
#include <iterator>

using namespace std;

vector<int> Range(int start, int end)
{
    int n = end - start;
    vector<int> range(n);
    for (int i = start; i < end; i++)
    {
        range[i - start] = i;
    }

    return range;
}

int main()
{
    for (int i : Range(4, 10))
    {
        cout << i << " ";
    }
    cout << endl;
}