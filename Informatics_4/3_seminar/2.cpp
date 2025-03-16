#include <iostream>
#include <vector>
#include <set>

using namespace std;

vector<int> Range(int n);
vector<int> Range(int start, int end);

void swap(int& a, int& b);

class Matrix {
    private:
        vector<vector<int>> matrix;
        int n, m;
    public:
        Matrix(int rows, int cols)
        : matrix(rows)
        , n(rows)
        , m(cols)
        {
            for (int i : Range(n)) 
            {
                matrix[i].resize(m, 0);
            }
        }
    
        void read()
        {
            for (int i : Range(n))
            {
                for (int j : Range(m))
                {
                    cin >> matrix[i][j];
                }
            }
        }
    
        void print()
        {
            for (int i : Range(n))
            {
                for (int j : Range(m))
                {
                    cout << matrix[i][j] << " ";
                }
                cout << endl;
            }
        }
    
        void transpond()
        {
            vector<vector<int>> copied_matrix = matrix;
            swap(n, m);
    
            // меняем размер массива
            matrix.resize(n);
            for (int i : Range(n))
            {
                matrix[i].resize(m, 0);
            }
    
            // заполняем массив новыми значениями
            for (int i : Range(n))
            {
                for(int j : Range(m))
                {
                    matrix[i][j] = copied_matrix[j][i];
                }
            }
        }
    };

int main() 
{
    int n;
    cin >> n;

    Matrix matrix(n, n);
    matrix.read();
    matrix.transpond();
    matrix.print();
}

void swap(int& a, int& b)
{
    int tmp = a;
    a = b;
    b = tmp;
}

vector<int> Range(int n)
{
    vector<int> range(n);
    for (int i = 0; i < n; i++)
    {
        range[i] = i;
    }
    return range;
}

vector<int> Range(int start, int end)
{
    int n = end - start;
    vector<int> range(n);
    for (int i = start; i < end; i++)
    {
        range[i - start] = i;
    }

    return range;
}