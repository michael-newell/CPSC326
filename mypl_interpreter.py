#Michael Newell

import sys
import mypl_token as token
import mypl_ast as ast
import mypl_symbol_table as symbol_table
import mypl_error as error

class ReturnException(Exception): pass
class Interpreter(ast.Visitor):
	#starts the interpreter
	def run(self, stmt_list):
		try:
			stmt_list.accept(self)
		except ReturnException:
			pass

	def __init__(self):
		self.sym_table = symbol_table.SymbolTable()
		self.current_value = None
		self.heap = {}
       
	def __write(self,msg): 
		sys.stdout.write(str(msg))
       
	def visit_stmt_list(self, stmt_list):
		self.current_value = None
		self.sym_table.push_environment()
		for stmt in stmt_list.stmts:
			stmt.accept(self)
		self.sym_table.pop_environment()
   
	def visit_if_stmt(self, if_stmt):
		elif_exe = True
		if_stmt.if_part.bool_expr.accept(self)
		if self.current_value:
			if_stmt.if_part.stmt_list.accept(self)
		else: 
			for elseif in if_stmt.elseifs:
				elseif.bool_expr.accept(self)
				if self.current_value and elif_exe:
					elseif.stmt_list.accept(self)
					elif_exe = False      #if one of them gets executed then the others shouldn't           
			if if_stmt.has_else and elif_exe: 
				if_stmt.else_stmts.accept(self)
				
	def visit_expr_stmt(self, expr_stmt):
		expr_stmt.expr.accept(self)  
		 
	def visit_while_stmt(self, while_stmt): 
		while_stmt.bool_expr.accept(self)
		while self.current_value:
			while_stmt.stmt_list.accept(self)
			while_stmt.bool_expr.accept(self)             
 
	def visit_assign_stmt(self, assign_stmt):
		assign_stmt.rhs.accept(self)		
		rhs = self.current_value
		lhs = assign_stmt.lhs.accept(self)
		self.sym_table.set_info(lhs, rhs)		
                                       
	def visit_simple_expr(self, simple_expr):
		simple_expr.term.accept(self)
                  
	def visit_complex_expr(self, complex_expr):
		complex_expr.first_operand.accept(self)
		curr = self.current_value
		complex_expr.rest.accept(self)
		if complex_expr.math_rel.tokentype == 'PLUS':
			self.current_value = curr + self.current_value 
		elif complex_expr.math_rel.tokentype == 'MINUS':
			self.current_value = curr - self.current_value
		elif complex_expr.math_rel.tokentype == 'MULTIPLY':
			self.current_value = curr * self.current_value
		elif complex_expr.math_rel.tokentype == 'DIVIDE':
			if type(curr) == int and type(self.current_value) == int:
				self.current_value = curr // self.current_value
			else:
				self.current_value = curr / self.current_value
		elif complex_expr.math_rel.tokentype == 'MODULO':
			self.current_value = curr % self.current_value
             
	def visit_var_decl_stmt(self, var_decl):
		var_decl.var_expr.accept(self)
		exp_value = self.current_value
			
		var_name = var_decl.var_id.lexeme
		self.sym_table.add_id(var_decl.var_id.lexeme)
		self.sym_table.set_info(var_decl.var_id.lexeme, exp_value)
	
	def visit_struct_decl_stmt(self, struct_decl):
		env_id = self.sym_table.get_env_id()
		self.sym_table.add_id(struct_decl.struct_id.lexeme)
		self.sym_table.set_info(struct_decl.struct_id.lexeme, [env_id, struct_decl])

	def visit_fun_decl_stmt(self, fun_decl):
		env_id = self.sym_table.get_env_id()
		self.sym_table.add_id(fun_decl.fun_name.lexeme)
		self.sym_table.set_info(fun_decl.fun_name.lexeme, [env_id, fun_decl])

	def visit_return_stmt(self, return_stmt):
		return_stmt.return_expr.accept(self)
		raise ReturnException()
		
		
	def visit_bool_expr(self, bool_expr):
		bool_expr.first_expr.accept(self)
		curr = self.current_value
		bool_expr.second_expr.accept(self)
		if bool_expr.bool_rel.tokentype == token.NOT_EQUAL:
			if curr != self.current_value:
				self.current_value = True
			else:
				self.current_value = False
		if bool_expr.bool_rel.tokentype == token.EQUAL:
			if curr == self.current_value:
				self.current_value = True
			else:
				self.current_value = False
		if bool_expr.bool_rel.tokentype == token.GREATER_THAN_EQUAL:
			if curr >= self.current_value:
				self.current_value = True
			else:
				self.current_value = False
		if bool_expr.bool_rel.tokentype == token.LESS_THAN_EQUAL:
			if curr <= self.current_value:
				self.current_value = True
			else:
				self.current_value = False
		if bool_expr.bool_rel.tokentype == token.GREATER_THAN:
			if curr > self.current_value:
				self.current_value = True
			else:
				self.current_value = False
		if bool_expr.bool_rel.tokentype == token.LESS_THAN:
			if curr < self.current_value:
				self.current_value = True
			else:
				self.current_value = False
		if bool_expr.negated:
			self.current_value = not(self.current_value)
		if bool_expr.bool_connector != None:
			curr = self.current_value
			bool_expr.rest.accept(self)
			if bool_expr.bool_connector.tokentype == token.AND:
				self.current_value = self.current_value and curr
			else:
				self.current_value = self.current_value or curr
    		
	def visit_lvalue(self, lval):
		identifier = lval.path[0].lexeme
		if len(lval.path) == 1:
			self.sym_table.set_info(identifier, self.current_value)
		else:
			oid = self.sym_table.get_info(identifier)
			struct_obj = self.heap[oid]
			for i in lval.path[1:-1]:
				oid = struct_obj[i.lexeme]
				struct_obj = self.heap[oid]
			struct_obj[lval.path[-1].lexeme] = self.current_value
				
  
	def visit_fun_param(self, fun_param):
		''''''
	def visit_simple_rvalue(self, simple_rvalue):
		if simple_rvalue.val.tokentype == token.INTVAL:
			self.current_value = int(simple_rvalue.val.lexeme)
		elif simple_rvalue.val.tokentype == token.FLOATVAL:
			self.current_value = float(simple_rvalue.val.lexeme)
		elif simple_rvalue.val.tokentype == token.BOOLVAL:
			self.current_value = True
			if simple_rvalue.val.lexeme == 'false':
				self.current_value = False
		elif simple_rvalue.val.tokentype == token.STRINGVAL:
			self.current_value = simple_rvalue.val.lexeme
		elif simple_rvalue.val.tokentype == token.NIL:
			self.current_value = None
			
	def visit_new_rvalue(self, new_rvalue):
		struct_info = self.sym_table.get_info(new_rvalue.struct_type.lexeme)
		curr_env = self.sym_table.get_env_id()
		self.sym_table.set_env_id(struct_info[0])
		struct_obj = {}
		self.sym_table.push_environment()
		for i in struct_info[1].var_decls:
			i.var_expr.accept(self)
			struct_obj[i.var_id.lexeme] = self.current_value
		self.sym_table.pop_environment()
		self.sym_table.set_env_id(curr_env)
		
		oid = id(struct_obj)
		self.heap[oid] = struct_obj
		self.current_value = oid
		
	def visit_call_rvalue(self, call_rvalue):
		# handle built in functions first
		built_ins = ['print', 'length', 'get', 'readi', 'reads',
'readf', 'itof', 'itos', 'ftos', 'stoi', 'stof']
		if call_rvalue.fun.lexeme in built_ins:
			self.__built_in_fun_helper(call_rvalue)
		else:
			#... handle user-defined function calls ...
			fun_info = self.sym_table.get_info(call_rvalue.fun.lexeme)
			curr_env = self.sym_table.get_env_id()
			
			
			arg_vals = []
			for i in call_rvalue.args:
				i.accept(self)
				arg_vals.append(self.current_value)

			self.sym_table.set_env_id(fun_info[0])
			self.sym_table.push_environment()
			
			count = 0
			for i in fun_info[1].params:
				self.sym_table.add_id(i.param_name.lexeme)
				self.sym_table.set_info(i.param_name.lexeme, arg_vals[count])
				count += 1
			try:
				fun_info[1].stmt_list.accept(self)
			except ReturnException:
				pass
			self.sym_table.pop_environment()
			self.sym_table.set_env_id(curr_env)

	def __built_in_fun_helper(self, call_rvalue):
		fun_name = call_rvalue.fun.lexeme
		arg_vals = []
		for i in call_rvalue.args:
			i.accept(self)
			arg_vals.append(self.current_value)
