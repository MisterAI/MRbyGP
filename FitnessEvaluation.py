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
from SympyManipulation import convert_to_sympy_expr


def evalSymbReg(individual, points, toolbox):
	# Transform the tree expression in a callable function
	#func = toolbox.compile(expr=individual)
	#print(individual)
	lhs = individual[0]
	rhs = individual[1]

	lhs_func = toolbox.compile(individual[0])
	rhs_func = toolbox.compile(individual[1])

	# Check whether there is nested pow, like pow(pow(x,2)) or pow(x,pow(2,10))
	#ind_str = str(individual)
	#my_ast = ast.parse(ind_str)

	lhs_ast = ast.parse(str(lhs))
	rhs_ast = ast.parse(str(rhs))

	checkPow = CheckNestedFunc()
	#checkPow.visit(my_ast)

	#nestedPowFlag = checkPow.getPowCount()
	#nestedTriFlag = checkPow.getTriCount()

	checkPow.visit(lhs_ast)
	checkPow.visit(rhs_ast)

	nestedPowFlag = checkPow.getPowCount()
	nestedTriFlag = checkPow.getTriCount()

	if nestedPowFlag or nestedTriFlag:
		#print("NESTED")
		avg_error = sys.float_info.max / len(points)  
		return 1- math.pow(1.16, -avg_error)

	try:
		# Evaluate the mean squared error between the expression
		# and the function to analyse
		#sqerrors = ((func(x) - individual.target_func(x))**2 for x in points)
		sqerrors = ((lhs.target_func(x) - rhs.individual.target_func(x))**2 for x in points)
		avg_error = math.fsum(sqerrors) / len(points)
		return 1 - math.pow(1.16, -avg_error)

	except Exception:
		#print("Exception")
		avg_error = sys.float_info.max / len(points) #sys.float_info.max 
		return 1 - math.pow(1.16, -avg_error)

	except ValueError as e:
		print('Erroneous individual:', individual)
		raise e

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
		if self.trigonometricCount > 3:
			return True
		else:
			return False

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
	#expr = convert_to_sympy_expr(individual)
	lhs_expr = convert_to_sympy_expr(individual[0])
	rhs_expr = convert_to_sympy_expr(individual[1])

	# Test for string distance with levenshtein algorithm
	#sdist = stringdist.levenshtein(str(expr), 'sinX(x)')
	sdist = stringdist.levenshtein(str(lhs_expr), str(rhs_expr))

	return 1 - math.pow(1.016, -sdist)

def get_fitness(individual, target_func, toolbox, points):
	return evalSymbReg(individual, points, toolbox), evalSimplicity(individual, target_func)
