#include <iostream>
#include <vector>
#include <set>

using namespace std;

vector<int> Range(int n);
vector<int> Range(int start, int end);

set<int> ReadNumbers(int n);

int Avarage(set<int> numbers);
void PrintHigher(set<int> numbers);

int main() 
{
    int n;
    cin >> n;

    set<int> numbers;
    numbers = ReadNumbers(n);

    // печетает элементы больше среднего
    PrintHigher(numbers);
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

set<int> ReadNumbers(int n)
{
    set<int> numbers;
    for (int i : Range(n))
    {
        int number;
        cin >> number;
        numbers.insert(number);
    }
    return numbers;
}

int Avarage(set<int> numbers)
{
    int sum = 0;
    for (int i : numbers)
    {
        sum += i;
    }
    return sum / numbers.size();
}

void PrintHigher(set<int> numbers)
{
    int avarage = Avarage(numbers);
    for (int i : numbers)
    {
        if (i > avarage)
        {
            cout << i << " ";
        }
    }
    cout << endl;
}