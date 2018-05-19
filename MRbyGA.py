import random
import math
import numpy
import operator
from deap import creator, base, tools, algorithms, gp
from GAToolbox import get_ga_toolbox

def main():
	functions = [math.sin]

	toolbox = get_ga_toolbox(functions[0])

	random.seed(318)

	pop = toolbox.population(n=300)
	hof = tools.HallOfFame(10)
	
	stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
	stats_size = tools.Statistics(len)
	mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
	mstats.register("avg", numpy.mean)
	mstats.register("std", numpy.std)
	mstats.register("min", numpy.min)
	mstats.register("max", numpy.max)

	pop, log = algorithms.eaSimple(pop, toolbox, 0.5, 0.1, 40, stats=mstats,
								   halloffame=hof, verbose=True)
	# print(log)
	for ind in hof:
		print(ind)
	return pop, log, hof

if __name__ == "__main__":
	main()
