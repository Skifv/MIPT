#include <iostream>
#include <string>

using namespace std;

class Animal
{
protected:
    string type;
    bool dangerous;
public:
    virtual string getType()
    {
        return type;
    }
    virtual bool isDangerous()
    {
        return dangerous;
    }
};

class ZooKeeper 
{
private:
    int count_dangerous;
public:
    ZooKeeper() 
    {
        count_dangerous = 0;
    }
    // Смотрителя попросили обработать очередного зверя.
    // Если зверь был опасный, смотритель фиксирует у себя этот факт.
    void handleAnimal(Animal* a)
    {
        if (a->isDangerous())
        {
            count_dangerous++;
        }
    }
    // Возвращает, сколько опасных зверей было обработано на данный момент.
    int getDangerousCount()
    {
        return count_dangerous;
    }
};
    
class Monkey: public Animal 
{
public:
    Monkey()
    {
        type = "monkey";
        dangerous = false;
    }
};

class Lion: public Animal
{
public:
    Lion()
    {
        type = "lion";
        dangerous = true;
    }
};

int main()
{
    ZooKeeper z;
    Monkey *m = new Monkey();
    z.handleAnimal(m);
    delete m;

    m = new Monkey();
    z.handleAnimal(m);
    delete m;

    Lion *l = new Lion();
    z.handleAnimal(l);
    delete l;

    cout << z.getDangerousCount() << endl;
}