#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

class Box
{
private:
    int price;
    int candles;
public:
    Box(int price, int candles)
    {
        this->price = price;
        this->candles = candles;
    }

    int get_price() const
    {
        return price;
    }

    int get_candles() const
    {
        return candles;
    }

    bool operator < (const Box& other) const
    {
        return price < other.price;
    }

    bool operator > (const Box& other) const
    {
        return price > other.price;
    }

    bool operator == (const Box& other) const
    {
        return price == other.price;
    }

    bool operator != (const Box& other) const
    {
        return price != other.price;
    }

    bool operator <= (const Box& other) const
    {
        return *this < other || *this == other;
    }

    bool operator >= (const Box& other) const
    {
        return *this > other || *this == other;
    }

    void print_box()
    {
        cout << price << " " << candles << endl;
    }
};

struct PurchasedItems
{
    int total_boxed;
    int total_candles;
};

vector<Box> ReadBoxes(int n)
{
    int price = 0;
    int candles = 0;

    vector<Box> boxes;
    for (int i = 0; i < n; i++)
    {
        cin >> price >> candles;
        cin.ignore();

        Box box = Box(price, candles);
        boxes.push_back(box);
    }

    return boxes;
}

void PrintBoxes(vector<Box> boxes)
{
    for (auto i : boxes)
    {
        i.print_box();
    }
}

PurchasedItems BuyBoxes (vector<Box> boxes, int S)
{
    int bought_boxes = 0;
    int bought_candles = 0;


    for (int i = 0; S > 0 && i < boxes.size(); i++)
    {
        if (boxes[i].get_price() <= S)
        {
            bought_boxes++;
            bought_candles += boxes[i].get_candles();
            S -= boxes[i].get_price();
        }
    }

    return PurchasedItems{bought_boxes, bought_candles};
}

int main()
{
    int n = 0;
    cin >> n;
    cin.ignore();

    vector<Box> boxes = ReadBoxes(n);

    int S = 0;
    cin >> S;
    cin.ignore();

    // по возрастанию цены коробок
    //если коробки одной цены - по возрастанию количества конфет
    sort(boxes.begin(), boxes.end(), [](Box a, Box b)
    {
        if (a < b)
        {
            return true;
        }
        if (a == b)
        {
            return a.get_candles() > b.get_candles();
        }
        else
        {
            return false;
        }

    });

    PrintBoxes(boxes);

    PurchasedItems bought_boxes_and_candles = BuyBoxes(boxes, S);

    cout << bought_boxes_and_candles.total_boxed << " ";
    cout << bought_boxes_and_candles.total_candles << endl;

}

