import random
import math
import numpy
import sympy
from FitnessEvaluation import convert_to_sympy_expr
from deap import tools, algorithms
from GAToolbox import get_toolbox
import sys
import datetime
import time

def main():
	# list all the functions to analyse
	functions = [math.sin]

	# create the toolbox
	toolbox = get_toolbox(functions[0])

	# random.seed(318)

	# create a new population
	pop = toolbox.population(n=1000)
	hof = tools.ParetoFront()
	
	# collect some statistics
	stats_fit_mse = tools.Statistics(lambda ind: ind.fitness.values[0])
	stats_fit_dist = tools.Statistics(lambda ind: ind.fitness.values[1])
	stats_size = tools.Statistics(len)
	mstats = tools.MultiStatistics(
		fitness_mse=stats_fit_mse, 
		fitness_dist=stats_fit_dist, 
		size=stats_size)
	mstats.register("avg", lambda data: numpy.around(numpy.mean(data), decimals=4))
	# mstats.register("std", lambda data: numpy.around(numpy.std(data), decimals=4))
	mstats.register("min", lambda data: numpy.around(numpy.min(data), decimals=4))
	mstats.register("max", lambda data: numpy.around(numpy.max(data), decimals=4))

	start = time.time()
	# do the evolution
	pop, log = algorithms.eaMuPlusLambda(pop, toolbox, mu=300, lambda_=400, cxpb=0.5, 
		mutpb=0.1, ngen=10000, stats=mstats, halloffame=hof, verbose=True)
	end = time.time()

	my_hof = [ind for ind in pop if 0.001 >= ind.fitness.getValues()[0]]
	my_hof = sorted(my_hof, key=lambda individual: individual.fitness.getValues()[1])

	currentTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	file = open("MRbyGA_" + currentTime + ".txt", 'w', encoding='utf8')

	file.write("Consumed time: " + str(end-start) + '\n')

	# print the HoF values without overlap
	temp = ""
	for ind in my_hof:
		if temp == convert_to_sympy_expr(ind):
			continue
		else:
			temp = convert_to_sympy_expr(ind)
			print('%.4f, %f'%(ind.fitness.getValues()), ':')
			# print(ind)
			sympy.pprint(temp)
			#pickle.dump(temp, file)
			file.write('%.4f, %f: '%(ind.fitness.getValues()) + '\n' + ind.__str__() + '\n')

	return pop, log, hof

if __name__ == "__main__":
	main()
