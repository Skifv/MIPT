#include <iostream>

int main() {
    int rows = 0, columns = 0;
    std::cin >> rows >> columns;

    for (int row = 0; row < rows; ++row) {
        for (int column = 0; column < columns; ++column) {
            if (row == 0 || row == rows - 1 || column == 0 || column == columns - 1) {
                std::cout << '+';
            } else {
                std::cout << ' ';
            }
        }
        std::cout << '\n';
    }

    return 0;
}

