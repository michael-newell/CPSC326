import mypl_token as token
import mypl_error as error
class Lexer(object):
	def __init__(self, input_stream):
		self.line = 1
		self.column = 0
		self.input_stream = input_stream
	def __peek(self):
		pos = self.input_stream.tell()
		symbol = self.input_stream.read(1)
		self.input_stream.seek(pos)
		return symbol
	def __read(self):
		return self.input_stream.read(1)
	def next_token(self):
		symbol = ''
		currToken = ''
		currColumn = self.column + 1
		currLine = self.line
		if self.__peek() == '':
			symbol = token.EOS
			currToken = ''
			the_token = token.Token(symbol, currToken, currLine, 0)
			return the_token
		elif self.__peek() == '#':
			while self.__peek() != '\n':
				self.__read()
			return self.next_token()
		elif self.__peek() == '\n':
			self.__read()
			self.line += 1
			self.column = 0
			return self.next_token()
		elif self.__peek() == '\t':
			while self.__peek() == '\t':
				self.__read()
				self.column += 1
				return self.next_token()
		elif self.__peek() == ' ':
			while self.__peek() == ' ':
				self.__read()
				self.column += 1
				return self.next_token()
		elif self.__peek() == '"':
			self.__read()
			self.column += 1
			symbol = token.STRINGVAL
			while self.__peek() != '"':
				currToken += self.__read()
				self.column += 1
			self.__read()
			self.column += 1
		elif self.__peek() == '=':
			self.__read()
			self.column += 1
			if self.__peek() == '=':
				self.__read()
				self.column += 1
				symbol = token.EQUAL
				currToken = '=='
			else:
				symbol = token.ASSIGN
				currToken = '='
		elif self.__peek() == ':':
			self.__read()
			self.column += 1
			symbol = token.COLON
			currToken = ':'
		elif self.__peek() == ',':
			self.__read()
			self.column += 1
			symbol = token.COMMA
			currToken = ','
		elif self.__peek() == '/':
			self.__read()
			self.column += 1
			symbol = token.DIVIDE
			currToken = '/'
		elif self.__peek().isdigit():
			symbol = token.INTVAL
			while self.__peek().isdigit():
				currToken += self.__read()
				self.column += 1
			if self.__peek() == '.':
				symbol = token.FLOATVAL
				currToken += self.__read()
				self.column += 1
				if self.__peek().isdigit():
					while self.__peek().isdigit():
						currToken += self.__read()
						self.column += 1
				#else:
					#exception
		elif self.__peek() == '.':
			self.__read()
			self.column += 1
			symbol = token.DOT
			currToken = '.'
		elif self.__peek() == '<':
			self.__read()
			self.column += 1
			symbol = token.LESS_THAN
			currToken = '<'
			if self.__peek() == '=':
				self.__read()
				self.column += 1
				symbol = token.LESS_THAN_EQUAL
				currToken = '<='
		elif self.__peek() == '>':
			self.__read()
			self.column += 1
			symbol = token.GREATER_THAN
			currToken = '>'
			if self.__peek() == '=':
				self.__read()
				self.column += 1
				symbol = token.GREATER_THAN_EQUAL
				currToken = '>='
		elif self.__peek() == '!':
			self.__read()
			self.column += 1
			#symbol = token.NOT
			currToken = '!'
			if self.__peek() == '=':
				self.__read()
				self.column += 1
				symbol = token.NOT_EQUAL
				currToken = '!='
		elif self.__peek() == '(':
			self.__read()
			self.column += 1
			symbol = token.LPAREN
			currToken = '('
		elif self.__peek() == ')':
			self.__read()
			self.column += 1
			symbol = token.RPAREN
			currToken = ')'
		elif self.__peek() == '-':
			self.__read()
			self.column += 1
			symbol = token.MINUS
			currToken = '-'
		elif self.__peek() == '%':
			self.__read()
			self.column += 1
			symbol = token.MODULO
			currToken = '%'
		elif self.__peek() == '*':
			self.__read()
			self.column += 1
			symbol = token.MULTIPLY
			currToken = '*'
		elif self.__peek() == '+':
			self.__read()
			self.column += 1
			symbol = token.PLUS
			currToken = '+'
		elif self.__peek() == ';':
			self.__read()
			self.column += 1
			symbol = token.SEMICOLON
			currToken = ';'
		elif self.__peek() == 'b':
			while self.__peek() != ' ' and self.__peek() != '' and self.__peek() != '\t' and self.__peek() != '\n' and self.__peek() != '.' and self.__peek() != ';' and self.__peek() != ',' and self.__peek() != '(' and self.__peek() != ')' and self.__peek() != '-' and self.__peek() != '+' and self.__peek() != '%' and self.__peek() != '*' and self.__peek() != '>' and self.__peek() != '<' and self.__peek() != '=' and self.__peek() != '/' and self.__peek() != ':':
				currToken += self.__read()
				self.column += 1
			if currToken == 'bool':
				symbol = token.BOOLTYPE
			else: 
				symbol = token.ID
		elif self.__peek() == 'i':
			while self.__peek() != ' ' and self.__peek() != '' and self.__peek() != '\t' and self.__peek() != '\n' and self.__peek() != '.' and self.__peek() != ';' and self.__peek() != ',' and self.__peek() != '(' and self.__peek() != ')' and self.__peek() != '-' and self.__peek() != '+' and self.__peek() != '%' and self.__peek() != '*' and self.__peek() != '>' and self.__peek() != '<' and self.__peek() != '=' and self.__peek() != '/' and self.__peek() != ':':
				currToken += self.__read()
				self.column += 1
			if currToken == 'int':
				symbol = token.INTTYPE
			elif currToken == 'if':
				symbol = token.IF
			else:
				symbol = token.ID
		elif self.__peek() == 's':
			while self.__peek() != ' ' and self.__peek() != '' and self.__peek() != '\t' and self.__peek() != '\n' and self.__peek() != '.' and self.__peek() != ';' and self.__peek() != ',' and self.__peek() != '(' and self.__peek() != ')' and self.__peek() != '-' and self.__peek() != '+' and self.__peek() != '%' and self.__peek() != '*' and self.__peek() != '>' and self.__peek() != '<' and self.__peek() != '=' and self.__peek() != '/' and self.__peek() != ':':
				currToken += self.__read()
				self.column += 1
			if currToken == 'string':
				symbol = token.STRINGTYPE
			elif currToken == 'struct':
				symbol = token.STRUCTTYPE
			elif currToken == 'set':
				symbol = token.SET
			else:
				symbol = token.ID
		elif self.__peek() == 'a':
			while self.__peek() != ' ' and self.__peek() != '' and self.__peek() != '\t' and self.__peek() != '\n' and self.__peek() != '.' and self.__peek() != ';' and self.__peek() != ',' and self.__peek() != '(' and self.__peek() != ')' and self.__peek() != '-' and self.__peek() != '+' and self.__peek() != '%' and self.__peek() != '*' and self.__peek() != '>' and self.__peek() != '<' and self.__peek() != '=' and self.__peek() != '/' and self.__peek() != ':':
				currToken += self.__read()
				self.column += 1
			if currToken == 'and':
				symbol = token.AND
			else: 
				symbol = token.ID
		elif self.__peek() == 'o':
			while self.__peek() != ' ' and self.__peek() != '' and self.__peek() != '\t' and self.__peek() != '\n' and self.__peek() != '.' and self.__peek() != ';' and self.__peek() != ',' and self.__peek() != '(' and self.__peek() != ')' and self.__peek() != '-' and self.__peek() != '+' and self.__peek() != '%' and self.__peek() != '*' and self.__peek() != '>' and self.__peek() != '<' and self.__peek() != '=' and self.__peek() != '/' and self.__peek() != ':':
				currToken += self.__read()
				self.column += 1
			if currToken == 'or':
				symbol = token.OR
			else:
				symbol = token.ID
		elif self.__peek() == 'w':
			while self.__peek() != ' ' and self.__peek() != '' and self.__peek() != '\t' and self.__peek() != '\n' and self.__peek() != '.' and self.__peek() != ';' and self.__peek() != ',' and self.__peek() != '(' and self.__peek() != ')' and self.__peek() != '-' and self.__peek() != '+' and self.__peek() != '%' and self.__peek() != '*' and self.__peek() != '>' and self.__peek() != '<' and self.__peek() != '=' and self.__peek() != '/' and self.__peek() != ':':
				currToken += self.__read()
				self.column += 1
			if currToken == 'while':
				symbol = token.WHILE
			else:
				symbol = token.ID
		elif self.__peek() == 'd':
			while self.__peek() != ' ' and self.__peek() != '' and self.__peek() != '\t' and self.__peek() != '\n' and self.__peek() != '.' and self.__peek() != ';' and self.__peek() != ',' and self.__peek() != '(' and self.__peek() != ')' and self.__peek() != '-' and self.__peek() != '+' and self.__peek() != '%' and self.__peek() != '*' and self.__peek() != '>' and self.__peek() != '<' and self.__peek() != '=' and self.__peek() != '/' and self.__peek() != ':':
				currToken += self.__read()
				self.column += 1
			if currToken == 'do':
				symbol = token.DO
			else: 
				symbol = token.ID
		elif self.__peek() == 't':
			while self.__peek() != ' ' and self.__peek() != '' and self.__peek() != '\t' and self.__peek() != '\n' and self.__peek() != '.' and self.__peek() != ';' and self.__peek() != ',' and self.__peek() != '(' and self.__peek() != ')' and self.__peek() != '-' and self.__peek() != '+' and self.__peek() != '%' and self.__peek() != '*' and self.__peek() != '>' and self.__peek() != '<' and self.__peek() != '=' and self.__peek() != '/' and self.__peek() != ':':
				currToken += self.__read()
				self.column += 1
			if currToken == 'then':
				symbol = token.THEN
			elif currToken == 'true':
				symbol = token.BOOLVAL
			else:
				symbol = token.ID
		elif self.__peek() == 'e':
			while self.__peek() != ' ' and self.__peek() != '' and self.__peek() != '\t' and self.__peek() != '\n' and self.__peek() != '.' and self.__peek() != ';' and self.__peek() != ',' and self.__peek() != '(' and self.__peek() != ')' and self.__peek() != '-' and self.__peek() != '+' and self.__peek() != '%' and self.__peek() != '*' and self.__peek() != '>' and self.__peek() != '<' and self.__peek() != '=' and self.__peek() != '/' and self.__peek() != ':':
				currToken += self.__read()
				self.column += 1
			if currToken == 'else':
				symbol = token.ELSE
			elif currToken == 'elif':
				symbol = token.ELIF
			elif currToken == 'end':
				symbol = token.END
			else: 
				symbol = token.ID
		elif self.__peek() == 'f':
			while self.__peek() != ' ' and self.__peek() != '' and self.__peek() != '\t' and self.__peek() != '\n' and self.__peek() != '.' and self.__peek() != ';' and self.__peek() != ',' and self.__peek() != '(' and self.__peek() != ')' and self.__peek() != '-' and self.__peek() != '+' and self.__peek() != '%' and self.__peek() != '*' and self.__peek() != '>' and self.__peek() != '<' and self.__peek() != '=' and self.__peek() != '/' and self.__peek() != ':':
				currToken += self.__read()
				self.column += 1
			if currToken == 'fun':
				symbol = token.FUN
			elif currToken == 'false':
				symbol = token.BOOLVAL
			elif currToken == 'float':
				symbol = token.FLOATTYPE
			else:
				symbol = token.ID
		elif self.__peek() == 'v':
			while self.__peek() != ' ' and self.__peek() != '' and self.__peek() != '\t' and self.__peek() != '\n' and self.__peek() != '.' and self.__peek() != ';' and self.__peek() != ',' and self.__peek() != '(' and self.__peek() != ')' and self.__peek() != '-' and self.__peek() != '+' and self.__peek() != '%' and self.__peek() != '*' and self.__peek() != '>' and self.__peek() != '<' and self.__peek() != '=' and self.__peek() != '/' and self.__peek() != ':':
				currToken += self.__read()
				self.column += 1
			if currToken == 'var':
				symbol = token.VAR
			else: 
				symbol = token.ID
		elif self.__peek() == 'r':
			while self.__peek() != ' ' and self.__peek() != '' and self.__peek() != '\t' and self.__peek() != '\n' and self.__peek() != '.' and self.__peek() != ';' and self.__peek() != ',' and self.__peek() != '(' and self.__peek() != ')' and self.__peek() != '-' and self.__peek() != '+' and self.__peek() != '%' and self.__peek() != '*' and self.__peek() != '>' and self.__peek() != '<' and self.__peek() != '=' and self.__peek() != '/' and self.__peek() != ':':
				currToken += self.__read()
				self.column += 1
			if currToken == 'return':
				symbol = token.RETURN
			else: 
				symbol = token.ID
		elif self.__peek() == 'n':
			while self.__peek() != ' ' and self.__peek() != '' and self.__peek() != '\t' and self.__peek() != '\n' and self.__peek() != '.' and self.__peek() != ';' and self.__peek() != ',' and self.__peek() != '(' and self.__peek() != ')' and self.__peek() != '-' and self.__peek() != '+' and self.__peek() != '%' and self.__peek() != '*' and self.__peek() != '>' and self.__peek() != '<' and self.__peek() != '=' and self.__peek() != '/' and self.__peek() != ':':
				currToken += self.__read()
				self.column += 1
			if currToken == 'new':
				symbol = token.NEW
			elif currToken == 'nil':
				symbol = token.NIL
			elif currToken == 'not':
				symbol = token.NOT
			else: 
				symbol = token.ID	
		else:
			while self.__peek() != ' ' and self.__peek() != '' and self.__peek() != '\t' and self.__peek() != '\n' and self.__peek() != '.' and self.__peek() != ';' and self.__peek() != ',' and self.__peek() != '(' and self.__peek() != ')' and self.__peek() != '-' and self.__peek() != '+' and self.__peek() != '%' and self.__peek() != '*' and self.__peek() != '>' and self.__peek() != '<' and self.__peek() != '=' and self.__peek() != '/' and self.__peek() != ':':
				currToken += self.__read()
				self.column += 1
			symbol = token.ID
		the_token = token.Token(symbol, currToken, currLine, currColumn)
		return the_token
