KEYWORDS = {"break", "else", "if", "int", "repeat", "return", "until", "void"}
OPERATORS = {"+", "-", "*", "**", "/", "&&", "||", "!", "==", "!=", "<", ">", "<=", ">=", "="}
SYMBOLS = {"(", ")", "{", "}", ";", ",", "[", "]", ":"}
special_chars = "!@#$^:'\",#.?~`"


def compile(code):
    tokens, errors = [], []
    line_number = 1
    inside_multiline_comment = False
    index = 0
    symbol_table = {kw: i + 1 for i, kw in enumerate(KEYWORDS)}
    unclosed_comment_start = 0
    comment_start_inex=0

    class Parser:
        def __init__(self, get_next_token_func):
            self.get_next_token = get_next_token_func
            self.current_token = self.get_next_token()
            self.parse_tree_lines = []
            self.syntax_errors = []
            self.depth = 0

        first_sets = {
            "S": {"$", "int", "void"},
            "Program": {"int", "void"},
            "Declaration-list": {"int", "void", "}", "{", "break", ";", "if", "repeat", "ID", "(", "NUM", "$"},
            "Declaration": {"int", "void"},
            "Declaration-initial": {"int", "void"},
            "Declaration-prime": {"(", ";", "["},
            "Var-declaration-prime": {";", "["},
            "Fun-declaration-prime": {"("},
            "Type-specifier": {"int", "void"},
            "Params": {"int", "void"},
            "Param-list": {",", "EPSILON"},
            "Param": {"int", "void"},
            "Param-prime": {"[", "EPSILON"},
            "Compound-stmt": {"{"},
            "Statement-list": {"{", "break", ";", "if", "repeat", "ID", "(", "NUM", "EPSILON"},
            "Statement": {"{", "break", ";", "if", "repeat", "ID", "(", "NUM"},
            "Expression-stmt": {"break", ";", "ID", "(", "NUM"},
            "Selection-stmt": {"if"},
            "Iteration-stmt": {"repeat"},
            "Return-stmt": {"return"},
            "Return-stmt-prime": {";", "ID", "(", "NUM"},
            "Expression": {"ID", "(", "NUM"},
            "B": {"=", "[", "<", "==", "(", "*", "+", "-", "EPSILON"},
            "H": {"=", "*", "+", "-", "<", "==", "EPSILON"},
            "Simple-expression-zegond": {"(", "NUM"},
            "Simple-expression-prime": {"<", "==", "(", "*", "+", "-", "EPSILON"},
            "C": {"<", "==", "EPSILON"},
            "Relop": {"<", "=="},
            "Additive-expression": {"(", "ID", "NUM"},
            "Additive-expression-prime": {"(", "*", "+", "-", "EPSILON"},
            "Additive-expression-zegond": {"(", "NUM"},
            "D": {"+", "-", "EPSILON"},
            "Addop": {"+", "-"},
            "Term": {"(", "ID", "NUM"},
            "Term-prime": {"(", "*", "EPSILON"},
            "Term-zegond": {"(", "NUM"},
            "G": {"*", "EPSILON"},
            "Factor": {"(", "ID", "NUM"},
            "Var-call-prime": {"(", "[", "EPSILON"},
            "Var-prime": {"[", "EPSILON"},
            "Factor-prime": {"(", "EPSILON"},
            "Factor-zegond": {"(", "NUM"},
            "Args": {"ID", "(", "NUM", "EPSILON"},
            "Arg-list": {"ID", "(", "NUM"},
            "Arg-list-prime": {",", "EPSILON"},
        }
        follow_sets = {
            "S": {"$"},
            "Program": {"$"},
            "Declaration-list": {"}", "{", "break", ";", "if", "repeat", "ID", "(", "NUM","return", "$"},
            "Declaration": {"int", "void", "}", "{", "break", ";", "if", "repeat", "ID", "(", "NUM","return", "$"},
            "Declaration-initial": {"(", ";", "[", ")", ","},
            "Declaration-prime": {"int", "void", "}", "{", "break", ";", "if", "repeat", "ID","return", "(", "NUM", "$"},
            "Var-declaration-prime": {"int", "void", "}", "{", "break", ";", "if", "repeat", "ID", "(","return", "NUM", "$"},
            "Fun-declaration-prime": {"int", "void", "}", "{", "break", ";", "if", "repeat", "ID", "(","return", "NUM", "$"},
            "Type-specifier": {"ID"},
            "Params": {")"},
            "Param-list": {")"},
            "Param": {")", ","},
            "Param-prime": {")", ","},
            "Compound-stmt": {"int", "void", "}", "{", "break", ";", "if", "repeat", "ID", "(", "NUM", "$", "else",
                              "until"},
            "Statement-list": {"}"},
            "Statement": {"}", "{", "break", ";", "if", "repeat", "ID", "(", "NUM", "else", "until","return"},
            "Expression-stmt": {"}", "{", "break", ";", "if", "repeat", "ID", "(", "NUM", "else", "until","return"},
            "Selection-stmt": {"}", "{", "break", ";", "if", "repeat", "ID", "(", "NUM", "else", "until","return"},
            "Iteration-stmt": {"}", "{", "break", ";", "if", "repeat", "ID", "(", "NUM", "else", "until","return"},
            "Return-stmt": {"}", "{", "break", ";", "if", "repeat", "ID", "(", "NUM", "else", "until","return"},
            "Return-stmt-prime": {"}", "{", "break", ";", "if", "repeat", "ID", "(", "NUM", "else", "until","return"},
            "Expression": {";", ")", "]", ","},
            "B": {";", ")", "]", ","},
            "H": {";", ")", "]", ","},
            "Simple-expression-zegond": {";", ")", "]", ","},
            "Simple-expression-prime": {";", ")", "]", ","},
            "C": {";", ")", "]", ","},
            "Relop": {"(", "ID", "NUM"},
            "Additive-expression": {";", ")", "]", ","},
            "Additive-expression-prime": {";", ")", "<", "==", "]", ","},
            "Additive-expression-zegond": {";", ")", "<", "==", "]", ","},
            "D": {";", ")", "<", "==", "]", ","},
            "Addop": {"(", "ID", "NUM"},
            "Term": {";", ")", "+", "-", "<", "==", "]", ","},
            "Term-prime": {";", ")", "<", "==", "+", "-", "]", ","},
            "Term-zegond": {";", ")", "<", "==", "+", "-", "]", ","},
            "G": {";", ")", "<", "==", "+", "-", "|", "]", ","},
            "Factor": {";", ")", "+", "-", "<", "==", "*", "|", "]", ","},
            "Var-call-prime": {";", ")", "+", "-", "<", "==", "*", "|", "]", ",",},
            "Var-prime": {";", ")", "+", "-", "<", "==", "*", "|", "]", ","},
            "Factor-prime": {";", ")", "<", "==", "+", "-", "*", "]", ","},
            "Factor-zegond": {";", ")", "<", "==", "+", "-", "*", "]", ","},
            "Args": {")"},
            "Arg-list": {")"},
            "Arg-list-prime": {")"},
        }

        def parse(self):
            self.program()
            self.write_outputs()
        def advance(self):
            self.current_token = self.get_next_token()
        def add_parse_tree_node(self, node_text):
            self.parse_tree_lines.append('\t' * self.depth + node_text)
        def error(self, unexpected=True, expected_symbol=None, sync_nonterminal=None):
            if unexpected and self.current_token[1] != '$':


                if sync_nonterminal and sync_nonterminal in self.follow_sets:
                    while ((self.current_token[1] not in self.follow_sets[sync_nonterminal] and self.current_token[0] not in self.follow_sets[sync_nonterminal]) and
                           self.current_token[1] != '$'):
                           self.syntax_errors.append(
                            f"#{self.current_token[2]} : syntax error, unexpected {self.current_token[1]} ")
                           self.advance()
                else:
                    self.syntax_errors.append(
                       f"#{self.current_token[2]} : syntax error, unexpected {self.current_token[1]}")

                    self.advance()
            elif unexpected and self.current_token[1] == '$':
                self.syntax_errors.append(f"#{self.current_token[2]} : syntax error, Unexpected EOF")

            elif expected_symbol and self.current_token[1] != '$':
                self.syntax_errors.append(f"#{self.current_token[2]} : syntax error, missing {expected_symbol}")
        def match(self, expected_type, expected_value=None):
            if (self.current_token[0] == expected_type and
                    (expected_value is None or self.current_token[1] == expected_value)):
                self.add_parse_tree_node(f"({self.current_token[0]}, {self.current_token[1]})")
                self.advance()
                return True
            else:
                self.error(expected_symbol=expected_value,unexpected=False)
                return False
        def write_outputs(self):
            def generate_tree_structure(lines):
                result = []
                stack = []
                for i, line in enumerate(lines):
                    stripped = line.lstrip('\t')
                    depth = len(line) - len(stripped)

                    prefix = ""
                    for d in range(depth):
                        if d + 1 < len(stack) and stack[d]:
                            prefix += "│   "
                        else:
                            prefix += "    "

                    is_last = True
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        next_depth = len(next_line) - len(next_line.lstrip('\t'))
                        if next_depth == depth:
                            is_last = False
                        elif next_depth < depth:
                            for j in range(next_depth, len(stack)):
                                if j < len(stack):
                                    stack[j] = False

                    if len(stack) <= depth:
                        stack.extend([False] * (depth - len(stack) + 1))
                    stack[depth] = not is_last

                    connector = "└── " if is_last else "├── "
                    result.append(prefix + connector + stripped)

                return result

            # تبدیل خطوط به ساختار درختی گرافیکی
            tree_lines = generate_tree_structure(self.parse_tree_lines)

            # نوشتن در فایل parse_tree.txt
            with open('parse_tree.txt', 'w', encoding='utf-8') as f:
                for line in tree_lines:
                    f.write(line + '\n')

            # نوشتن در فایل syntax_errors.txt
            with open('syntax_errors.txt', 'w', encoding='utf-8') as f:
                if not self.syntax_errors:
                    f.write("There is no syntax error.\n")
                else:
                    for error in self.syntax_errors:
                        f.write(error + '\n')
        # === Now Non-Terminal rules based on your grammar ===
        # Start with Program
        def program(self):
            if self.current_token[1] in self.first_sets["Program"] or self.current_token[0] in self.first_sets["Program"]:
                 self.add_parse_tree_node('Program')
                 self.depth += 1
                 self.declaration_list()
                 self.depth -= 1
            else:
                self.error(sync_nonterminal="Program")

        def declaration_list(self):
            self.add_parse_tree_node('Declaration-list')
            self.depth += 1
            if self.current_token[1] in ['int', 'void']:
                self.declaration()
                self.declaration_list()
            elif self.current_token[1] in self.follow_sets["Declaration-list"] or self.current_token[0] in self.follow_sets["Declaration-list"]:
                self.add_parse_tree_node('epsilon')
            else:
                self.error(sync_nonterminal="Declaration-list")


            self.depth -= 1
        def declaration(self):
            self.add_parse_tree_node('Declaration')
            if self.current_token[1]in['int', 'void']:

                self.depth += 1
                self.declaration_initial()
                self.declaration_prime()
                self.depth -= 1
            else:
                self.error(sync_nonterminal="Declaration")
        def declaration_initial(self):
            self.add_parse_tree_node('Declaration-initial')
            if self.current_token[1] in ['int', 'void']:

                self.depth += 1
                self.type_specifier()
                self.match('ID')
            else:
                self.error(sync_nonterminal="Declaration-initial")

            self.depth -= 1
        def declaration_prime(self):
            self.add_parse_tree_node('Declaration-prime')
            self.depth += 1
            if self.current_token[1] in ['(', ';', '[']:
                if self.current_token[1] == ';' or self.current_token[1] == '[':
                    self.var_declaration_prime()
                elif self.current_token[1] == '(':
                    self.fun_declaration_prime()
            else:

                self.error(sync_nonterminal="Declaration-prime")

            self.depth -= 1
        def var_declaration_prime(self):
            self.add_parse_tree_node('Var-declaration-prime')
            self.depth += 1
            if self.current_token[1] == ';':
                self.match('SYMBOL', ';')
            elif self.current_token[1] == '[':
                self.match('SYMBOL', '[')
                self.match('NUM')
                self.match('SYMBOL', ']')
                self.match('SYMBOL', ';')
            else:
                self.error(sync_nonterminal="Var-declaration-prime")

            self.depth -= 1
        def fun_declaration_prime(self):
            if self.current_token[1] == '(':
                self.add_parse_tree_node('Fun-declaration-prime')
                self.depth += 1
                self.match('SYMBOL', '(')
                self.params()
                self.match('SYMBOL', ')')
                self.compound_stmt()
                self.depth -= 1
            else:
                self.error(sync_nonterminal="Fun-declaration-prime")

        def type_specifier(self):
            self.add_parse_tree_node('Type-specifier')
            self.depth += 1
            if self.current_token[1] == 'int':
                self.match('KEYWORD', 'int')
            elif self.current_token[1] == 'void':
                self.match('KEYWORD', 'void')
            else:
                self.error(sync_nonterminal="Type-specifier")

            self.depth -= 1
        def params(self):
            self.add_parse_tree_node('Params')
            self.depth += 1
            if self.current_token[1] in ['int', 'void']:
                if self.current_token[1] == 'void':
                    self.match('KEYWORD', 'void')
                else:
                    self.match('KEYWORD', 'int')
                    self.match('ID')
                    self.param_prime()
                    self.param_list()
            else:
                self.error(sync_nonterminal="Params")

            self.depth -= 1
        def param_list(self):
            self.add_parse_tree_node('Param-list')
            self.depth += 1
            if self.current_token[1] == ',':
                self.match('SYMBOL', ',')
                self.param()
                self.param_list()
            elif self.current_token[1] in self.follow_sets["Param-list"] or self.current_token[0] in self.follow_sets["Param-list"]:
                self.add_parse_tree_node('epsilon')
            else:
                self.error(sync_nonterminal="Param-list")
            self.depth -= 1
        def param(self):
            if self.current_token[1] in ['int', 'void']:
                self.add_parse_tree_node('Param')
                self.depth += 1
                self.declaration_initial()
                self.param_prime()
                self.depth -= 1
            else:
                self.error(sync_nonterminal="Param")
        def param_prime(self):
            self.add_parse_tree_node('Param-prime')
            self.depth += 1
            if self.current_token[1] == '[':
                self.match('SYMBOL', '[')
                self.match('SYMBOL', ']')
            elif self.current_token[1] in [')',',']or self.current_token[1] in self.follow_sets["Param-prime"] or self.current_token[0] in self.follow_sets["Param-prime"]:
                self.add_parse_tree_node('epsilon')
            else:
                self.error(sync_nonterminal="Param-prime")
            self.depth -= 1
        def compound_stmt(self):
            if self.current_token[1] in ['{']:
                self.add_parse_tree_node('Compound-stmt')
                self.depth += 1
                self.match('SYMBOL', '{')
                self.declaration_list()
                self.statement_list()
                self.match('SYMBOL', '}')
                self.depth -= 1
            else:
                self.error(sync_nonterminal="Compound-stmt")
        def statement_list(self):

            self.add_parse_tree_node('Statement-list')
            self.depth += 1
            if (self.current_token[0] in ['ID', 'NUM']) or \
                    (self.current_token[1] in ['if', 'repeat', 'return', 'break', ';', '(', '{']):
                self.statement()
                self.statement_list()
            elif self.current_token[1] == '}' or self.current_token[1] in self.follow_sets["Statement-list"] or self.current_token[0] in self.follow_sets["Statement-list"]:
                self.add_parse_tree_node('epsilon')
            else:
                self.error(sync_nonterminal="Statement-list")


            self.depth -= 1
        def statement(self):
            self.add_parse_tree_node('Statement')
            self.depth += 1

            if self.current_token[1] == ';' or \
                    self.current_token[0] in ['ID','NUM'] or \
                    self.current_token[1] in ['(', 'break']:
                self.expression_stmt()
            elif self.current_token[1] in ['{']:
                self.compound_stmt()
            elif self.current_token[1] == 'if':
                self.selection_stmt()
            elif self.current_token[1] == 'repeat':
                self.iteration_stmt()
            elif self.current_token[1] == 'return':
                self.return_stmt()
            else:
                self.error(sync_nonterminal="Statement")

            self.depth -= 1
        def expression_stmt(self):
            self.add_parse_tree_node('Expression-stmt')
            self.depth += 1
            if self.current_token[1] == ';':
                self.match('SYMBOL', ';')
            elif self.current_token[1] == 'break':
                self.match('KEYWORD', 'Break')
                self.match('SYMBOL', ';')
            elif self.current_token[1] in ['('] or self.current_token[0]in['ID','NUM']:
                self.expression()
                self.match('SYMBOL', ';')
            else:
                self.error(sync_nonterminal="Expression-stmt")
            self.depth -= 1
        def selection_stmt(self):
            if self.current_token[1] == 'if':
                self.add_parse_tree_node('Selection-stmt')
                self.depth += 1
                self.match('KEYWORD', 'if')
                self.match('SYMBOL', '(')
                self.expression()
                self.match('SYMBOL', ')')
                self.statement()
                self.match('KEYWORD', 'else')
                self.statement()
                self.depth -= 1
            else:
                self.error(sync_nonterminal="Selection-stmt")
        def iteration_stmt(self):
            if self.current_token[1] == 'repeat':
                self.add_parse_tree_node('Iteration-stmt')
                self.depth += 1
                self.match('KEYWORD', 'repeat')
                self.statement()
                self.match('KEYWORD', 'until')
                self.match('SYMBOL', '(')
                self.expression()
                self.match('SYMBOL', ')')
                self.depth -= 1
            else:
                self.error(sync_nonterminal="Iteration-stmt")
        def return_stmt(self):
            if self.current_token[1] == 'return':

                self.add_parse_tree_node('Return-stmt')
                self.depth += 1
                self.match('KEYWORD', 'return')
                self.return_stmt_prime()
                self.depth -= 1
            else:
                self.error(sync_nonterminal="Return-stmt")
        def return_stmt_prime(self):
            self.add_parse_tree_node('Return-stmt-prime')
            self.depth += 1
            if self.current_token[1] == ';':
                self.match('SYMBOL', ';')
            elif self.current_token[1] in ['(']or self.current_token[0] in ['ID','NUM']:
                self.expression()
                self.match('SYMBOL', ';')
            else:
                self.error(sync_nonterminal="Return-stmt-prime")
            self.depth -= 1
        def expression(self):
            self.add_parse_tree_node('Expression')
            self.depth += 1

            if self.current_token[0] == 'ID':
                self.match('ID')
                self.b()


            elif self.current_token[0]=='NUM'or self.current_token[1] in ['(']:
                self.simple_expression_zegond()
            else:
                self.error(sync_nonterminal="Expression")
            self.depth -= 1
        def b(self):
            self.add_parse_tree_node('B')
            self.depth += 1
            if self.current_token[1] == '=':
                self.match('OPERATOR', '=')
                self.expression()
            elif self.current_token[1] == '[':
                self.match('SYMBOL', '[')
                self.expression()
                self.match('SYMBOL', ']')
                self.h()
            elif self.current_token[1] in ['(','+','-','==','<',')'] or self.current_token[0] in ['ID' ,'NUM'] or self.current_token[0] in self.follow_sets["B"] or self.current_token[1] in self.follow_sets["B"]:
                self.simple_expression_prime()
            else:
                self.error(sync_nonterminal="B")
            self.depth -= 1
        def h(self):
            self.add_parse_tree_node('H')
            self.depth += 1
            if self.current_token[1] == '=':
                self.match('OPERATOR', '=')
                self.expression()

            elif self.current_token[1] in [ "*", "+", "-", "<", "==", "EPSILON"]or self.current_token[0] in [ "*", "+", "-", "<", "==", "EPSILON"] or self.current_token[0] in self.follow_sets["H"] or self.current_token[1] in self.follow_sets["H"]:
                self.g()
                self.d()
                self.c()

            else:
                self.error(sync_nonterminal="H")
            self.depth -= 1
        def simple_expression_zegond(self):
            if self.current_token[1] == '('or self.current_token[0] in ['NUM']:
                self.add_parse_tree_node('Simple-expression-zegond')
                self.depth += 1
                self.additive_expression_zegond()
                self.c()
            else:
                self.error(sync_nonterminal="Simple-expression-zegond")
            self.depth -= 1
        def simple_expression_prime(self):
            if self.current_token[1] in self.first_sets["Simple-expression-prime"] or self.current_token[0] in self.first_sets["Simple-expression-prime"] or self.current_token[1] in self.follow_sets["Simple-expression-prime"] or self.current_token[0] in self.follow_sets["Simple-expression-prime"]:

                self.add_parse_tree_node('Simple-expression-prime')
                self.depth += 1

                self.additive_expression_prime()
                self.c()
            else:
                self.error(sync_nonterminal="Simple-expression-prime")


            self.depth -= 1
        def c(self):
            self.add_parse_tree_node('C')
            self.depth += 1
            if self.current_token[1] in ['<', '==', '!=', '<=', '>=', '>']:
                self.relop()
                self.additive_expression()

            elif self.current_token[1] in self.follow_sets["C"] or self.current_token[0] in \
                    self.follow_sets["C"]:

                self.add_parse_tree_node('epsilon')
            else:
                self.error(sync_nonterminal='C')
            self.depth -= 1
        def relop(self):
            self.add_parse_tree_node('Relop')
            self.depth += 1
            if self.current_token[1] in ['<', '==']:
                self.match('OPERATOR', self.current_token[1])
            else:
                self.error(sync_nonterminal="Relop")

            self.depth -= 1
        def additive_expression(self):
            if self.current_token[1] in self.first_sets["Additive-expression"] or self.current_token[0] in self.first_sets["Additive-expression"]:

                self.add_parse_tree_node('Additive-expression')
                self.depth += 1
                self.term()
                self.d()
                self.depth -= 1
            else:
                self.error(sync_nonterminal="Additive-expression")
        def additive_expression_prime(self):
            if self.current_token[1] in self.first_sets["Additive-expression-prime"]or self.current_token[0] in self.follow_sets["Additive-expression-prime"] or self.current_token[0] in self.first_sets["Additive-expression-prime"]or self.current_token[1] in self.follow_sets["Additive-expression-prime"]:
                self.add_parse_tree_node('Additive-expression-prime')
                self.depth += 1
                self.term_prime()
                self.d()
                self.depth -= 1
            else:
                self.error(sync_nonterminal="Additive-expression-prime")
        def additive_expression_zegond(self):
            if self.current_token[1] in self.first_sets["Additive-expression-zegond"] or self.current_token[0] in self.first_sets["Additive-expression-zegond"]:
                self.add_parse_tree_node('Additive-expression-zegond')
                self.depth += 1
                self.term_zegond()
                self.d()
                self.depth -= 1
            else:
                self.error(sync_nonterminal="Additive-expression-zegond")
        def d(self):
            self.add_parse_tree_node('D')
            self.depth += 1
            if self.current_token[1] in ['+','-']:
                self.addop()
                self.term()
                self.d()
            elif self.current_token[1] in self.follow_sets["D"] or self.current_token[0] in self.follow_sets["D"]:
                    self.add_parse_tree_node('epsilon')
            self.depth -= 1
        def addop(self):
            self.add_parse_tree_node('Addop')
            self.depth += 1
            if self.current_token[1] in ['+', '-']:
                self.match('OPERATOR', self.current_token[1])
            else:
                self.error(sync_nonterminal="Addop")

            self.depth -= 1
        def term(self):
            if self.current_token[1] in self.first_sets["Term"] or self.current_token[0] in self.first_sets["Term"]:
                self.add_parse_tree_node("Term")
                self.depth += 1
                self.Factor()
                self.g()
                self.depth -= 1
            else:
                self.error(sync_nonterminal="Term")
        def term_prime(self):
            if self.current_token[1] in self.follow_sets["Term-prime"] or self.current_token[0] in self.follow_sets["Term-prime"] or self.current_token[1] in self.first_sets["Term-prime"] or self.current_token[0] in self.first_sets["Term-prime"]:
                self.add_parse_tree_node('Term-prime')
                self.depth += 1
                self.factor_prime()
                self.g()
                self.depth -= 1
            else:
                self.error(sync_nonterminal="Term-prime")
        def term_zegond(self):
            if self.current_token[1] in self.first_sets["Term-zegond"] or self.current_token[0] in self.first_sets["Term-zegond"]:
                self.add_parse_tree_node('Term-zegond')
                self.depth += 1
                self.factor_zegond()
                self.g()
            else:
                self.error(sync_nonterminal="Term-zegond")
        def g(self):
            self.add_parse_tree_node('G')
            self.depth += 1
            if self.current_token[1] in ['*']:
                self.match('OPERATOR','*')
                self.Factor()
                self.g()
            elif self.current_token[1] in self.follow_sets["G"] or self.current_token[0] in self.follow_sets["G"]:
                self.add_parse_tree_node('epsilon')
            else:
                self.error(sync_nonterminal="G")
                self.depth -= 1
        def Factor(self):
            self.add_parse_tree_node('Factor')
            if self.current_token[1] == '(':
                self.match('SYMBOL', '(')
                self.expression()
                self.match('SYMBOL', ')')
            elif self.current_token[0] == 'ID':
                self.match('ID')
                self.var_call_prime()
            elif self.current_token[0] == 'NUM':
                self.match('NUM')
            else:
                self.error(sync_nonterminal="Factor")

        def var_call_prime(self):
            self.add_parse_tree_node('Var_call_prime')
            if self.current_token[1] == '(':
                self.match('SYMBOL', '(')
                self.args()
                self.match('SYMBOL', ')')
            elif self.current_token[1] in self.follow_sets["Var-call-prime"] or self.current_token[0] in self.follow_sets["Var-call-prime"] or self.current_token[1] in ['[']:
                self.var_prime()
            else:
                self.error(sync_nonterminal="Var-call-prime")
        def var_prime(self):
            self.add_parse_tree_node('var-prime')
            self.depth += 1
            if self.current_token[1] == '[':
                self.match('SYMBOL', '[')
                self.expression()
                self.match('SYMBOL', ']')
            elif self.current_token[1] in self.follow_sets["Var-prime"] or self.current_token[0] in self.follow_sets["Var-prime"]:
                self.add_parse_tree_node('epsilon')
            else:
                self.error(sync_nonterminal='Var-prime')
            self.depth += 1
        def factor_prime(self):
            self.add_parse_tree_node('Factor-prime')
            self.depth += 1
            if self.current_token[1] == '(':
                self.match('SYMBOL', '(')
                self.args()
                self.match('SYMBOL', ')')
            elif self.current_token[1] in self.follow_sets["Factor-prime"] or self.current_token[0] in self.follow_sets["Factor-prime"]:
                 self.add_parse_tree_node('epsilon')
            else:
                self.error(sync_nonterminal="Factor-prime")
            self.depth -= 1

        def factor_zegond(self):
            self.add_parse_tree_node('factor_zegond')
            self.depth += 1
            if self.current_token[1] == '(':
                self.match('SYMBOL', '(')
                self.expression()
                self.match('SYMBOL', ')')
            elif self.current_token[0] == 'NUM':
                self.match('NUM')
            else:
                self.error(sync_nonterminal="Factor-zegond")
            self.depth -= 1
        def args(self):
            self.add_parse_tree_node('Args')
            self.depth += 1
            if self.current_token[1] in ['(']or (self.current_token[0]in ['ID','NUM']):
                self.arg_list()
            elif self.current_token[1] in self.follow_sets["Args"] or self.current_token[0] in self.follow_sets["Args"]:
                self.add_parse_tree_node('epsilon')
            else:
                self.error( sync_nonterminal='Args')
            self.depth -= 1
        def arg_list(self):
            if self.current_token[1] in self.first_sets["Arg-list"] or self.current_token[0] in self.first_sets["Arg-list"]:
                self.add_parse_tree_node('Arg-list')
                self.depth += 1
                self.expression()
                self.arg_list_prime()
                self.depth -=1
            else:
                self.error(sync_nonterminal="Arg-list")
        def arg_list_prime(self):
            self.add_parse_tree_node('Arg-list-prime')
            self.depth += 1
            if self.current_token[1] == ',':
                self.match('SYMBOL', ',')
                self.expression()
                self.arg_list_prime()
            elif self.current_token[1] in self.follow_sets["Arg-list-prime"] or self.current_token[0] in self.follow_sets["Arg-list-prime"]:
                 self.add_parse_tree_node('epsilon')
            else:
                self.error(sync_nonterminal="Arg-list-prime")
            self.depth -= 1

    def get_next_token():
        nonlocal index, line_number, inside_multiline_comment, unclosed_comment_start,comment_start_inex,code


        token=None
        if index >= len(code):
            if inside_multiline_comment:
                snippet = code[comment_start_inex:comment_start_inex + 8] if comment_start_inex + 8 < len(code) else code[comment_start_inex:]
                errors.append(('/*', f'{snippet}..., Unclosed comment', unclosed_comment_start))
            return ('$','$',-1)

        char = code[index]

        # Handle multi-line comments
        if inside_multiline_comment:
            if index + 1 < len(code) and code[index:index + 2] == '*/':
                inside_multiline_comment = False
                index += 2
                return get_next_token()
            else:
                if char == '\n':
                    line_number += 1
                    index += 1
                    return get_next_token()

        # Skip whitespace
        elif char in ' \t\f':
            index += 1
            return get_next_token()

        # Handle newlines
        elif char == '\n':
            line_number += 1
            index += 1
            return get_next_token()

        # Handle comment start
        elif index + 1 < len(code) and code[index:index + 2] == '/*':
            inside_multiline_comment = True
            unclosed_comment_start = line_number
            comment_start_inex=index
            index += 2
            return get_next_token()

        # Handle unmatched comment closer
        elif index + 1 < len(code) and code[index:index + 2] == '*/':
            errors.append(('*/', 'Unmatched comment', line_number))
            index += 2
            return get_next_token()

        # Handle symbols
        elif char in SYMBOLS:
            token = ('SYMBOL', char, line_number)
            index += 1
            if token:
                tokens.append(token)
            return token

        # Handle operators
        elif char in OPERATORS:
            # Handle // as two invalid / operators
            if char == '/' and index + 1 < len(code) and code[index + 1] == '/':
                errors.append(('/', 'Invalid input', line_number))
                errors.append(('/', 'Invalid input', line_number))
                index += 2
                return get_next_token()
            # Handle operator followed by newline
            elif index + 1 < len(code) and code[index + 1] == '\n':
                errors.append((char, 'Invalid input', line_number))
                index += 1
                return get_next_token()
            # Handle operator followed by special character
            elif index + 1 < len(code) and code[index + 1] in special_chars:
                start = index
                index += 1
                # Skip all consecutive special chars
                while index < len(code) and code[index] in special_chars:
                    index += 1
                errors.append((code[start:index], 'Invalid input', line_number))
                return get_next_token()
            # Handle ** operator
            elif char == '*' and index + 1 < len(code) and code[index + 1] == '*':
                token=('OPERATOR', '**', line_number)
                index += 2
            # Handle && operator
            elif char == '&' and index + 1 < len(code) and code[index + 1] == '&':
                token=('OPERATOR', '&&', line_number)
                index += 2
            # Handle || operator
            elif char == '|' and index + 1 < len(code) and code[index + 1] == '|':
                token=('OPERATOR', '||', line_number)
                index += 2
            # Handle == operator
            elif char == '=' and index + 1 < len(code) and code[index + 1] == '=':
                token=('OPERATOR', '==', line_number)
                index += 2
            # Handle != operator
            elif char == '!' and index + 1 < len(code) and code[index + 1] == '=':
                token=('OPERATOR', '!=', line_number)
                index += 2
            # Handle <= operator
            elif char == '<' and index + 1 < len(code) and code[index + 1] == '=':
                token=('OPERATOR', '<=', line_number)
                index += 2
            # Handle >= operator
            elif char == '>' and index + 1 < len(code) and code[index + 1] == '=':
                token=('OPERATOR', ">=", line_number)
                index += 2
            # Single character operators
            else:
                token=('OPERATOR', char, line_number)
                index += 1
            if token:
                tokens.append(token)
            return token

        # Handle numbers
        elif char.isdigit() or (char == '-' and index + 1 < len(code) and code[index + 1].isdigit()):
            start = index
            if char == '-':
                index += 1
            while index < len(code) and code[index].isdigit():
                index += 1

            # Check for float
            if index < len(code) and code[index] == '.':
                index += 1
                while index < len(code) and code[index].isdigit():
                    index += 1
                token = ('FLOAT', code[start:index], line_number)
                if token:
                    tokens.append(token)
                return token

            # Check for invalid number (like 2a)
            if index < len(code) and code[index].isalpha():
                invalid_num = code[start:index + 1]
                errors.append((invalid_num, 'Invalid number', line_number))
                index += 1
                return get_next_token()
            token = ('NUM',code[start:index], line_number)
            if token:
                tokens.append(token)
            return token

        # Handle identifiers and keywords
        elif char.isalpha() or char == '_':
            start = index
            while index < len(code) and ((code[index].isalpha() or code[index] == '_' or code[index].isdigit()))and code[index]!=',':
                index += 1

            word = code[start:index]

            # Check for invalid input (like cd!)
            if index < len(code) and code[index] in special_chars and code[index] != ',':
                invalid_id = word + code[index]
                errors.append((invalid_id, 'Invalid input', line_number))
                index += 1
                return get_next_token()

            if word in KEYWORDS:
                token = ('KEYWORD', word, line_number)
                if token:
                    tokens.append(token)
                return token
            else:
                if word not in symbol_table:
                    symbol_table[word] = len(symbol_table) + 1
                token = ('ID', word, line_number)
                if token:
                    tokens.append(token)
                return token

        # Handle invalid characters
        elif char in special_chars:
            errors.append((char, 'Invalid input', line_number))

        else:
            errors.append((char, 'Invalid character', line_number))
        index += 1
        return get_next_token()
    parser = Parser(get_next_token)
    parser.parse()
    return tokens, errors, symbol_table


