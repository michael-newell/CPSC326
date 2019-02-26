import mypl_token as token
import mypl_ast as ast
import mypl_error as error
import mypl_symbol_table as symbol_table
class TypeChecker(ast.Visitor):
	"""A MyPL type checker visitor implementation where struct types
	take the form: type_id -> {v1:t1, ..., vn:tn} and function types
	take the form: fun_id -> [[t1, t2, ..., tn,], return_type]
	"""
	def __init__(self):
		# initialize the symbol table (for ids -> types)
		self.sym_table = symbol_table.SymbolTable()
		# current_type holds the type of the last expression type
		self.current_type = None
		# global env (for return)
		self.sym_table.push_environment()
		# set global return type to int
		self.sym_table.add_id('return')
		self.sym_table.set_info('return', token.INTTYPE)
		# load in built-in function types
		self.sym_table.add_id('print')
		self.sym_table.set_info('print', [[token.STRINGTYPE], token.NIL])
"""... put remaining built-in function types here ..."""

	def visit_stmt_list(self, stmt_list):
		# add new block (scope)
		self.sym_table.push_environment()
		for stmt in stmt_list.stmts:
			stmt.accept(self)
		# remove new block
		self.sym_table.pop_environment()
		
	def visit_expr_stmt(self, expr_stmt):
		expr_stmt.expr.accept(self)
		
	def visit_var_decl_stmt(self, var_decl):
		"""... you need to define this one ..."""
		
	def visit_assign_stmt(self, assign_stmt):
		assign_stmt.rhs.accept(self)
		rhs_type = self.current_type
		assign_stmt.lhs.accept(self)
		lhs_type = self.current_type
		if rhs_type != token.NIL and rhs_type != lhs_type:
			msg = 'mismatch type in assignment'
			self.__error(msg, assign_stmt.lhs.path[0])
"""... finish remaining visit calls ..."""