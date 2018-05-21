import random
import math
import numpy
import operator
from deap import creator, base, tools, algorithms, gp
from GAToolbox import get_ga_toolbox

def main():
	# list all the functions to analyse
	functions = [math.sin]

	# create the toolbox
	toolbox = get_ga_toolbox(functions[0])

	random.seed(318)

	# create a new population
	pop = toolbox.population(n=300)
	hof = tools.HallOfFame(30)
	
	# collect some statistics
	stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
	stats_size = tools.Statistics(len)
	mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
	mstats.register("avg", numpy.mean)
	mstats.register("std", numpy.std)
	mstats.register("min", numpy.min)
	mstats.register("max", numpy.max)

	# do the evolution
	pop, log = algorithms.eaSimple(pop, toolbox, 0.5, 0.1, 40, stats=mstats,
								   halloffame=hof, verbose=True)
	# print(log)
	# print the Hall of Fame together with their fitness value
	for ind in hof:
		print('%.4f'%(ind.fitness.getValues())[0], ':', ind)
	return pop, log, hof

if __name__ == "__main__":
	main()
