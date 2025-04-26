#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

class ResultsTable
{
private:
    vector<unsigned int> resultsTable;
public:
    ResultsTable() : resultsTable(0) {}
    // Зарегистрировать новый результат,
    // нас волнуют только баллы, имена пользователей не важны
    void addResult(unsigned int score)
    {
        resultsTable.push_back(score);
        
        sort(resultsTable.begin(), resultsTable.end(), [](unsigned int a, unsigned int b)
        {
            return a > b;
        });
    }
    // Получить минимальный балл из всех результатов за всё время
    unsigned int getMinScore() const
    {
        unsigned int minScore;

        resultsTable.size() > 0 ? minScore = resultsTable[0] : minScore = 0;

        for (unsigned int score : resultsTable)
        {
            if (score < minScore)
            {
                minScore = score;
            }
        }

        return minScore;
    }
    // Получить, сколько баллов у игрока на заданном месте.
    // Внимание: места нумеруются так, как это принято на турнирах, то есть
    // лучший результат - 1-ое место, за ним 2-ое место и т.д.
    unsigned int getScoreForPosition(unsigned int positionNumber) const
    {
        if (positionNumber > 0 && positionNumber <= resultsTable.size())
        {
            return resultsTable[positionNumber - 1];
        }
        else
        {
            throw out_of_range("Invalid position number");
        }
    }
};

int main()
{
    ResultsTable t;

    t.addResult(30);
    t.addResult(85);
    t.addResult(12);
    t.addResult(31);

    cout << "1st place score: " << t.getScoreForPosition(1) << endl;
    cout << "2nd place score: " << t.getScoreForPosition(2) << endl;
    cout << "3rd place score: " << t.getScoreForPosition(3) << endl;
    cout << "Min score during the tournament: " << t.getMinScore() << endl;

    return 0;
}