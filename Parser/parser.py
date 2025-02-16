import argparse
import os
from lexer import main as lex
import json
from anytree.exporter import DictExporter 
from anytree.importer import JsonImporter
import Parser.ast_builder as ast_builder 

token_stream = None; # token stream (line number, token number, token type, lexeme)
                    # lexeme is not always important
current_token = None
position = -1
token_value = None
line_nb = None

variable_list = {} # this dictionary is used to store the variables and their values temporarily for the current scope

global_scope = {} # this dictionary is used to store the variables and their values in the global scope
local_scope = {} # this dictionary is used to store the variables and their values in the local scope
function_arguments = {} # this dictionary is used to store the number of variables that a function takes {function_name: number_of_arguments}

current_scope = "global" # this variable is used to keep track of the current scope

# this function takes a root of a tree and prints it
def print_tree(program):
    for pre, fill, node in RenderTree(program):
        if node.name == "UIDSTAT" or node.name == "NUMSTAT" and node.value != None:
            print("%s%s %s" % (pre, node.name, node.value))
        else:
            print("%s%s" % (pre, node.name))

# this function gets the next token from the token stream
def get_next_token():
    global token_stream, position, token_value, line_nb
    try:
        position = position + 1
        (line_number, token_number, token_type, lexeme) = token_stream[position]
        token_value = lexeme
        line_nb = line_number
        # print("Token: " + token_type + " Lexeme: " + lexeme + " Line: " + str(line_number) )
        return token_type
    except:
        print("No tokens found in the source code")
        return None

def error(line_number, excpected , current_token):
    print("Error in line " + str(line_number) + " Expected " + excpected + " but found " + current_token)
    return False

# handling the array_index production
def array_index():
    global current_token, current_scope, local_scope, global_scope, position, line_nb, token_value
    array_list_children = []

    current_token = get_next_token()
    if current_token == None: return False

    if current_token == "LBRACKET":
        current_token = get_next_token()
        if current_token == None: return False
        if(current_token != "NUMSTAT" and current_token != "UIDSTAT"):
            error(line_nb, "NUMSTAT or UIDSTAT", current_token)
            return False
        
        # check if UIDSTAT was declared
        # since array_index is used in global and local scope, we need to check in both scopes
        if current_token == "UIDSTAT":
            if current_scope == "global":
                if token_value not in global_scope:
                    print("Error in line " + str(line_nb) + " Variable " + token_value + " was not declared")
                    return False
            else:
                if token_value in local_scope[current_scope]:
                    pass
                elif token_value in global_scope:
                    pass
                else:
                    print("Error at line " + str(line_nb) + ": Variable " + token_value + " is not defined")
                    return False

        node1 = Node(current_token, token_value)
        array_list_children.append(node1)

        current_token = get_next_token()
        if current_token == None: return False
        if(current_token != "RBRACKET"):
            error(line_nb, "RBRACKET", current_token)
            return False
    else:
        position = position - 1
        return 

    current_token = get_next_token()
    if current_token == None: return False
    if current_token == "LBRACKET":
        current_token = get_next_token()
        if current_token == None: return False
        if(current_token != "NUMSTAT" and current_token != "UIDSTAT"):
            error(line_nb, "NUMSTAT or UIDSTAT", current_token)
            return False
        
        # check if UIDSTAT was declared
        # since array_index is used in global and local scope, we need to check in both scopes
        if current_token == "UIDSTAT":
            if current_scope == "global":
                if token_value not in global_scope:
                    print("Error in line " + str(line_nb) + " Variable " + token_value + " was not declared")
                    return False
            else:
                if token_value in local_scope[current_scope]:
                    pass
                elif token_value in global_scope:
                    pass
                else:
                    print("Error at line " + str(line_nb) + ": Variable " + token_value + " is not defined")
                    return False

        node2 = Node(current_token, token_value)
        array_list_children.append(node2)

        current_token = get_next_token()
        if current_token == None: return False
        if(current_token != "RBRACKET"):
            error(line_nb, "RBRACKET", current_token)
            return False
    else:
        position = position - 1
    
    return array_list_children

# handling the define production
def define():
    # define is always in the global scope

    global current_token, line_nb, token_value, current_scope, global_scope, token_value

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "DOLLAREADONLY": 
        error(line_nb, "DOLLAREADONLY", current_token)
        return False
    node1 = Node(current_token, token_value)

    current_token = get_next_token()
    if current_token == None: return False

    if current_token != "UIDSTAT": 
        error(line_nb, "UIDSTAT", current_token)
        return False
    node2 = Node(current_token, token_value)

    variable_name = token_value


    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "NUMSTAT": 
        error(line_nb, "NUMSTAT", current_token)
        return False

    node3 = Node(current_token, token_value)
    variable_value = token_value

    global_scope[variable_name] = variable_value

    return [node1, node2, node3]


