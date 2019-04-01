import mypl_error as error
import mypl_lexer as lexer
import mypl_token as token
import mypl_ast as ast

class Parser(object):

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None
        
    def parse(self):
        """succeeds if program is syntactically well-formed"""
        self.__advance()
        stmt_list_node = self.__stmts(ast.StmtList())
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
        raise error.MyPLError(s, l, c)
        
    # Beginning of recursive descent functions
    
    def __stmts(self, stmt_list_node):
        """<stmts> ::= <stmt> <stmts> | e"""
        if self.current_token.tokentype != token.EOS:
            stmt_list_node.stmts.append(self.__stmt())
            self.__stmts(stmt_list_node)
        return stmt_list_node
            
    def __stmt(self):
        """<stmt> ::= <sdecl> | <fdecl> | <bstmt>"""
        if self.current_token.tokentype == token.STRUCTTYPE:
            return self.__sdecl()
        elif self.current_token.tokentype == token.FUN:
            return self.__fdecl()
        else:
            return self.__bstmt()
        
    def __bstmts(self, stmt_list_node):
        """<bstmts> ::= <bstmt> <bstmts> | e"""
        help = [token.VAR, token.SET, token.IF, token.WHILE, token.LPAREN, token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.ID, token.RETURN]
        if(self.current_token.tokentype in help):
          stmt_list_node.stmts.append(self.__bstmt())
          stmt_list_node = self.__bstmts(stmt_list_node)
        return stmt_list_node
          
    def __bstmt(self):
        """<bstmt> ::= <vdecl> | <assign> | <cond> | <while> | <expr> SEMICOLON | <exit>"""
        if(self.current_token.tokentype == token.VAR):
            return self.__vdecl()
        elif(self.current_token.tokentype == token.SET):
            return self.__assign()
        elif(self.current_token.tokentype == token.IF):
            return self.__cond()
        elif(self.current_token.tokentype == token.WHILE):
            return self.__while()
        elif(self.current_token.tokentype == token.RETURN):
            return self.__exit()
        else:
            expr_stmt_node = ast.ExprStmt()
            expr_stmt_node.expr = self.__expr()
            self.__eat(token.SEMICOLON, 'expecting ";"')
            return expr_stmt_node
            
    def __sdecl(self):
        """<sdecl> ::= STRUCT ID <vdecls> END"""
        struct_node = ast.StructDeclStmt()
        self.__eat(token.STRUCTTYPE, 'expecting "struct"')
        struct_node.struct_id = self.current_token
        self.__eat(token.ID, 'expecting "ID"')
        struct_node.var_decls = self.__vdecls([])
        self.__eat(token.END, 'expecting "end"')
        return struct_node
    
    def __vdecls(self, var_list):
        """<vdecls> ::= <vdecl> <vdecls> | e"""
        if(self.current_token.tokentype == token.VAR):
            var_list.append(self.__vdecl())
            self.__vdecls(var_list)
        return var_list
            
    def __fdecl(self):
        """<fdecl> ::= FUN ( <type> | NIL ) ID LPAREN <params> RPAREN <bstmts> END"""
        fun_decl_node = ast.FunDeclStmt()
        self.__eat(token.FUN, 'expecting "fun"')
        fun_decl_node.return_type = self.current_token
        if(self.current_token.tokentype == token.NIL):
            self.__advance()
        else:
            self.__type()
        fun_decl_node.fun_name = self.current_token
        self.__eat(token.ID, 'expecting "ID"')
        self.__eat(token.LPAREN, 'expecting "("')
        fun_decl_node.params = self.__params()
        self.__eat(token.RPAREN, 'expecting ")"')
        fun_decl_node.stmt_list = self.__bstmts(ast.StmtList())
        self.__eat(token.END, 'expecting "end"')
        return fun_decl_node
        
    def __params(self):
        """<params> ::= ID COLON <type> ( COMMA ID COLON <type> )* | e"""
        param_list = []
        if(self.current_token.tokentype == token.ID):
            fun_params_node = ast.FunParam()
            fun_params_node.param_name = self.current_token
            self.__advance()
            self.__eat(token.COLON, 'expecting ":"')
            fun_params_node.param_type = self.__type()
            param_list.append(fun_params_node)
            while(self.current_token.tokentype == token.COMMA):
                self.__advance()
                fun_params_node = ast.FunParam()
                fun_params_node.param_name = self.current_token
                self.__eat(token.ID, 'expecting "ID"')
                self.__eat(token.COLON, 'expecting ":"')
                fun_params_node.param_type = self.__type()
                param_list.append(fun_params_node)
        return param_list
                
    def __type(self):
        """<type> ::= ID | INTTYPE | FLOATTYPE | BOOLTYPE | STRINGTYPE"""
        if(self.current_token.tokentype == token.ID):
            type = self.current_token
            self.__eat(token.ID, 'expecting "ID"')
            return type
        elif(self.current_token.tokentype == token.INTTYPE):
            type = self.current_token
            self.__eat(token.INTTYPE, 'expecting "int"')
            return type
        elif(self.current_token.tokentype == token.FLOATTYPE):
            type = self.current_token
            self.__eat(token.FLOATTYPE, 'execting "float"')
            return type
        elif(self.current_token.tokentype == token.BOOLTYPE):
            type = self.current_token
            self.__eat(token.BOOLTYPE, 'expecting "bool"')
            return type
        elif(self.current_token.tokentype == token.STRINGTYPE):
            type = self.current_token
            self.__eat(token.STRINGTYPE, 'expecting "string"')
            return type
        else:
            self.__error('expecting a type')
            
    def __exit(self):
        """<exit> ::= RETURN ( <expr> | e ) SEMICOLON"""
        return_stmt_node = ast.ReturnStmt()
        exprhelp = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.ID, token.LPAREN]
        return_stmt_node.return_token = self.current_token
        self.__eat(token.RETURN, 'expecting "return"')
        if(self.current_token.tokentype in exprhelp):
            return_stmt_node.return_expr = self.__expr()
        self.__eat(token.SEMICOLON, 'expecting ";"')
        return return_stmt_node
        
    def __vdecl(self):
        """<vdecl> ::= VAR ID <tdecl> ASSIGN <expr> SEMICOLON"""
        var_decl_node = ast.VarDeclStmt()
        self.__eat(token.VAR, 'expecting "var"')
        var_decl_node.var_id = self.current_token
        self.__eat(token.ID, 'expecting "ID"')
        var_decl_node.var_type = self.__tdecl()
        self.__eat(token.ASSIGN, 'expecting "="')
        var_decl_node.var_expr = self.__expr()
        self.__eat(token.SEMICOLON, 'expecting ";"')
        return var_decl_node
        
    def __tdecl(self):
        """<tdecl> ::= COLON <type> | e"""
        if(self.current_token.tokentype == token.COLON):
            self.__advance()
            return self.__type()
        else:
            return None
            
    def __assign(self):
        """<assign> ::= SET <lvalue> ASSIGN <expr> SEMICOLON"""
        assign_stmt_node = ast.AssignStmt()
        self.__eat(token.SET, 'expecting "set"')
        assign_stmt_node.lhs = self.__lvalue()
        self.__eat(token.ASSIGN, 'expecting "="')
        assign_stmt_node.rhs = self.__expr()
        self.__eat(token.SEMICOLON, 'expecting ";"')
        return assign_stmt_node
        
    def __lvalue(self):
        """<lvalue> ::= ID ( DOT ID )*"""
        l_value_node = ast.LValue()
        l_value_node.path.append(self.current_token)
        self.__eat(token.ID, 'expecting "ID"')
        while(self.current_token.tokentype == token.DOT):
            self.__advance()
            l_value_node.path.append(self.current_token)
            self.__eat(token.ID, 'expecting "ID"')
        return l_value_node
            
    def __cond(self):
        """<cond> ::= IF <bexpr> THEN <bstmts> <condt> END"""
        if_stmt_node = ast.IfStmt()
        self.__eat(token.IF, 'expecting "if"')
        if_stmt_node.if_part.bool_expr = self.__bexpr()
        self.__eat(token.THEN, 'expecting "then"')
        if_stmt_node.if_part.stmt_list = self.__bstmts(ast.StmtList())
        if_stmt_node = self.__condt(if_stmt_node)
        self.__eat(token.END, 'expecting "end"')
        return if_stmt_node
        
    def __condt(self, if_stmt_node):
        """<condt> ::= ELIF <bexpr> THEN <bstmts> <condt> | ELSE <bstmts> | e"""
        if(self.current_token.tokentype == token.ELIF):
            self.__advance()
            basic_if_node = ast.BasicIf()
            basic_if_node.bool_expr = self.__bexpr()
            self.__eat(token.THEN, 'expecting "then"')
            basic_if_node.stmt_list = self.__bstmts(ast.StmtList())
            if_stmt_node.elseifs.append(basic_if_node)
            return self.__condt(if_stmt_node)
        elif(self.current_token.tokentype == token.ELSE):
            if_stmt_node.has_else = True
            self.__advance()
            if_stmt_node.else_stmts = self.__bstmts(ast.StmtList())
            return if_stmt_node
        else:
            return if_stmt_node
            
    def __while(self):
        """<while> ::= WHILE <bexpr> DO <bstmts> END"""
        while_stmt_node = ast.WhileStmt()
        self.__eat(token.WHILE, 'expecting "while"')
        while_stmt_node.bool_expr = self.__bexpr()
        self.__eat(token.DO, 'expecting "do"')
        while_stmt_node.stmt_list = self.__bstmts(ast.StmtList())
        self.__eat(token.END, 'expecting "end"')
        return while_stmt_node
        
    def __expr(self):
        """<expr> ::= ( <rvalue> | LPAREN <expr> RPAREN ) ( <mathrel> <expr> | e )"""
        expr = None
        if self.current_token.tokentype == token.LPAREN:
            self.__advance()
            expr = self.__expr()
            self.__eat(token.RPAREN, 'expecting ")"')
        else:
            expr = self.__rvalue()
        mathrels = [token.PLUS, token.MINUS, token.DIVIDE, token.MULTIPLY, token.MODULO]
        if self.current_token.tokentype in mathrels:
            complex_expr_node = ast.ComplexExpr()
            complex_expr_node.first_operand = expr
            complex_expr_node.math_rel = self.__mathrel()
            complex_expr_node.rest = self.__expr()
            return complex_expr_node
        else:
            simple_expr_node = ast.SimpleExpr()
            simple_expr_node.term = expr
            return simple_expr_node
            
    def __mathrel(self):
        """<mathrel> ::= PLUS | MINUS | DIVIDE | MULTIPLY | MODULO"""
        if(self.current_token.tokentype == token.PLUS):
            mathrel = self.current_token
            self.__advance()
            return mathrel
        elif(self.current_token.tokentype == token.MINUS):
            mathrel = self.current_token
            self.__advance()
            return mathrel
        elif(self.current_token.tokentype == token.DIVIDE):
            mathrel = self.current_token
            self.__advance()
            return mathrel
        elif(self.current_token.tokentype == token.MULTIPLY):
            mathrel = self.current_token
            self.__advance()
            return mathrel
        elif(self.current_token.tokentype == token.MODULO):
            mathrel = self.current_token
            self.__advance()
            return mathrel
        else:
            self.__error('expecting a math expression')
            
    def __rvalue(self):
        """<rvalue> ::= STRING | INT | BOOL | FLOAT | NIL | NEW ID | <idrval>"""
        if(self.current_token.tokentype == token.STRINGVAL):
            simple_r_value_node = ast.SimpleRValue()
            simple_r_value_node.val = self.current_token
            self.__advance()
            return simple_r_value_node
        elif(self.current_token.tokentype == token.INTVAL):
            simple_r_value_node = ast.SimpleRValue()
            simple_r_value_node.val = self.current_token
            self.__advance()
            return simple_r_value_node
        elif(self.current_token.tokentype == token.BOOLVAL):
            simple_r_value_node = ast.SimpleRValue()
            simple_r_value_node.val = self.current_token
            self.__advance()
            return simple_r_value_node
        elif(self.current_token.tokentype == token.FLOATVAL):
            simple_r_value_node = ast.SimpleRValue()
            simple_r_value_node.val = self.current_token
            self.__advance()
            return simple_r_value_node
        elif(self.current_token.tokentype == token.NIL):
            simple_r_value_node = ast.SimpleRValue()
            simple_r_value_node.val = self.current_token
            self.__advance()
            return simple_r_value_node
        elif(self.current_token.tokentype == token.NEW):
            new_r_value_node = ast.NewRValue()
            self.__advance()
            new_r_value_node.struct_type = self.current_token
            self.__eat(token.ID, 'expecting "ID"')
            return new_r_value_node
        else:
            return self.__idrval()
            
    def __idrval(self):
        """<idrval> ::= ID ( DOT ID )* | ID LPAREN <exprlist> RPAREN"""
        first = self.current_token
        self.__eat(token.ID, 'expecting "ID"')
        if(self.current_token.tokentype == token.LPAREN):
            call_r_value_node = ast.CallRValue()
            call_r_value_node.fun = first
            self.__advance()
            call_r_value_node.args = self.__exprlist()
            self.__eat(token.RPAREN, 'expecting ")"')
            return call_r_value_node
        else:
            id_r_value_node = ast.IDRValue()
            id_r_value_node.path.append(first)
            while(self.current_token.tokentype == token.DOT):
                self.__advance()
                id_r_value_node.path.append(self.current_token)
                self.__eat(token.ID, 'expecting "ID"')
            return id_r_value_node
                
    def __exprlist(self):
        """<exprlist> ::= <expr> ( COMMA <expr> )* | e"""
        expr = []
        exprhelp = [token.STRINGVAL, token.INTVAL, token.BOOLVAL, token.FLOATVAL, token.NIL, token.NEW, token.ID, token.LPAREN]
        if(self.current_token.tokentype in exprhelp):
            expr.append(self.__expr())
            while(self.current_token.tokentype == token.COMMA):
                self.__advance()
                expr.append(self.__expr())
        return expr
                
    def __bexpr(self):
        """<bexpr> ::= <expr> <bexprt> | NOT <bexpr> <bexprt> | LPAREN <bexpr> RPAREN <bconnct>"""
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
        """<bexprt> ::= <boolrel> <expr> <bconnct> | <bconnct>"""
        ctt = self.current_token.tokentype
        if ctt == token.EQUAL or ctt == token.LESS_THAN or ctt == token.GREATER_THAN or ctt == token.LESS_THAN_EQUAL or ctt == token.GREATER_THAN_EQUAL or ctt == token.NOT_EQUAL:
            bexpr.bool_rel = self.__boolrel()
            bexpr.second_expr = self.__expr()
            self.__bconnct(bexpr)
        else:
            self.__bconnct(bexpr)
            
    def __bconnct(self, bool_expr_node):
        """<bconnct> ::= AND <bexpr> | OR <bexpr> | e"""
        if(self.current_token.tokentype == token.AND):
            bool_expr_node.bool_connector = self.current_token
            self.__advance()
            bool_expr_node.rest = self.__bexpr()
        elif(self.current_token.tokentype == token.OR):
            bool_expr_node.bool_connector = self.current_token
            self.__advance()
            bool_expr_node.rest = self.__bexpr()
        return bool_expr_node
            
    def __boolrel(self):
        """<boolrel> ::= EQUAL | LESS_THAN | GREATER_THAN | LESS_THAN_EQUAL |GREATER_THAN_EQUAL | NOT_EQUAL"""
        if(self.current_token.tokentype == token.EQUAL):
            rel = self.current_token
            self.__advance()
            return rel
        elif(self.current_token.tokentype == token.LESS_THAN):
            rel = self.current_token
            self.__advance()
            return rel
        elif(self.current_token.tokentype == token.GREATER_THAN):
            rel = self.current_token
            self.__advance()
            return rel
        elif(self.current_token.tokentype == token.LESS_THAN_EQUAL):
            rel = self.current_token
            self.__advance()
            return rel
        elif(self.current_token.tokentype == token.GREATER_THAN_EQUAL):
            rel = self.current_token
            self.__advance()
            return rel
        elif(self.current_token.tokentype == token.NOT_EQUAL):
            rel = self.current_token
            self.__advance()
            return rel
        else:
            self.__error('expecting boolean expression')
                  
