#include <iostream>
#include <string>

using namespace std;


class Vector2D
{
private:
    int x, y;
public:
    // Конструкторы
    Vector2D() : x(0), y(0) {}
    Vector2D(int x, int y) : x(x), y(y) {}
    // Деструктор
    ~Vector2D() {}
    // Получение координат
    int getX() const
    {
        return x;
    }
    int getY() const
    {
        return y;
    }
    // Задание координат
    void setX(int x)
    {
        this->x = x;
    }
    void setY(int y)
    {
        this->y = y;
    }
    // Перегруженный оператор - сравнение двух векторов на равенство
    bool operator== (const Vector2D& v2) const
    {
        return this->x == v2.getX() && this->y == v2.getY();
    }
    // Ещё один перегруженный оператор - неравенство векторов
    // Да, это отдельный оператор! Хинт - настоящие джедаи смогут для != использовать уже написанное ==
    bool operator!= (const Vector2D& v2) const
    {
        return !(*this == v2);
    }
    // Сумма двух векторов, исходные вектора не меняются, возвращается новый вектор
    Vector2D operator+ (const Vector2D& v2) const
    {
        return Vector2D(this->x + v2.getX(), this->y + v2.getY());
    }
    // Вычитание векторов, исходные вектора не меняются, возвращается новый вектор
    Vector2D operator- (const Vector2D& v2) const
    {
        return Vector2D(this->x - v2.getX(), this->y - v2.getY());
    }
    // Оператор умножения вектора на скаляр, исходный вектор не меняется, возвращается новый вектор
    Vector2D operator* (const int a) const
    {
        return Vector2D(this->x * a, this->y * a);
    }
};

// Оператор умножения скаляра на вектор, исходный вектор не меняется, возвращается новый вектор
// Неожиданно, правда? Умножение скаляра на вектор - это отдельный оператор, причём описанный *вне* класса.
Vector2D operator* (int a, const Vector2D& v)
{
    return Vector2D(a * v.getX(), a * v.getY());
}
// Вывод вектора, ожидается строго в формате (1; 1)
std::ostream& operator<<(std::ostream& os, const Vector2D& v)
{
    os << "(" << v.getX() << "; " << v.getY() << ")" << endl;
    return os;
}
// Чтение вектора, читает просто две координаты без хитростей
std::istream& operator>>(std::istream &is, Vector2D &v)
{
    int x, y;
    is >> x >> y;

    v.setX(x);
    v.setY(y);
    
    return is;
}

int main()
{
    Vector2D v1;
    cin >> v1;
    cout << v1 << endl;
    Vector2D v2;
    cin >> v2;
    cout << v2 << endl;
    cout << boolalpha << (v1 == v2) << endl;
    cout << boolalpha << (v1 != v2) << endl;
    Vector2D v3 = v1 - v2;
    cout << v3 << endl;
    cout << v3 * 42 << endl;
    cout << 42 * v3 << endl;
    return 0;
}