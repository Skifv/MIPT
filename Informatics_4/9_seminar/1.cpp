#include <iostream>
#include <string>

using namespace std;

class Student
{
private:
    string name;
    unsigned int score;
public:
    Student() : name(""), score(0) {}

    // Задать имя студента
    void setName(string name) 
    {
        this->name = name;
    }

    // Указать количество баллов за контрольную
    void setScore(unsigned int score)
    {
        this->score = score;
    }
    // Получить имя студента
    string getName() const
    {
        return name;
    }
    // Получить количество баллов студента
    unsigned int getScore() const
    {
        return score;
    }
};

istream& operator>>(istream& in, Student& s) 
{
    string name;
    getline(in, name);
    s.setName(name);
    s.setScore(0);
    return in;
}

ostream& operator<<(ostream& out, const Student& s)
{
    out << "'" << s.getName() << "': " << s.getScore();
    return out;
}

int main()
{
    Student s;
    cin >> s;
    s.setScore(10);
    cout << s << endl;
}