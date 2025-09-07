#include <string>
#include <unordered_map>
#include <climits> // для LONG_MIN и LONG_MAX
#include <iostream>

using namespace std;

class TelemetryController
{
public:
    // Обработать событие от устройства
    void handleEvent(const string& device, long value)
    {
        // Если устройство новое - инициализируем для него данные
        if (deviceStats.find(device) == deviceStats.end())
        {
            deviceStats[device] = {1, value, value};
        }
        else
        {
            // Увеличиваем счетчик событий
            deviceStats[device].count++;
            // Обновляем минимальное значение
            if (value < deviceStats[device].minValue)
                deviceStats[device].minValue = value;
            // Обновляем максимальное значение
            if (value > deviceStats[device].maxValue)
                deviceStats[device].maxValue = value;
        }
    }

    // Получить количество событий от устройства
    unsigned int getEventsCount(const string& device) const
    {
        auto it = deviceStats.find(device);
        return it != deviceStats.end() ? it->second.count : 0;
    }

    // Получить минимальное значение от устройства
    long getMinValue(const string& device) const
    {
        auto it = deviceStats.find(device);
        return it != deviceStats.end() ? it->second.minValue : LONG_MAX;
    }

    // Получить максимальное значение от устройства
    long getMaxValue(const string& device) const
    {
        auto it = deviceStats.find(device);
        return it != deviceStats.end() ? it->second.maxValue : LONG_MIN;
    }

private:
    // Структура для хранения статистики по устройству
    struct DeviceData
    {
        unsigned int count = 0;  // количество событий
        long minValue = LONG_MAX; // минимальное значение
        long maxValue = LONG_MIN; // максимальное значение
    };

    // Хранилище статистики по устройствам
    unordered_map<string, DeviceData> deviceStats;
};


int main()
{
    TelemetryController tc;
    tc.handleEvent("d1", 42);
    tc.handleEvent("d1", -42);
    tc.handleEvent("d2", 100);
    cout << "Events count for d1: " << tc.getEventsCount("d1") << endl;
    cout << "Min value for d1: " << tc.getMinValue("d1") << endl;
    cout << "Max value for d1: " << tc.getMaxValue("d1") << endl;
    
    return 0;
}