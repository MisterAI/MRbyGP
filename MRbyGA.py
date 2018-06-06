import random
import math
import numpy
import sympy
from FitnessEvaluation import convert_to_sympy_expr
from deap import tools, algorithms
from GAToolbox import get_toolbox

def main():
	# list all the functions to analyse
	functions = [math.sin]

	# create the toolbox
	toolbox = get_toolbox(functions[0])

	# random.seed(318)

	# create a new population
	pop = toolbox.population(n=300)
	hof = tools.ParetoFront()
	
	# collect some statistics
	stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
	stats_size = tools.Statistics(len)
	mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
	mstats.register("avg", lambda data: numpy.around(numpy.mean(data), decimals=4))
	mstats.register("std", lambda data: numpy.around(numpy.std(data), decimals=4))
	mstats.register("min", lambda data: numpy.around(numpy.min(data), decimals=4))
	mstats.register("max", lambda data: numpy.around(numpy.max(data), decimals=4))

	# do the evolution
	pop, log = algorithms.eaMuPlusLambda(pop, toolbox, mu=300, lambda_=400, cxpb=0.5, 
		mutpb=0.1, ngen=40, stats=mstats, halloffame=hof, verbose=True)

	my_hof = [ind for ind in pop if 0.001 >= ind.fitness.getValues()[0]]
	my_hof = sorted(my_hof, key=lambda individual: individual.fitness.getValues()[1])
	# print the Hall of Fame together with their fitness value
	for ind in my_hof:
		# print('%.4f, %f'%(ind.fitness.getValues()), ':')
		# print(ind)
		sympy.pprint(convert_to_sympy_expr(ind))
	return pop, log, hof

if __name__ == "__main__":
	main()
