# Michael Newell
# Assignment 3
# mypl_parser.py aims to identify errors in syntax in mypl

import mypl_error as error
import mypl_lexer as lexer
import mypl_token as token


class Parser(object):
	ctt = ''
	def __init__(self, lexer):
		self.lexer = lexer
		self.current_token = None
		
	def parse(self):
		"""succeeds if program is syntactically well-formed"""
		self.__advance()
		self.__stmts()
		self.__eat(token.EOS, 'expecting end of file')
		
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
	
	def __stmts(self):
		"""<stmts> ::= <stmt> <stmts> | e"""
		if self.current_token.tokentype != token.EOS:
			self.__stmt()
			self.__stmts()
		
	def __stmt(self):
		"""<stmt> ::= <sdecl> | <fdecl> | <bstmt>"""
		if self.current_token.tokentype == token.STRUCTTYPE:
			self.__sdecl()
		elif self.current_token.tokentype == token.FUN:
			self.__fdecl()
		else:
			self.__bstmt()
	
	def __sdecl(self):
		self.__eat(token.STRUCTTYPE, "Expected STRUCT token")
		self.__eat(token.ID, "Expected ID token")
		self.__vdecls()
		self.__eat(token.END, "Expected END token")
		
	def __fdecl(self):
		self.__eat(token.FUN, "Expected FUN token")
		if self.current_token.tokentype == token.NIL:
			self.__advance()
		else: 
			self.__type()
		self.__eat(token.ID, "Expected ID token")
		self.__eat(token.LPAREN, "Expected LPAREN token")
		self.__params()
		self.__eat(token.RPAREN, "Expected RPAREN token")
		self.__bstmts()
		self.__eat(token.END, "Expected END token")
	def __bstmt(self):
		if self.current_token.tokentype == token.VAR:
			self.__vdecl()
		elif self.current_token.tokentype == token.SET:
			self.__assign()
		elif self.current_token.tokentype == token.IF:
			self.__cond()
		elif self.current_token.tokentype == token.WHILE:
			self.__while()
		elif self.current_token.tokentype == token.RETURN:
			self.__exit()
		else:
			self.__expr()
			self.__eat(token.SEMICOLON, "Expected SEMICOLON token")
	def __bstmts(self):
		ctt = self.current_token.tokentype
		if ctt == token.VAR or ctt == token.SET or ctt == token.IF or ctt == token.WHILE or ctt == token.RETURN or ctt == token.LPAREN or ctt == token.STRINGVAL or ctt == token.INTVAL or ctt == token.BOOLVAL or ctt == token.NIL or ctt == token.NEW or ctt == token.ID:
			self.__bstmt()
			self.__bstmts()
		#else:
			#nothing	
	def __params(self):
		if self.current_token.tokentype == token.ID:
			self.__eat(token.ID, "Expected ID token")
			self.__eat(token.COLON, "Expected COLON token")
			self.__type()
			while self.current_token.tokentype == token.COMMA:
				self.__advance()
				self.__eat(token.ID, "Expected ID token")
				self.__eat(token.COLON, "Expected COLON token")
				self.__type()
		#else:
			#nothing
	def __vdecls(self):
		if self.current_token.tokentype == token.VAR:
			self.__vdecl()
			self.__vdecls()
		#else: nothing
	
	def __type(self):
		ctt = self.current_token.tokentype
		if not ctt == token.ID and not ctt == token.INTTYPE and not ctt == token.FLOATTYPE and not ctt == token.BOOLTYPE and not ctt == token.STRINGTYPE:
			self.__eat(token.ID, "Expected a type")
		else:
			self.__advance()
	
	def __exit(self):
		self.__eat(token.RETURN, "Expected a RETURN token")
		if self.isEXPR():
			self.__expr()
		self.__eat(token.SEMICOLON, "Expected a SEMICOLON token")
	
	def __vdecl(self):
		self.__eat(token.VAR, "Expected VAR token")
		self.__eat(token.ID, "Expected ID token")
		self.__tdecl()
		self.__eat(token.ASSIGN, "Expected ASSIGN token")
		self.__expr()
		self.__eat(token.SEMICOLON, "Expected SEMICOLON token")
	
	def __tdecl(self):
		if self.current_token.tokentype == token.COLON:
			self.__eat(token.COLON, "Expected COLON token")
			self.__type()
	
	def __assign(self):
		self.__eat(token.SET, "Expected SET token")
		self.__lvalue()
		self.__eat(token.ASSIGN, "Expected ASSIGN token")
		self.__expr()
		self.__eat(token.SEMICOLON, "Expected SEMICOLON token")
		
	def __lvalue(self):
		self.__eat(token.ID, "Expected ID token")
		while self.current_token.tokentype == token.DOT:
			self.__eat(token.DOT, "Expected DOT token")
			self.__eat(token.ID, "Expected ID token")
	
	def __cond(self):
		self.__eat(token.IF, "Expected IF token")
		self.__bexpr()
		self.__eat(token.THEN, "Expected THEN token")
		self.__bstmts()
		self.__condt()
		self.__eat(token.END, "Expected END token")
	
	def __condt(self):
		if self.current_token.tokentype == token.ELIF:
			self.__eat(token.ELIF, "Expected ELIF token")
			self.__bexpr()
			self.__eat(token.THEN, "Expected THEN token")
			self.__bstmts()
			self.__condt()
		elif self.current_token.tokentype == token.ELSE:
			self.__eat(token.ELSE, "Expected ELSE token")
			self.__bstmts()
	def __while(self):
		self.__eat(token.WHILE, "Expected WHILE token")
		self.__bexpr()
		self.__eat(token.DO, "Expected DO token")
		self.__bstmts()
		self.__eat(token.END, "Expected END token")
	def __expr(self):
		if self.current_token.tokentype == token.LPAREN:
			self.__eat(token.LPAREN, "Expected LPAREN token")
			self.__expr()
			self.__eat(token.RPAREN, "Expected RPAREN token")
			if self.current_token.tokentype == token.PLUS or self.current_token.tokentype == token.MINUS or self.current_token.tokentype == token.DIVIDE or self.current_token.tokentype == token.MULTIPLY or self.current_token.tokentype == token.MODULO:
				self.__mathrel()
				self.__expr()			
		else:
			self.__rvalue()
			if self.current_token.tokentype == token.PLUS or self.current_token.tokentype == token.MINUS or self.current_token.tokentype == token.DIVIDE or self.current_token.tokentype == token.MULTIPLY or self.current_token.tokentype == token.MODULO:
				self.__mathrel()
				self.__expr()
				
	def __mathrel(self):
		ctt = self.current_token.tokentype
		if not ctt == token.PLUS and not ctt == token.MINUS and not ctt == token.DIVIDE and not ctt == token.MULTIPLY and not ctt == token.MODULO:
			self.__eat(token.PLUS, "Expected Math operator")
		else:
			self.__advance()
	def __rvalue(self):
		ctt = self.current_token.tokentype
		if ctt == token.STRINGVAL or ctt == token.INTVAL or ctt == token.BOOLVAL or ctt == token.FLOATVAL or ctt == token.NIL:
			self.__advance()
		elif ctt == token.NEW:
			self.__eat(token.NEW, "Expected NEW token")
			self.__eat(token.ID, "Expected ID token")
		else:
			self.__idrval()
		
	def __idrval(self):
		self.__eat(token.ID, "Expected ID token")
		if self.current_token.tokentype == token.DOT:
			while self.current_token.tokentype == token.DOT:
				self.__eat(token.DOT, "Expected DOT token")
				self.__eat(token.ID, "Expected ID token")
		elif self.current_token.tokentype == token.LPAREN:
			self.__eat(token.LPAREN, "Expected LPAREN token")
			self.__exprlist()
			self.__eat(token.RPAREN, "Expected RPAREN token")
			
	def __exprlist(self):
		if self.isEXPR():
			self.__expr()
			while self.current_token.tokentype == token.COMMA:
				self.__eat(token.COMMA, "Expected COMMA token")
				self.__expr()
		
	def __bexpr(self):
		if self.current_token.tokentype == token.LPAREN:
			self.__eat(token.LPAREN, "Expected expression")
			self.__bexpr()
			self.__eat(token.RPAREN, "Expected RPAREN token")
			self.__bconnct()
		elif self.current_token.tokentype == token.NOT:
			self.__eat(token.NOT, "Expected NOT token")
			self.__bexpr()
			self.__bexprt()
		else:
			self.__expr()
			self.__bexprt()
			
			
	def __bexprt(self):
		ctt = self.current_token.tokentype
		if ctt == token.EQUAL or ctt == token.LESS_THAN or ctt == token.GREATER_THAN or ctt == token.LESS_THAN_EQUAL or ctt == token.GREATER_THAN_EQUAL or ctt == token.NOT_EQUAL:
			self.__boolrel()
			self.__expr()
			self.__bconnct()
		else:
			self.__bconnct()
			
	def __bconnct(self):
		if self.current_token.tokentype == token.AND:
			self.__advance()
			self.__bexpr()
		elif self.current_token.tokentype == token.OR:
			self.__advance()
			self.__bexpr()
		
	def __boolrel(self):
		ctt = self.current_token.tokentype
		if ctt == token.EQUAL or ctt == token.LESS_THAN or ctt == token.GREATER_THAN or ctt == token.LESS_THAN_EQUAL or ctt == token.GREATER_THAN_EQUAL or ctt == token.NOT_EQUAL:
			self.__advance()
		else:
			self.__eat(token.EQUAL, "Expected boolrel token")
			
