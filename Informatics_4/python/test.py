from numpy import random
import time

tries = []
count = 0
for j in range(1000):
    for i in range(2500):
        count += random.poisson(lam=0.02, size=None)
    tries.append(count)
    count = 0
    print(sum(tries) / len(tries))
    