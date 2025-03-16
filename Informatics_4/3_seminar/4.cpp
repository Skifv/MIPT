#include <iostream>
#include <vector>
#include <set>
#include <type_traits>

using namespace std;

vector<int> Range(int n);
vector<int> Range(int start, int end);

void swap(int& a, int& b);

void Clear(void);

template <typename T = int>
class Matrix {
private:
    vector<vector<T>> matrix;
    int n, m;
public:
    Matrix(int rows, int cols)
    : matrix(rows)
    , n(rows)
    , m(cols)
    {
        matrix.assign(n, vector<T>(m, T()));
    }

    void read()
    {
        for (int i : Range(n))
        {
            if (is_same<T, char>::value)
            {
                Clear();
                for (int j : Range(m))
                {
                    cin.get(matrix[i][j]);
                }
            }
            else
            {
                for (int j : Range(m))
                {
                    cin >> matrix[i][j];
                }
            }
            
        }
    }

    void print()
    {
        for (int i : Range(n))
        {
            for (int j : Range(m))
            {
                if (is_same<T, char>::value)
                {
                    cout << matrix[i][j] << "";
                }
                else
                {
                    cout << matrix[i][j] << " ";
                }
            }
            cout << endl;
        }
    }

    void transpond()
    {
        vector<vector<T>> copied_matrix = matrix;
        swap(n, m);

        // меняем размер массива
        matrix.assign(n, vector<T>(m, T()));

        // заполняем массив новыми значениями
        for (int i : Range(n))
        {
            for(int j : Range(m))
            {
                if (is_same<T, char>::value)
                {
                    matrix[i][j] = copied_matrix[j][n - 1 - i];
                }
                else
                {
                    matrix[i][j] = copied_matrix[j][i];
                }
            }
        }
    }
};

int main() 
{
    int n = 0, m = 0;
    cin >> n >> m;

    Matrix<char> matrix(n, m);
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

void Clear(void)
{
    char c;
    while ((c = getchar()) != '\n')
    {
        ;
    }
}