# handling the declaration production
def declaration():
    global current_token, position, current_scope, local_scope, token_value, variable_list

    # these two variables are used to store the variable name and value in the assignmed scope
    variable_name = ""
    variable_value = ""

    declaration_children = []

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "NUMBER":
        position = position - 1
        return None
    node1 = Node(current_token, token_value)
    declaration_children.append(node1)
    
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "UIDSTAT":
        error(line_nb, "UIDSTAT", current_token)
        return False

    node2 = Node(current_token, token_value)
    declaration_children.append(node2)
    variable_name = token_value


    array_index_children = array_index()
    if array_index_children == False:
        return False
    elif array_index_children != None:
        array_index_node = Node("<array_index>", value = token_value, parent = None ,children=array_index_children)
        declaration_children.append(array_index_node)

    
    current_token = get_next_token()
    if current_token == None: return False
    if current_token == "ASG":
        assign_node = Node(current_token, token_value)
        declaration_children.append(assign_node)
        current_token = get_next_token()
        if current_token == None: return False

        if(current_token != "NUMSTAT" and current_token != "UIDSTAT"):
            return False

        elif current_token == "NUMSTAT":
            node3 = Node(current_token, token_value)
            declaration_children.append(node3)
            variable_value = token_value

        elif current_token == "UIDSTAT":
            uid_node = Node(current_token, token_value)
            declaration_children.append(uid_node)
            variable_value = token_value

            array_index_children = array_index()
            if array_index_children == False:
                return False
            elif array_index_children != None:
                array_index_node = Node("<array_index>", value = token_value ,parent = None ,children=array_index_children)
                declaration_children.append(array_index_node)

        
    else:
        position = position - 1
    
    if current_scope == "global":
        # append the variable name and value to the global scope dictionary
        global_scope[variable_name] = variable_value
    else:
        # append the variable name and value to the variable list dictionary as key pair
        # variable_list[str(variable_name)] = variable_value
        variable_list.update({variable_name: variable_value})



    
    return declaration_children


# handling the scan production
def scan():
    global current_token, current_scope, local_scope, global_scope, token_value, line_nb
    scan_children = []

    current_token = get_next_token()
    if current_token == None: return False
    if current_token == "READ":
        node1 = Node(current_token, token_value)
        scan_children.append(node1)
        current_token = get_next_token()
        if current_token == None: return False
        if current_token != "NUMSTAT" and current_token != "UIDSTAT":
            error(line_nb, "NUMSTAT or UIDSTAT", current_token)
            return False

        else:
            # if it's UIDSTAT we should perfor the checks first
            if current_token == "UIDSTAT":
                # check if the variable is defined in the current scope
                # check first in the local scope
                # if it's not defined in the local scope check in the global scope
                # if it's not defined in the global scope then it's an error
                if token_value in local_scope[current_scope]:
                    pass
                elif token_value in global_scope:
                    pass
                else:
                    print("Error at line " + str(line_nb) + ": Variable " + token_value + " is not defined")
                    return False
            
            # if checks passed then we can add the node to the tree
            node2 = Node(current_token, token_value)
            scan_children.append(node2)
            scan_node = Node("<scan>", value=token_value ,children=scan_children)
            return scan_node
    else:   
        return None
    

# handling the print production
# this was names print_f instead of print because print is a keyword in python
def print_f():
    global current_token, current_scope, local_scope, global_scope, token_value, line_nb
    print_children = []

    current_token = get_next_token()
    if current_token == None: return False
    if current_token == "ECHO":
        node1 = Node(current_token, token_value)
        print_children.append(node1)
        current_token = get_next_token()
        if current_token == None: return False
        if current_token != "NUMSTAT" and current_token != "UIDSTAT":
            error(line_nb, "NUMSTAT or UIDSTAT", current_token)
            return False
        else:
            # if it's UIDSTAT we should perfor the checks first
            if current_token == "UIDSTAT":
                # check if the variable is defined in the current scope
                # check first in the local scope
                # if it's not defined in the local scope check in the global scope
                # if it's not defined in the global scope then it's an error
                if token_value in local_scope[current_scope]:
                    pass
                elif token_value in global_scope:
                    pass
                else:
                    print("Error at line " + str(line_nb) + ": Variable " + token_value + " is not defined")
                    return False
            
            # if checks passed then we can add the node to the tree
            node2 = Node(current_token, token_value)
            print_children.append(node2)
            print_node = Node("<print>" , value = token_value , children=print_children)
            return print_node
    else:   
        return None
    

