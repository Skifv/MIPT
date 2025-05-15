#include <iostream>
#include <vector>
#include <algorithm>
#include <set>
#include <iterator>

using namespace std;

int main()
{
    int N;
    cin >> N;

    set<int> numbers1;
    set<int> numbers2;
    set<int> numbers_crossed;

    int tempNumber;

    for (int i = 0; i < N; i++)
    {
        cin >> tempNumber;
        numbers1.emplace(tempNumber);
    }

    for (int i = 0; i < N; i++)
    {
        cin >> tempNumber;
        numbers2.emplace(tempNumber);
    }

    set_intersection(numbers1.begin(), numbers1.end(), 
                     numbers2.begin(), numbers2.end(), 
                     inserter(numbers_crossed, numbers_crossed.begin())); // итератор для вставки

    for (const auto& number : numbers_crossed)
    {
        cout << number << " ";
    }
    cout << endl;

    return 0;
}