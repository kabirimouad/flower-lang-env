import json
import os


def replace_program(node):
    if isinstance(node, dict):
        # If the node is a dictionary, check its "name" field.
        if node["name"] == "<program>":
            # If the node's name is "<program>", replace it with "CODE".
            node["name"] = "CODE"

            # Remove the "CODE" node from the children array, if it exists.
            if "children" in node:
                node["children"] = [
                    child for child in node["children"]
                    if child["name"] != "CODE"
                ]

        # Recurse over the node's children, if it has any.
        if "children" in node:
            for child in node["children"]:
                replace_program(child)


def replace_define(node):
    if isinstance(node, dict):
        # If the node is a dictionary, check its "name" field.
        if node["name"] == "<define>":
            # If the node's name is "<define>", replace it with "DOLLAREADONLY".
            node["name"] = "DOLLAREADONLY"

            # Remove the "DOLLAREADONLY" node from the children array, if it exists.
            if "children" in node:
                node["children"] = [
                    child for child in node["children"]
                    if child["name"] != "DOLLAREADONLY"
                ]

        # Recurse over the node's children, if it has any.
        if "children" in node:
            for child in node["children"]:
                replace_define(child)


def replace_array_index_math_code_lines(node):
    if isinstance(node, dict):
        # If the node is a dictionary, check its "name" field.
        if node["name"] == "<array_index>":
            # If the node's name is "<array_index>", replace it with "ARRAY".
            node["name"] = "ARRAY"

        if node["name"] == "<math_expression>":
            # If the node's name is "<math_expression>", replace it with "MATH".
            node["name"] = "MATH"

        if node["name"] == "<code_lines>":
            # If the node's name is "<math_expression>", replace it with "MATH".
            node["name"] = "LINE"

        # Recurse over the node's children, if it has any.
        if "children" in node:
            for child in node["children"]:
                replace_array_index_math_code_lines(child)


def replace_declaration(node):
    if isinstance(node, dict):
        # If the node is a dictionary, check its "name" field.
        if node["name"] == "<declaration>":
            # If the node's name is "<declaration>", replace it with "UIDSTAT".
            node["name"] = "NUMBER"
            if "children" in node:
                node["children"] = [
                    child for child in node["children"]
                    if child["name"] != "NUMBER"
                ]
        # elif node["name"] == "UIDSTAT":
        #     # If the node's name is "UIDSTAT", remove it from the parent's
        #     # children list.
        #     node.pop()

        # Recurse over the node's children, if it has any.
        if "children" in node:
            for child in node["children"]:
                replace_declaration(child)


def remove_ops(node):
    # If the node has no children, return it as is
    if not node.get("children"):
        return node

    # Otherwise, recursively remove <ops> nodes from each child
    children = [remove_ops(child) for child in node["children"]]

    # If any of the children is an <ops> node, remove it and append its
    # children to this node's children list
    for child in children:
        if child["name"] == "<ops>":
            children.remove(child)
            children.extend(child["children"])

    # Return the node with its remaining children
    return {
        "name": node["name"],
        "children": children
    }


def remove_code_lines(node):
    # If the node is not a <code_lines> node, then search its children for the node
    if node['name'] != '<code_lines>':
        if 'children' in node:
            node['children'] = [remove_code_lines(
                child) for child in node['children']]
        return node

    # Otherwise, remove the <code_lines> node and add its children to the parent node
    if 'children' in node:
        children = node['children']
    else:
        children = []
    return children


def rename_main_node(node):
    # If the node is not a <main_node> node, then search its children for the node
    if node['name'] != '<main_node>':
        if 'children' in node:
            node['children'] = [rename_main_node(
                child) for child in node['children']]
        return node

    # Otherwise, rename the node to START and remove START from its children
    node['name'] = 'START'
    if 'children' in node:
        node['children'] = [child for child in node['children']
                            if child['name'] != 'START']

    # Recursively process the children of this node
    if 'children' in node:
        node['children'] = [rename_main_node(
            child) for child in node['children']]

    return node


def replace_scan_node(node):
    # If the node is not a <scan> node, then search its children for the node
    if node['name'] != '<scan>':
        if 'children' in node:
            node['children'] = [replace_scan_node(
                child) for child in node['children']]
        return node

    # Otherwise, rename the node to READ and remove READ from its children
    node['name'] = 'READ'
    if 'children' in node:
        node['children'] = [child for child in node['children']
                            if child['name'] != 'READ']

    # Recursively process the children of this node
    if 'children' in node:
        node['children'] = [replace_scan_node(
            child) for child in node['children']]

    return node


def replace_print_node(node):
    if node['name'] != '<print>':
        if 'children' in node:
            node['children'] = [replace_print_node(
                child) for child in node['children']]
        return node

    node['name'] = 'ECHO'
    if 'children' in node:
        node['children'] = [child for child in node['children']
                            if child['name'] != 'ECHO']

    # Recursively process the children of this node
    if 'children' in node:
        node['children'] = [replace_print_node(
            child) for child in node['children']]

    return node


