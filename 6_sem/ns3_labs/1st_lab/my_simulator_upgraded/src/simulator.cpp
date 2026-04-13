#include "simulator.h"
#include <iostream>

static std::map<double, std::function<void()>> g_eventQueue;
static double g_currentTime = 0;
static double g_simTime = 0;
static std::mt19937 g_engine;

Simulator::Simulator()
{
}

void Simulator::Schedule(double time, std::function<void()> handler)
{
    g_eventQueue.insert(std::pair<double, std::function<void()>>(g_currentTime + time, handler));
}

double Simulator::Now()
{
    return g_currentTime;
}

std::mt19937 &Simulator::Engine()
{
    return g_engine;
}

void Simulator::Run()
{
    while (!g_eventQueue.empty() && g_currentTime <= g_simTime)
    {
        auto it = g_eventQueue.begin();
        if (it->first > g_simTime)
        {
            g_eventQueue.clear();
            break;
        }
        g_currentTime = it->first;
        it->second();
        g_eventQueue.erase(g_eventQueue.begin());
    }
}

void Simulator::SetStop(double simTime)
{
    g_simTime = simTime;
}

void Simulator::SetSeed(int seed)
{
    g_engine.seed(seed);
}
