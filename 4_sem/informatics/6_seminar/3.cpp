#include <iostream>
#include <string>

using namespace std;

class Material
{
public:
    virtual float getStress(float strain) = 0;
};

class PlasticMaterial: public Material
{
private: 
    float elasticModulus;
    float strainLimit;
public:
    PlasticMaterial(float elasticModulus, float strainLimit)   
        : elasticModulus(elasticModulus), strainLimit(strainLimit) { }

    float getStress(float strain) override 
    {
        if (strain < 0) 
        {
            return 0;
        }
        else if (strain >= strainLimit)
        {
            return strainLimit * elasticModulus;
        }
        else 
        {
            return strain * elasticModulus;
        }
    }
};

class ElasticMaterial: public Material
{
private: 
    float elasticModulus;
public:
    ElasticMaterial(float elasticModulus)   
        : elasticModulus(elasticModulus) { }

    float getStress(float strain) override 
    {
        if (strain < 0) 
        {
            return 0;
        }

        return strain * elasticModulus;
    }
};


int main()
{
    Material* m;

    m = new ElasticMaterial(100);
    cout << "Material stress is: " << m->getStress(0.1) << endl;
    delete m;

    m = new PlasticMaterial(100, 0.01);
    cout << "Material stress is: " << m->getStress(0.1) << endl;
    delete m;

    return 0;
}