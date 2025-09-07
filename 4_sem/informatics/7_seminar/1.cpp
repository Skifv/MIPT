#include <iostream>

namespace namespaceA {
    class Engine {
    public:
        void run() {
            std::cout << "EngineA run" << std::endl;
        }
    };
}

namespace namespaceB {
    class Engine {
    public:
        void run() {
            std::cout << "EngineB run" << std::endl;
        }
    };
}

namespace namespaceC {
    class Engine {
    public:
        void run() {
            std::cout << "EngineC run" << std::endl;
        }
    };
}

class MyEngine {
private:
    namespaceA::Engine engineA;
    namespaceB::Engine engineB;
    namespaceC::Engine engineC;

public:
    void run(unsigned int number) {
        switch (number) {
            case 1:
                engineA.run();
                break;
            case 2:
                engineB.run();
                break;
            case 3:
                engineC.run();
                break;
            default:
                break;
        }
    }
};

int main() {
    MyEngine e;
    e.run(1); // EngineA run
    e.run(2); // EngineB run
    e.run(3); // EngineC run
    e.run(10); // Ничего не происходит
    return 0;
}