def replace_assignment_node(node):
    # If the node is not a <assignment> node, then search its children for the node
    if node['name'] != '<assignment>':
        if 'children' in node:
            node['children'] = [replace_assignment_node(
                child) for child in node['children']]
        return node

    # Otherwise, rename the node to ASG and remove ASG from its children
    node['name'] = 'ASG'
    if 'children' in node:
        node['children'] = [child for child in node['children']
                            if child['name'] != 'ASG']

    # Recursively process the children of this node
    if 'children' in node:
        node['children'] = [replace_assignment_node(
            child) for child in node['children']]

    return node


def replace_function_declaration_node(node):
    # If the node is not a <assignment> node, then search its children for the node
    if node['name'] != '<function_declaration>' and node['name'] != '<function_call>':
        if 'children' in node:
            node['children'] = [replace_function_declaration_node(
                child) for child in node['children']]
        return node

    # Otherwise, rename the node to ASG and remove ASG from its children
    node['name'] = 'FUNCTION'
    if 'children' in node:
        node['children'] = [child for child in node['children']
                            if child['name'] != 'FUNCTION']

    # Recursively process the children of this node
    if 'children' in node:
        node['children'] = [replace_function_declaration_node(
            child) for child in node['children']]

    return node


def replace_selection_node(node):
    # If the node is not a <assignment> node, then search its children for the node
    if node['name'] != '<selection>':
        if 'children' in node:
            node['children'] = [replace_selection_node(
                child) for child in node['children']]
        return node

    # Otherwise, rename the node to ASG and remove ASG from its children
    node['name'] = 'IF'
    if 'children' in node:
        node['children'] = [child for child in node['children']
                            if child['name'] != 'IF']

    # Recursively process the children of this node
    if 'children' in node:
        node['children'] = [replace_selection_node(
            child) for child in node['children']]

    return node

def replace_comparison_node(node):
    # If the node is not a <assignment> node, then search its children for the node
    if node['name'] != '<comparison>':
        if 'children' in node:
            node['children'] = [replace_comparison_node(
                child) for child in node['children']]
        return node

    # Otherwise, rename the node to ASG and remove ASG from its children
    node['name'] = node['children'][1]['name']
    if 'children' in node:
        node['children'] = [child for child in node['children']
                            if child['name'] != node['children'][1]['name']]

    # Recursively process the children of this node
    if 'children' in node:
        node['children'] = [replace_comparison_node(
            child) for child in node['children']]

    return node


def replace_loop_node(node):
    # If the node is not a <assignment> node, then search its children for the node
    if node['name'] != '<loop>':
        if 'children' in node:
            node['children'] = [replace_loop_node(
                child) for child in node['children']]
        return node

    # Otherwise, rename the node to ASG and remove ASG from its children
    node['name'] = 'FOR'
    if 'children' in node:
        node['children'] = [child for child in node['children']
                            if child['name'] != 'FOR']

    # Recursively process the children of this node
    if 'children' in node:
        node['children'] = [replace_loop_node(
            child) for child in node['children']]

    return node

def replace_inc_dec_node(node):
    # If the node is not a <assignment> node, then search its children for the node
    if node['name'] != '<inc_dec>':
        if 'children' in node:
            node['children'] = [replace_inc_dec_node(
                child) for child in node['children']]
        return node

    # Otherwise, rename the node to ASG and remove ASG from its children
    node['name'] = node['children'][1]['name'] 
    if 'children' in node:
        node['children'] = [child for child in node['children']
                            if child['name'] != node['children'][1]['name']]

    # Recursively process the children of this node
    if 'children' in node:
        node['children'] = [replace_inc_dec_node(
            child) for child in node['children']]

    return node


def build_ast():
    dirname = os.path.dirname(__file__)
    # Load the JSON-formatted text from a file.

    with open(os.path.join(dirname, 'cst.json')) as fp:
        json_text = fp.read()


    # Load the JSON-formatted text into a Python object.
    json_obj = json.loads(json_text)

    # Recurse over the object and replace the "<program>" nodes.
    replace_program(json_obj)

    # Recurse over the object and replace the "<define>" nodes.
    replace_define(json_obj)

    # Recurse over the object and replace the "<array_index>" nodes.
    replace_array_index_math_code_lines(json_obj)

    # Replace "<declaration>" nodes with "UIDSTAT" nodes.
    replace_declaration(json_obj)

    json_obj = remove_ops(json_obj)
    json_obj = rename_main_node(json_obj)
    json_obj = replace_scan_node(json_obj)
    json_obj = replace_print_node(json_obj)
    json_obj = replace_assignment_node(json_obj)
    json_obj = replace_function_declaration_node(json_obj)
    json_obj = replace_selection_node(json_obj)
    json_obj = replace_comparison_node(json_obj)
    json_obj = replace_loop_node(json_obj)
    json_obj = replace_inc_dec_node(json_obj)


    # json_obj = remove_code_lines(json_obj)

    # Convert the updated object back into JSON-formatted text.
    updated_json_text = json.dumps(json_obj, indent=4)
    # print(updated_json_text)

    with open(os.path.join(dirname, 'ast.json'), 'w') as fp:
        fp.write(updated_json_text)


if __name__ == '__main__':
    build_ast()