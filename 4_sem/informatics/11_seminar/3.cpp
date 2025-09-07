#include <iostream>
#include <algorithm>
#include <vector>

using namespace std;

class Person
{
private:
    string surname;
    string name;
    string middleName;
public:
    Person() : surname(""), name(""), middleName("") {}
    // Создать человека с ФИО
    Person(string surname, string name, string middleName) 
        : surname(surname), name(name), middleName(middleName) {}

    string getFullName() const { return surname + " " + name + " " + middleName; }

    friend ostream& operator<<(ostream& out, const Person& p);
    friend istream& operator>>(istream& in, Person& p);
};

// Перегрузить операторы <, <<, >>
istream& operator>>(istream& is, Person& p)
{
    is >> p.surname >> p.name >> p.middleName;

    return is;
}

ostream& operator<<(ostream& os, const Person& p)
{
    os << p.getFullName();

    return os;
}

bool operator<(const Person& p1, const Person& p2)
{
    return p1.getFullName() < p2.getFullName();
}

int main()
{
    cout << "Testing I/O" << endl;
    Person p;
    cin >> p;
    cout << p << endl;

    cout << "Testing sorting" << endl;
    vector<Person> people;
    people.push_back(Person("Ivanov", "Ivan", "Ivanovich"));
    people.push_back(Person("Petrov", "Petr", "Petrovich"));
    people.push_back(Person("Ivanov", "Ivan", "Petrovich"));
    people.push_back(Person("Ivanov", "Petr", "Ivanovich"));

    sort(people.begin(), people.end());

    for(vector<Person>::const_iterator it = people.begin(); it < people.end(); it++) 
    {
        cout << *it << endl;
    }
}