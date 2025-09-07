#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>

class Connector {
public:
    Connector(const std::string& address) {
        if (address.empty()) {
            throw std::runtime_error("Empty address");
        }
        if (address.find("fail") != std::string::npos) {
            throw std::runtime_error("Connection failed to " + address);
        }
    }

    void sendRequest(const std::string& data) {
        if (data.empty()) {
            throw std::runtime_error("Empty message");
        }
        if (data == "HELLO" && rand() % 4 == 0) { // 25% вероятность ошибки
            throw std::runtime_error("Failed to send HELLO");
        }
    }
};

int main() {
    int N;
    std::cin >> N;
    std::cin.ignore(); // Игнорируем оставшийся символ новой строки после числа

    std::vector<std::string> addresses(N);
    for (int i = 0; i < N; ++i) {
        std::getline(std::cin, addresses[i]);
    }

    for (const auto& address : addresses) {
        try {
            // Пытаемся подключиться и отправить сообщение
            Connector connector(address);
            connector.sendRequest("HELLO");
            
            // Если дошли сюда - всё успешно
            std::cout << address << ": ok" << std::endl;
        }
        catch (const std::exception& e) {
            // Ловим любые исключения и выводим сообщение об ошибке
            std::cout << address << ": " << e.what() << std::endl;
        }
    }

    return 0;
}