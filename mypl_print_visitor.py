import mypl_token as token
import mypl_ast as ast

class PrintVisitor(ast.Visitor):
	"""An AST pretty printer"""
	def __init__(self, output_stream):
		self.indent = 0 # to increase/decrease indent level
		self.output_stream = output_stream # where printing to
	def __indent(self):
		"""Get default indent of four spaces"""
		return ' ' * self.indent
	def __write(self, msg):
		self.output_stream.write(msg)
		
	def visit_stmt_list(self, stmt_list):
		for stmt in stmt_list.stmts:
			stmt.accept(self)
			
	def visit_expr_stmt(self, expr_stmt):
		self.__write(self.__indent())
		expr_stmt.expr.accept(self)
		self.__write(';\n')
		
	def visit_var_decl_stmt(self, var_decl):
		self.__write('var ')
		self.__write(var_decl.var_id.lexeme)
		if var_decl.var_type != None:
			self.__write(": " + var_decl.var_type.lexeme)
		self.__write(" = ")
		var_decl.var_expr.accept(self)
		self.__write(';\n')
		 
	def visit_assign_stmt(self, assign_stmt):
		self.__write('set ')
		for item in assign_stmt.lhs.path:
			self.__write(item.lexeme + '.')
		self.__write(' = ')
		assign_stmt.rhs.accept(self)
		self.__write(';\n')
		
	def visit_struct_decl_stmt(self, struct_decl):
		self.__write('struct ')
		self.__write(struct_decl.struct_id.lexeme)
		self.__write('\n')
		self.__write(self.__indent())
		for item in struct_decl.var_decls:
			if item.var_id != None:
				item.accept(self)
				self.__write('\n')
				self.__write(self.__indent())
		self.__write('end\n')
		
	def visit_fun_decl_stmt(self, fun_decl):
		self.__write('fun ')
		if fun_decl.return_type != None:
			self.__write(fun_decl.return_type.lexeme)
		else:
			self.__write('nil')
		self.__write(' ' + fun_decl.fun_name.lexeme)
		self.__write('(')
		for item in fun_decl.params:
			item.accept(self)
		self.__write(')\n')
		self.__write(self.__indent())
		fun_decl.stmt_list.accept(self)
		self.__write('end\n')
		
	def visit_return_stmt(self, return_stmt):
		self.__write('return ')
		if return_stmt.return_expr != None:
			return_stmt.return_expr.accept(self)
		self.__write(';\n')
		
	def visit_while_stmt(self, while_stmt):
		self.__write('while ')
		while_stmt.bool_expr.accept(self)
		self.__write(' do \n')
		while_stmt.stmt_list.accept(self)
		self.__write('end\n')
		
	def visit_if_stmt(self, if_stmt):
		self.__write('if ')
		if_stmt.if_part.bool_expr.accept(self)
		self.__write(' then \n')
		self.__write(self.__indent())
		if_stmt.if_part.stmt_list.accept(self)
		self.__write('\n' + self.__indent())
		if if_stmt.elseifs != None:
			for item in if_stmt.elseifs:
				item.bool_expr.accept(self)
				self.__write(' then \n')
				self.__write(self.__indent())
				item.stmt_list.accept(self)
			self.__write('\n')
		if if_stmt.has_else:
			self.__write('else ')
			self.__write('\n' + self.__indent())
			if_stmt.else_stmts.accept(self)
		self.__write('end \n')
			
	def visit_simple_expr(self, simple_expr):
		simple_expr.term.accept(self)
		#self.__write('\n')
		
	def visit_complex_expr(self, complex_expr):
		complex_expr.first_operand.accept(self)
		self.__write(' ' + complex_expr.math_rel.lexeme + ' ')
		complex_expr.rest.accept(self)
		#self.__write('\n')
		
	def visit_bool_expr(self, bool_expr):
		if bool_expr.negated:
			self.__write('not ')
		bool_expr.first_expr.accept(self)
		if bool_expr.bool_rel != None:
			self.__write(' ' + bool_expr.bool_rel.lexeme + ' ')
			bool_expr.second_expr.accept(self)
		if bool_expr.bool_connector != None:
			self.__write(' ' + bool_expr.bool_connector.lexeme + ' ')
			bool_expr.rest.accept(self)
				
	def visit_lvalue(self, lval):
		for item in lval.path:
			self.__write(item.lexeme)
			if item != lval.path[len(lval.path)-1]:
				self.__write('.')
		
	def visit_fun_param(self, fun_param):
		self.__write(fun_param.param_name.lexeme + ': ')
		self.__write(fun_param.param_type.lexeme)
		
		
	def visit_simple_rvalue(self, simple_rvalue):
		self.__write(simple_rvalue.val.lexeme)
		
	def visit_new_rvalue(self, new_rvalue):
		self.__write(new_rvalue.struct_type.lexeme)
		
	def visit_call_rvalue(self, call_rvalue):
		self.__write(call_rvalue.fun.lexeme)
		self.__write('(')
		for item in call_rvalue.args:
			item.accept(self)
			if item != call_rvalue.args[len(call_rvalue.args)-1]:
				self.__write(', ')
		self.__write(')')
		
	def visit_id_rvalue(self, id_rvalue):
		for item in id_rvalue.path:
			self.__write(item.lexeme)
			if item != id_rvalue.path[len(id_rvalue.path)-1]:
				self.__write('.')
	
