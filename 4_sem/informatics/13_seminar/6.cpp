#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main()
{
    int N;
    cin >> N;

    vector<int> numbers;
    int tempNumber;

    for (int i = 0; i < N; i++)
    {
        cin >> tempNumber;
        numbers.push_back(tempNumber);
    }

    vector<int> even_indexes, odd_indexes;
    for (int i = 0; i < N; i++) 
    {
        numbers[i] % 2 == 0 ? even_indexes.push_back(i) : odd_indexes.push_back(i);
    }

    vector<int> even, odd;
    for (auto i : even_indexes) 
        even.push_back(numbers[i]);
    for (auto i : odd_indexes)
        odd.push_back(numbers[i]);

    sort(even.begin(), even.end(), [](int a, int b) { return a > b; });
    sort(odd.begin(),  odd.end(),  [](int a, int b) { return a < b; });

    vector<int> sorted_numbers(N);

    for (int i = 0; i < even_indexes.size(); i++)
    {
        numbers[even_indexes[i]] = even[i];
    }
    
    for (int i = 0; i < odd_indexes.size(); i++)
    {
        numbers[odd_indexes[i]] = odd[i];
    }

    for (int number : numbers)
    {
        cout << number << " ";
    }
    cout << endl;


    return 0;
}