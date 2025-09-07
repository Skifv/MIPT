#include <iostream>

int main() {
    int a;
    std::cin >> a;
    (a % 13 == 0) ? std::cout << "yes\n" : std::cout << "no\n";
    return 0;
}