# handling the function call production
def function_call():
    global current_token, position, function_arguments, token_value, line_nb, current_scope, local_scope, global_scope
    function_call_children = [] 

    function_call_name = "" # used to store the name of the function being called to check if it is defined in the function definition
    arguments_count = 0 # used to track the number of arguments in a function call to check if it matches the number of arguments in the function definition


    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "FUNCTION": 
        position = position - 1
        return None
    node1= Node(current_token, token_value)
    function_call_children.append(node1)

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "UIDSTAT": 
        error(line_nb, "UIDSTAT", current_token)
        return False

    function_call_name = token_value
    node2= Node(current_token, token_value)
    function_call_children.append(node2)

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "LPAREN": 
        error(line_nb, "LPAREN", current_token)
        return False
    
    optional_block = False
    current_token = get_next_token()
    if current_token == None: return False
    while current_token == "UIDSTAT":
        # check if UIDSTAT was decalraed
        if token_value in local_scope[current_scope]:
            pass
        elif token_value in global_scope:
            pass
        else:
            print("Error in line " + str(line_nb) + " Variable " + token_value + " is not defined")
            return False

        arguments_count = arguments_count + 1
        if current_token == None: return False

        if current_token != "UIDSTAT": 
            error(line_nb, "UIDSTAT", current_token)
            return False

        node1 = Node(current_token, token_value)
        function_call_children.append(node1)

        optional_block = True


        current_token = get_next_token()
        if current_token == None: return False
        optional_block = False
    
    # check if the function being called is defined
    if function_call_name not in function_arguments:
        print("Error in line " + str(line_nb) + " Function " + function_call_name + " is not defined")
        return False
    
    # check if the number of arguments in the function call matches the number of arguments in the function definition
    if function_arguments[function_call_name] != arguments_count:
        print("Error in line " + str(line_nb) + " Expected " + str(function_arguments[function_call_name]) + " arguments but found " + str(arguments_count) + " in function call: " + function_call_name)
        return False


    if optional_block == False:
        position = position - 1
        
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "RPAREN": 
        error(line_nb, "RPAREN", current_token)
        return False
    else:
        function_call_node = Node("<function_call>", value = token_value ,children=function_call_children)
        return function_call_node
    
# handling the math_expression production
def math_expression():
    global current_token, current_scope, local_scope, global_scope, position

    math_expression_children = []

    current_token = get_next_token()
    if current_token == None: return False
    if(current_token != "NUMSTAT" and current_token != "UIDSTAT"):
        return False
    elif current_token == "NUMSTAT":
            node3 = Node(current_token, token_value)
            math_expression_children.append(node3)
    elif current_token == "UIDSTAT":
        if token_value in local_scope[current_scope]:
            pass
        elif token_value in global_scope:
            pass
        else:
            print("Error at line " + str(line_nb) + ": Variable " + token_value + " is not defined")
            return False
        uid_node1 = Node(current_token, token_value)
        math_expression_children.append(uid_node1)
        array_index_children = array_index()
        if array_index_children == False:
            return False
        elif array_index_children != None:
            array_index_node = Node("<array_index>", value = token_value, parent = None ,children=array_index_children)
            math_expression_children.append(array_index_node)
    
    current_token = get_next_token()
    if current_token == None: return False
    if current_token == "ADD" or current_token == "SUB" or current_token == "MUL" or current_token == "DIV" or current_token == "MOD":
        node = Node(current_token, token_value)
        math_expression_children.append(node)
        current_token = get_next_token()
        if current_token == None: return False
        if(current_token != "NUMSTAT" and current_token != "UIDSTAT"):
            return False
        elif current_token == "NUMSTAT":
                node33 = Node(current_token, token_value)
                math_expression_children.append(node33)
        elif current_token == "UIDSTAT":
            if token_value in local_scope[current_scope]:
                pass
            elif token_value in global_scope:
                pass
            else:
                print("Error at line " + str(line_nb) + ": Variable " + token_value + " is not defined")
                return False
            uid_node = Node(current_token, token_value)
            math_expression_children.append(uid_node)
            array_index_children = array_index()
            if array_index_children == False:
                return False
            elif array_index_children != None:
                array_index_node = Node("<array_index>", value = token_value, parent = None ,children=array_index_children)
                math_expression_children.append(array_index_node)
    else:
        position = position - 1
    math_expression_node = Node("<math_expression>", value = token_value ,children=math_expression_children)
    return math_expression_node

# handling the assignment production
def assignment():
    global current_token, token_value
    assignment_children=[]

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "ASG": 
        return False
    node1= Node(current_token, token_value)
    assignment_children.append(node1)

    function_call_node = function_call()

    if function_call_node == False:
        return False
    elif isinstance(function_call_node, Node):
        assignment_children.append(function_call_node)

    
    # create and return node
    math_expression_node = math_expression()

    if math_expression_node == False:
        return False
    elif isinstance(math_expression_node, Node):
        assignment_children.append(math_expression_node)

    assignment_node= Node("<assignment>", value = token_value, children = assignment_children)
    return assignment_node

    # create and return node


