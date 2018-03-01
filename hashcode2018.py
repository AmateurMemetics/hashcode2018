#!/usr/bin/env python3
"""Wet Bandits back at it again!"""
import sys
import types
import random
from deap import base, creator, tools

MAX_Y, MAX_X, MAX_VEHICLES, MAX_RIDES, BONUS, TIME_LIMIT = (None for i in range(6))

def evalVRPTW(individual, instance, bonus=0):
    """Fitness function ayy"""
    totalCost = 0
    route = ind2route(individual, instance)
    

def gaVRPTW(individual, instance, indSize, popSize):
    creator.create('FitnessMax', base.Fitness, weights=(1.0,))
    creator.create('Individual', list, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()

    # attribute generator
    toolbox.register('indexes', random.sample, range(1, indSize + 1), indSize)
    # structure initializers
    toolbox.register('individual', tools.initIterate, creator.Individual, toolbox.indexes)
    toolbox.register('population', tools.initRepeat, list, toolbox.individual)
    # operator registering
    toolbox.register('evaluate', evalVRPTW, instance=instance, )
    

class Ride(types.SimpleNamespace):
    def __init__(self, ride_number, start_x, start_y, end_x, end_y, start_time,
                 end_time):
        self.ride_number = ride_number
        self.start_pos = start_x, start_y
        self.end_pos = end_x, end_y
        self.start_time = start_time
        self.end_time = end_time


class Solution(types.SimpleNamespace):
    def __init__(self):
        self.count = [0 for _ in range(MAX_VEHICLES)]
        self.rides = [set() for _ in range(MAX_VEHICLES)]

    def assign(self, vehicle_number, ride_number):
        for vehicle in range(MAX_VEHICLES):
            assert ride_number not in self.rides[vehicle_number]

        self.count[vehicle_number] += 1
        self.rides[vehicle_number].add(ride_number)

    def __str__(self):
        output = ""
        for count, rides in zip(self.count, self.rides):
            output += str(count) + " "
            output += " ".join(str(r) for r in rides)
            output += "\n"
        return output


def main():
    global MAX_Y, MAX_X, MAX_VEHICLES, MAX_RIDES, BONUS, TIME_LIMIT
    rides = []
    with open(sys.argv[1]) as f:
        MAX_Y, MAX_X, MAX_VEHICLES, MAX_RIDES, BONUS, TIME_LIMIT = \
            (int(i) for i in f.readline().split(" "))
        for ride_number, line in enumerate(f.read().splitlines()):
            rides.append(Ride(ride_number,
                              *(int(i) for i in line.split(" "))))

    print("Solving " + sys.argv[1])
    print("Assigning {} vehicles to {} rides in {} time steps"
          .format(MAX_VEHICLES, MAX_RIDES, TIME_LIMIT))
    print("Size ({}, {}), with a bonus of {}".format(MAX_X, MAX_Y, BONUS))

    output = solve(rides)
    with open(sys.argv[1].replace(".in", ".out"), "w") as f:
        f.write(output)


def solve(rides):
    s = Solution()
    rides.sort(key=lambda r: r.start_time)

    vehicle_number = 0
    for ride in rides:
        s.assign(vehicle_number, ride_number=ride.ride_number)
        vehicle_number += 1
        vehicle_number %= MAX_VEHICLES

    return str(s)


def vrptw_solution_to_output(solution):
    assert len(solution) == MAX_VEHICLES
    output = ""
    for rides in solution:
        output += str(len(rides)) + " "
        output += " ".join(str(r) for r in rides)
        output += "\n"
    return output


if __name__ == "__main__":
    main()
