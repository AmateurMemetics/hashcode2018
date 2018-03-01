#!/usr/bin/env python3
"""Wet Bandits back at it again!"""
import sys
import types
import random
from deap import base, creator, tools

MAX_Y, MAX_X, MAX_VEHICLES, MAX_RIDES, BONUS, TIME_LIMIT = (None for i in range(6))


def distance_between(start, finish):
    start_x, start_y = start
    finish_x, finish_y = finish
    return abs(start_x - finish_x) + abs(start_y - finish_x)


def ind2route(individual, rides):
    route = [[] for _ in range(MAX_VEHICLES)]
    i = 0
    for vehicle in range(MAX_VEHICLES):
        vehicle_time = 0
        vehicle_location = 0, 0
        while True:
            ride = rides[individual[i]]
            # go to start pos
            vehicle_time += distance_between(vehicle_location, ride.start_pos)
            vehicle_location = ride.start_pos
            if vehicle_time <= ride.start_time:
                vehicle_time = ride.start_time

            # go to end pos
            vehicle_time += distance_between(vehicle_location, ride.end_pos)
            vehicle_location = ride.end_pos
            if vehicle_time <= TIME_LIMIT:
                route[vehicle].append(individual[i])
                i += 1
                if i == len(individual):
                    break
            else:
                break
    return route


def evalVRPTW(individual, rides):
    """Fitness function ayy"""
    total_score = 0
    routes = ind2route(individual)
    for vehicle in routes:
        vehicle_score = 0
        vehicle_time = 0
        vehicle_location = 0, 0
        for ride_number in vehicle:
            ride = rides[ride_number]
            # go to start pos
            vehicle_time += distance_between(vehicle_location, ride.start_pos)
            vehicle_location = ride.start_pos

            # wait for ride to start
            if vehicle_time <= ride.start_time:
                # Additionally, each ride which started exactly in its earliest
                # allowed start step gets an additional timeliness bonus of B.
                vehicle_time = ride.start_time
                vehicle_score += BONUS

            # go to end pos
            vehicle_time += distance_between(vehicle_location, ride.end_pos)
            vehicle_location = ride.end_pos
            if vehicle_time < ride.end_time:
                # Each ride completed before its latest finish earns the number
                # of points equal to the distance between the start intersection
                # and the finish intersection.
                vehicle_score += distance_between(ride.start_pos, ride.end_pos)

        total_score += vehicle_score
    return total_score


def cxPartiallyMatched(ind1, ind2):
    size = min(len(ind1), len(ind2))
    cxpoint1, cxpoint2 = sorted(random.sample(range(size), 2))
    temp1 = ind1[cxpoint1:cxpoint2+1] + ind2
    temp2 = ind1[cxpoint1:cxpoint2+1] + ind2
    ind1 = []
    for x in temp1:
        if x not in ind1:
            ind1.append(x)
    ind2 = []
    for x in temp2:
        if x not in ind2:
            ind2.append(x)
    return ind1, ind2


def mutInverseIndexes(individual):
    start, stop = sorted(random.sample(range(len(individual)), 2))
    individual = individual[:start] + individual[stop:start-1:-1] + individual[stop+1:]
    return individual,


def gaVRPTW(individual, instance, indSize, popSize, cxPb, mutPb, nGen):
    creator.create('FitnessMax', base.Fitness, weights=(1.0,))
    creator.create('Individual', list, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()

    # attribute generator
    toolbox.register('indexes', random.sample, range(1, indSize + 1), indSize)
    # structure initializers
    toolbox.register('individual', tools.initIterate, creator.Individual, toolbox.indexes)
    toolbox.register('population', tools.initRepeat, list, toolbox.individual)
    # operator registering
    toolbox.register('evaluate', evalVRPTW, instance=instance)
    toolbox.register('select', tools.selRoulette)
    toolbox.register('mate', cxPartiallyMatched)
    toolbox.register('mutate', mutInverseIndexes)
    pop = toolbox.population(n=popSize)
    # evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    # begin evolution
    for g in range(nGen):
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cxPb:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values
        for mutant in offspring:
            if random.random() < mutPb:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        # evaluate individuals with an invalid fitness
        invalidInd = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalidInd)
        for ind, fit in zip(invalidInd, fitnesses):
            ind.fitness.values = fit
        pop[:] = offspring
        bestInd = tools.selBest(pop, 1)[0]
        ind2route(bestInd, instance)


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
