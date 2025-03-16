#include <iostream>
#include <vector>
#include <set>
#include <type_traits>

using namespace std;


void swap(int& a, int& b)
{
    int tmp = a;
    a = b;
    b = tmp;
}

void Clear(void)
{
    char c;
    while ((c = getchar()) != '\n' && c != EOF)
    {
        ;
    }
}

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
        for (int i = 0; i < n; i++)
        {
            for (int j = 0; j < m; j++)
            {
                cin >> matrix[i][j];
            }            
        }
    }

    void print() const
    {
        for (int i = 0; i < n; i++)
        {
            for (int j = 0; j < m; j++)
            {
                cout << matrix[i][j] << " ";
                
            }
            cout << endl;
        }
    }

    T column_sum(int j) const
    {
        T sum = 0;
        for (int i = 0; i < n; i++)
        {
            sum += matrix[i][j];
        }
        return sum;
    }

    T row_sum(int i) const
    {
        T sum = 0;
        for (int j = 0 ; j < m; j++)
        {
            sum += matrix[i][j];
        }
        return sum;
    }

    vector<T> column_sums() const
    {
        vector<T> res(m);
        for (int i = 0; i < m; i++)
        {
            res[i] = column_sum(i);
        }
        return res;
    }

    vector<T> row_sums() const
    {
        vector<T> res(n);
        for (int i = 0; i < n; i++)
        {
            res[i] = row_sum(i);
        }
        return res;
    }

    void transpond()
    {
        vector<vector<T>> copied_matrix = matrix;
        swap(n, m);

        // меняем размер массива
        matrix.assign(n, vector<T>(m, T()));

        // заполняем массив новыми значениями
        for (int i = 0; i < n; i++)
        {
            for(int j = 0; j < m; j++)
            {
                matrix[i][j] = copied_matrix[j][i];
            }
        }
    }
};

int FindBestColumn(const Matrix<int>& matrix)
{
    int max_sum = 0, column = 0;

    vector<int> column_sums = matrix.column_sums();
    for (size_t i = 0; i < column_sums.size(); i++)
    {
        if (column_sums[i] > max_sum)
        {
            max_sum = column_sums[i];
            column = i; 
        }
    }
    return column;
}

int main() 
{
    int n = 0, m = 0;
    cin >> n >> m;

    Matrix matrix(n, m);
    matrix.read();
    
    // ищет столбец с наибольшей суммой элементов
    int column = FindBestColumn(matrix);

    cout << column << endl;

}
