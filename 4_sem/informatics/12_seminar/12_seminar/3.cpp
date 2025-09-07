#include <string>
#include <unordered_map>
#include <algorithm> // для min и max
#include <iostream>

using namespace std;

class Tracker
{
    private:
    // Структура для хранения данных о пользователе
    struct UserStats
    {
        unsigned long long clickCount = 0; // счетчик кликов
        unsigned long long firstClick = 0; // время первого клика
        unsigned long long lastClick = 0;  // время последнего клика
    };

    // Хранилище данных пользователей
    unordered_map<std::string, UserStats> userData;
public:
    // При любом действии пользователя вызывается этот метод
    void click(const string& username, unsigned long long timestamp)
    {
        // Если пользователь новый - создаем для него запись
        if (userData.find(username) == userData.end())
        {
            userData[username] = {1, timestamp, timestamp};
        }
        else
        {
            // Увеличиваем счетчик кликов
            userData[username].clickCount++;
            // Обновляем время первого клика (если текущее раньше)
            userData[username].firstClick = min(userData[username].firstClick, timestamp);
            // Обновляем время последнего клика (если текущее позже)
            userData[username].lastClick = max(userData[username].lastClick, timestamp);
        }
    }

    // Получить количество кликов пользователя
    unsigned long long getClickCount(const string& username) const
    {
        auto it = userData.find(username);
        return it != userData.end() ? it->second.clickCount : 0;
    }

    // Получить время первого клика пользователя
    unsigned long long getFirstClick(const string& username) const
    {
        auto it = userData.find(username);
        return it != userData.end() ? it->second.firstClick : 0;
    }

    // Получить время последнего клика пользователя
    unsigned long long getLastClick(const string& username) const
    {
        auto it = userData.find(username);
        return it != userData.end() ? it->second.lastClick : 0;
    }
};

int main()
{
    Tracker t;
    t.click("alice", 1000);
    t.click("bob", 1100);
    t.click("alice", 1001);
    t.click("alice", 1200);
    t.click("alice", 1002);
    cout << t.getClickCount("alice") << endl;
    cout << t.getClickCount("bob") << endl;
    cout << t.getFirstClick("alice") << endl;
    cout << t.getFirstClick("bob") << endl;
    cout << t.getLastClick("alice") << endl;
    cout << t.getLastClick("bob") << endl;
    
    return 0;
}