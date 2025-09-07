#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main()
{
    int N;
    cin >> N;

    vector<int> numbers(N);
    int tempNumber;

    for (int i = 0; i < N; i++)
    {
        cin >> tempNumber;
        numbers[i] = tempNumber;
    }

    int k;
    cin >> k;

    numbers.erase(std::remove_if(numbers.begin(), numbers.end(), [k](int number) { return number > k; }), 
                  numbers.end());

    for (auto number : numbers)
    {
        cout << number << " ";
    }

    cout << endl;

    return 0;
}