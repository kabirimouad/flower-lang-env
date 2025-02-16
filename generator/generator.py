import os
import json

var_symbol_table = {}  # symbol table for variables (name -> address)

# uninitialized variables will be initialized to 0
arrays = {}  # array variables (name -> nb_of_columns)
data_section = []
code_section = []
input_section = []
symbol_count = 1  # start at 1 because 0 is reserved for 0
label_count = 1


# the default zero
data_section.append("+0000001000")
data_section.append("+0000000000")

# load function_arguments.json
dirname = os.path.dirname(__file__)
# Load the JSON-formatted text from a file.
with open(os.path.join(dirname, 'local_variables.json')) as fp:
    json_text = fp.read()
# Load the JSON-formatted text into a Python object.
local_variables = json.loads(json_text)

# load gloabal_variables.json
with open(os.path.join(dirname, 'global_variables.json')) as fp:
    json_text = fp.read()
# Load the JSON-formatted text into a Python object.
global_variables = json.loads(json_text)


######################## HELPER FUNCTIONS ########################

def get_value(var):
    global global_variables, local_variables

    # check if the variable is in local variables
    # currently we return the value just for the main function scope
    return local_variables["main"][var]


def add_numstat(value):
    global data_section, symbol_count, var_symbol_table

    # add value to the data section and var_symbol_table
    var_symbol_table[value] = symbol_count
    data_section.append("+0" + '0'*(3-len(str(symbol_count))
                                    ) + str(symbol_count) + "001000")
    if int(value) > 0:
        data_section.append("+" + '0'*(10-len(str(value))) + str(value))
    else:
        data_section.append("-" + '0'*(10-len(str(value))) + str(value))

    symbol_count += 1


def get_array_size(node):
    global arrays
    array_node = node['children'][1]

    if len(array_node['children']) > 1:
        size = int(array_node['children'][0]['value']) * int(array_node['children'][1]['value'])
        # add the array_name and the size of the columd to the arrays dictionary
        arrays[node['children'][0]['value']] = int(array_node['children'][1]['value'])

    else:
        size = int(array_node['children'][0]['value'])
    return size



def reverse_comparison(comparison):
    if comparison == 'EQUAL':
        return "-4"
    elif comparison == "NOT_EQUAL":
        return "+4"
    elif comparison == "LESS_THAN":
        return "+5"
    elif comparison == "LESS_EQUAL":
        return "-5"


def has_array_node(node):
    if node["name"] == "ARRAY":
        return True
    if "children" in node:
        for child in node["children"]:
            if has_array_node(child):
                return True
    return False


######################## GENERATOR FUNCTIONS ########################

def declare_variables(node):
    global data_section, symbol_count
    array_size = 1
    declaration_is_array = False
    assignment_is_array = False

    if node['name'] == "NUMBER":
        if len(node['children']) > 1 and node['children'][1]['name'] == "ARRAY":
            # get the array size
            array_size = get_array_size(node)
            if array_size > 1:
                declaration_is_array = True

        # add the variable to the symbol table
        var_symbol_table[node['children'][0]['value']] = symbol_count
        # add the variable to the data section
        data_section.append("+0" + '0'*(3-len(str(symbol_count))) + str(
            symbol_count) + '0'*(3-len(str(array_size))) + str(array_size) + "000")

        symbol_count += 1

        # the assignment part
        # we could assign to NUMSTAT or UIDSTAT

        if declaration_is_array:
            # if the array is initialized
            if len(node['children']) > 2:

                # the assignment could be a UIDSTAT or a NUMSTAT
                if node['children'][3]['name'] == "NUMSTAT":
                    value = node['children'][3]['value']
                else:
                    value = get_value(node['children'][3]['value'])

            # if the array is not initialized
            elif len(node['children']) == 2:
                value = 0

        elif not declaration_is_array:
            # if the variable is initialized
            if len(node['children']) > 1:
                # get the variable value

                # the assignment could be a UIDSTAT or a NUMSTAT
                if node['children'][2]['name'] == "NUMSTAT":
                    value = node['children'][2]['value']
                else:
                    value = get_value(node['children'][2]['value'])

            # if the variable is not initialized
            elif len(node['children']) == 1:
                value = 0

        # add the value to the data section
        if not assignment_is_array:
            data_section.append("+" + '0'*(10-len(str(value))) + str(value))

    elif "children" in node:
        for child in node["children"]:
            result = declare_variables(child)
            if result:
                return result
    return None

