import math
# Token types
#
# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
REAL, INTEGER, PLUS, MINUS, MUL, DIV, EOF, POPEN, PCLOSE, EQ, LOG_EQ, LOG_LEQ, LOG_LT, LOG_GT, LOG_GEQ, VAR, SQRT = (
    'REAL', 'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', 'EOF', 'POPEN', 'PCLOSE', 'EQ', 'LOG_EQ', 'LOG_LEQ', 'LOG_LT', 'LOG_GT', 'LOG_GEQ', 'VAR', 'SQRT'
)

MATH_KEYWORDS = ['SQRT']

variables = {}


class Token(object):
    def __init__(self, type, value):
        # token type: INTEGER, PLUS, MINUS, MUL, DIV, POPEN, PCLOSE or EOF
        self.type = type
        # token value: non-negative integer value, '+', '-', '*', '/', or None
        self.value = value

    def __str__(self):
        """String representation of the class instance.
        Examples:
            Token(INTEGER, 3)
            Token(PLUS, '+')
            Token(MUL, '*')
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()



class Lexer(object):
    def __init__(self, text):
        # client string input, e.g. "3 * 5", "12 / 3 * 4", etc
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        self.current_char = self.text[self.pos]


    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        """Return a (multidigit) integer consumed from the input."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            return (REAL, round(float(result), 3))
        else:
            return (INTEGER, int(result))

    def identifier(self):
        result = ''
        while self.current_char is not None and self.current_char.isalpha():
            result += self.current_char
            self.advance()
        return result


    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)
        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:

            if self.current_char.isalpha():
                id = self.identifier()
                if id == 'SQRT':
                    return Token(SQRT, id)
                return Token(VAR, id)

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit() or self.current_char == '.':
                tkn = self.number()
                return Token(tkn[0], tkn[1])

            if self.current_char == '(':
                self.advance()
                return Token(POPEN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(PCLOSE, ')')

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(DIV, '/')

            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(LOG_EQ, '==')
                return Token(EQ, '=')

            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(LOG_LEQ, '<=')
                return Token(LOG_LT, '<')

            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(LOG_GEQ, '>=')
                return Token(LOG_GT, '>')

            self.error()

        return Token(EOF, None)


class Interpreter(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def var_error(self, var):
        raise Exception('No such variable: ' + var)

    def eat_var(self, var):
        if var not in variables:
            self.var_error(var)

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    # def variable(self):
    #     self.factor()
    #
    #     token = self.current_token
    #     if token.type == VAR:
    #         self.eat(VAR)
    #         return self.variables[token.value]


    def factor(self):
        """factor : INTEGER | REAL"""
        token = self.current_token
        if token.type == SQRT:
            self.eat(SQRT)
            self.eat(POPEN)
            result = math.sqrt(self.expr())
            self.eat(PCLOSE)
            return round(result, 3)

        if token.type == POPEN:
            self.eat(POPEN)
            result = self.expr()
            self.eat(PCLOSE)
            return result
        elif token.type == INTEGER:
            self.eat(INTEGER)
            return token.value
        elif token.type == REAL:
            self.eat(REAL)
            return token.value
        elif token.type == VAR:
            self.eat(VAR)
            self.eat_var(token.value)
            return variables[token.value]


    def unary(self):
        token = self.current_token
        minus_eaten = 1
        if token.type == MINUS:
            self.eat(MINUS)
            minus_eaten = -1
        if token.type == PLUS:
            self.eat(PLUS)
        return self.factor() * minus_eaten


    def term(self):
        """term : factor ((MUL | DIV) factor)*"""
        result = self.unary()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
                result = result * self.unary()
            elif token.type == DIV:
                self.eat(DIV)
                result = result / self.unary()

        return result

    def logical(self):
        '''logical : term ((LOG_LEQ | LOG_GEQ | LOG_EQ | LOG_GT | LOG_LT) term)* '''

        result = self.term()

        while self.current_token.type in (LOG_GEQ, LOG_LEQ, LOG_EQ, LOG_GT, LOG_LT):
            token = self.current_token
            if token.type == LOG_EQ:
                self.eat(LOG_EQ)
                result = result == self.term()
            elif token.type == LOG_LT:
                self.eat(LOG_LT)
                result = result < self.term()
            elif token.type == LOG_GT:
                self.eat(LOG_GT)
                result = result > self.term()
            elif token.type == LOG_LEQ:
                self.eat(LOG_LEQ)
                result = result <= self.term()
            elif token.type == LOG_GEQ:
                self.eat(LOG_GEQ)
                result = result >= self.term()

        return result


    def expr(self):
        """Arithmetic expression parser / interpreter.
        >  14 + 2 * 3 - 6 / 2`
        17
        expr   : logical ((PLUS | MINUS) logical)*
        logical: term ((LOG_LEQ | LOG_EQ | LOG_GEQ | LOG_GT | LOG_LT) term)*
        term   : unary ((MUL | DIV) unary)*
        unary  : MINUS? INTEGER
        factor : (POPENexprPCLOSE) | INTEGER | REAL | VAR
        """
        result = self.logical()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
                result = result + self.logical()
            elif token.type == MINUS:
                self.eat(MINUS)
                result = result - self.logical()

        return result


    def statement(self):
        text = self.lexer.text
        flag = False
        for i in range(len(text) - 1):
            if text[i] == '=' and text[i+1] != '=':
                flag = True

        if not flag:
            return self.expr()

        else:
            token = self.current_token
            self.eat(VAR)
            self.eat(EQ)
            result = self.expr()
            variables[token.value] = result
            return None


def main():
    while True:
        try:
            text = input('rafmathz: ')
        except (EOFError, KeyboardInterrupt):
            break
        if text.lower() == 'exit':
            break
        if not text:
            continue
        lexer = Lexer(text)
        interpreter = Interpreter(lexer)
        result = interpreter.statement()
        if result is not None:
            print(result)


if __name__ == '__main__':
    main()