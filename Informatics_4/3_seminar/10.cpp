#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

void ReadNumbers(int n, vector<int>& numbers)
{
    for (int i = 0; i < n; i++)
    {
        int number;
        cin >> number;
        numbers.push_back(number);
    }
}

void PrintNumbers(const vector<int>& numbers, int sign)
{

    for (int i : numbers)
    {
        if (sign > 0 && i >= 0)
        {
            cout << i << " ";
        }
        else if (sign < 0 && i < 0)
        {

            cout << i << " ";
        }
    }
}

int main()
{
    int n = 0;
    cin >> n;

    vector<int> numbers;

    ReadNumbers(n, numbers);

    
    sort(numbers.begin(), numbers.end()); // по возрастанию

    int sign = 1;
    PrintNumbers(numbers, sign);

    sort(numbers.begin(), numbers.end(), greater<int>()); // по убыванию

    sign = -1;
    PrintNumbers(numbers, sign);

    cout << endl;
    
    return 0;
}