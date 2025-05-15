#include <string>
#include <vector>
#include <unordered_map>
#include <set>
#include <algorithm>
#include <iostream>

using namespace std;

class Connection
{
protected:
        string source;
        unsigned short int port;
        unsigned long long timestamp;
public:
    Connection(string source, unsigned short int port, unsigned long long timestamp) {
        this->source = source;
        this->port = port;
        this->timestamp = timestamp;
    }
    ~Connection() {}
    string getSource() const {
        return source;
    }
    unsigned short int getPort() const {
        return port;
    }
    unsigned long long getTimestamp() const {
        return timestamp;
    }
};

class IntrusionDetector
{
public:
    void setTimeThreshold(unsigned short int timeThreshold)
    {
        this->timeThreshold = timeThreshold;
    }

    void setPortLimit(unsigned short int portLimit)
    {
        this->portLimit = portLimit;
    }

    void handleConnection(const Connection& c)
    {
        // Сохраняем подключение в истории
        connections[c.getSource()].push_back(c);
    }

    bool isIntruder(const std::string& source) const
    {
        // Если нет записей об этом источнике
        if (connections.find(source) == connections.end())
            return false;

        const auto& conns = connections.at(source);

        // Если подключений меньше порогового значения
        if (conns.size() < portLimit)
            return false;

        // Создаем копию подключений для сортировки по времени
        std::vector<Connection> sortedConns = conns;
        std::sort(sortedConns.begin(), sortedConns.end(),
            [](const Connection& a, const Connection& b) {
                return a.getTimestamp() < b.getTimestamp();
            });

        // Проверяем все возможные временные окна
        for (size_t i = 0; i < sortedConns.size(); ++i)
        {
            std::set<unsigned short int> portsInWindow;
            portsInWindow.insert(sortedConns[i].getPort());

            for (size_t j = i + 1; j < sortedConns.size(); ++j)
            {
                // Если разница во времени превышает порог - прекращаем проверку этого окна
                if (sortedConns[j].getTimestamp() - sortedConns[i].getTimestamp() > timeThreshold)
                    break;

                portsInWindow.insert(sortedConns[j].getPort());

                // Если найдено достаточное количество уникальных портов
                if (portsInWindow.size() >= portLimit)
                    return true;
            }
        }

        return false;
    }

private:
    unsigned short int timeThreshold = 0;
    unsigned short int portLimit = 0;
    std::unordered_map<std::string, std::vector<Connection>> connections;
};


int main()
{
    IntrusionDetector id;
    id.setTimeThreshold(5);
    id.setPortLimit(3);
    id.handleConnection({"evil.com", 21, 100504});
    id.handleConnection({"evil.com", 22, 100501});
    id.handleConnection({"evil.com", 23, 100502});
    id.handleConnection({"evil.com", 24, 100503});
    id.handleConnection({"evil.com", 25, 100500});
    cout << boolalpha << "Checking if evil.com is intruder: " << id.isIntruder("evil.com") <<
    endl;
    id.handleConnection({"load.com", 80, 100504});
    id.handleConnection({"load.com", 80, 100501});
    id.handleConnection({"load.com", 80, 100502});
    id.handleConnection({"load.com", 80, 100503});
    id.handleConnection({"load.com", 80, 100500});
    cout << boolalpha << "Checking if load.com is intruder: " << id.isIntruder("load.com") <<
    endl;

    return 0;
}