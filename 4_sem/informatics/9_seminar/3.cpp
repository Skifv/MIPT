#include <iostream>
#include <string>
#include <vector>

using namespace std;


class VectorN
{
private:
    vector<int> vec;
public:
    // Конструктор вектора размерности n
    VectorN(unsigned int n) : vec(n, 0) {}
    // Деструктор
    ~VectorN() {}
    // Получение размерности вектора
    unsigned getSize() const
    {
        return vec.size();
    }
    // Получение значения i-ой координаты вектора,
    // i находится в диапазоне от 0 до n-1
    int getValue(unsigned int i) const
    {
        return vec[i];
    }
    // Задание значения i-ой координаты вектора равным value,
    // i находится в диапазоне от 0 до n-1
    void setValue(unsigned int i, int value)
    {
        vec[i] = value;
    }
    /*
    * Далее реализуйте перегруженные операторы
    */

    bool operator==(const VectorN& v2)
    {
        if (this->getSize() != v2.getSize())
        {
            return false;
        }
    
        for (unsigned int i = 0; i < this->getSize(); i++)
        {
            if (vec[i] == v2.getValue(i))
            {
                return false;
            }
        }

        return true;
    }
    // Оператор != проверяет два вектора на неравенство,
    // они не равны, если хотя бы одна координата отличается

    bool operator!=(const VectorN& v)
    {
        return !(*this == v);
    }
    // Оператор + складывает два вектора покоординатно,
    // возвращает результат как новый экземпляр вектора
    VectorN operator+(const VectorN& v2)
    {
        VectorN result(this->getSize());

        for (unsigned int i = 0; i < this->getSize(); i++)
        {
            result.setValue(i, this->getValue(i) + v2.getValue(i));
        }

        return result;
    }
    // Оператор * умножает вектор на скаляр типа int покоординатно,
    // возвращает результат как новый экземпляр вектора.
    // Умножение должно работать при любом порядке операндов.
};

VectorN operator * (int a, const VectorN& v)
{
    VectorN result(v.getSize());

    for (unsigned int i = 0; i < v.getSize(); i++)
    {
        result.setValue(i, a * v.getValue(i));
    }

    return result;
}

VectorN operator * (const VectorN& v, int a)
{
    VectorN result(v.getSize());

    for (unsigned int i = 0; i < v.getSize(); i++)
    {
        result.setValue(i, a * v.getValue(i));
    }

    return result;
}

int main()
{
    VectorN a(4);
    a.setValue(0, 0);
    a.setValue(1, 1);
    a.setValue(2, 2);
    a.setValue(3, 3);
    VectorN b(4);
    b.setValue(0, 0);
    b.setValue(1, -1);
    b.setValue(2, -2);
    b.setValue(3, -3);
    cout << (a == b) << endl;
    cout << (a != b) << endl;
    VectorN c = a + b;
    VectorN d = 5 * c;
    for(unsigned int i = 0; i < a.getSize(); ++i)
    cout << d.getValue(i) << endl;

    return 0;
}