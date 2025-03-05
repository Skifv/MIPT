#include <iostream>

int main() {
    int n;
    std::cin >> n;

    int rows = (n - 1) / 2;
    int spaces = rows;

    for (int i = 0; i < rows; i++) {
        std::cout << std::string(spaces, ' ') << std::string(2 * i + 1, '+') << std::endl;
        spaces--;
    }

    std::cout << std::string(n, '+') << std::endl;

    for (int i = 0; i < rows; i++) {
        spaces++;
        std::cout << std::string(spaces, ' ') << std::string(n - 2 - 2 * i, '+') << std::endl;
    }

    return 0;
}
