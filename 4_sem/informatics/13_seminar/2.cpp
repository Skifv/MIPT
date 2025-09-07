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

    sort(numbers1.begin(), numbers1.end(), [](int a, int b) { return a > b; });
    sort(numbers2.begin(), numbers2.end(), [](int a, int b) { return a > b; });

    bool isTheSame = true;

    for (int i = 0; i < N; i++)
    {
        if (numbers1[i] != numbers2[i])
        {
            isTheSame = false;
            break;
        }
    }

    cout << std::boolalpha << isTheSame << endl;

    return 0;
}