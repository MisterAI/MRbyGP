import math
import operator
import copy
import random
import sys
from deap import gp
from functools import wraps


def protectedDiv(left, right):
	# make sure, there will be no divison by zero

	#if right == 0:
	#	return sys.float_info.max

	try:
		return left / right
	except ZeroDivisionError:
		return 1


def sinX(x):
	return math.sin(x)

def protectedPow(left, right):
	if not isinstance(right, int):
		right = int(right)
	try:
		return left ** right

	except ZeroDivisionError:
		return 1

	except ValueError:
		return 1

	except OverflowError:
		return sys.float_info.max

def square(x):
	return x ** 2

def cube(x):
	return x ** 3
