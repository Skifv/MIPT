#include <iostream>
#include <vector>
#include <memory>
#include <string>

using namespace std;

// Класс мозга гоблина (заглушка)
class Brain {
protected:
    vector<double> data;
    string phrase;
public:
    Brain() {
        data.resize(1000000);
        phrase = "Booyahg Booyahg Booyahg";
    }
    
    string speak() {
        return phrase;
    }
};

// Класс гоблина
class Goblin {
private:
    shared_ptr<Brain> army_brain;  // Общий мозг для всей армии

public:
    // Конструктор принимает shared_ptr на мозг армии
    Goblin(shared_ptr<Brain> brain) : army_brain(brain) {}
    
    // Метод для получения фразы из мозга
    string speak() {
        return army_brain->speak();
    }
};

// Функция создания армии гоблинов
vector<Goblin> create_goblin_army(unsigned int size) {
    // Создаём один мозг на всю армию
    shared_ptr<Brain> army_brain = make_shared<Brain>();
    
    // Создаём армию гоблинов с общим мозгом
    vector<Goblin> army;
    for (unsigned int i = 0; i < size; i++) {
        army.emplace_back(army_brain);
    }
    
    return army;
}

int main() {
    unsigned int size1 = 1;
    unsigned int size2 = 10;
    
    vector<Goblin> army1 = create_goblin_army(size1);
    vector<Goblin> army2 = create_goblin_army(size2);
    
    for(unsigned int i = 0; i < size1; i++) {
        cout << army1[i].speak() << endl;
    }
    
    for(unsigned int i = 0; i < size2; i++) {
        cout << army2[i].speak() << endl;
    }
    
    return 0;
}