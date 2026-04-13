#include "system.h"
#include <iostream>
#include <functional>

System::System()
{
    m_verbose = false;
    m_mode = 0;
    m_c = 1;
    m_busyServers = 0;
}

int System::GetSystemSize()
{
    return m_system.size();
}

void System::SetVerbose(bool verbose)
{
    m_verbose = verbose;
}

void System::SetMode(int mode, int c)
{
    m_mode = mode;
    m_c = c;
}

void System::AddPacket(std::shared_ptr<Packet> packet)
{
    m_stats.totalArrivedPackets++;

    if (m_mode == 0 || m_mode == 1) // M/M/1 and M/U/1
    {
        m_stats.systemSizeHist[m_system.size()] += Simulator::Now() - m_stats.lastSystemChange;
        m_stats.totalBusyTime += (!m_system.empty()) ? (Simulator::Now() - m_stats.lastSystemChange) : 0;
        m_stats.lastSystemChange = Simulator::Now();

        m_system.push_back(packet);
        if (m_system.size() == 1)
        {
            std::function<void()> callback = std::bind(&System::RemoveFirstPacket, this);
            Simulator::Schedule(packet->GetServiceTime(), callback);
        }
    }
    else if (m_mode == 2) // M/M/c/c. Теперь у нас не FIFO, поэтому использовать RemoveFirstPacket будет некорректно
    {   
        if (m_busyServers < m_c)
        {
            m_stats.systemSizeHist[m_busyServers] += Simulator::Now() - m_stats.lastSystemChange;
            m_stats.totalBusyTime += (m_busyServers > 0) ? (Simulator::Now() - m_stats.lastSystemChange) : 0;
            m_stats.lastSystemChange = Simulator::Now();

            m_busyServers++;
            m_stats.sumSojournTime += packet->GetServiceTime();
            m_stats.totalServedPackets++;
            
            std::function<void()> callback = [this]() {
                
                this->m_stats.systemSizeHist[this->m_busyServers] += Simulator::Now() - this->m_stats.lastSystemChange;
                this->m_stats.totalBusyTime += (this->m_busyServers > 0) ? (Simulator::Now() - this->m_stats.lastSystemChange) : 0;
                this->m_stats.lastSystemChange = Simulator::Now();

                this->m_busyServers--;
            };
            Simulator::Schedule(packet->GetServiceTime(), callback);
        }
        else
        {
            // Мест нет, заявка отбрасывается
            m_stats.totalDroppedPackets++;
        }
    }
}

void System::RemoveFirstPacket()
{
    m_stats.sumSojournTime += Simulator::Now() - m_system.front()->GetArrivalTime();
    m_stats.sumWaitingTime += Simulator::Now() - m_system.front()->GetArrivalTime() - m_system.front()->GetServiceTime();
    m_stats.totalServedPackets++;
    m_stats.systemSizeHist[m_system.size()] += Simulator::Now() - m_stats.lastSystemChange;
    m_stats.totalBusyTime += (!m_system.empty()) ? (Simulator::Now() - m_stats.lastSystemChange) : 0;
    m_stats.lastSystemChange = Simulator::Now();

    m_system.erase(m_system.begin());
    if (!m_system.empty())
    {
        std::function<void()> callback = std::bind(&System::RemoveFirstPacket, this);
        Simulator::Schedule(m_system.front()->GetServiceTime(), callback);
    }
}

System::~System()
{
    if (m_mode == 0 || m_mode == 1)
    {
        m_stats.systemSizeHist[m_system.size()] += Simulator::Now() - m_stats.lastSystemChange;
        m_stats.totalBusyTime += (!m_system.empty()) ? (Simulator::Now() - m_stats.lastSystemChange) : 0;
    }
    else if (m_mode == 2)
    {
        m_stats.systemSizeHist[m_busyServers] += Simulator::Now() - m_stats.lastSystemChange;
        m_stats.totalBusyTime += (m_busyServers > 0) ? (Simulator::Now() - m_stats.lastSystemChange) : 0;
    }

    double avgSystemSize = 0;
    for (const auto &it : m_stats.systemSizeHist)
    {
        avgSystemSize += it.first * it.second / Simulator::Now();
    }

    double dropProb = (double)m_stats.totalDroppedPackets / m_stats.totalArrivedPackets;

    double avgSojournTime = m_stats.totalServedPackets > 0 ? m_stats.sumSojournTime / m_stats.totalServedPackets : 0;
    double avgWaitTime = m_stats.totalServedPackets > 0 ? m_stats.sumWaitingTime / m_stats.totalServedPackets : 0;
    
    // Для многоканальной системы логичнее считать загрузку серверов как (среднее число заявок / число каналов)
    double util = (m_mode == 2) ? (avgSystemSize / m_c) : (m_stats.totalBusyTime / Simulator::Now());

    if (m_verbose)
    {
        std::cout << "===================PRINT SYSTEM STATS======================" << std::endl;
        std::cout << "Total served packets: " << m_stats.totalServedPackets << std::endl;
        std::cout << "Total dropped packets: " << m_stats.totalDroppedPackets << std::endl;
        std::cout << "Total arrived packets: " << m_stats.totalArrivedPackets << std::endl;
        std::cout << "Average Sojourn time: " << avgSojournTime << std::endl;
        std::cout << "Average waiting time: " << avgWaitTime << std::endl;
        std::cout << "Average system size: " << avgSystemSize << std::endl;
        std::cout << "Utilization: " << util << std::endl;
        std::cout << "Drop Probability: " << dropProb << std::endl;
        std::cout << "===========================================================" << std::endl;
    }
    else
    {
        std::cout << m_stats.totalServedPackets << ' ' 
                  << avgSojournTime << ' '
                  << avgWaitTime << ' ' 
                  << avgSystemSize << ' ' 
                  << util << ' ' 
                  << dropProb << std::endl;
    }

    m_system.clear();
}