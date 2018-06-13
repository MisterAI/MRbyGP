import math
import operator
import re
import ast
import astor
from helperFunctions import protectedDiv, sinX


def require_function(individual):
	# penalise individuals that do not contain the original function
	if individual.target_func.__name__ in str(individual):
		return True
	return False

def regex_matching_ind(individual, regex):
	# penalise individuals that match the given regex
	return not re.search(regex, str(individual))

def add_no_zero(individual):
	# penalise adding a value of zero to an expression
	return regex_matching_ind(individual, 
		r'add\(((0, [\-\.\w]+(\([\w]+\))?)|([\-\.\w]+(\([\w]+\))?, 0))\)')

def sub_no_zero(individual):
	# penalise subtracting a value of zero of an expression
	return regex_matching_ind(individual, 
		r'sub\([\-\.\w]+(\([\w]+\))?, 0\)')

def sub_no_equal(individual):
	# penalise subtracting equal values of each other
	return regex_matching_ind(individual, 
		r'sub\(([\w\.\-]+), \1\)')

def mul_no_zero_one(individual):
	# penalise multiplying an expression by either one or zero
	return regex_matching_ind(individual, 
		r'mul\((([01], [\-\.\w]+(\([\w_]+\))?)|([\-\.\w]+(\([\w]+\))?, [01]))\)')

def neg_no_double(individual):
	# penalise a series of an even number of neg() functions
	return regex_matching_ind(individual, 
		r'(^|((?!neg)\w{3,}\()|((^|\()\w{1,2}\())'
		+ r'((neg\(){2})+(?!neg\()[\w.\-]+(\([\w.\-]+\))?(\)\))+')

def div_no_zero_one(individual):
	# penalise a division by zero
	return regex_matching_ind(individual, 
		r'protectedDiv\((([\-\.\w]+(\([\w]+\))?, [01])|(0, [\-\.\w]+(\([\w]+\))?))\)')

def div_no_equal(individual):
	# penalise dividing equal values of each other
	return regex_matching_ind(individual, 
		r'protectedDiv\(([\w\.\-]+), \1\)')

def orig_func_no_single(individual):
	# penalise a line containing only a call to the original function
	return regex_matching_ind(individual, 
		r'(?m)^[\.\w]+(\([\w, ]+\)){1}$')

def neg_no_zero(individual):
	# penalise a negation of zero
	return regex_matching_ind(individual, 
		r'neg\((0|-1)\)')

def sin_no_zero_pi(individual):
	# don't calculate the sin() of zero or n*pi
	return regex_matching_ind(individual, 
		r'sin\((3\.141592653589793|0|mul\(((\-?[0-9]+, 3.141592653589793)|(3\.141592653589793, \-?[0-9]+))\)|add\(3\.141592653589793, 3\.141592653589793\))\)')

def add_no_inverse(individual):
	# don't add inverse numbers
	return regex_matching_ind(individual, 
		r'add\(((\-([\.\d]+), \3)|(([\.\d]+), \-\5))\)')

def cos_no_zero_pi(individual):
	# don't calculate the cos() of zero or n*pi
	return regex_matching_ind(individual, 
		r'cos\((3\.141592653589793|0|mul\(((\-?[0-9]+, 3.141592653589793)|(3\.141592653589793, \-?[0-9]+))\)|add\(3\.141592653589793, 3\.141592653589793\))\)')

def nested_pow(individual):
	return regex_matching_ind(individual,
		r'protectedPow\(((protectedPow\(([\-\.\w]+(\([\w]+\))?, [\-\.\w]+(\([\w]+\))?), [\-\.\w]+(\([\w]+\))?) | ([\-\.\w]+(\([\w]+\))?), protectedPow([\-\.\w]+(\([\w]+\))?, [\-\.\w]+(\([\w]+\))?))')

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
				'sinX': sinX,
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

filters = [
	# require_function,
	# add_no_zero,
	# sub_no_zero,
	# sub_no_equal,
	# mul_no_zero_one,
	# neg_no_double,
	# div_no_zero_one,
	# div_no_equal,
	# orig_func_no_single,
	# neg_no_zero,
	# sin_no_zero_pi,
	# add_no_inverse,
	# cos_no_zero_pi,
	# ast_no_zero_one_subtree,
	#nested_pow
	]
