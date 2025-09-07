#include <iostream>
#include <stdexcept>
#include <vector>

// Класс исключения для некорректного индекса
class IncorrectIndexException : public std::out_of_range {
public:
    IncorrectIndexException(unsigned int index, unsigned int size)
        : std::out_of_range("Incorrect index: " + std::to_string(index) + 
                            ". Storage size is " + std::to_string(size)) {}
};

// Класс хранилища
class Storage {
private:
    std::vector<int> data;

public:
    // Конструктор хранилища размерности n
    Storage(unsigned int n) : data(n) {}

    // Получение размерности хранилища
    unsigned int getSize() const {
        return data.size();
    }

    // Получение значения i-го элемента из хранилища
    int getValue(unsigned int i) const {
        if (i >= data.size()) {
            throw IncorrectIndexException(i, data.size());
        }
        return data[i];
    }

    // Задание значения i-го элемента из хранилища
    void setValue(unsigned int i, int value) {
        if (i >= data.size()) {
            throw IncorrectIndexException(i, data.size());
        }
        data[i] = value;
    }
};

int main() {
    try {
        unsigned int index;
        std::cout << "Enter index: ";
        std::cin >> index;
        
        Storage s(42);
        s.setValue(index, 0);
        std::cout << s.getValue(index) << std::endl;
        
    } catch (const IncorrectIndexException& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "Unexpected error: " << e.what() << std::endl;
        return 2;
    }

    return 0;
}