#pragma once

#include "simulator.h"
#include "server.h"
#include "packet.h"
#include <memory>

template <typename ArrivalDistribution, typename ServiceDistribution>
class PacketGenerator
{
    using ArrivalParamType = typename ArrivalDistribution::param_type;
    using ServiceParamType = typename ServiceDistribution::param_type;

public:
    PacketGenerator(const ArrivalParamType &, const ServiceParamType &);
    void SetServer(std::shared_ptr<Server> server);
    void Start();
    void NewPacket();
    void PacketServed();

private:
    ArrivalDistribution m_arrivalGen;
    ServiceDistribution m_serviceGen;
    std::shared_ptr<Server> m_server;
};

template <typename ArrivalDistribution, typename ServiceDistribution>
PacketGenerator<ArrivalDistribution, ServiceDistribution>::PacketGenerator(const ArrivalParamType &arrivalParams, const ServiceParamType &serviceParams)
    : m_arrivalGen(arrivalParams),
      m_serviceGen(serviceParams)
{
}

template <typename ArrivalDistribution, typename ServiceDistribution>
void PacketGenerator<ArrivalDistribution, ServiceDistribution>::SetServer(std::shared_ptr<Server> server)
{
    m_server = server;
}

template <typename ArrivalDistribution, typename ServiceDistribution>
void PacketGenerator<ArrivalDistribution, ServiceDistribution>::Start()
{
    std::function<void()> callback = std::bind(&PacketGenerator<ArrivalDistribution, ServiceDistribution>::NewPacket, this);
    Simulator::Schedule(m_arrivalGen(Simulator::Engine()), callback);
}

template <typename ArrivalDistribution, typename ServiceDistribution>
void PacketGenerator<ArrivalDistribution, ServiceDistribution>::NewPacket()
{
    std::shared_ptr<Packet> p(new Packet(Simulator::Now(), m_serviceGen(Simulator::Engine())));
    m_server->AddPacket(p);
    std::function<void()> callback = std::bind(&PacketGenerator<ArrivalDistribution, ServiceDistribution>::NewPacket, this);
    Simulator::Schedule(m_arrivalGen(Simulator::Engine()), callback);
}
