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
		self.sym_table.add_id('get')
		self.sym_table.set_info('get', [[token.INTTYPE, token.STRINGTYPE], token.STRINGTYPE])
		self.sym_table.add_id('length')
		self.sym_table.set_info('length', [[token.STRINGTYPE], token.INTTYPE])
		self.sym_table.add_id('reads')
		self.sym_table.set_info('reads', [[token.NIL], token.STRINGTYPE])
		self.sym_table.add_id('readi')
		self.sym_table.set_info('readi', [[token.NIL], token.INTTYPE])
		self.sym_table.add_id('readf')
		self.sym_table.set_info('readf', [[token.NIL], token.FLOATTYPE])
		self.sym_table.add_id('itos')
		self.sym_table.set_info('itos', [[token.INTTYPE], token.STRINGTYPE])
		self.sym_table.add_id('ftos')
		self.sym_table.set_info('ftos', [[token.FLOATTYPE], token.STRINGTYPE])
		self.sym_table.add_id('itof')
		self.sym_table.set_info('itof', [[token.INTTYPE], token.FLOATTYPE])
		self.sym_table.add_id('stoi')
		self.sym_table.set_info('stoi', [[token.STRINGTYPE], token.INTTYPE])
		self.sym_table.add_id('stof')
		self.sym_table.set_info('stof', [[token.STRINGTYPE], token.FLOATTYPE])
		self.sym_table.add_id('println')
		self.sym_table.set_info('println', [[token.STRINGTYPE], token.NIL])
		
	def __error(self, msg, the_token):
		raise error.MyPLError(msg, the_token.line, the_token.column)
		
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
		var_decl.var_expr.accept(self)
		var_type = self.current_type
		var_id = var_decl.var_id
		curr_env = self.sym_table.get_env_id()
	
		# check that variable isnt already defined
		if self.sym_table.id_exists_in_env(var_id.lexeme, curr_env):
			msg = 'variable already defined in current enviroment'
			self.__error(msg, var_id)

		if var_decl.var_type != None:
			if var_decl.var_type.tokentype == token.ID:
				var_decl.var_type.tokentype = var_decl.var_type.lexeme
			if var_type != token.NIL and var_decl.var_type.tokentype != var_type:
				msg = "type mismatch in var decl"
				self.__error(msg, var_decl.var_id)
			self.sym_table.add_id(var_decl.var_id.lexeme)
			self.sym_table.set_info(var_decl.var_id.lexeme, var_decl.var_type.tokentype)
			self.current_type = var_decl.var_type.tokentype
		else:
			if var_type == token.NIL:
				msg = "undefined var type can not be set to NIL"
				self.__error(msg, var_decl.var_id)
			self.sym_table.add_id(var_decl.var_id.lexeme)
			self.sym_table.set_info(var_decl.var_id.lexeme, var_type)
			self.current_type = var_type
		
	def visit_assign_stmt(self, assign_stmt):
		assign_stmt.rhs.accept(self)
		rhs_type = self.current_type
		assign_stmt.lhs.accept(self)
		lhs_type = self.current_type
		if rhs_type != token.NIL and rhs_type != lhs_type:
			msg = 'mismatch type in assignment'
			self.__error(msg, assign_stmt.lhs.path[0])

	def visit_struct_decl_stmt(self, struct_decl):
		self.sym_table.add_id(struct_decl.struct_id.lexeme)
		struct_type = struct_decl.struct_id.lexeme
		self.sym_table.push_environment()
		var_stmts = {}
		for i in struct_decl.var_decls:
			i.accept(self)
			var_stmts[i.var_id.lexeme] = self.current_type
		self.sym_table.pop_environment()
		self.sym_table.set_info(struct_type, var_stmts)
		
		
	def visit_fun_decl_stmt(self, fun_decl):
		self.sym_table.add_id(fun_decl.fun_name.lexeme)
		self.sym_table.push_environment()
		fun_list = []
		param_names = []
		for i in fun_decl.params:
			i.accept(self)
			fun_list.append(i.param_type.tokentype)
			param_names.append(i.param_name.lexeme)
		#I could'nt figure out how to do this error
		"""count = 0
		for i in param_names:
			for j in param_names[count+1:]:
				if  j == i:
					msg = "Duplicate parameters in function declaration"
					self.__error(msg, fun_decl.fun_name)
			count += 1"""
		if fun_decl.return_type != None:
			self.sym_table.set_info(fun_decl.fun_name.lexeme, [fun_list, fun_decl.return_type.tokentype])
		else:
			self.sym_table.set_info(fun_decl.fun_name.lexeme, [fun_list, token.NIL])
		self.sym_table.pop_environment()
		
	def visit_return_stmt(self, return_stmt):
		return_stmt.return_expr.accept(self)
		if self.current_type == token.STRINGVAL:
			msg = "String literals can't be returned"
			self.__error(msg, return_stmt.return_token)
		
	def visit_while_stmt(self, while_stmt):
		while_stmt.bool_expr.accept(self)
		while_stmt.stmt_list.accept(self)
	
	#if-stmt helper functions	
	def basic_if(self, b_if):
		b_if.bool_expr.accept(self)
		b_if.stmt_list.accept(self)
		
	def visit_if_stmt(self, if_stmt):
		self.basic_if(if_stmt.if_part)
		for i in if_stmt.elseifs:
			self.basic_if(i)
		if if_stmt.has_else:
			if_stmt.else_stmts.accept(self)
		
	def visit_simple_expr(self, simple_expr):
		simple_expr.term.accept(self);
		
	def visit_complex_expr(self, complex_expr):
		complex_expr.first_operand.accept(self)
		lhs = self.current_type
		complex_expr.rest.accept(self)
		rhs = self.current_type		
		if rhs == token.NIL or lhs == token.NIL:
			msg = "Can't do operations with Nil"
			self.__error(msg, complex_expr.math_rel)
		if rhs == token.STRINGTYPE and lhs == token.STRINGTYPE:
			if complex_expr.math_rel.tokentype != token.PLUS:
				msg = "Strings can only be added"
				self.__error(msg, complex_expr.math_rel)
		if rhs == token.BOOLTYPE and lhs == token.BOOLTYPE:
			msg = "Invalid type for complex expr: BOOL"
			self.__error(msg, complex_expr.math_rel)
		if rhs != token.NIL and rhs != lhs:
			msg = "mismatch type in expr"
			self.__error(msg, complex_expr.math_rel)
			 
	def visit_bool_expr(self, bool_expr):
		bool_expr.first_expr.accept(self)
		lhs = self.current_type
		if bool_expr.second_expr != None:
			bool_expr.second_expr.accept(self)
			rhs = self.current_type
			if rhs != token.NIL and rhs != lhs:
				msg = "mismatch type in bool expr"
				self.__error(msg, bool_expr.bool_rel)
			if lhs == token.NIL:
				if bool_expr.bool_rel.tokentype != token.EQUAL and bool_expr.bool_rel.tokentype != token.NOT_EQUAL:
					msg = "Can't preform comparison on NIL object"
					self.__error(msg, bool_expr.bool_rel)
		if bool_expr.bool_connector != None:
			bool_expr.rest.accept(self)
			
	def visit_lvalue(self, lval):
		var_name = lval.path[0].lexeme
		var_type = self.sym_table.get_info(var_name)
		if var_type == None:
			msg = "Variable " + var_name + " undeclared"
			self.__error(msg, lval.path[0])
		if len(lval.path) == 1:
			self.current_type = var_type
		else:
			struct_type = self.sym_table.get_info(var_type)
			for i in lval.path[1:]:
				if not i.lexeme in struct_type:
					msg = "Variable " + i.lexeme + " is not a member of " + var_type
					self.__error(msg, i)
				else:
					self.current_type = struct_type[i.lexeme]	
				
			 	
	def visit_fun_param(self, fun_param):
		self.sym_table.add_id(fun_param.param_name.lexeme)
		self.sym_table.set_info(fun_param.param_name.lexeme, fun_param.param_type)
				
	def visit_simple_rvalue(self, simple_rvalue):
		if simple_rvalue.val.tokentype == token.INTVAL:
			self.current_type = token.INTTYPE
		elif simple_rvalue.val.tokentype == token.FLOATVAL:
			self.current_type = token.FLOATTYPE
		elif simple_rvalue.val.tokentype == token.BOOLVAL:
			self.current_type = token.BOOLTYPE
		elif simple_rvalue.val.tokentype == token.STRINGVAL:
			self.current_type = token.STRINGTYPE
		elif simple_rvalue.val.tokentype == token.NIL:
			self.current_type = token.NIL
		else:
			msg = "bad type for simple rvalue"
			self.__error(msg, simple_rvalue)
		
	def visit_new_rvalue(self, new_rvalue):
		if not self.sym_table.id_exists(new_rvalue.struct_type.lexeme):
			msg = "The struct " + new_rvalue.struct_type.lexeme + " does not exist"
			self.__error(msg, new_rvalue.struct_type)
		else:
			self.current_type = new_rvalue.struct_type.lexeme
			
	def visit_call_rvalue(self, call_rvalue):
		if not self.sym_table.id_exists(call_rvalue.fun.lexeme):
			msg = "The function " + call_rvalue.fun.lexeme + "does not exist"
			self.__error(msg, call_rvalue.fun)
		else:
			fun_type = self.sym_table.get_info(call_rvalue.fun.lexeme)
			if len(fun_type[0]) != len(call_rvalue.args):
				if fun_type[0][0] != token.NIL:
					msg = "Wrong number of elements, function " + call_rvalue.fun.lexeme + " requires " + str(len(fun_type[0])) + " parameters"
					self.__error(msg, call_rvalue.fun)
			if len(call_rvalue.args) != 0:
				err = False
				count = 0
				for i in fun_type[0]:
					call_rvalue.args[count].accept(self)
					if i != self.current_type and self.current_type != token.NIL:
						err = True
					count += 1
				if err:
					msg = "Incorect type of arguments in function call: " + call_rvalue.fun.lexeme
					self.__error(msg, call_rvalue.fun)
			self.current_type = fun_type[1]
					
	def visit_id_rvalue(self, id_rvalue):
		var_name = id_rvalue.path[0].lexeme
		var_type = self.sym_table.get_info(var_name)
		if var_type == None:
			msg = "Variable " + var_name + " undeclared"
			self.__error(msg, id_rvalue.path[0])
		if len(id_rvalue.path) == 1:
			self.current_type = var_type
		else:
			struct_type = self.sym_table.get_info(var_type)
			for i in id_rvalue.path[1:]:
				if i != id_rvalue.path[-1]:
					var_type = struct_type[i.lexeme]
					struct_type = self.sym_table.get_info(var_type)
				if not i.lexeme in struct_type:
					msg = "Variable " + i.lexeme + " is not a member of " + var_type
					self.__error(msg, i)
				else:
					self.current_type = struct_type[i.lexeme]	
