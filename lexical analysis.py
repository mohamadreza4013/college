KEYWORDS = {"break", "else", "if", "int", "repeat", "return", "until", "void"}
OPERATORS = {"+", "-", "*", "**", "/", "&&", "||", "!", "==", "!=", "<", ">", "<=", ">=", "="}
SYMBOLS = {"(", ")", "{", "}", ";", ",", "[", "]", ":"}
special_chars = "!@#$^:'\",#.?~`"


def tokenize(code):
    tokens, errors = [], []
    line_number = 1
    inside_multiline_comment = False
    index = 0
    symbol_table = {kw: i + 1 for i, kw in enumerate(KEYWORDS)}
    unclosed_comment_start = 0
    comment_start_inex=0
    def get_next_token():
        nonlocal index, line_number, inside_multiline_comment, unclosed_comment_start,comment_start_inex

        if index >= len(code):
            if inside_multiline_comment:
                snippet = code[comment_start_inex:comment_start_inex + 8] if comment_start_inex + 8 < len(code) else code[comment_start_inex:]
                errors.append(('/*', f'{snippet}..., Unclosed comment', unclosed_comment_start))
            return None

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
        if char in ' \t\f':
            index += 1
            return get_next_token()

        # Handle newlines
        if char == '\n':
            line_number += 1
            index += 1
            return get_next_token()

        # Handle comment start
        if index + 1 < len(code) and code[index:index + 2] == '/*':
            inside_multiline_comment = True
            unclosed_comment_start = line_number
            comment_start_inex=index
            index += 2
            return get_next_token()

        # Handle unmatched comment closer
        if index + 1 < len(code) and code[index:index + 2] == '*/':
            errors.append(('*/', 'Unmatched comment', line_number))
            index += 2
            return get_next_token()

        # Handle symbols
        if char in SYMBOLS:
            token = ('SYMBOL', char, line_number)
            index += 1
            return token

        # Handle operators
        if char in OPERATORS:
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
            return token

        # Handle numbers
        if char.isdigit() or (char == '-' and index + 1 < len(code) and code[index + 1].isdigit()):
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
                return ('FLOAT', code[start:index], line_number)

            # Check for invalid number (like 2a)
            if index < len(code) and code[index].isalpha():
                invalid_num = code[start:index + 1]
                errors.append((invalid_num, 'Invalid number', line_number))
                index += 1
                return get_next_token()

            return ('NUM', code[start:index], line_number)

        # Handle identifiers and keywords
        if char.isalpha() or char == '_':
            start = index
            while index < len(code) and (code[index].isalpha() or code[index] == '_' or code[index].isdigit()):
                index += 1

            word = code[start:index]

            # Check for invalid input (like cd!)
            if index < len(code) and code[index] in special_chars:
                invalid_id = word + code[index]
                errors.append((invalid_id, 'Invalid input', line_number))
                index += 1
                return get_next_token()

            if word in KEYWORDS:
                return ('KEYWORD', word, line_number)
            else:
                if word not in symbol_table:
                    symbol_table[word] = len(symbol_table) + 1
                return ('ID', word, line_number)

        # Handle invalid characters
        if char in special_chars:
            errors.append((char, 'Invalid input', line_number))

        else:
            errors.append((char, 'Invalid character', line_number))
        index += 1
        return get_next_token()

    # Main tokenization loop
    while index < len(code):
        token = get_next_token()
        if token:
            tokens.append(token)

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
    tokens, errors, symbol_table = tokenize(code)
    write_output(tokens, errors, symbol_table)
    print("Lexical analysis completed.")


if __name__ == "__main__":
    main()