import random
import math
import operator
import sympy
from sympy.abc import x, pi
# from sympy.core.functions import sub, mul
from sympy.core.sympify import kernS
import re
import ast
import astor
from deap import creator, base, tools, gp

from FilterSet import filters
from helperFunctions import protectedDiv, sin_

class ReplaceDiv(ast.NodeTransformer):
	def visit_Call(self, node):
		self.generic_visit(node)
		if node.func.id == 'protectedDiv':
			div_node = ast.Call(
				func=ast.Name(id='Mul', ctx=ast.Load()), 
				args=[
					node.args[0], 
					ast.Call(
						func=ast.Name(id='Pow', ctx=ast.Load()), 
						args=[
							node.args[1], 
							ast.Call(
								func=ast.Name(id='Rational', ctx=ast.Load()),
								args=[ast.Num(-1)], 
								keywords=[])
						], 
						keywords=[])
				], 
				keywords=[])
			return div_node
		return node

class ReplaceSub(ast.NodeTransformer):
	def visit_Call(self, node):
		self.generic_visit(node)
		if node.func.id == 'sub':
			div_node = ast.Call(
				func=ast.Name(id='Add', ctx=ast.Load()), 
				args=[
					node.args[0], 
					ast.Call(
						func=ast.Name(id='Mul', ctx=ast.Load()), 
						args=[
							node.args[1], 
							ast.Call(
								func=ast.Name(id='Rational', ctx=ast.Load()),
								args=[ast.Num(-1)], 
								keywords=[])
						], 
						keywords=[])
				], 
				keywords=[])
			return div_node
		return node

class ReplaceNeg(ast.NodeTransformer):
	def visit_Call(self, node):
		self.generic_visit(node)
		if node.func.id == 'neg':
			div_node = ast.Call(
				func=ast.Name(id='Mul', ctx=ast.Load()), 
				args=[
					node.args[0], 
					ast.Call(
						func=ast.Name(id='Rational', ctx=ast.Load()),
						args=[ast.Num(-1)], 
						keywords=[])
				], 
				keywords=[])
			return div_node
		return node

def replace_const_sin(expr):
	"""Replace sin_() function by sin() function 
	if its argument is independent of x."""
	if sympy.Function('sin_') == expr.func:
		has_const_arg = True
		for arg in sympy.preorder_traversal(expr):
			if sympy.Symbol('x') == arg:
				has_const_arg = False
		if has_const_arg:
			args = [replace_const_sin(arg) for arg in expr.args]
			return sympy.Function('sin')(*args)
	
	args = [replace_const_sin(arg) for arg in expr.args]
	if args == []:
		return expr
	else:
		return expr.func(*args)


def evalSymbReg(individual, points, toolbox):
	# Transform the tree expression in a callable function
	func = toolbox.compile(expr=individual)
	# Evaluate the mean squared error between the expression
	# and the function to analyse
	sqerrors = ((func(x) - individual.target_func(x))**2 for x in points)
	return math.fsum(sqerrors) / len(points),

def evalSimplicity(individual, target_func):
	# convert graph to AST
	ind_function = str(individual)
	# ind_function = 'sin(add(ARG0, mul(2, 3.141592653589793)))'
	# print('ind_function: ', ind_function)
	my_ast = ast.parse(ind_function)

	my_ast = ReplaceDiv().visit(my_ast)
	my_ast = ReplaceSub().visit(my_ast)
	my_ast = ReplaceNeg().visit(my_ast)

	# print('back to source: ', astor.to_source(my_ast))

	expr_string = astor.to_source(my_ast)
	# print('expr_string original: ', expr_string)
	expr_string = re.sub(r'add\(', 'Add(', expr_string)
	expr_string = re.sub(r'mul\(', 'Mul(', expr_string)
	expr_string = re.sub(r'3.141592653589793', 'pi', expr_string)
	expr_string = re.sub(r'ARG0', 'x', expr_string)
	# print('expr_string substituted: ', expr_string)
	expr = sympy.sympify(expr_string)
	# expr = kernS(expr_string)
	print('orig expr ', expr)
	
	expr = replace_const_sin(expr)
	print('const sin expr ', expr)

	return 1,

def get_toolbox(target_func):

	# collect the atomic building blocks of the individuals
	pset = gp.PrimitiveSet("MAIN", 1)
	pset.addPrimitive(operator.add, 2)
	pset.addPrimitive(operator.sub, 2)
	pset.addPrimitive(operator.mul, 2)
	pset.addPrimitive(protectedDiv, 2)
	pset.addPrimitive(operator.neg, 1)
	pset.addPrimitive(math.cos, 1)
	pset.addPrimitive(sin_, 1)
	pset.addEphemeralConstant("rand101", lambda: random.randint(-1,1))
	pset.addEphemeralConstant("rand10010", lambda: random.randint(-10,10))
	pset.addTerminal(math.pi)

	# define the general form of an individual
	creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
	creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin, target_func=target_func)

	toolbox = base.Toolbox()

	toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=3)
	toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
	toolbox.register("population", tools.initRepeat, list, toolbox.individual)
	toolbox.register("compile", gp.compile, pset=pset)

	eval_range = [x/10. for x in range(-10,10)] + [x for x in range(-100, 100)]
	# toolbox.register("evaluate", evalSymbReg, points=eval_range, toolbox=toolbox)
	toolbox.register("evaluate", evalSimplicity, target_func=target_func)
	
	# add filters for unwanted behaviour
	for filter_ in filters:
		toolbox.decorate('evaluate', tools.DeltaPenalty(filter_, 1000.))
	
	toolbox.register("select", tools.selTournament, tournsize=3)
	toolbox.register("mate", gp.cxOnePoint)
	toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
	toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

	toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
	toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
	return toolbox
