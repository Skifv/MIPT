#include <iostream>
#include <vector>
#include <map>
using namespace std;

int sum(vector<int> array) {
    int res = 0;
    for (auto i : array) {
        res += i;
    }
    return res;
}

int main() {
    int n;
    cin >> n;
    vector<int> temp(n);

    for (int i = 0; i < n; i++) {
        cin >> temp[i];
    }

    int avarage = sum(temp) / n;

    vector<int> special_days;

    // заполняет special_days номерами дней, температура в которых превышает среднюю
    for (auto i : temp) {
        if (i > avarage) {
            special_days.push_back(i);
        }
    }

    // выводит их на экран
    cout << special_days.size() << endl;

    for (int i = 0; i < n; i++) {
        if (temp[i] > avarage) {
            cout << i << " ";
        }
    }

    cout << endl;

    return 0;
}