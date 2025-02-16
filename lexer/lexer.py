import ply.lex as lex
import argparse 
from prettytable import PrettyTable


# reserved words in the language
reserved = {
    "$readonly" : "DOLLARREADONLY",
    "code" : "CODE",
    "if" : "IF",
    "then" : "THEN",
    "elif" : "ELIF",
    "fi" : "FI",
    "for" : "FOR",
    "do" : "DO",
    "else" : "ELSE",
    "function" : "FUNCTION",
    "done" : "DONE",
    "echo" : "ECHO",
    "read" : "READ",
    "number" : "NUMBER",
    "nothing" : "NOTHING",
    "return" : "RETURN",
    "stop" : "STOP",
    "start" : "START",
}

# list of tokens
tokens = [
    'UIDSTAT',
    'NUMSTAT',
    'ADD',
    'MUL',
    'DIV',
    'SUB',
    'ASG',
    'MOD',
    'AND',
    'OR',
    'NOT',
    'EQUAL',
    'NOT_EQUAL',
    'LESS_THAN',
    'LESS_EQUAL',
    'SEPERATOR',
    'SEMI',
    'LPAREN', 
    'RPAREN',  
    'LBRACE', 
    'RBRACE', 
    'LBRACKET', 
    'RBRACKET', 

] + list(reserved.values())

# symbol table for tokens 
symbol_table = {
    "DOLLARREADONLY" : 1,
    "CODE" : 2,

    "IF" : 10,
    "THEN" : 11,
    "ELIF" : 12,
    "FI" : 13,
    "FOR" : 14,
    "DO" : 15,
    "ELSE" : 16,
    "DONE" : 17,

    "FUNCTION" : 20,
    "RETURN" : 21,
    
    "ECHO" : 30,
    "READ" : 31,

    "NUMBER" : 40,
    "NOTHING" : 41,

    "STOP" : 50,
    "START" : 51,

    "UIDSTAT" : 60,
    "NUMSTAT" : 61,
    'ADD' : 62,
    'MUL' : 63,
    'DIV' : 64,
    'SUB' : 65,
    'ASG' : 66,
    'MOD' : 67,
    'AND' : 68,
    'OR'  : 69,
    'NOT' : 70,
    'SEPERATOR' : 71,
    'SEMI' : 72,
    'LPAREN' : 81, 
    'RPAREN' : 82,  
    'LBRACE' : 83, 
    'RBRACE' : 84, 
    'LBRACKET' : 85, 
    'RBRACKET' : 86, 

    'EQUAL' : 90,
    'NOT_EQUAL' : 91,
    'LESS_THAN' : 92,
    'LESS_EQUAL' : 93,

}

def t_DOLLARREADONLY(t):
    r'\$readonly'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_CODE(t):
    r'code'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_IF(t):
    r'if'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_THEN(t):
    r'then'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_ELIF(t):
    r'elif'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_FI(t):
    r'fi'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_FOR(t):
    r'for'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_DONE(t):
    r'done'
    t.value = (t.value, symbol_table[t.type])
    return t   

def t_DO(t):
    r'do'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_ELSE(t):
    r'else'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_FUNCTION(t):
    r'function'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_RETURN(t):
    r'return'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_ECHO(t):
    r'echo'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_READ(t):
    r'read'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_NUMBER(t): # number the data type 
    r'number'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_NOTHING(t):
    r'nothing'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_STOP(t):
    r'stop'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_START(t):
    r'start'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_EQUAL(t):
    r'-eq'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_NOT_EQUAL(t):
    r'-ne'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_LESS_THAN(t):
    r'-lt'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_LESS_EQUAL(t):
    r'-le'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_ADD(t):
    r'\+'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_MUL(t):
    r'\*'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_DIV(t):
    r'/'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_SUB(t):
    r'-'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_ASG(t):
    r'='
    t.value = (t.value, symbol_table[t.type])
    return t

def t_MOD(t):
    r'%'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_AND(t):
    r'&'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_OR(t):
    r'\|'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_NOT(t):
    r'!'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_SEPERATOR(t):
    r','
    t.value = (t.value, symbol_table[t.type])
    return t

def t_SEMI(t):
    r';'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_LPAREN(t):
    r'\('
    t.value = (t.value, symbol_table[t.type])
    return t

def t_RPAREN(t):
    r'\)'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_LBRACE(t):
    r'{'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_RBRACE(t):
    r'}'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_LBRACKET(t):
    r'\['
    t.value = (t.value, symbol_table[t.type])
    return t

def t_RBRACKET(t):
    r'\]'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_NUMSTAT(t):
    r'0|(-?[1-9][0-9]*)'
    t.value = (t.value, symbol_table[t.type])
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Illegal character {} at line {}".format(t.value[0], t.lineno))
    t.lexer.skip(1)

def t_UIDSTAT(t):
    r'[a-zA-Z]+(_[a-zA-Z]+)*[0-9]{0,3}'
    t.type = reserved.get(t.value, 'UIDSTAT') # check for reserved words
    t.value = (t.value, symbol_table[t.type])
    return t

# ignore comments (only one line comments are allowed)
t_ignore_COMMENT = r'~.*~'
# ignore spaces
t_ignore = ' \t'



def main(source_code_filepath, output_filepath, debug):

    # initlize the table to print in the command line
    table = PrettyTable()
    table.field_names = ["Line Number", "Token Number", "Token Type" ,"Lexemes"]


    source_code = open(source_code_filepath, "r", encoding="utf8").read()
    output_file = open(output_filepath, "w", encoding="utf8")

    # build the lexer
    lexer = lex.lex(debug = debug)
    lexer.input(source_code)

    while True: 
        tok = lexer.token()
        if not tok:
            break
        # add row containing the line number, token number and lexeme to the table
        table.add_row([tok.lineno, tok.value[1], tok.type ,tok.value[0]])
        
        # print the line number, token number, token type and lexeme to the file 
        output_file.write(str(tok.lineno) + " " + str(tok.value[1]) + " " + str(tok.type) + " " + str(tok.value[0]) + "\n") 
    
    # print the table 
    print(table)

if __name__ == "__main__":

    # parse arguments from command line
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Add file path to the source code', type=str)
    parser.add_argument('-d', '--debug', help='Activate debug mode', action='store_true')
    parser.add_argument('-o', '--output', help='Add file path to the output file', type=str)
    args = parser.parse_args()

    # if no source code file is provided
    if args.file is None:
        print("\nError: No input file provided\n")
        print("Usage: python3 lexer.py -f <file_path>")
        print("Arguments:")
        print("\t-f, --file\t\tAdd file path to the source code")
        print("\t-d, --debug\t\tRun the program in debug mode")
        print("\t-o, --output\t\tAdd file path to the output file")
        exit(1)

    # if no output file is provided 
    if(args.output is None):
        print("No output file provided. Using ./output.txt")
        args.output = "output.txt"
    
    main(args.file, args.output, args.debug)