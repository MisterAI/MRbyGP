import ast
import astor
import re
import sympy


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

class ReplacePow(ast.NodeTransformer):
	def visit_Call(self,node):
		self.generic_visit(node)
		if node.func.id == 'protectedPow':
			div_node = ast.Call(
				func=ast.Name(id='Pow', ctx=ast.Load()),
				args=[node.args[0], node.args[1]],
				keywords=[])
			return div_node
		return node

def replace_const_sin(expr):
	"""Replace sinX() function by sin() function 
	if its argument is independent of x."""
	if sympy.Function('sinX') == expr.func:
		has_const_arg = True
		for arg in sympy.preorder_traversal(expr):
			if sympy.Symbol('x') == arg:
				has_const_arg = False
		if has_const_arg:
			args = [replace_const_sin(arg) for arg in expr.args]
			return sympy.sin(*args)
	
	args = [replace_const_sin(arg) for arg in expr.args]
	if args == []:
		return expr
	else:
		return expr.func(*args)

def convert_to_sympy_expr(individual):
	# convert graph to AST
	ind_str = str(individual)
	my_ast = ast.parse(ind_str)
	# replace deap specific functions 
	# with ast specific functions
	my_ast = ReplaceDiv().visit(my_ast)
	my_ast = ReplaceSub().visit(my_ast)
	my_ast = ReplaceNeg().visit(my_ast)
	my_ast = ReplacePow().visit(my_ast)

	expr_string = astor.to_source(my_ast)
	expr_string = re.sub(r'add[\n ]*\(', 'Add(', expr_string)
	expr_string = re.sub(r'mul[\n ]*\(', 'Mul(', expr_string)
	expr_string = re.sub(r'3.141592653589793', 'pi', expr_string)
	expr_string = re.sub(r'ARG0', 'x', expr_string)
	expr_string = re.sub(r'pow[\n ]*\(', 'Pow(', expr_string)

	expr = sympy.sympify(expr_string)
	expr = replace_const_sin(expr)
	return expr


def eval_const_subtrees(expr):
	# recursive function to numerically 
	# evaluate constant subtrees
	args = [arg.evalf(3) for arg in expr.args]
	for i in range(len(args)):
		args[i] = eval_const_subtrees(args[i])
	if args:
		return expr.func(*args)
	return expr

def conv_to_simple_expr(expr):
	# simplify expression by numerically evaluating 
	# constant subtrees and approximating constants 
	# to three digits
	expr = convert_to_sympy_expr(expr)

	# Numerically evaluate constant subtrees
	expr = eval_const_subtrees(expr)
	expr = sympy.printing.str.sstr(expr, full_prec=False)
	# Get rid of '-1.0*'
	return re.sub(r'-[ ]*1\.0\*', '-', expr)
