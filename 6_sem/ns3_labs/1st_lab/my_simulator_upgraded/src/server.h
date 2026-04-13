#pragma once

#include "system.h"
#include <memory>

class Server
{
public:
    Server();
    void AddPacket(std::shared_ptr<Packet> packet);
    void SetVerbose(bool verbose);
    void SetMode(int mode, int c);

private:
    System m_system;
};