def read_input():
    with open("input.txt", "r", encoding="utf-8") as file:
        return file.read()


def write_output(tokens, errors, symbol_table):
    # Write tokens.txt
    with open("tokens.txt", "w", encoding="utf-8") as file:
        current_line = 1
        line_tokens = []

        # Group tokens by line number
        token_lines = {}
        for token in tokens:
            line = token[2]
            if line not in token_lines:
                token_lines[line] = []
            token_lines[line].append(f"({token[0]}, {token[1]})")

        # Find the maximum line number with tokens
        max_token_line = max(token_lines.keys()) if token_lines else 1

        # Write tokens line by line
        for line in range(1, max_token_line + 1):
            if line in token_lines:
                file.write(f"{line}. {' '.join(token_lines[line])}\n")
            else:
                file.write(f"{line}.\n")

    # Write lexical_errors.txt
    with open("lexical_errors.txt", "w", encoding="utf-8") as file:
        if not errors:
            file.write("No lexical errors found.\n")
        else:
            # Group errors by line number
            error_lines = {}
            for error in errors:
                line = error[2]
                if line not in error_lines:
                    error_lines[line] = []
                # Format each error message exactly as specified
                if error[1] == 'Unclosed comment':
                    error_lines[line].append(f"({error[0]}, {error[1]})")
                elif error[1] == 'Unmatched comment':
                    error_lines[line].append(f"({error[0]}, {error[1]})")
                elif error[1] == 'Invalid number':
                    error_lines[line].append(f"({error[0]}, {error[1]})")
                else:
                    error_lines[line].append(f"({error[0]}, Invalid input)")

            # Find the maximum line number with errors
            max_error_line = max(error_lines.keys()) if error_lines else 1

            # Write errors line by line
            for line in range(1, max_error_line + 1):
                if line in error_lines:
                    file.write(f"{line}. {' '.join(error_lines[line])}\n")
                else:
                    continue

    # Write symbol_table.txt
    with open("symbol_table.txt", "w", encoding="utf-8") as file:
        for idx, symbol in enumerate(symbol_table.keys(), start=1):
            file.write(f"{idx}. {symbol}\n")

def main():
    code = read_input()
    tokens, errors, symbol_table = compile(code)
    print("compile completed.")


if __name__ == "__main__":
    main()