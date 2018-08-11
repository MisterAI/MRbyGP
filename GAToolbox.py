import random
import math
import operator
from deap import creator, base, tools, gp
from FitnessEvaluation import get_fitness
from FilterSet import filters
from helperFunctions import protectedDiv, sinX, protectedPow

def twosided_mate(ind1, ind2):
	# Mate function for individuals consisting of two trees.
	# It will mate randomly mate either the first or the second
	# trees of the individuals
	ind1_fitness = ind1.fitness
	ind2_fitness = ind2.fitness
	if random.random() < 0.5:
		hs1, hs2 = gp.cxOnePoint(ind1[0], ind2[0])
		ind1 = creator.Individual((hs1, ind1[1]))
		ind2 = creator.Individual((hs2, ind2[1]))
	else:
		hs1, hs2 = gp.cxOnePoint(ind1[1], ind2[1])
		ind1 = creator.Individual((ind1[0], hs1))
		ind2 = creator.Individual((ind2[0], hs2))
	ind1.fitness = ind1_fitness
	ind2.fitness = ind2_fitness
	return ind1, ind2

def twosided_mutate(individual, expr, pset):
	# Mutation function for individuals consisting of two trees.
	# It will randomly mutate either the first or the second tree
	# of the individual
	ind_fitness = individual.fitness
	if random.random() < 0.5:
		ind_tuple = gp.mutUniform(individual[0], expr, pset)
		individual = creator.Individual((ind_tuple[0], individual[1]))
	else:
		ind_tuple = gp.mutUniform(individual[1], expr, pset)
		individual = creator.Individual((individual[0], ind_tuple[0]))
	individual.fitness = ind_fitness
	return individual,

def get_max_height(individual):
	return max(individual[0].height, individual[1].height)

def get_max_len(individual):
	return max(len(individual[0]), len(individual[1]))

def get_toolbox(target_func, weights):
	# collect the atomic building blocks of the individuals
	pset = gp.PrimitiveSet("MAIN", 1)
	pset.addPrimitive(operator.add, 2)
	pset.addPrimitive(operator.sub, 2)
	pset.addPrimitive(operator.mul, 2)
	pset.addPrimitive(protectedDiv, 2)
	pset.addPrimitive(operator.neg, 1)
	pset.addPrimitive(protectedPow, 2)
	pset.addPrimitive(math.cos, 1)
	pset.addPrimitive(sinX, 1)
	pset.addEphemeralConstant("rand101", lambda: random.randint(-1,1))
	pset.addEphemeralConstant("rand10010", lambda: random.randint(-10,10))
	pset.addTerminal(math.pi)

	# Constant Simplification
	pset.addEphemeralConstant("randfloat10010", lambda: random.uniform(-10.0,10.0))


	# define the general form of an individual
	# (one individual consists of two hand-sides, left and right;
	# each hand-side consists of one computational graph)
	creator.create("FitnessMulti", base.Fitness, weights=weights)
	creator.create("Handside", gp.PrimitiveTree, target_func=target_func)
	creator.create("Individual", tuple, fitness=creator.FitnessMulti)

	toolbox = base.Toolbox()

	toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=3)
	toolbox.register("handside", tools.initIterate, creator.Handside, toolbox.expr)
	toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.handside, 2)
	toolbox.register("population", tools.initRepeat, list, toolbox.individual)
	toolbox.register("compile", gp.compile, pset=pset)

	eval_range = [x/20. * math.pi for x in range(-20,20)] + [x for x in range(-20, 20)]
	toolbox.register("evaluate", get_fitness, target_func=target_func, toolbox=toolbox, points=eval_range)

	# add filters for unwanted behaviour
	for filter_ in filters:
		toolbox.decorate('evaluate', tools.DeltaPenalty(filter_, [1000., 0.]))
	
	toolbox.register("select", tools.selSPEA2)
	toolbox.register("mate", twosided_mate)
	toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
	toolbox.register("mutate", twosided_mutate, expr=toolbox.expr_mut, pset=pset)

	toolbox.decorate("mate", gp.staticLimit(key=get_max_height, max_value=17))
	toolbox.decorate("mate", gp.staticLimit(key=get_max_len, max_value=20))
	toolbox.decorate("mutate", gp.staticLimit(key=get_max_height, max_value=17))
	toolbox.decorate("mutate", gp.staticLimit(key=get_max_len, max_value=20))
	return toolbox
