#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <sstream>
#include <iterator>

using namespace std;    

// функции для использования for (int i : Range(n))
vector<int> Range(int n);
vector<int> Range(int start, int end);

// читает последовательно n строк (команд), возвращая их в виде массива строк
vector<string> ReadCommands(int n);
void           ProcessCommands(const vector<string>& commands);

// чистит буфер ввода до \n
void Clear(void);


int main() {
    int n;
    cin >> n;

    // переходим на новую строку
    Clear();

    vector<string> commands = ReadCommands(n);
    ProcessCommands(commands);

    return 0;
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

vector<string> ReadCommands(int n) 
{   

    vector<string> commands(n);

    for (int i : Range(n)) 
    {
        string command;
        getline(cin, command);
        commands[i] = command;
    }

    return commands;
}

void ProcessCommands(const vector<string>& commands) 
{
    // {месяц, количество дней в нем}
    map<int, int> number_of_days = {{1, 31}, {2, 28}, {3, 31}, {4, 30} , {5, 31} , {6, 30},
                                    {7, 31}, {8, 31}, {9, 30}, {10, 31}, {11, 30}, {12, 31}}; 
    
    int previous_month = 12;
    int current_month = 1;
    
    // {день, массив из слов(планов)}
    map<int, vector<string>> plans;

    for (auto command : commands) 
    {
        istringstream iss(command); // iss - поток ввода (содержит команду)
        
        string cmd;
        iss >> cmd;

        int day;
        string plan_name;
        if (cmd == "ADD") // 2 аргумента, добавляет дело plan_name в день day
        {
            iss >> day >> plan_name;
            plans[day].push_back(plan_name);
        }
        else if (cmd == "DUMP") // 1 аргумент, выводит список дел в дне day
        {
            iss >> day;

            // если есть планы на день
            if (plans.count(day))
            {
                cout << plans[day].size();

                for (string i : plans[day])
                {
                    cout << " " << i;
                }
            }
            else // если нет
            {
                cout << 0;
            }
            

            cout << endl;
        }
        else if (cmd == "NEXT") // 0 аргументов
        {
            // переводим счетчик месяца
            if (current_month == 1)
            {
                previous_month = 1;
                current_month++;
            }
            else if (current_month == 12)
            {
                previous_month++;
                current_month = 1;
            }
            else
            {
                previous_month++;
                current_month++;
            }

            // число дней в месяце уменьшилось
            if (number_of_days[current_month] < number_of_days[previous_month])
            {
                for (int i : Range(number_of_days[current_month] + 1, number_of_days[previous_month] + 1))
                {
                    if (plans.count(i))
                    {
                        // вставляем планы в конец
                        vector<string>& v = plans[number_of_days[current_month]];
                        v.insert(end(v), begin(plans[i]), end(plans[i]));
                    }

                    // стираем день
                    plans.erase(i);
                }
            }
            

        }
        else if (cmd == "DUMP_ALL") // 0 аргументов (доп опция, не по заданию)
        {
            cout << "*** Plans for month " << current_month << " ***" << endl;
            for (auto& item : plans)
            {
                cout << item.first << " ";
                for (auto& plan : item.second)
                {
                    cout << plan << " ";
                }
                cout << endl;
            }
            cout << "***" << endl;
        }
    }
}

void Clear(void)
{
    char c;
    while ((c = getchar()) != '\n')
    {
        ;
    }
}
