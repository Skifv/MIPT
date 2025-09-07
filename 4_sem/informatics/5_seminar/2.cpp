#include <iostream>

using namespace std;

const double R = 8.31;

class GasHolder
{
private:
    float V;
    float T;
    float m;
    float M;
public:
    // Создать газгольдер заданного объёма.
    // Температура созданного термостата равна 273 К.
    GasHolder(float v) 
        : V(v), T(273), m(0), M(0) {}
    // Уничтожить газгольдер.
    ~GasHolder()
    {
        V = 0;
        T = 0;
        m = 0;
        M = 0;
    }
    // Впрыск порции газа массой m и молярной массой M.
    // Считать, что газ принимает текущую температуру газгольдера за
    //пренебрежимо малое время.
    void inject(float m, float M)
    {
        if (this->m == 0 || this->M == 0)
        {
            this->M = M;
            this->m = m;
        }
        else
        {
            this->M = (this->m + m) / (this->m / this->M + m / M);
            this->m += m;
        }
    }
    // Подогреть газгольдер на dT градусов.
    // Считать, что нагрев возможен до любых значений температуры.
    void heat(float dT)
    {
        T += dT;
    }
    // Охладить газгольдер на dT градусов.
    // При попытке охладить ниже 0 К температура становится ровно 0 К.
    void cool(float dT)
    {
        T -= dT;
        if (T < 0)
        {
            T = 0;
        }
    }
    // Получить текущее давление в газгольдере.
    // Считать, что для газа верно уравнение состояния PV = (m/M)RT.
    // Значение постоянной R принять 8.31 Дж/(моль*К).
    float getPressure()
    {
        return m / M * R * T;
    }
};

int main()
{
    GasHolder h(1.0);
    h.inject(29, 29);
    cout << "Pressure after operation: " << h.getPressure() << " Pa" << endl;
    h.inject(29, 29);
    cout << "Pressure after operation: " << h.getPressure() << " Pa" << endl;
    h.heat(273);
    cout << "Pressure after operation: " << h.getPressure() << " Pa" << endl;
    h.cool(373);
    cout << "Pressure after operation: " << h.getPressure() << " Pa" << endl;
    h.cool(373);
    cout << "Pressure after operation: " << h.getPressure() << " Pa" << endl;
}