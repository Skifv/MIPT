#include <iostream>

class Storage {
protected:
    int* data;
    unsigned int size;
    
public:
    Storage(unsigned int n) : size(n) {
        data = new int[n];
    }

    virtual ~Storage() {  // Ключевое слово virtual!
        delete[] data;
    }

    unsigned int getSize() {
        return size;
    }

    int getValue(unsigned int i) {
        return data[i];
    }

    void setValue(unsigned int i, int value) {
        data[i] = value;
    }
};

class TestStorage : public Storage {
    int* more_data;
public:
    TestStorage(unsigned int n) : Storage(n) {
        more_data = new int[n];
    }

    ~TestStorage() override {
        delete[] more_data;
    }
};

int main() {
    Storage* ts = new TestStorage(42);
    delete ts; 
    
    
    Storage s(5);
    s.setValue(0, 42);
    std::cout << s.getValue(0) << std::endl; // 42
    
    return 0;
}