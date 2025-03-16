#include <iostream>

using namespace std;

class Train
{
private:
    double m;
    double x;
    double v;
public:
    Train(double m) 
        : m(m), x(0) {}

    // Ехать с текущей скоростью в течение времени dt
    void move(double dt)
    {
        x += v * dt;
    }
    // Изменить полный импульс паровоза (p = mv) на dp
    // Изменение может менять знак скорости
    void accelerate(double dp)
    {
        v += dp / m;
    }
    // Получить текущую координату паровоза
    double getX()
    {
    return x;
    }
};

int main()
{
    Train t(10);
    t.accelerate(1); // Скорость стала 0.1
    t.move(1);
    cout << "Current X: " << t.getX() << endl;
    t.move(1);
    cout << "Current X: " << t.getX() << endl;
    t.accelerate(-2); // Скорость стала -0.1
    t.move(3);
    cout << "Current X: " << t.getX() << endl;
}

/*

Базовый тест должен вывести:
Current X: 0.1
Current X: 0.2
Current X: -0.1

*/