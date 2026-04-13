#include "server.h"

Server::Server()
{
}

void Server::AddPacket(std::shared_ptr<Packet> p)
{
    m_system.AddPacket(p);
}

void Server::SetVerbose(bool verbose)
{
    m_system.SetVerbose(verbose);
}

void Server::SetMode(int mode, int c)
{
    m_system.SetMode(mode, c);
}