def ops():
    global current_token, position, current_scope, local_scope, global_scope

    ops_children = []

    scan_node = scan()
    
    if scan_node == False:
        return False
    elif scan_node == None:
        position = position - 1
    elif isinstance(scan_node,Node) == True:
        ops_children.append(scan_node)
        ops_node = Node("<ops>", value = token_value, children = ops_children)
        return ops_node 
    #here we should return the node


    print_node = print_f()
    
    if print_node == False:
        return False
    elif print_node == None:
        position = position - 1
    elif isinstance(print_node,Node) == True:
        ops_children.append(print_node)
        ops_node = Node("<ops>", value = token_value, children = ops_children)
        return ops_node 

    
    ############################################################

    current_token = get_next_token()
    if current_token == None: return False
    if current_token == "UIDSTAT":
        # check if the variable is defined in the current scope
        # check first in the local scope
        # if it's not defined in the local scope check in the global scope
        # if it's not defined in the global scope then it's an error
        if token_value in local_scope[current_scope]:
            pass
        elif token_value in global_scope:
            pass
        else:
            print("Error at line " + str(line_nb) + ": Variable " + token_value + " is not defined")
            return False
        
        # if checks passed then create the node
        node1= Node(current_token, token_value)
        ops_children.append(node1)
        array_index_children = array_index()
        if array_index_children == False:
            return False
        elif array_index_children != None:
            array_index_node = Node("<array_index>", value = token_value, parent = None ,children=array_index_children)
            ops_children.append(array_index_node)
        
        assignment_node = assignment()
        if assignment_node == False:
            return False
        else:
            ops_children.append(assignment_node)
            ops_node = Node("<ops>", value = token_value, children = ops_children)
            return ops_node
    else:
        position = position - 1

    # create and return node 

def comparison():
    global current_token, position, current_scope, local_scope, global_scope
    comparison_children = []

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "NUMSTAT" and current_token != "UIDSTAT":
        return False
    else:
        # perform checks for the variable
        if current_token == "UIDSTAT":
            if token_value in local_scope[current_scope]:
                pass
            elif token_value in global_scope:
                pass
            else:
                print("Error at line " + str(line_nb) + ": Variable " + token_value + " is not defined")
                return False

        node1 = Node(current_token, token_value)
        comparison_children.append(node1)
    
    current_token = get_next_token()
    if current_token == None: return False
    if current_token == "EQUAL" or current_token == "NOT_EQUAL" or current_token == "LESS_THAN" or current_token == "LESS_EQUAL" or current_token == "AND" or current_token == "OR":
        node = Node(current_token, token_value)
        comparison_children.append(node)
        if current_token == None: return False


        current_token = get_next_token()

        if current_token != "NUMSTAT" and current_token != "UIDSTAT":
            return False
        else:
            # perform checks for the variable
            if current_token == "UIDSTAT":
                if token_value in local_scope[current_scope]:
                    pass
                elif token_value in global_scope:
                    pass
                else:
                    print("Error at line " + str(line_nb) + ": Variable " + token_value + " is not defined")
                    return False

            node = Node(current_token, token_value)
            comparison_children.append(node)
            comparison_node = Node("<comparison>", value = token_value, children = comparison_children)
            return comparison_node

    else:
        position = position - 1
    
    

