#include <iostream>
#include <map>
#include <string>
#include <vector>

using namespace std;

class Animal
{
public:
    virtual string getType() const = 0;
    virtual ~Animal() {}                 
};

class ZooKeeper 
{
    map<string, int> animals;
public:
    void handleAnimal(const Animal& a) {
        animals[a.getType()]++;
    }

    int getAnimalCount(const string& type) const {
        auto it = animals.find(type);
        return it != animals.end() ? it->second : 0;
    }
};

class Monkey : public Animal
{
public:
    string getType() const override { return "monkey"; }
};

class Lion : public Animal
{
public:
    string getType() const override { return "lion"; }
};

class Cat : public Animal
{
public:
    string getType() const override { return "cat"; }
};

int main()
{
    // Пример оживаеомго сценария работы:
    ZooKeeper z;
    Animal *a = new Monkey();
    z.handleAnimal(*a);
    delete a;
    a = new Monkey();
    z.handleAnimal(*a);
    delete a;
    a = new Lion();
    z.handleAnimal(*a);
    delete a;
    cout << z.getAnimalCount("monkey") << endl;
    cout << z.getAnimalCount("lion") << endl;
    cout << z.getAnimalCount("cat") << endl;
}


// Должно напечатать:
// 2
// 1
// 0