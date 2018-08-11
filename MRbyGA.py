import random
import math
import numpy
import sympy
from SympyManipulation import convert_to_sympy_expr, eval_const_subtrees, conv_to_simple_expr
from deap import tools, algorithms
from GAToolbox import get_toolbox, get_max_len
import datetime
import time
import matplotlib.pyplot as plt
import re

def main():
	init_pop_size = 2000
	num_offsprings = 1000
	pop_size = 2000
	num_generations = 20
	mse_fitness_weight = -1.0
	symb_equiv_fitness_weight = 2.0
	weights = (mse_fitness_weight, symb_equiv_fitness_weight)
	# list all the functions to analyse
	functions = [math.sin]

	# create the toolbox
	toolbox = get_toolbox(functions[0], weights)

	# random.seed(318)

	# create a new population
	pop = toolbox.population(n=init_pop_size)
	
	# collect some statistics
	stats_fit_mse = tools.Statistics(lambda ind: ind.fitness.values[0])
	stats_fit_dist = tools.Statistics(lambda ind: ind.fitness.values[1])
	stats_size = tools.Statistics(get_max_len)
	mstats = tools.MultiStatistics(
		fitness_mse=stats_fit_mse, 
		fitness_dist=stats_fit_dist, 
		size=stats_size)
	# round statistics to four decimal places
	mstats.register("avg", lambda data: numpy.around(numpy.mean(data), decimals=4))
	mstats.register("min", lambda data: numpy.around(numpy.min(data), decimals=4))
	mstats.register("max", lambda data: numpy.around(numpy.max(data), decimals=4))

	start = time.time()
	# do the evolution
	pop, log = algorithms.eaMuPlusLambda(pop, toolbox, mu=pop_size, lambda_=num_offsprings, cxpb=0.5, 
		mutpb=0.1, ngen=num_generations, stats=mstats, verbose=True)
	end = time.time()

	# create Hall of Fame (HoF) with mean squared error (mse) fitness below 0.001
	my_hof = [ind for ind in pop if 0.001 >= ind.fitness.getValues()[0]]
	my_hof = sorted(my_hof, key=lambda individual: individual.fitness.getValues()[1])

	currentTime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
	file = open("out/MRbyGA_" + currentTime + ".txt", 'w', encoding='utf8')

	m, s = divmod((end-start), 60)
	h, m = divmod(m, 60)

	file.write("Consumed time: %d:%02d:%02d" % (h,m,s) + '\n\n')

	# print the HoF values without overlap
	temp = ["",""]
	for ind in my_hof:
		if temp[0] == convert_to_sympy_expr(ind[0]) and temp[1] == convert_to_sympy_expr(ind[1]):
			continue
		else:
			temp[0] = convert_to_sympy_expr(ind[0])
			temp[1] = convert_to_sympy_expr(ind[1])

			print('%.4f, %f:'%(ind.fitness.getValues()))
			print('before ind: ', str(ind[0]) + ' = ' + str(ind[1]))
			print('before: ', str(temp[0]) + ' = ' + str(temp[1]))
			
			simplfd_ind = [conv_to_simple_expr(ind[0]), conv_to_simple_expr(ind[1])]
			print('after: ', simplfd_ind[0] + ' = ' + simplfd_ind[1] , '\n')

			#file.write('%.4f, %f: '%(ind.fitness.getValues()) + '\n' + str(ind) + '\n' + sympy.pretty(temp) + '\n\n')

	'''# plot the progress of the fitness values
	try:
		plt.figure(1)
		plt.subplot(211)
		plt.axis(ymax=1.0)
		plt.plot(log.chapters['fitness_mse'].select('avg'))
		plt.plot(log.chapters['fitness_mse'].select('min'))
		plt.plot(log.chapters['fitness_mse'].select('max'))
		plt.title('Mean squared error')

		plt.subplot(212)
		plt.axis(ymax=1.0)
		plt.plot(log.chapters['fitness_dist'].select('avg'))
		plt.plot(log.chapters['fitness_dist'].select('min'))
		plt.plot(log.chapters['fitness_dist'].select('max'))
		plt.title('String distance')
		plt.show()
	except:
		pass'''

	return pop, log

if __name__ == "__main__":
	main()
