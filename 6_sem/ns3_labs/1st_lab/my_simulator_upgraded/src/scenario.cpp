#include <iostream>
#include <memory>
#include <random>
#include "packet-generator.h"
#include "simulator.h"

int main(int argc, char **argv)
{
    if (argc < 6)
    {
        std::cout << "Usage: ./scenario seed lambda mu simTime mode [c] [verbose]" << std::endl;
        std::cout << "Modes: 0 = M/M/1, 1 = M/U/1, 2 = M/M/c/c" << std::endl;
        return -1;
    }
    int seed = atoi(argv[1]);
    double lambda = atof(argv[2]);
    double mu = atof(argv[3]);
    time_t simTime = atof(argv[4]);
    int mode = atoi(argv[5]);

    int c = 1;
    bool verbose = false;
    if (argc >= 7) 
        c = atoi(argv[6]);
    if (argc == 8) 
        verbose = bool(atoi(argv[7]));

    std::shared_ptr<Server> server(new Server());
    server->SetVerbose(verbose);
    server->SetMode(mode, c);

    Simulator sim;
    sim.SetStop(simTime);
    sim.SetSeed(seed);

    std::exponential_distribution<double>::param_type params1(lambda);

    if (mode == 0 || mode == 2)
    {
        std::exponential_distribution<double>::param_type params2(mu);
        PacketGenerator<std::exponential_distribution<double>, std::exponential_distribution<double>> packetGen(params1, params2);
        packetGen.SetServer(server);
        packetGen.Start();
        sim.Run();
    }
    else if (mode == 1)
    {
        std::uniform_real_distribution<double>::param_type params2(0.0, 2.0 / mu);
        PacketGenerator<std::exponential_distribution<double>, std::uniform_real_distribution<double>> packetGen(params1, params2);
        packetGen.SetServer(server);
        packetGen.Start();
        sim.Run();
    }
    
    return 0;
}