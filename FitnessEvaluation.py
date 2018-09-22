import math
#import cmath
import ast
import astor
import re
import sympy
from sympy.abc import x, pi
import zss
import stringdist
import sys
from SympyManipulation import convert_to_sympy_expr, eval_const_subtrees, conv_to_simple_expr


def evalSymbReg(individual, points, toolbox):
	# Transform the tree expression in a callable function
	lhs = individual[0]
	rhs = individual[1]

	lhs_func = toolbox.compile(individual[0])
	rhs_func = toolbox.compile(individual[1])

	# Check whether there is nested pow, like pow(pow(x,2)) or pow(x,pow(2,10))
	lhs_ast = ast.parse(str(lhs))
	rhs_ast = ast.parse(str(rhs))

	checkPow = CheckNestedFunc()

	checkPow.visit(lhs_ast)

	lhsNestedPowFlag = checkPow.getPowCount()
	lhsNestedTriFlag = checkPow.getTriCount()

	checkPow.clearVariable()

	checkPow.visit(rhs_ast)

	rhsNestedPowFlag = checkPow.getPowCount()
	rhsNestedTriFlag = checkPow.getTriCount()

	if lhsNestedPowFlag or lhsNestedTriFlag or rhsNestedTriFlag or rhsNestedTriFlag:
		return 1, True

	try:
		# Evaluate the mean squared error between the expression
		# on the left and the right hand-side
		sqerrors = ((lhs_func(x) - rhs_func(x))**2 for x in points)
		avg_error = math.fsum(sqerrors) / len(points)
		# normalise the fitness value
		return 1 - math.pow(1.16, -avg_error), False

	except Exception as e:
		print("MSE fitness calculation exception")
		print(e)
		return 1, True

class CheckNestedFunc(ast.NodeVisitor):

	def __init__(self):
		self.powCount = 0
		self.trigonometricCount = 0

	def visit_Call(self, node):
		self.generic_visit(node)
		
		if node.func.id == 'protectedPow':
			self.powCount += 1
			
		elif node.func.id == 'sinX' or node.func.id == 'cos':
			self.trigonometricCount += 1

		return node

	def getPowCount(self):
		if self.powCount >= 2:
			return True
		else:
			return False

	def getTriCount(self):
		if self.trigonometricCount >= 3:
			return True
		else:
			return False

	def clearVariable(self):
		self.powCount = 0
		self.trigonometricCount = 0

def get_label(expr):
	return str(expr.func)

def strdist(a, b):
	if a == b:
		return 0
	else:
		return 1

def get_children(expr):
	first_suppresed = False
	children = []
	for child in sympy.preorder_traversal(expr):
		if first_suppresed:
			children.append(child)
		else:
			first_suppresed = True
	return children

def evalSimplicity(individual, target_func):
	lhs_expr = conv_to_simple_expr(individual[0])
	rhs_expr = conv_to_simple_expr(individual[1])

	# Test for string distance with levenshtein algorithm
	sdist = stringdist.levenshtein(str(lhs_expr), str(rhs_expr))

	# Normalise string distance
	return 1 - math.pow(1.016, -sdist)

def get_fitness(individual, target_func, toolbox, points):
	evalValue, exceptionFlag = evalSymbReg(individual, points, toolbox) 
	#print(str(evalValue) + " " + str(exceptionFlag))

	if exceptionFlag:
		evalDist = 1
	else:
		evalDist = evalSimplicity(individual, target_func)

	return evalValue,evalDist





