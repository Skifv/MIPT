#include <iostream>
using namespace std;

struct Protoss {
    unsigned long long int id;
    unsigned int health, shield, position[2];
 char name[100];
};

unsigned int count_wounded(Protoss* army, unsigned int n, unsigned int threshold)
{
    int count = 0;

    Protoss * p = army;
    
    for (int i = 0; i < n; i++, p++)
    {
        if (p->health < threshold)
        {
            count++;
        }
    }
    
    return count;
}

int main()
{
    Protoss army[10];
    for (int i=0; i<10; i++)
    {
    army[i].id = i;
        cin >> army[i].health >> army[i].shield >> army[i].position[0] >> army[i].position[1] >> army[i].name;
    }
    cout <<count_wounded(army, 10, 100);
    cout <<endl;
    return 0;
}