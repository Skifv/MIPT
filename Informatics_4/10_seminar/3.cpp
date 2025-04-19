#include <iostream>
#include <string>

using namespace std;

template<typename T>
class Vector2D
{
private:
    T x, y;
public:
    // Конструкторы
    Vector2D() : x(0), y(0) {}
    Vector2D(T x, T y) : x(x), y(y) {}
    // Деструктор
    ~Vector2D() {}
    // Получение координат
    T getX() const
    {
        return x;
    }
    T getY() const
    {
        return y;
    }
    // Задание координат
    void setX(T x)
    {
        this->x = x;
    }
    void setY(T y)
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
    template<typename U>
    Vector2D operator* (const U a) const
    {
        return Vector2D(this->x * a, this->y * a);
    }
};

// Внешний оператор умножения скаляра на вектор слева
template<typename T, typename U>
Vector2D<T> operator*(U scalar, const Vector2D<T>& vec) {
    return vec * scalar;
}

// Оператор вывода вектора
template<typename T>
std::ostream& operator<<(std::ostream& os, const Vector2D<T>& v) {
    os << "(" << v.getX() << "; " << v.getY() << ")";
    return os;
}

// Оператор ввода вектора
template<typename T>
std::istream& operator>>(std::istream& is, Vector2D<T>& v) {
    T x, y;
    is >> x >> y;
    v.setX(x);
    v.setY(y);
    return is;
}

int main()
{
    Vector2D<int> v1;
    cin >> v1;
    cout << "Read vector: " << v1 << endl;
    cout << "Vector multiplied by 42: " << v1 * 42 << endl;
    Vector2D<double> v2;
    cin >> v2;
    cout << "Read vector: " << v2 << endl;
    cout << "Vector multiplied by 42: " << 42 * v2 << endl;
}