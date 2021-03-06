import random
import math
import numpy
import sympy
from FitnessEvaluation import convert_to_sympy_expr
from deap import tools, algorithms
from GAToolbox import get_toolbox
import datetime
import time
import matplotlib.pyplot as plt

def main():
	init_pop_size = 1000
	num_offsprings = 400
	pop_size = 300
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
	# hof = tools.HallOfFame(40)
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
	pop, log = algorithms.eaMuPlusLambda(pop, toolbox, mu=pop_size, lambda_=num_offsprings, cxpb=0.5, 
		mutpb=0.1, ngen=num_generations, stats=mstats, halloffame=hof, verbose=True)
	end = time.time()

	my_hof = [ind for ind in pop if 0.001 >= ind.fitness.getValues()[0]]
	my_hof = sorted(my_hof, key=lambda individual: individual.fitness.getValues()[1])

	currentTime = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
	file = open("out/MRbyGA_" + currentTime + ".txt", 'w', encoding='utf8')

	m, s = divmod((end-start), 60)
	h, m = divmod(m, 60)

	file.write("Consumed time: %d:%02d:%02d" % (h,m,s) + '\n\n')

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
			file.write('%.4f, %f: '%(ind.fitness.getValues()) + '\n' + str(ind) + '\n' + sympy.pretty(temp) + '\n\n')

	plt.figure(1)
	plt.subplot(211)
	plt.axis(ymax=1.0)
	plt.plot(log.chapters['fitness_mse'].select('avg'))
	plt.plot(log.chapters['fitness_mse'].select('min'))
	plt.plot(log.chapters['fitness_mse'].select('max'))

	plt.subplot(212)
	plt.axis(ymax=1.0)
	plt.plot(log.chapters['fitness_dist'].select('avg'))
	plt.plot(log.chapters['fitness_dist'].select('min'))
	plt.plot(log.chapters['fitness_dist'].select('max'))
	plt.show()

	return pop, log, hof

if __name__ == "__main__":
	main()
