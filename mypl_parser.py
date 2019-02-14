# Michael Newell
# mypl_parser.py aims to identify errors in syntax in mypl

import mypl_error as error
import mypl_lexer as lexer
import mypl_token as token
import mypl_ast as ast


class Parser(object):
	ctt = ''
	def __init__(self, lexer):
		self.lexer = lexer
		self.current_token = None
		
	def parse(self):
		"""succeeds if program is syntactically well-formed"""
		stmt_list_node = ast.StmtList()
		self.__advance()
		self.__stmts(stmt_list_node)
		self.__eat(token.EOS, 'expecting end of file')
		return stmt_list_node
		
	def __advance(self):
		self.current_token = self.lexer.next_token()
	def __eat(self, tokentype, error_msg):
		if self.current_token.tokentype == tokentype:
			self.__advance()
		else:
			self.__error(error_msg)
			
	def __error(self, error_msg):
		s = error_msg + ', found "' + self.current_token.lexeme + '" in parser'
		l = self.current_token.line
		c = self.current_token.column
		raise error.MyPLError(error_msg, l, c)
		
	#Helper function
	
	def isEXPR(self): 
	#Helps by checking if token is an expr
		ctt = self.current_token.tokentype
		if ctt == token.LPAREN or ctt == token.STRINGVAL or ctt == token.INTVAL or ctt == token.BOOLVAL or ctt == token.FLOATVAL or ctt == token.NIL or ctt == token.NEW or ctt == token.ID:
			return True
		else:
			return False
		
	# Beginning of recursive descent functions
	
	def __stmts(self, stmt_list_node):
		"""<stmts> ::= <stmt> <stmts> | e"""
		if self.current_token.tokentype != token.EOS:
			self.__stmt(stmt_list_node)
			self.__stmts(stmt_list_node)
		
	def __stmt(self, stmt_list_node):
		"""<stmt> ::= <sdecl> | <fdecl> | <bstmt>"""
		if self.current_token.tokentype == token.STRUCTTYPE:
			stmt_list_node.stmts.append(self.__sdecl())
		elif self.current_token.tokentype == token.FUN:
			stmt_list_node.stmts.append(self.__fdecl())
		else:
			stmt_list_node.stmts.append(self.__bstmt())
	
	def __sdecl(self):
		s_decl_stmt = ast.StructDeclStmt()
		self.__eat(token.STRUCTTYPE, "Expected STRUCT token")
		s_decl_stmt.struct_id = self.current_token
		self.__eat(token.ID, "Expected ID token")
		s_decl_stmt.var_decls.append(self.__vdecls())
		self.__eat(token.END, "Expected END token")
		return s_decl_stmt
		
	def __fdecl(self):
		fun_decl = ast.FunDeclStmt()
		self.__eat(token.FUN, "Expected FUN token")
		if self.current_token.tokentype == token.NIL:
			self.__advance()
		else: 
			fun_decl.return_type = self.__type()
		fun_decl.fun_name = self.current_token
		self.__eat(token.ID, "Expected ID token")
		self.__eat(token.LPAREN, "Expected LPAREN token")
		self.__params(fun_decl)
		self.__eat(token.RPAREN, "Expected RPAREN token")
		fun_decl.stmt_list = self.__bstmts()
		self.__eat(token.END, "Expected END token")
		
	def __bstmt(self):
		if self.current_token.tokentype == token.VAR:
			stmt = ast.VarDeclStmt()
			self.__vdecl(stmt)
			return stmt
		elif self.current_token.tokentype == token.SET:
			stmt = ast.AssignStmt()
			self.__assign(stmt)
			return stmt
		elif self.current_token.tokentype == token.IF:
			stmt = ast.IfStmt()
			self.__cond(stmt)
			return stmt
		elif self.current_token.tokentype == token.WHILE:
			stmt = ast.WhileStmt()
			self.__while(stmt)
			return stmt
		elif self.current_token.tokentype == token.RETURN:
			stmt = ast.ReturnStmt()
			self.__exit(stmt)
			return stmt
		else:
			stmt = ast.ExprStmt()
			stmt.expr = self.__expr()
			self.__eat(token.SEMICOLON, "Expected SEMICOLON token")
			return stmt
			
	def __bstmts(self):
		stmt_list = ast.StmtList()
		ctt = self.current_token.tokentype
		if ctt == token.VAR or ctt == token.SET or ctt == token.IF or ctt == token.WHILE or ctt == token.RETURN or ctt == token.LPAREN or ctt == token.STRINGVAL or ctt == token.INTVAL or ctt == token.BOOLVAL or ctt == token.NIL or ctt == token.NEW or ctt == token.ID:
			stmt_list.stmts.append(self.__bstmt())
			stmt_list.stmts.append(self.__bstmts())
		return stmt_list
		#else:
			#nothing	
	def __params(self, fun):
		funParam = ast.FunParam()
		if self.current_token.tokentype == token.ID:
			funParam.param_name = self.current_token
			self.__eat(token.ID, "Expected ID token")
			self.__eat(token.COLON, "Expected COLON token")
			funParam.param_type = self.__type()
			fun.params.append(funParam)
			while self.current_token.tokentype == token.COMMA:
				self.__advance()
				funParam.param_name = self.current_token
				self.__eat(token.ID, "Expected ID token")
				self.__eat(token.COLON, "Expected COLON token")
				funParam.param_type = self.__type()
				fun.params.append(funParam)
		#else:
			#nothing
	def __vdecls(self):
		v_decl_stmt = ast.VarDeclStmt()
		if self.current_token.tokentype == token.VAR:
			self.__vdecl(v_decl_stmt)
			self.__vdecls()
		return v_decl_stmt
		#else: nothing
	
	def __type(self):
		ctt = self.current_token.tokentype
		if not ctt == token.ID and not ctt == token.INTTYPE and not ctt == token.FLOATTYPE and not ctt == token.BOOLTYPE and not ctt == token.STRINGTYPE:
			self.__eat(token.ID, "Expected a type")
		else:
			curr = self.current_token
			self.__advance()
			return curr
	
	def __exit(self, stmt):
		self.__eat(token.RETURN, "Expected a RETURN token")
		if self.isEXPR():
			stmt.return_expr = self.__expr()
		self.__eat(token.SEMICOLON, "Expected a SEMICOLON token")
	
	def __vdecl(self, v_decl_stmt):
		self.__eat(token.VAR, "Expected VAR token")
		v_decl_stmt.var_id = self.current_token
		self.__eat(token.ID, "Expected ID token")
		v_decl_stmt.var_type = self.__tdecl()
		self.__eat(token.ASSIGN, "Expected ASSIGN token")
		v_decl_stmt.var_expr = self.__expr()
		self.__eat(token.SEMICOLON, "Expected SEMICOLON token")
	
	def __tdecl(self): 
		if self.current_token.tokentype == token.COLON:
			self.__eat(token.COLON, "Expected COLON token")
			return self.__type()
	
	def __assign(self, a_stmt):
		self.__eat(token.SET, "Expected SET token")
		a_stmt.lhs = self.__lvalue()
		self.__eat(token.ASSIGN, "Expected ASSIGN token")
		a_stmt.rhs = self.__expr()
		self.__eat(token.SEMICOLON, "Expected SEMICOLON token")
		
	def __lvalue(self):
		Lval = ast.LValue()
		Lval.path.append(self.current_token)
		self.__eat(token.ID, "Expected ID token")
		while self.current_token.tokentype == token.DOT:
			self.__eat(token.DOT, "Expected DOT token")
			Lval.path.append(self.current_token)
			self.__eat(token.ID, "Expected ID token")
		return Lval
	
	def __cond(self, stmt):
		basic_if = ast.BasicIf()
		self.__eat(token.IF, "Expected IF token")
		basic_if.bool_expr = self.__bexpr()
		self.__eat(token.THEN, "Expected THEN token")
		basic_if.stmt_list = self.__bstmts()
		stmt.if_part = basic_if
		self.__condt(stmt)
		self.__eat(token.END, "Expected END token")
	
	def __condt(self, stmt):
		basic_if = ast.BasicIf()
		if self.current_token.tokentype == token.ELIF:
			self.__eat(token.ELIF, "Expected ELIF token")
			basic_if.bool_expr = self.__bexpr()
			self.__eat(token.THEN, "Expected THEN token")
			basic_if.stmt_list = self.__bstmts()
			stmt.elseifs.append(basic_if)
			self.__condt(stmt)
		elif self.current_token.tokentype == token.ELSE:
			stmt.has_else = True
			self.__eat(token.ELSE, "Expected ELSE token")
			stmt.else_stmts = self.__bstmts()
	def __while(self, stmt):
		self.__eat(token.WHILE, "Expected WHILE token")
		stmt.bool_expr = self.__bexpr()
		self.__eat(token.DO, "Expected DO token")
		stmt.stmt_list = self.__bstmts()
		self.__eat(token.END, "Expected END token")
	def __expr(self):
		if self.current_token.tokentype == token.LPAREN:
			SExpr = ast.SimpleExpr()
			self.__eat(token.LPAREN, "Expected LPAREN token")
			SExpr = self.__expr()
			self.__eat(token.RPAREN, "Expected RPAREN token")
			if self.current_token.tokentype == token.PLUS or self.current_token.tokentype == token.MINUS or self.current_token.tokentype == token.DIVIDE or self.current_token.tokentype == token.MULTIPLY or self.current_token.tokentype == token.MODULO:
				CExpr = ast.ComplexExpr()
				CExpr.first_operand = SExpr
				CExpr.math_rel = self.__mathrel()
				CExpr.rest = self.__expr()
				return CExpr
			return SExpr			
		else:
			SExpr = ast.SimpleExpr()
			SExpr.term = self.__rvalue()
			if self.current_token.tokentype == token.PLUS or self.current_token.tokentype == token.MINUS or self.current_token.tokentype == token.DIVIDE or self.current_token.tokentype == token.MULTIPLY or self.current_token.tokentype == token.MODULO:
				CExpr = ast.ComplexExpr()
				CExpr.first_operand = SExpr
				CExpr.math_rel = self.__mathrel()
				CExpr.rest = self.__expr()
				return CExpr
			return SExpr
				
	def __mathrel(self):
		ctt = self.current_token.tokentype
		if not ctt == token.PLUS and not ctt == token.MINUS and not ctt == token.DIVIDE and not ctt == token.MULTIPLY and not ctt == token.MODULO:
			self.__eat(token.PLUS, "Expected Math operator")
			#error?
		else:
			curr = self.current_token
			self.__advance()
			return curr
	def __rvalue(self):
		ctt = self.current_token.tokentype
		if ctt == token.STRINGVAL or ctt == token.INTVAL or ctt == token.BOOLVAL or ctt == token.FLOATVAL or ctt == token.NIL:
			rval = ast.SimpleRValue()
			rval.val = self.current_token
			self.__advance()
		elif ctt == token.NEW:
			rval = ast.NewRValue()
			self.__eat(token.NEW, "Expected NEW token")
			rval.struct_type = self.current_token
			self.__eat(token.ID, "Expected ID token")
		else:
			rval = self.__idrval()
		return rval
		
	def __idrval(self):
		curr = self.current_token
		self.__eat(token.ID, "Expected ID token")
		rval = ast.IDRValue()
		rval.path.append(curr)
		if self.current_token.tokentype == token.DOT:
			while self.current_token.tokentype == token.DOT:
				self.__eat(token.DOT, "Expected DOT token")
				rval.path.append(self.current_token)
				self.__eat(token.ID, "Expected ID token")
			return rval
		elif self.current_token.tokentype == token.LPAREN:
			rval = ast.CallRValue()
			rval.fun = curr
			self.__eat(token.LPAREN, "Expected LPAREN token")
			self.__exprlist(rval)
			self.__eat(token.RPAREN, "Expected RPAREN token")
			return rval
		return rval
			
	def __exprlist(self, rval):
		if self.isEXPR():
			rval.args.append(self.__expr())
			while self.current_token.tokentype == token.COMMA:
				self.__eat(token.COMMA, "Expected COMMA token")
				rval.args.append(self.__expr())
		
	def __bexpr(self):
		bexpr = ast.BoolExpr()
		if self.current_token.tokentype == token.LPAREN:
			self.__eat(token.LPAREN, "Expected expression")
			bexpr = self.__bexpr()
			self.__eat(token.RPAREN, "Expected RPAREN token")
			self.__bconnct(bexpr)
			return bexpr
		elif self.current_token.tokentype == token.NOT:
			self.__eat(token.NOT, "Expected NOT token")
			bexpr = self.__bexpr()
			self.__bexprt(bexpr)
			bexpr.negated = True
			return bexpr
		else:
			bexpr.first_expr = self.__expr()
			self.__bexprt(bexpr)
			return bexpr
			
			
	def __bexprt(self, bexpr):
		ctt = self.current_token.tokentype
		if ctt == token.EQUAL or ctt == token.LESS_THAN or ctt == token.GREATER_THAN or ctt == token.LESS_THAN_EQUAL or ctt == token.GREATER_THAN_EQUAL or ctt == token.NOT_EQUAL:
			bexpr.bool_rel = self.__boolrel()
			bexpr.second_expr = self.__expr()
			self.__bconnct(bexpr)
		else:
			self.__bconnct(bexpr)
			
	def __bconnct(self, bexpr):
		if self.current_token.tokentype == token.AND:
			bexpr.bool_connector = self.current_token
			self.__advance()
			bexpr.rest = self.__bexpr()
		elif self.current_token.tokentype == token.OR:
			bexpr.bool_connector = self.current_token
			self.__advance()
			bexpr.rest = self.__bexpr()
		
	def __boolrel(self):
		ctt = self.current_token.tokentype
		if ctt == token.EQUAL or ctt == token.LESS_THAN or ctt == token.GREATER_THAN or ctt == token.LESS_THAN_EQUAL or ctt == token.GREATER_THAN_EQUAL or ctt == token.NOT_EQUAL:
			curr = self.current_token
			self.__advance()
			return curr
		else:
			self.__eat(token.EQUAL, "Expected boolrel token")	
			
