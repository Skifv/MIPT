#include <iostream>
#include <vector>

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

    for (int i = N - 1; i >= 0; i--)
    {
        cout << numbers[i] << " ";
    }

    return 0;
}