def handle_array_assignment(node):
    global data_section, symbol_count, var_symbol_table, symbol_count, arrays

    # in this case it's either writing to an array or reading from an array
    left_is_array = False
    right_is_array = False

    destination = node['children'][0]['value']
    destination_address = var_symbol_table[destination]

    # in the case of reading from array, this means that second child name is ASG
    if node['children'][1]['name'] == "ASG":
        math_node = node['children'][1]['children'][0]
        src_array_name = math_node['children'][0]['value']
        src_array_name_address = var_symbol_table[src_array_name]

        src_index_node = math_node['children'][1]

        # the array could be 1D or 2D
        if len(src_index_node['children']) == 1:
            # it could be a UIDSTAT or a NUMSTAT
            if src_index_node['children'][0]['name'] == "UIDSTAT":
                src_index = src_index_node['children'][0]['value']
                src_index = var_symbol_table[src_index]
            else:
                src_index = src_index_node['children'][0]['value']
                add_numstat(src_index)
                src_index = var_symbol_table[src_index]

        elif len(src_index_node['children']) == 2:
            # it could be a UIDSTAT or a NUMSTAT
            if src_index_node['children'][0]['name'] == "UIDSTAT":
                src_index1 = src_index_node['children'][0]['value']
                src_index1 = var_symbol_table[src_index1]
            else:
                src_index1 = src_index_node['children'][0]['value']

            # it could be a UIDSTAT or a NUMSTAT
            if src_index_node['children'][1]['name'] == "UIDSTAT":
                src_index2 = src_index_node['children'][1]['value']
                src_index2 = var_symbol_table[src_index2]
            else:
                src_index2 = src_index_node['children'][1]['value']

            src_index = int(src_index1) * int(arrays[src_array_name]) + int(src_index2)
            add_numstat(src_index)
            src_index = var_symbol_table[src_index]

        code_section.append("+6" + '0'*(3-len(str(src_array_name_address))) + str(src_array_name_address) + '0'*(3-len(str(src_index))) + str(src_index) + '0'*(3-len(str(destination_address))) + str(destination_address))
    

    if node['children'][1]['name'] == "ARRAY":
        array_name = node['children'][0]['value']
        array_name_address = var_symbol_table[array_name]

        array_index_node = node['children'][1]

        if len(array_index_node['children']) == 1:
            # it could be a UIDSTAT or a NUMSTAT
            if array_index_node['children'][0]['name'] == "UIDSTAT":
                array_index = get_value(array_index_node['children'][0]['value'])
            else:
                array_index = array_index_node['children'][0]['value']
        elif len(array_index_node['children']) == 2:
            # it could be a UIDSTAT or a NUMSTAT
            if array_index_node['children'][0]['name'] == "UIDSTAT":
                array_index1 = array_index_node['children'][0]['value']
                array_index1 = var_symbol_table[array_index1]
            else:
                array_index1 = array_index_node['children'][0]['value']

            # it could be a UIDSTAT or a NUMSTAT
            if array_index_node['children'][1]['name'] == "UIDSTAT":
                array_index2 = array_index_node['children'][1]['value']
                array_index2 = var_symbol_table[array_index2]
            else:
                array_index2 = array_index_node['children'][1]['value']

            array_index = int(array_index1) * int(arrays[array_name]) + int(array_index2)
            add_numstat(array_index)
            array_index = var_symbol_table[array_index]
        
        math_node = node['children'][2]['children'][0]
        # it could be a UIDSTAT or a NUMSTAT
        if math_node['children'][0]['name'] == "UIDSTAT":
            src = get_value(math_node['children'][0]['value'])
        else:
            src = math_node['children'][0]['value']
            add_numstat(src)
            src = var_symbol_table[src]

        code_section.append("-6" + '0'*(3-len(str(src))) + str(src) + '0'*(3-len(str(array_name_address))) + str(array_name_address) + '0'*(3-len(str(array_index))) + str(array_index))




