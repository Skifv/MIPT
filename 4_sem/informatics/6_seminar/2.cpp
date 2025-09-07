#include <iostream>
#include <string>

using namespace std;

class Item 
{
protected:
    string title;

    int weight;
    int level;

    bool magical;
public:
    // Так можно создать предмет, указав его название, вес, уровень и магичность
    Item(string title, int weight, int level, bool magical) 
        : title(title), weight(weight), level(level), magical(magical) { }
    
    string getTitle()
    {
        return title;
    }

    int getWeight()
    {
        return weight;
    }
    int getLevel()
    {
        return level;
    }
    int isMagical()
    {
        return magical;
    }
};

class Player {
protected:
    int strength;
    int level;
public:
    Player() { }
    
    virtual ~Player() { }
    
    void setStrength(int strength)
    {
        this->strength = strength;
    }
    
    void setLevel(int level)
    {
        this->level = level;
    }
    
    int getStrength() 
    {
        return this->strength;
    }
    
    int getLevel() 
    {
        return this->level;
    }
    
    virtual bool canUse(Item* item) = 0;
};

class Wizard: public Player 
{
public:
    bool canUse(Item* item)
    {
        if (strength >= item->getWeight()   
            && level >= item->getLevel())
        {
            return true;
        }
        
        return false;
    }
};

class Knight: public Player 
{
public:
    bool canUse(Item* item)
    {
        if (!item->isMagical() 
            && strength >= item->getWeight() 
            && level    >= item->getLevel())
        {
            return true;
        }
        
        return false;
    }
};
   
int main()
{
    cout << boolalpha;

    Item* items[3];
    items[0] = new Item("Small sword", 1, 1, false);
    items[1] = new Item("Big sword", 5, 3, false);
    items[2] = new Item("Ward", 1, 3, true);

    Player* players[2];

    players[0] = new Wizard();
    players[0]->setStrength(3);
    players[0]->setLevel(5);

    players[1] = new Knight();
    players[1]->setStrength(6);
    players[1]->setLevel(5);

// Проверяем, какие предметы могут использовать игроки
    for (int i = 0; i < 2; i++) 
    {
        string className = typeid(*players[i]).name();
        className = className.substr(1); // Убираем лишнее из имени класса
        cout << "--- " << className << " ---" << endl;

        for (int j = 0; j < 3; j++) 
        {
            cout << "Can use " << items[j]->getTitle() << "? "
                << players[i]->canUse(items[j]) << endl;
        }
        cout << endl;
    }

    // Освобождаем память
    for (int i = 0; i < 3; i++) 
    {
        delete items[i];
    }
    for (int i = 0; i < 2; i++) 
    {
        delete players[i];
    }

}
