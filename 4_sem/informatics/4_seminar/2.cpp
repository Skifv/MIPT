#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <sstream>

using namespace std;    

// функции для использования for (int i : Range(n))
vector<int> Range(int n);
vector<int> Range(int start, int end);

// читает последовательно n строк (команд), возвращая их в виде массива строк
vector<string> ReadCommands(int n);
void           ProcessCommands(const vector<string>& commands);
// считает количество тех, кто встревожен
int            AmountOfWorry(const vector<int>& queue);

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

int AmountOfWorry(const vector<int>& queue) 
{
    int res = 0;
    for (auto i : queue) 
    {
        if (i == 1) 
        {
            res++;
        }
    }
    return res;
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

    vector<int> queue; // vector[i] == 1 -> worry, vector[i] == 0 -> not worry

    for (auto command : commands) 
    {
        istringstream iss(command); // iss - поток ввода (содержит команду)
        
        string cmd;
        iss >> cmd;

        int arg;
        if (cmd == "WORRY") 
        {
            iss >> arg;
            queue[arg] = 1;
        }
        else if (cmd == "QUIET")
        {
            iss >> arg;
            queue[arg] = 0;
        }
        else if (cmd == "COME")
        {
            iss >> arg;

            if (arg > 0)
            {
                queue.insert(queue.end(), arg, 0);
            }
            else
            {
                queue.resize(queue.size() + arg); // - abs(arg) == + arg 
            }
        }
        else if (cmd == "WORRY_COUNT")
        {
            cout << AmountOfWorry(queue) << endl;
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