def code(node):
    global data_section, code_section, input_section, symbol_count, var_symbol_table, label_count, local_variables

    if node['name'] == "NUMBER":
        return

    if node['name'] == "ECHO":
        # get the variable name
        var_name = node["children"][0]['value']
        # get the variable address
        var_address = var_symbol_table[var_name]
        # print the variable address
        code_section.append(
            "-8" + '0'*(3-len(str(var_address))) + str(var_address) + "000000")

    if node['name'] == "READ":
        # get input from the user
        value = input("input generator: ")
        # get the variable name
        var_name = node["children"][0]['value']
        local_variables['main'][var_name] = value
        # get the variable address
        var_address = var_symbol_table[var_name]
        # read the variable address
        code_section.append("+8" + '0'*6 + '0' *
                            (3-len(str(var_address))) + str(var_address))
        var_value = data_section[var_address+1]
        input_section.append(value)
        return

    if node['name'] == "LINE" and node['children'][0]['name'] == "UIDSTAT":
        # check if arrays are involved
        if has_array_node(node):
            handle_array_assignment(node)
            return

        destination = node['children'][0]['value']
        destination_address = var_symbol_table[destination]

        # check if it's a math expressions or just simple assignment
        math_node = node['children'][1]['children'][0]
        if len(math_node['children']) > 1:
            if math_node['children'][0]['name'] == "NUMSTAT":
                value = math_node['children'][0]['value']
                add_numstat(value)

            if math_node['children'][2]['name'] == "NUMSTAT":
                value2 = math_node['children'][2]['value']
                add_numstat(value2)

            # get the variable name
            var_name = math_node['children'][0]['value']
            var_name2 = math_node['children'][2]['value']

            # get the variable address
            var_address = var_symbol_table[var_name]
            var_address2 = var_symbol_table[var_name2]

            # get the operator
            operator = math_node['children'][1]['name']

            # do the math

            opcode = ""
            if operator == "ADD":
                opcode = "+1"
            elif operator == "SUB":
                opcode = "-1"
            elif operator == "MUL":
                opcode = "+2"
            elif operator == "DIV":
                opcode = "-2"

            code_section.append(opcode + '0'*(3-len(str(var_address))) + str(var_address) + '0'*(3-len(str(
                var_address2))) + str(var_address2) + '0'*(3-len(str(destination_address))) + str(destination_address))

        elif len(math_node['children']) == 1:

            # if it's NUMSTAT then we need to add the value to the data section
            if math_node['children'][0]['name'] == "NUMSTAT":
                value = math_node['children'][0]['value']
                add_numstat(value)

            # get the variable name
            var_name = math_node['children'][0]['value']

            # get the variable address
            var_address = var_symbol_table[var_name]

            code_section.append("+0" + '0'*(3-len(str(var_address))) + str(var_address) +
                                '0'*3 + '0'*(3-len(str(destination_address))) + str(destination_address))

    # handle the selection statement
    # the comparison that we have are :
    if node['name'] == "LINE" and node['children'][0]['name'] == "IF":
        comparison_node = node['children'][0]
        condition_node = comparison_node['children'][0]

        comparison_element1 = condition_node['children'][0]['name']
        comparison_element2 = condition_node['children'][1]['name']

        # comparison element could be NUMSTAT or UIDSTAT
        # if it's NUMSTAT then we need to add the value to the data section
        if comparison_element1 == "NUMSTAT":
            value1 = condition_node['children'][0]['value']
            add_numstat(value1)
        value1 = var_symbol_table[condition_node['children'][0]['value']]

        if comparison_element2 == "NUMSTAT":
            value2 = condition_node['children'][1]['value']
            add_numstat(value2)
        value2 = var_symbol_table[condition_node['children'][1]['value']]

        # we reverse the comparison because we want to jump if the condition is false
        comparison = reverse_comparison(comparison_node['children'][0]['name'])
        # if we have less_equal we need to reverse the values and make it less than
        if comparison == "-5":
            value1, value2 = value2, value1

        # in case the condition is false we need to remove the input section that we added
        input_section_copy = input_section.copy()
        # truth_value = evaluate_condition(condition_node)

        current_index = len(code_section)
        selection_lines_nb = len(comparison_node['children']) - 2
        for i in range(selection_lines_nb):
            code(comparison_node['children'][i+1])

        # if truth_value == False:
        #     input_section = input_section_copy

        # label for the end of the selection
        code_section.append(
            "-7000000" + '0'*(3-len(str(label_count))) + str(label_count))
        # add the jump instruction before the selection lines
        # code_section.insert(current_index, comparison + '0'*(3-len(str(value1))) + str(value1) + '0'*(3-len(str(value2))) + str(value2)  + '0'*(3-len(str(label_count))) + str(label_count))
        line = comparison + '0'*(3-len(str(value1))) + str(value1) + '0'*(3-len(
            str(value2))) + str(value2) + '0'*(3-len(str(label_count))) + str(label_count)
        code_section.insert(current_index, line)
        label_count = label_count + 1

        return

    if node['name'] == "LINE" and node['children'][0]['name'] == "FOR":
        loop_node = node['children'][0]
        initialisation_node = loop_node['children'][0]
        condition_node = loop_node['children'][1]
        increment_node = loop_node['children'][2]


        # initialise the loop variable

        bound_type = condition_node['children'][1]['name']
        if bound_type == "NUMSTAT":
            bound = condition_node['children'][1]['value']
            add_numstat(bound)
        bound_address = var_symbol_table[bound]

        declare_variables(initialisation_node)
        # do an assignment for the initialisation node
        left = initialisation_node['children'][0]['value']
        right = initialisation_node['children'][2]['value']

        add_numstat(right)
        right_address = var_symbol_table[right]
        code_section.append("+0" + '0'*(3-len(str(right_address))) + str(right_address) + '0'*3 + '0'*(3-len(str(var_symbol_table[left]))) + str(var_symbol_table[left]))



        # add a label at the beginning of the loop
        code_section.append(
            "-7000000" + '0'*(3-len(str(label_count))) + str(label_count))
        label = label_count
        label_count = label_count + 1
        current_index = len(code_section)

        increment = increment_node['children'][0]['value']
        increment_address = var_symbol_table[increment]

        for_loop_lines_nb = len(loop_node['children']) - 4
        # start the loop fro index 3 and end at index -1
        for i in range(for_loop_lines_nb):
            code(loop_node['children'][i+3])

        # add the jump instruction at the end of the loop
        line = '+7' + '0'*(3-len(str(increment_address))) + str(increment_address) + '0'*(
            3-len(str(bound_address))) + str(bound_address) + '0'*(3-len(str(label))) + str(label)

        code_section.append(line)

    elif "children" in node:
        for child in node["children"]:
            result = code(child)
            if result:
                return result
    return None


def generator():
    global data_section, code_section, input_section, var_symbol_table

    dirname = os.path.dirname(__file__)
    # Load the JSON-formatted text from a file.

    with open(os.path.join(dirname, 'ast.json')) as fp:
        json_text = fp.read()

    # Load the JSON-formatted text into a Python object.
    json_obj = json.loads(json_text)

    declare_variables(json_obj)
    code(json_obj)
    print(var_symbol_table)

    print("---------------data section---------------")
    for line in data_section:
        print(line)

    print("---------------code section---------------")
    for line in code_section:
        print(line)

    print("---------------input section---------------")
    for line in input_section:
        print(line)

    data_section.append("+9999999999")
    code_section.append("+9000000000")
    code_section.append("+9999999999")

    code_merged = data_section + code_section + input_section
    # output code_merged to a file
    with open(os.path.join(dirname, 'code_merged.txt'), 'w') as fp:
        for line in code_merged:
            fp.write(line + "\n")


if __name__ == "__main__":
    generator()