def selection():
    global current_token, position
    selection_children = []

    ########## the IF part ############
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != 'IF': 
        position = position - 1
        return None
    else:
        node1 = Node(current_token, token_value)
        selection_children.append(node1)
    
    comparison_node = comparison()
    if comparison_node == False:
        return False
    elif isinstance(comparison_node, Node):
        selection_children.append(comparison_node)
    

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "SEMI":
        error(line_nb, "SEMI", current_token)
        return False
    
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "THEN":
        error(line_nb, "THEN", current_token)
        return False
    


    code_child = code_lines()
    if(code_child == False):
        return False
    elif isinstance(code_child, Node):
        selection_children.append(code_child)
    
    
    optional_block = False
    current_token = get_next_token()
    if current_token == None: return False
    while current_token != "ELIF" and current_token != "FI" and current_token != "ELSE":
        optional_block = True
        position = position - 1
        code_child = code_lines()
        if(code_child == False):
            return False
        elif isinstance(code_child, Node):
            selection_children.append(code_child)
        current_token = get_next_token()
        if current_token == None: return False
        optional_block = False
    
    if(optional_block == False):
        position = position - 1


    ########## the EILF part ############

    # repeat code lines until we find elif or else or fi
    optional_block = False
    current_token = get_next_token()
    if current_token == None: return False


    ## ELIF is optional 

    if current_token != 'ELIF': 
        position = position - 1
    else:
        while current_token == "ELIF":
            node1 = Node(current_token, token_value)
            selection_children.append(node1)
        
            comparison_node = comparison()
            if comparison_node == False:
                return False
            elif isinstance(comparison_node, Node):
                selection_children.append(comparison_node)
        

        
        
            current_token = get_next_token()
            if current_token == None: return False
            if current_token != "SEMI":
                error(line_nb, "SEMI", current_token)
                return False
            
            current_token = get_next_token()
            if current_token == None: return False
            if current_token != "THEN":
                error(line_nb, "THEN", current_token)
                return False

            ## if there is only one line of code in the elif block
            code_child = code_lines()
            if(code_child == False):
                return False
            elif isinstance(code_child, Node):
                selection_children.append(code_child)
            
            ## if there are multiple lines of code in the elif block
            optional_block = False
            current_token = get_next_token()
            if current_token == None: return False
            while current_token != "ELSE" and current_token != "FI" and current_token != "ELIF":
                optional_block = True
                position = position - 1
                #insert current token here to get more elif lines
                code_child = code_lines()
                if(code_child == False):
                    return False
                elif isinstance(code_child, Node):
                    selection_children.append(code_child)
                
                current_token = get_next_token()
                if current_token == None: return False
                optional_block = False

        if optional_block == False:
            position = position - 1
        
        

    ########## the ELSE part ############
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != 'ELSE': 
        position = position - 1
    else:
        node1 = Node(current_token, token_value)
        selection_children.append(node1)
    
        code_child = code_lines()
        if(code_child == False):
            return False
        elif isinstance(code_child, Node):
            selection_children.append(code_child)

        
        optional_block = False
        current_token = get_next_token()
        if current_token == None: return False
        while current_token != "FI":
            optional_block = True
            position = position - 1
            code_child = code_lines()
            if(code_child == False):
                return False
            elif isinstance(code_child, Node):
                selection_children.append(code_child)
            current_token = get_next_token()
            if current_token == None: return False
            optional_block = False
        
        if(optional_block == False):
            position = position - 1

    current_token = get_next_token()
    if current_token == None: return False
    if current_token == "FI":
        node = Node("FI", token_value)
        selection_children.append(node)
    else:
        error(line_nb, "FI", current_token)
        return False
    
    selection_node = Node("<selection>", value = token_value, children = selection_children)

    return selection_node

def inc_dec():
    global current_token, position, current_scope, local_scope, global_scope, line_nb 


    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "UIDSTAT": 
        error(line_nb, "UIDSTAT", current_token)
        return False
    
    if token_value in local_scope[current_scope]:
        pass
    elif token_value in global_scope:
        pass
    else:
        print("Error at line " + str(line_nb) + ": Variable " + token_value + " is not defined")
        return False
    node1 = Node(current_token, token_value)

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "ASG": 
        error(line_nb, "ASG", current_token)
        return False

    node2 = Node(current_token, token_value)


    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "UIDSTAT": 
        error(line_nb, "UIDSTAT", current_token)
        return False
    
    if token_value in local_scope[current_scope]:
        pass
    elif token_value in global_scope:
        pass
    else:
        print("Error at line " + str(line_nb) + ": Variable " + token_value + " is not defined")
        return False
    node3 = Node(current_token, token_value)


    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "ADD" and current_token != "SUB": 
        error(line_nb, "ADD or SUB", current_token)
        return False

    node4 = Node(current_token, token_value)

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "NUMSTAT": 
        error(line_nb, "NUMSTAT", current_token)
        return False

    node5 = Node(current_token, token_value)


    return [node1, node2, node3, node4, node5]

