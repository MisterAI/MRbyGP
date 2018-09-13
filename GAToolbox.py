import random
import math
import operator
from deap import creator, base, tools, gp
from FitnessEvaluation import get_fitness
from FilterSet import filters
from helperFunctions import protectedDiv, sinX, protectedPow, extendedCxOnePoint, extendedMutUniform, extendedSetStaticLimit

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
	creator.create("FitnessMulti", base.Fitness, weights=weights)
	#creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMulti, target_func=target_func)
	creator.create("Tree", gp.PrimitiveTree, target_func=target_func)
	creator.create("Pair", list, fitness=creator.FitnessMulti)

	toolbox = base.Toolbox()

	toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=3)
	toolbox.register("indTree", tools.initIterate, creator.Tree, toolbox.expr)
	toolbox.register("pair", tools.initRepeat, creator.Pair, toolbox.indTree, 2)
	#toolbox.register("population", tools.initRepeat, list, toolbox.individual)
	toolbox.register("population", tools.initRepeat, list, toolbox.pair)
	toolbox.register("compile", gp.compile, pset=pset)

	eval_range = [x/20. * math.pi for x in range(-20,20)] + [x for x in range(-20, 20)]
	toolbox.register("evaluate", get_fitness, target_func=target_func, toolbox=toolbox, points=eval_range)

	
	# add filters for unwanted behaviour
	for filter_ in filters:
		toolbox.decorate('evaluate', tools.DeltaPenalty(filter_, [1000., 0.]))
	
	toolbox.register("select", tools.selSPEA2)
	#toolbox.register("mate", gp.cxOnePoint)
	toolbox.register("mate", extendedCxOnePoint)
	toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
	#toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
	toolbox.register("mutate", extendedMutUniform, expr=toolbox.expr_mut, pset=pset)

	#toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
	toolbox.decorate("mate", extendedSetStaticLimit(key=operator.attrgetter("height"), max_value=17))
	#toolbox.decorate("mate", gp.staticLimit(key=len, max_value=20))
	toolbox.decorate("mate", extendedSetStaticLimit(key=len, max_value=20))
	#toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
	toolbox.decorate("mutate", extendedSetStaticLimit(key=operator.attrgetter("height"), max_value=17))
	#toolbox.decorate("mutate", gp.staticLimit(key=len, max_value=20))
	toolbox.decorate("mutate", extendedSetStaticLimit(key=len, max_value=20))
	return toolbox
