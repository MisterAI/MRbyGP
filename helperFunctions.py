import math

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
	if isinstance(right, float):
		right = int(right)
	try:
		return left ** right

	except ZeroDivisionError:
		return 1

	except ValueError:
		return 1

	except OverflowError:
		return sys.float_info.max