def loop():
    global current_token, position, variable_list
    loop_children = []

    # copy variable list
    # this is used as a backup for the variable list since the variables declared in the loop are only valid inside the loop
    variable_list_copy = variable_list.copy()

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != 'FOR': 
        position = position - 1
        return None
    else:
        node1 = Node(current_token, token_value)
        loop_children.append(node1)
    
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "LPAREN":
        error(line_nb, "LPAREN", current_token)
        return False
    
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "LPAREN":
        error(line_nb, "LPAREN", current_token)
        return False

    # handling only one declaration
    declaration_children = declaration()
    if declaration_children == False:
        return False
    declaration_node = Node("<declaration>", value = token_value, children=declaration_children)
    loop_children.append(declaration_node)
    
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "SEMI":
        error(line_nb, "SEMI", current_token)
        return False
    
    comparison_node = comparison()
    if comparison_node == False:
        return False
    elif isinstance(comparison_node, Node):
        loop_children.append(comparison_node)
    
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "SEMI":
        error(line_nb, "SEMI", current_token)
        return False
    

    inc_dec_children = inc_dec()
    if inc_dec_children == False:
        return False
    elif isinstance(inc_dec_children, list):
        inc_dec_node = Node("<inc_dec>", value = token_value, children=inc_dec_children)
        loop_children.append(inc_dec_node)
    
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "RPAREN":
        error(line_nb, "RPAREN", current_token)
        return False
    
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "RPAREN":
        error(line_nb, "RPAREN", current_token)
        return False

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "SEMI":
        error(line_nb, "SEMI", current_token)
        return False
    
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "DO":
        error(line_nb, "DO", current_token)
        return False

    ##### handling code lines in loop #######
    code_child = code_lines()
    if(code_child == False):
        return False
    elif isinstance(code_child, Node):
        loop_children.append(code_child)
    
    optional_block = False
    current_token = get_next_token()
    if current_token == None: return False
    while current_token != "DONE":
        optional_block = True
        position = position - 1
        code_child = code_lines()
        if(code_child == False):
            return False
        elif isinstance(code_child, Node):
            loop_children.append(code_child)
        current_token = get_next_token()
        if current_token == None: return False
        optional_block = False
    if optional_block == False:
        position = position - 1
    
    #### end of code line ####
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != 'DONE': 
        error(line_nb, "DONE", current_token)
        return False
    else:
        node1 = Node(current_token, token_value)
        loop_children.append(node1)
    
    loop_node = Node("<loop>", value = token_value, children=loop_children)

    variable_list = variable_list_copy.copy()
    return loop_node


    
    



def code_lines():
    global current_token, position

    code_lines_children = []


    ops_child = ops()
    if ops_child == False:
        return False
    elif isinstance(ops_child, Node):
        code_lines_children.append(ops_child)
        code_lines_node = Node("<code_lines>", value = token_value, children = code_lines_children) 
        return code_lines_node
    

    selection_child = selection()
    if selection_child == False:
        return False
    elif isinstance(selection_child, Node):
        code_lines_children.append(selection_child)
        code_lines_node = Node("<code_lines>", value = token_value, children = code_lines_children)
        return code_lines_node
    
    function_call_child = function_call()
    if function_call_child == False:
        return False
    elif isinstance(function_call_child, Node):
        code_lines_children.append(function_call_child)
        code_lines_node = Node("<code_lines>", value = token_value, children = code_lines_children)
        return code_lines_node


    loop_child = loop()
    if loop_child == False:
        return False
    elif isinstance(loop_child, Node):
        code_lines_children.append(loop_child)
        code_lines_node = Node("<code_lines>", value = token_value, children = code_lines_children)
        return code_lines_node
    
    declaration_child = declaration()
    if declaration_child == False:
        return False
    elif isinstance(declaration_child, list):
        declaration_node = Node("<declaration>", value = token_value, children = declaration_child)
        code_lines_children.append(declaration_node)
        code_lines_node = Node("<code_lines>", value = token_value, children = code_lines_children)
        return code_lines_node
    
    error(line_nb, "code_lines", current_token)
    return False
    