# check for nil values
		for i, arg in enumerate(arg_vals):
			if arg is None:
				msg = "Nil value in arguments for function call"
				self.__error(msg, call_rvalue.fun)
# perform each function
		if fun_name == 'print':
			arg_vals[0] = arg_vals[0].replace(r'\n','\n')
			print(arg_vals[0], end='')
		elif fun_name == 'length':
			self.current_value = len(arg_vals[0])
		elif fun_name == 'get':
			if 0 <= arg_vals[0] < len(arg_vals[1]):
				self.current_value = arg_vals[1][arg_vals[0]]
			else:
				msg = "index out of range"
				self.__error(msg, call_rvalue.fun)
		elif fun_name == 'reads':
			self.current_value = input()
		elif fun_name == 'readi':
			try:
				self.current_value = int(input())
			except ValueError:
				self.__error('bad int value', call_rvalue.fun)
		elif fun_name == 'readf':
			try:
				self.current_value = float(input())
			except ValueError:
				self.error('bad float value'. call_rvalue.fun)
		elif fun_name == 'itof':
			try:
				self.current_value = float(arg_vals[0])
			except ValueError:
				self.error('bad conversion from int to float'. call_rvalue.fun)
		elif fun_name == 'itos':
			try:
				self.current_value = str(arg_vals[0])
			except ValueError:
				self.error('bad conversion from int to string'. call_rvalue.fun)
		elif fun_name == 'ftos':
			try:
				self.current_value = str(arg_vals[0])
			except ValueError:
				self.error('bad conversion from float to string'. call_rvalue.fun)
		elif fun_name == 'stoi':
			try:
				self.current_value = int(arg_vals[0])
			except ValueError:
				self.error('bad conversion from string to int'. call_rvalue.fun)
		elif fun_name == 'stof':
			try:
				self.current_value = float(arg_vals[0])
			except ValueError:
				self.error('bad conversion from string to float'. call_rvalue.fun)

	def visit_id_rvalue(self, id_rvalue):
		var_name = id_rvalue.path[0].lexeme
		var_val = self.sym_table.get_info(var_name)
		for path_id in id_rvalue.path[1:]:
			struct_obj = self.heap[var_val]
			var_val = struct_obj[path_id.lexeme]
		 
		self.current_value = var_val

