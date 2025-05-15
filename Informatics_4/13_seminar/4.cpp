#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

int main()
{
    int N;
    cin >> N;

    vector<int> numbers1(N);
    vector<int> numbers2(N);
    vector<int> numbersIntersection;
    int tempNumber;

    for (int i = 0; i < N; i++)
    {
        cin >> tempNumber;
        numbers1[i] = tempNumber;
    }

    for (int i = 0; i < N; i++)
    {
        cin >> tempNumber;
        numbers2[i] = tempNumber;
    }

    for (int i = 0; i < N; i++)
    {
        tempNumber = numbers1[i];
        auto found = find_if(numbers2.begin(), numbers2.end(), [tempNumber](const int& number) { return number == tempNumber; });
        
        if (found != numbers2.end())
        {
            numbersIntersection.push_back(tempNumber);
            numbers2.erase(found);
        }
    }

    for (int number : numbersIntersection)
    {
        cout << number << " ";
    }

    cout << endl;

    return 0;
}