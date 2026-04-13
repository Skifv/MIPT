#include "packet.h"

Packet::Packet(double arrivalTime, double serviceTime)
{
    m_arrivalTime = arrivalTime;
    m_serviceTime = serviceTime;
}

double Packet::GetArrivalTime()
{
    return m_arrivalTime;
}

double Packet::GetServiceTime()
{
    return m_serviceTime;
}
