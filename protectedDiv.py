def protectedDiv(left, right):
	# make sure, there will be no divison by zero
	try:
		return left / right
	except ZeroDivisionError:
		return 1
