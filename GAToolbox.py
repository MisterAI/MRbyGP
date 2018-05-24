import random
import math
import operator
import re
from deap import creator, base, tools, gp
import ast
import astor

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
		# and the function to analyse
		sqerrors = ((func(x) - func_to_analyse(x))**2 for x in points)
		return math.fsum(sqerrors) / len(points),

	def require_function(individual):
		# penalise individuals that do not contain the original function
		if func_to_analyse.__name__ in str(individual):
			return True
		return False

	def regex_matching_ind(individual, regex):
		# penalise individuals that match the given regex
		return not re.search(regex, str(individual))

	def add_no_zero(individual):
		# penalise adding a value of zero to an expression
		return regex_matching_ind(individual, 
			r'add\(((0, [-\.\w]+(\([\w]+\))?)|([-\.\w]+(\([\w]+\))?, 0))\)')

	def sub_no_zero(individual):
		# penalise subtracting a value of zero of an expression
		return regex_matching_ind(individual, 
			r'sub\([-\.\w]+(\([\w]+\))?, 0\)')

	def sub_no_equal(individual):
		# penalise subtracting equal values of each other
		return regex_matching_ind(individual, 
			r'sub\(([\w\.-]+), \1\)')

	def mul_no_zero_one(individual):
		# penalise multiplying an expression by either one or zero
		return regex_matching_ind(individual, 
			r'mul\((([01], [-\.\w]+(\([\w_]+\))?)|([-\.\w]+(\([\w]+\))?, [01]))\)')

	def neg_no_double(individual):
		# penalise a series of an even number of neg() functions
		return regex_matching_ind(individual, 
			r'(^|((?!neg)\w{3,}\()|((^|\()\w{1,2}\())'
			+ r'((neg\(){2})+(?!neg\()[\w.-]+(\([\w.-]+\))?(\)\))+')

	def div_no_zero_one(individual):
		# penalise a division by zero
		return regex_matching_ind(individual, 
			r'protectedDiv\((([-\.\w]+(\([\w]+\))?, [01])|(0, [-\.\w]+(\([\w]+\))?))\)')

	def orig_func_no_single(individual):
		# penalise a line containing only a call to the original function
		return regex_matching_ind(individual, 
			r'(?m)^[\.\w]+(\([\w, ]+\)){1}$')

	def neg_no_zero(individual):
		# penalise a negation of zero
		return regex_matching_ind(individual, 
			r'neg\((0|-1)\)')

	def check_childs(ast_node, constant_subtrees):
		has_non_constant_child = False
		for node in ast.walk(ast_node):
			if isinstance(node, ast.Name):
				if 'ARG' in node.id:
					has_non_constant_child = True
		if not has_non_constant_child:
			constant_subtrees.append(ast_node)
		else:
			for child in ast.iter_child_nodes(ast_node):
				check_childs(child, constant_subtrees)

	def ast_no_zero_one_subtree(individual):
		# penalise a subtree in the computational graph that
		# evaluates to zero or one

		# convert graph to AST
		ind_function = str(individual)
		my_ast = ast.parse(ind_function)

		# find subtrees in AST that only contain constants
		constant_subtrees = []
		check_childs(my_ast, constant_subtrees)

		has_zero_one_subtree = False
		for subtree in constant_subtrees:
			# check for the presence of at least one child node
			# (subtree shouldn't be a terminal)
			has_child_nodes = False
			for child in ast.iter_child_nodes(subtree):
				if isinstance(child, ast.Load):
					continue
				has_child_nodes = True
				break

			if has_child_nodes:
				# evaluate the subtree
				source = astor.to_source(subtree)
				globals_ = {
					'protectedDiv': protectedDiv,
					'add': operator.add,
					'sub': operator.sub,
					'mul': operator.mul,
					'neg': operator.neg,
					'cos': math.cos,
					'sin': math.sin,
					'pi': math.pi,
					}
				return_val = eval(source, globals_)

				# check if the return value is close to either zero or one
				margin = 0.0001
				if ((0. - margin) < return_val < margin) \
					or ((1. - margin) < return_val < (1. + margin)):
					# found a 0/1 subtree
					has_zero_one_subtree = True
		return not has_zero_one_subtree

	# collect the atomic building blocks of the individuals
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

	# define the general form of an individual
	creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
	creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

	toolbox = base.Toolbox()

	toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=3)
	toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
	toolbox.register("population", tools.initRepeat, list, toolbox.individual)
	toolbox.register("compile", gp.compile, pset=pset)

	eval_range = [x/10. for x in range(-10,10)] + [x for x in range(-100, 100)]
	toolbox.register("evaluate", evalSymbReg, points=eval_range)
	
	# add filters for unwanted behaviour
	filters = [
		require_function,
		add_no_zero,
		sub_no_zero,
		sub_no_equal,
		mul_no_zero_one,
		neg_no_double,
		div_no_zero_one,
		orig_func_no_single,
		neg_no_zero,
		ast_no_zero_one_subtree,
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
