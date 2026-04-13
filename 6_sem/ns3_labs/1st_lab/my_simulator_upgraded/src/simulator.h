#pragma once

#include <functional>
#include <map>
#include <random>

class Simulator
{
public:
    Simulator();
    static void Schedule(double time, std::function<void()> handler);
    static double Now();
    static std::mt19937 &Engine();
    static void Run();
    static void SetStop(double simTime);
    static void SetSeed(int seed);
};
