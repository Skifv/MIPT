#include <iostream>
#include <vector>
#include <set>
#include <iterator>
#include <algorithm>

using namespace std;

vector<int> Range(int n);
vector<int> Range(int start, int end);

vector<int> ReadNumbers(int n);

void PrintHighest(int m, vector<int> numbers);

int main() 
{
    int n;
    cin >> n;

    // сортировка по убыванию
    vector<int> numbers;
    numbers = ReadNumbers(n);

    int m;
    cin >> m;

    // печетает m наибольших
    PrintHighest(m, numbers);
}

vector<int> Range(int n)
{
    vector<int> range(n);
    for (int i = 0; i < n; i++)
    {
        range[i] = i;
    }
    return range;
}

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

vector<int> ReadNumbers(int n)
{
    vector<int> numbers;
    for (int i : Range(n))
    {
        int number;
        cin >> number;
        numbers.push_back(number);
    }
    return numbers;
}

void PrintHighest(int m, vector<int> numbers)
{
    sort(numbers.begin(), numbers.end());
    {
        for (int i : Range(numbers.size() - m, numbers.size()))
        {
            cout << numbers[i] << " ";
        }
        cout << endl;
    }
}