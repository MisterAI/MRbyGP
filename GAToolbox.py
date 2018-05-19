import random
import math
import operator
from deap import creator, base, tools, gp

def get_ga_toolbox(func_to_analyse):
	def protectedDiv(left, right):
		# make sure, there will be no divison by zero
		try:
			return left / right
		except ZeroDivisionError:
			return 1

	pset = gp.PrimitiveSet("MAIN", 1)
	pset.addPrimitive(operator.add, 2)
	pset.addPrimitive(operator.sub, 2)
	pset.addPrimitive(operator.mul, 2)
	pset.addPrimitive(protectedDiv, 2)
	pset.addPrimitive(operator.neg, 1)
	pset.addPrimitive(math.cos, 1)
	pset.addPrimitive(math.sin, 1)
	pset.addEphemeralConstant("rand101", lambda: random.randint(-1,1))

	creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
	creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

	toolbox = base.Toolbox()

	toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=3)
	toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
	toolbox.register("population", tools.initRepeat, list, toolbox.individual)
	toolbox.register("compile", gp.compile, pset=pset)

	def evalSymbReg(individual, points):
		# Transform the tree expression in a callable function
		func = toolbox.compile(expr=individual)
		# Evaluate the mean squared error between the expression
		# and the real function : x**4 + x**3 + x**2 + x
		sqerrors = ((func(x) - func_to_analyse(x))**2 for x in points)
		return math.fsum(sqerrors) / len(points),

	toolbox.register("evaluate", evalSymbReg, points=[x/10. for x in range(-10,10)])
	toolbox.register("select", tools.selTournament, tournsize=3)
	toolbox.register("mate", gp.cxOnePoint)
	toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
	toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

	toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
	toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
	return toolbox
