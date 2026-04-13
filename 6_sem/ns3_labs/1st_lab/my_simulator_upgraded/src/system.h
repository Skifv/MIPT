#pragma once

#include "packet.h"
#include "simulator.h"
#include <memory>
#include <vector>
#include <map>

class System
{
public:
    System();
    int GetSystemSize();
    void SetVerbose(bool verbose);
    void SetMode(int mode, int c);
    void AddPacket(std::shared_ptr<Packet>);
    void RemoveFirstPacket();
    ~System();

    struct stats_t
    {
        double sumSojournTime;
        int totalServedPackets;
        int totalArrivedPackets;
        int totalDroppedPackets;
        double sumWaitingTime;
        double lastSystemChange;
        std::map<int, double> systemSizeHist;
        double totalBusyTime;

        stats_t()
            : sumSojournTime(0),
              totalServedPackets(0),
              totalArrivedPackets(0),
              totalDroppedPackets(0),
              sumWaitingTime(0),
              lastSystemChange(0),
              totalBusyTime(0)
        {
        }
    };

private:
    std::vector<std::shared_ptr<Packet>> m_system;
    stats_t m_stats;
    bool m_verbose;
    int m_mode;
    int m_c;
    int m_busyServers;
};