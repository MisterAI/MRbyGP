import random
import math
import operator
import re
from deap import creator, base, tools, gp

def get_ga_toolbox(func_to_analyse):
	def protectedDiv(left, right):
		# make sure, there will be no divison by zero
		try:
			return left / right
		except ZeroDivisionError:
			return 1

	def evalSymbReg(individual, points):
		# Transform the tree expression in a callable function
		func = toolbox.compile(expr=individual)
		# Evaluate the mean squared error between the expression
		# and the real function : x**4 + x**3 + x**2 + x
		sqerrors = ((func(x) - func_to_analyse(x))**2 for x in points)
		return math.fsum(sqerrors) / len(points),

	def require_function(individual):
		# penalise individuals that do not contain the original function

		if func_to_analyse.__name__ in str(individual):
			return True
		return False

	def regex_matching_ind(individual, regex):
		return not re.search(regex, str(individual))

	def add_no_zero(individual):
		return regex_matching_ind(individual, 
			r'add\(((0, [-\.\w]+(\([\w]+\))?)|([-\.\w]+(\([\w]+\))?, 0))\)')

	def sub_no_zero(individual):
		return regex_matching_ind(individual, 
			r'sub\([-\.\w]+(\([\w]+\))?, 0\)')

	def sub_no_equal(individual):
		return regex_matching_ind(individual, 
			r'sub\(([\w\.-]+), \1\)')

	def mul_no_zero_one(individual):
		return regex_matching_ind(individual, 
			r'mul\((([01], [-\.\w]+(\([\w_]+\))?)|([-\.\w]+(\([\w]+\))?, [01]))\)')

	def neg_no_double(individual):
		return regex_matching_ind(individual, 
			r'(^|((?!neg)\w{3,}\()|((^|\()\w{1,2}\())'
			+ r'((neg\(){2})+(?!neg\()[\w.-]+(\([\w.-]+\))?(\)\))+')

	def div_no_zero_one(individual):
		return regex_matching_ind(individual, 
			r'protectedDiv\((([-\.\w]+(\([\w]+\))?, [01])|(0, [-\.\w]+(\([\w]+\))?))\)')

	def orig_func_no_single(individual):
		return regex_matching_ind(individual, 
			r'(?m)^[\.\w]+(\([\w]+\)){1}$')


	pset = gp.PrimitiveSet("MAIN", 1)
	pset.addPrimitive(operator.add, 2)
	pset.addPrimitive(operator.sub, 2)
	pset.addPrimitive(operator.mul, 2)
	pset.addPrimitive(protectedDiv, 2)
	pset.addPrimitive(operator.neg, 1)
	pset.addPrimitive(math.cos, 1)
	pset.addPrimitive(math.sin, 1)
	pset.addEphemeralConstant("rand101", lambda: random.randint(-1,1))
	pset.addEphemeralConstant("rand10010", lambda: random.randint(-10,10))
	pset.addTerminal(math.pi)

	creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
	creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

	toolbox = base.Toolbox()

	toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=3)
	toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
	toolbox.register("population", tools.initRepeat, list, toolbox.individual)
	toolbox.register("compile", gp.compile, pset=pset)

	eval_range = [x/10. for x in range(-10,10)] + [x for x in range(-100, 100)]
	toolbox.register("evaluate", evalSymbReg, points=eval_range)
	
	filters = [
	require_function, 
	add_no_zero, 
	sub_no_zero, 
	sub_no_equal, 
	mul_no_zero_one, 
	neg_no_double, 
	div_no_zero_one, 
	orig_func_no_single,
	]
	for filter_ in filters:
		toolbox.decorate('evaluate', tools.DeltaPenalty(filter_, 1000.))
	
	toolbox.register("select", tools.selTournament, tournsize=3)
	toolbox.register("mate", gp.cxOnePoint)
	toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
	toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

	toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
	toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
	return toolbox
