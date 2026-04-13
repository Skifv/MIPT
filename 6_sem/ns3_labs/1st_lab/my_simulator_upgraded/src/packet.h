#pragma once

class Packet
{
public:
    Packet(double arrivalTime, double serviceTime);
    double GetArrivalTime();
    double GetServiceTime();

private:
    double m_arrivalTime;
    double m_serviceTime;
};