def function_declaration():
    global token_value, function_arguments, current_scope, variable_list, global_scope

    # change the value of the curret scope 
    current_scope = "function"


    # this variables are used for function call to check if the number of arguments is correct
    function_declaration_children= []
    function_argument_number = 0
    function_name = "" 

    global current_token, position

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "LPAREN": 
        error(line_nb, "LPAREN", current_token)
        return False

    # handling only one declaration
    declaration_children = declaration()
    if declaration_children == False:
        return False
    declaration_node = Node("<declaration>", value = token_value, children=declaration_children)
    function_declaration_children.append(declaration_node)
    function_argument_number = function_argument_number + 1


    # handling multiple declarations
    optional_block = False
    current_token = get_next_token()
    if current_token == None: return False
    while current_token == "NUMBER":
        optional_block = True
        position = position - 1
        declaration_children = declaration()
        if declaration_children == False:
            return False
        
        declaration_node = Node("<declaration>", value = token_value, children=declaration_children)
        function_declaration_children.append(declaration_node)
        function_argument_number = function_argument_number + 1

        optional_block = False
        current_token = get_next_token()
        if current_token == None: return False
    if optional_block == False:
        position = position - 1
    
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "RPAREN": 
        error(line_nb, "RPAREN", current_token)
        return False

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "NUMBER":
        error(line_nb, "NUMBER", current_token)
        return False
    node = Node(current_token, token_value)
    function_declaration_children.append(node)

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "FUNCTION": 
        print("Error at line " + str(line_nb) + ": Expected a variable name : FUNCTION" + " but found " + current_token)
        return False
    node = Node(current_token, token_value)
    function_declaration_children.append(node)

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "UIDSTAT": 
        print("Error at line " + str(line_nb) + ": Expected a variable name : UIDSTAT" + " but found " + current_token)
        return False
    node = Node(current_token, token_value)
    function_declaration_children.append(node)
    function_name = token_value
    current_scope = token_value



    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "LBRACE":
        return False
    

    ######## handling code_lines in function declaration ######

    code_child = code_lines()
    if(code_child == False):
        return False
    elif isinstance(code_child, Node):
        function_declaration_children.append(code_child)
        function_node = Node("<function_declaration>", value = token_value, children = function_declaration_children)
        

    # append function name and the variables it uses to the local_scope (this is used for scope checking)
    # the first line might contain a variable declaration
    local_scope[function_name] =  variable_list
    
    optional_block = False
    current_token = get_next_token()
    if current_token == None: return False
    while current_token != "RETURN":
        position = position - 1
        optional_block = True
        code_child = code_lines()
        if(code_child == False):
            return False
        elif isinstance(code_child, Node):
            function_declaration_children.append(code_child)
            # append function name and the variables it uses to the local_scope (this is used for scope checking)
            # if there is a declaration in the function, it will be added to the variable_list
            local_scope[function_name] =  variable_list

        current_token = get_next_token()
        if current_token == None: return False
        optional_block = False
    if(optional_block == False):
        position = position - 1

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "RETURN": 
        print("Error at line " + str(line_nb) + ": Expected a variable name : RETURN" + " but found " + current_token)
        return False
    node = Node(current_token, token_value)
    function_declaration_children.append(node)

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "UIDSTAT" and current_token != "NUMSTAT": 
        print("Error at line " + str(line_nb) + ": Expected a variable name : UIDSTAT or NUMSTAT" + " but found " + current_token)
        return False
    
    # perform the checks if the return is already declared
    if current_token == "UIDSTAT":
        if token_value in local_scope[current_scope]:
            pass
        elif token_value in global_scope:
            pass
        else:
            print("Error at line " + str(line_nb) + ": Variable " + token_value + " is not defined")
            return False

    node = Node(current_token, token_value)
    function_declaration_children.append(node)

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "RBRACE":
        return False

    # add function name and number of arguments to the function arguments dictionary (this is used for the function call) 
    function_arguments[function_name] = function_argument_number

    
    # clear the variable list
    variable_list = {} 
    
    # empty current scope after the function declaration for the next function declaration
    current_scope = ""
    
    return function_declaration_children


def main_f():
    global current_token, position, current_scope, variable_list 
    main_f_children = []

    current_scope = "main"
    # add main to the local scope
    local_scope["main"] = {}

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "START":
        print("Error at line " + str(line_nb) + ": Expected a variable name : START" + " but found " + current_token)
        return False
    else:
        node = Node(current_token, token_value)
        main_f_children.append(node)
    
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "LBRACE":
        print("Error at line " + str(line_nb) + ": Expected a variable name : LBRACE" + " but found " + current_token)
        return False
    

    ######## handling code_lines in main function ######

    code_child = code_lines()
    if(code_child == False):
        return False
    elif isinstance(code_child, Node):
        main_f_children.append(code_child)
        # append function name and the variables it uses to the local_scope (this is used for scope checking)
        local_scope[current_scope] =  variable_list
    
    
    optional_block = False
    current_token = get_next_token()
    if current_token == None: return False
    while current_token != "RBRACE":
        optional_block = True
        position = position - 1
        code_child = code_lines()
        if(code_child == False):
            return False
        elif isinstance(code_child, Node):
            main_f_children.append(code_child)
            # append function name and the variables it uses to the local_scope (this is used for scope checking)
            local_scope[current_scope] =  variable_list
        current_token = get_next_token()
        if current_token == None: return False
        optional_block = False
    
    if(optional_block == False):
        position = position - 1

    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "RBRACE":
        print("Error at line " + str(line_nb) + ": Expected a variable name : RBRACE" + " but found " + current_token)
        return False
    

    
    # clear the variable list
    variable_list = {} 
    
    
    return main_f_children


