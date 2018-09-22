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


def extendedCxOnePoint(ind1, ind2):
	lhsInd1, rhsInd1 = ind1[0], ind1[1]
	lhsInd2, rhsInd2 = ind2[0], ind2[1]
	# In current state, simply crossover lhs with lhs and rhs with rhs
	ind1[0], ind1[1] = gp.cxOnePoint(lhsInd1, lhsInd2)
	ind2[0], ind2[1] = gp.cxOnePoint(rhsInd1, rhsInd2)

	return ind1, ind2

def extendedMutUniform(ind1, expr, pset):
	lhsInd1, rhsInd1 = ind1[0], ind1[1]
	ind1[0], = gp.mutUniform(lhsInd1, expr, pset)

	if random.uniform(0,1.0) > 0.7 :
		ind1[1], = gp.mutUniform(rhsInd1, expr, pset)

	# return tuple following the deap mutation function
	return ind1,

def extendedSetStaticLimit(key, max_value):
	
	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			keep_inds = [copy.deepcopy(ind) for ind in args]
			new_inds = list(func(*args, **kwargs))
			for i, ind in enumerate(new_inds):
				if key(ind[0]) > max_value or (len(ind) > 1 and key(ind[1]) > max_value):
					new_inds[i] = random.choice(keep_inds)
			return new_inds
		return wrapper

	return decorator
