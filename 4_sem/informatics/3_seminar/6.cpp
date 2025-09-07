#include <iostream>
#include <vector>
#include <set>
#include <iterator>
#include <algorithm>

using namespace std;

vector<int> Range(int n);
vector<int> Range(int start, int end);

vector<int> ReadNumbers(int n);

vector<int> FindHighest(int m, vector<int> numbers);
void PrintHighest(int m, vector<int> number);

int main() 
{
    int n;
    cin >> n;

    // сортировка по убыванию
    vector<int> numbers;
    numbers = ReadNumbers(n);

    int m;
    cin >> m;

    // печать m наибольших в порядке вектора
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

vector<int> FindHighest(int m, vector<int> numbers)
{
    vector<int> res;
    sort(numbers.begin(), numbers.end());

    for (int i : Range(numbers.size() - m, numbers.size()))
    {
        res.push_back(numbers[i]);
    }

    return res;
}

bool is_exist(int number, vector<int>& sorted_numbers)
{
    auto it = find(sorted_numbers.begin(), sorted_numbers.end(), number);
    if (it != sorted_numbers.end())
    {
        sorted_numbers.erase(it);
        return true;
    }
    else
    {
        return false;
    }
}

void PrintHighest(int m, vector<int> numbers)
{
    vector<int> highest_numbers = FindHighest(m, numbers);

    for (int i : numbers)
    {
        if (is_exist(i, highest_numbers))
        {
            cout << i << " ";
        }
    }
    cout << endl;
}