def program():
    global current_token, position, current_scope, token_value

    program = Node("<program>", None, None)

    program_children = []
    define_children = []
    declaration_children = []

    ast_code_children = []
    ast_define_children = []
    ast_declaration_children = []

    current_token = get_next_token()
    if current_token == None: 
        return False

    if current_token != "CODE": 
        error(line_nb, "CODE", current_token)
        return False

    code_node = Node(current_token, value = token_value ,parent=program, children=None)
    program_children.append(code_node)
    

    while current_token != "START":

        optional_define = False
        current_token = get_next_token()
        if current_token == None: return False
        while current_token == "DOLLAREADONLY":
            position = position - 1 # this is to make sure that the current token is not lost
            optional_define = True
            define_children = define()
            if(define_children == False):
                return False
            define_node = Node("<define>" , value = token_value, parent=program, children=define_children)
            program_children.append(define_node)


            current_token = get_next_token()
            optional_define = False
            if current_token == None:
                return False


        
        if optional_define == False:
            position = position - 1
        
        declaration_children = []
        optional_define = False
        current_token = get_next_token()
        if current_token == None: return False
        while current_token == "NUMBER":
            position = position - 1 # this is to make sure that the current token is not lost
            optional_define = True
            declaration_children = declaration()
            if(declaration_children == False):
                print("ERROR in declaration")
                return False
            
            declaration_node = Node("<declaration>" , value = token_value ,parent=program, children=declaration_children)
            program_children.append(declaration_node)
            current_token = get_next_token()
            if current_token == None: return False
            optional_define = False
        
        if optional_define == False:
            position = position - 1
        

        optional_define = False
        current_token = get_next_token()
        if current_token == None: return False
        while current_token == "LPAREN":
            position = position - 1 # this is to make sure that the current token is not lost
            optional_define = True
            function_declaration_children = function_declaration()
            if(function_declaration_children == False):
                print("ERROR in function declaration")
                return False
            function_declaration_node = Node("<function_declaration>" , value = token_value, parent=program, children=function_declaration_children)
            program_children.append(function_declaration_node)


            current_token = get_next_token()
            if current_token == None: return False
            optional_define = False
        
        if optional_define == False:
            position = position - 1
    
        
    main_node = main_f()
    if(main_node == False):
        print("ERROR in main function")
        return False

    main_node = Node("<main_node>" , value= token_value, parent=program, children=main_node)
    
    current_token = get_next_token()
    if current_token == None: return False
    if current_token != "STOP":
        error(line_nb, "STOP", current_token)
        return False
    else:
        stop_node = Node(current_token, value = token_value ,parent=program, children=None)
        program_children.append(stop_node)
    
    program_children.append(main_node)
    return program

def clean_json(obj):
    if isinstance(obj, dict):
        # Check if the name of the object is not "UIDSTAT" or "NUMSTAT"
        if obj.get("name") not in ["UIDSTAT", "NUMSTAT"]:
            # If the name is not "UIDSTAT" or "NUMSTAT", remove the "value" field
            obj.pop("value", None)
        # Recursively clean the children of the object
        if "children" in obj:
            obj["children"] = [clean_json(child) for child in obj["children"]]
    return obj
    
    


def main(source_filepath, output_filepath, debug):
    global token_stream, current_token, function_arguments, global_scope, local_scope
    dirname = os.path.dirname(__file__)

    exporter = DictExporter()

    token_stream = lex(source_filepath,output_filepath, debug)


    program_node = program()
    if program_node == False:
        print("Error in program")
        return False
    else:
        print_tree(program_node)

        exported = exporter.export(program_node)

        #clean the json from non terminals
        cst_json = clean_json(exported)
        cst_json = json.dumps(exported, indent=4)

        with open(os.path.join(dirname,'cst.json'), 'w') as fp:
            fp.write(cst_json)
        
        print("------------------------------------------------------------------------------------")

        # build the ast from the cst
        ast = ast_builder.build_ast()

        importer = JsonImporter()
        # import the CST from the JSON file
        ast = importer.read(open(os.path.join(dirname,'ast.json'), 'r'))
        print_tree(ast)
    
    # print a seperator
    print("--------------------------------------------------")

    
    
    
    # output function arguments to JSON file in the same directory with indent of 4
    with open(os.path.join(dirname,'function_arguments.json'), 'w') as fp:
        json.dump(function_arguments, fp, indent=4)

    
    # output global variables to JSON file in the same directory
    with open(os.path.join(dirname,'global_variables.json'), 'w') as fp:
        json.dump(global_scope, fp, indent=4)
    

    # output local variables to JSON file in the same directory
    with open(os.path.join(dirname,'local_variables.json'), 'w') as fp:
        json.dump(local_scope, fp, indent=4)




if __name__ == '__main__':
    # parse arguments from command line
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='Add file path to the source code', type=str)
    args = parser.parse_args()

    # # if no source code file is provided
    if args.file is None:
        # assign code3.txt as default source code file
        print("No source code file provided. Using code3.txt as default source code file.")
        dirname = os.path.dirname(__file__)
        args.file = os.path.join(dirname, 'code3.txt')

    args.output = "output.txt"
    
    main(args.file, args.output, 0)


