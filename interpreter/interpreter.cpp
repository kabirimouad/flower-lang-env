#include <stdio.h>
#include <iostream>
#include <math.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <unordered_map>

#define TRUE 1
#define FALSE 0
#define WORD_SIZE 11
#define MEMORY_SIZE 2000

long long int memory[MEMORY_SIZE];

std::unordered_map<int, int> symbol_table; // a hash table for symbols
std::unordered_map<int, int> label_table;  // a hash table for labels

typedef struct
{
    int opcode;
    int operand1;
    int operand2;
    int operand3;
} instruction;

FILE *program_code;

long long int IP = 0;
int label_exist = FALSE; // if a -7 is found this value becomes TRUE
int VERBOSE = FALSE;     // if set to TRUE the program will output extra information about the processs
int data_bp = 0;         // last cell occupied by data
int code_bp = 0;         // last cell occupied by code

// code to initialize data memory and instruction memory to 0
void initialize_memory()
{
    if(VERBOSE)
        printf("Initializing memory...\n");
    int i;
    for (i = 0; i < MEMORY_SIZE; i++)
    {
        memory[i] = 0;
    }
}

instruction decode(long long int line)
{
    /* this function takes a line of code and returns an instruction struct
       with the opcode and operands */

    instruction instr;
    instr.opcode = abs(line) / 1000000000 % 1000;
    instr.operand1 = abs(line) / 1000000 % 1000;
    instr.operand2 = abs(line) / 1000 % 1000;
    instr.operand3 = abs(line) % 1000;

    // handling the sign part of the instruction
    if (line < 0)
    {
        instr.opcode = -instr.opcode;
    }

    return instr;
}

long long int encode(instruction instr)
{
    // this helper function is used to take a instruction structure and return the encoded instruction

    long long int encoded_instruction;
    int isNegative = FALSE;

    long long int opcode = instr.opcode;
    long long int operand1 = instr.operand1;
    long long int operand2 = instr.operand2;
    long long int operand3 = instr.operand3;
    
    if (opcode < 0)
    {
        isNegative = TRUE;
        opcode = -opcode;
    }

    opcode = opcode * 1000000000;
    operand1 = operand1 * 1000000;
    operand2 = operand2 * 1000;


    encoded_instruction = opcode + operand1 + operand2 + operand3;

    if(isNegative)
        encoded_instruction = -encoded_instruction;
    


    return encoded_instruction;
}

// checks if a specefic label exist, if not it will stop the program
void check_label(instruction line)
{
    // we need a label check for all instructions that have a jump (+4, -4, +5, -5, +7)

    int generate_error = FALSE;
    int not_found_symbol;

    // search if the 3rd operand exist in the label table
    // for opcodes +4 -4 +5 -5 +7 : 1st and 3nd operands are labels
    if (line.opcode == 4 || line.opcode == -4 || line.opcode == 5 || line.opcode == -5 || line.opcode == 7)
    {
        if (label_table.count(line.operand3) == 0)
        {
            generate_error = TRUE;
            not_found_symbol = line.operand3;
        }
    }

    if (generate_error == TRUE)
    {
        printf("Error: Label %d not found", not_found_symbol);
        printf("Error at instruction : %lld\n", encode(line));
        exit(1); // EXIT FAILURE
    }
}

// checks if a symbol exists, if not it will stop the program
void check_symbol(instruction line)
{
    // we need a symbol check for all instructions that use DATA MEMORY

    int generate_error = FALSE;
    int not_found_symbol;

    // for opcode +0 we will use operand1 and operand3 as symbols (src and dst)
    if (line.opcode == 0 && (symbol_table.count(line.operand1) == 0 || symbol_table.count(line.operand1) == 0))
    {
        generate_error = TRUE;

        // save the symbol that was not found for the error message
        if (symbol_table.count(line.operand1) == 0)
        {
            not_found_symbol = line.operand1;
        }
        else
        {
            not_found_symbol = line.operand3;
        }
    }

    // for opcodes +1 -1 +2 -2  +6 -6 : all operands are symbols (nn1 nn2 dst)
    else if (line.opcode == 1 || line.opcode == -1 || line.opcode == 2 || line.opcode == -2 || line.opcode == 6 || line.opcode == -6)
    {
        if (symbol_table.count(line.operand1) == 0 || symbol_table.count(line.operand2) == 0 || symbol_table.count(line.operand3) == 0)
        {
            generate_error = TRUE;
        }

        // save the symbol that was not found for the error message
        if (symbol_table.count(line.operand1) == 0)
        {
            not_found_symbol = line.operand1;
        }
        else if (symbol_table.count(line.operand2) == 0)
        {
            not_found_symbol = line.operand2;
        }
        else
        {
            not_found_symbol = line.operand3;
        }
    }

    // for opcodes +4 -4 +5 -5 +7 : 1st and 2nd operands are symbols
    else if (line.opcode == 4 || line.opcode == -4 || line.opcode == 5 || line.opcode == -5 || line.opcode == 7)
    {
        if (symbol_table.count(line.operand1) == 0 || symbol_table.count(line.operand2) == 0)
        {
            generate_error = TRUE;
        }

        // save the symbol that was not found for error message
        if (symbol_table.count(line.operand1) == 0)
        {
            not_found_symbol = line.operand1;
        }
        else
        {
            not_found_symbol = line.operand2;
        }
    }

    // for opcode +8 : 3rd operand is a symbol
    else if (line.opcode == 8)
    {
        if (symbol_table.count(line.operand3) == 0)
        {
            generate_error = TRUE;
        }

        not_found_symbol = line.operand3;
    }

    // for opcode -8 : 1st operand is a symbol
    else if (line.opcode == -8)
    {
        if (symbol_table.count(line.operand1) == 0)
        {
            generate_error = TRUE;
        }

        not_found_symbol = line.operand1;
    }

    if (generate_error == TRUE)
    {
        printf("Error: Symbol %d not found\n", not_found_symbol);
        printf("Error at instruction : %lld\n", encode(line));
        exit(1); // EXIT FAILURE
    }
}


int parse_data(int symbol_line, int value_line, int data_idx)
{
    /* This function takes the symbol line and the value line and parse them into the symbol table
    and stores the data in the data memory. It returns the index where the last value is stored */

    instruction symbol_instruction;
    // decode the symbol_line and store it the symbol_table

    // decode the symbol_line and store it in the symbol_instruction struct
    symbol_instruction = decode(symbol_line);
    // insert the symbol into the symbol table
    symbol_table.insert(std::pair<int, int>(symbol_instruction.operand1, data_idx));

    if(VERBOSE)
        printf("Symbol %d is at memory location %d\n", symbol_instruction.operand1, data_idx);

    // initilize the data section to the value_line
    int limit = data_idx + symbol_instruction.operand2;
    for (int i = data_idx; i < limit; i++)
    {
        memory[i] = value_line;
    }
    data_idx = data_idx + symbol_instruction.operand2;

    return data_idx; // return the index where the last value is stored in the data section
}

int parse_code(long long int instruction_line, int memory_idx)
{
    /* this function takes a code line and if it starts wiht -7 it stores the label in the label_table
     * otherwise it stores the instruciton in the memory array */

    instruction code_instruction;

    // decode the instruction line and store it in the code_instruction struct
    code_instruction = decode(instruction_line);

    // if the line is a label declarartion
    if (code_instruction.opcode == -7)
    {
        // store the label in the label_table
        label_table.insert(std::pair<int, int>(code_instruction.operand3, memory_idx));
        label_exist = TRUE;

        if(VERBOSE)
            printf("Label %d is at memory location %d\n", code_instruction.operand3, memory_idx);
    }
    else
    {
        memory[memory_idx] = instruction_line;
        memory_idx++;
    }

    // check if the symbol in the instruction actually exists in the symbol_table
    check_symbol(code_instruction);

    return memory_idx;
}

void load_memory()
{
    /* This function loads the memory with the instructions and data from the input file */

    char *ch;
    char code_line[WORD_SIZE]; /* The line currently being read from the program file. */
    int memory_idx = 0;        /* The index of the memory we are reached so far */
    int sep_count = 0;         /* The number of separators encountered so far. To determine which section we are reading. */
    long long int value;

    while (!feof(program_code))
    {
        fgets(code_line, 100, program_code);

        if (strcmp(code_line, "+9999999999\n") == 0) // increment the separator count if we encounter a seperator
        {
            if(VERBOSE)
                printf("Separator found\n");


            sep_count++;

            if (sep_count == 1)
            { // if we are in the data section we work in the second part of the memory
                memory_idx = 1000;
            }

            if (sep_count == 2)
            {
                break; // if we encountered the seperator after the data section we stop
            }

            continue; // this serves to skip reading +9999999999 line
        }

        // the data secion
        if (sep_count == 0)
        {
            // if the sep_count is 0 we will read another line containing the initilization value

            char value_line[WORD_SIZE];
            long int value;
            long int symbol = atoi(code_line);
            fgets(value_line, 100, program_code);
            value = strtoll(value_line, &ch, 10);

            memory_idx = parse_data(symbol, value, memory_idx);
            data_bp = memory_idx;
        }

        // the code section
        if (sep_count == 1)
        {
            long long int value;
            char instruction[WORD_SIZE + 1];
            strcpy(instruction, code_line);


            if(instruction[strlen(instruction)] != '\0')
                instruction[strlen(instruction)] = '\0'; // remove the new line character if exist to use strtoll

            value = strtoll(instruction, &ch, 10);
            memory_idx = parse_code(value, memory_idx);
            code_bp++;
        }
    }

    // do the label check after loading everything to avoid forward reference problems
    if (label_exist == TRUE)
    {
        for (int i = 1000; i < 1000 + code_bp; i++)
        {
            check_label(decode(memory[i]));
        }
    }

    // The file pointer is at the input section now
}

long long int symbol_lookup(int symbol)
{
    // this function takes a symbol and returns its value
    return memory[symbol_table[symbol]];
}

void arithmetic_operations(instruction instr)
{
    long long int result; // store the result of the arithmetic operation
    long long int value1 = symbol_lookup(instr.operand1);
    long long int value2 = symbol_lookup(instr.operand2);

    if (instr.opcode == 1)
        result = value1 + value2;
    else if (instr.opcode == -1)
        result = value1 - value2;
    else if (instr.opcode == 2)
        result = value1 * value2;
    else if (instr.opcode == -2)
    {
        result = value1 / value2;
    }

    // store the result in the destination
    memory[symbol_table[instr.operand3]] = result;
}

int conditional_operation(instruction instr, int index)
{
    long long int value1 = symbol_lookup(instr.operand1);
    long long int value2 = symbol_lookup(instr.operand2);


    if (instr.opcode == 4)
    {
        if (value1 == value2)
        {
            index = 1000 + instr.operand3;
        }
        else
        {
            index++;
        }
    }
    else if (instr.opcode == -4)
    {
        if (value1 != value2)
        {
            index = 1000 + instr.operand3;
        }
        else
        {
            index++;
        }
    }
    else if (instr.opcode == 5)
    {
        if (value1 >= value2)
        {
            index = 1000 + instr.operand3;
        }
        else
        {
            index++;
        }
    }
    else if (instr.opcode == -5)
    {
        if (value1 < value2)
        {
            index = 1000 + instr.operand3;
        }
        else
        {
            index++;
        }
    }

    return index;
}

void array_operation(instruction instr)
{
    int arrays_start;
    long long int index;
    long long int value;
    int destination;

    if (instr.opcode == 6)
    {
        // read from array and store the value in the destination

        arrays_start = symbol_table[instr.operand1]; // get the start of the array
        index = symbol_lookup(instr.operand2);       // get the current value stored in index
        value = symbol_table[instr.operand3];        // get the memory address of the value

        memory[value] = memory[arrays_start + index]; // store the value from the array in the destination
    }
    else if (instr.opcode == -6)
    {
        // write to array
        value = symbol_lookup(instr.operand1);       // get the source value
        arrays_start = symbol_table[instr.operand2]; // get the start of the array
        index = symbol_lookup(instr.operand3);       // get the value stored in index

        memory[arrays_start + index] = value; // store the value from destination in the array
    }
}

int loop(instruction instr, int index)
{
    long long int inc = symbol_lookup(instr.operand1); // get the value of the increment
    long long int bnd = symbol_lookup(instr.operand2); // get the value of the bound
    // long long int jmp;


    inc++; // increment the value of the increment

    if (inc < bnd)
    {
        index = 1000 + instr.operand3;
    }
    else
    {
        index++;
    }

    memory[symbol_table[instr.operand1]] = inc; // store the new value of the increment

    return index;
}

void input_output(instruction instr)
{
    long long int value; // store the value of input or output

    // read from input file and store the value in the destination (operand3)
    if (instr.opcode == 8)
    {
        char *ch;
        char instruction[WORD_SIZE + 1];
        long long int address; // the address of the destination

        // check if we reached the end of the input file
        fgets(instruction, 100, program_code);


        // this check avoids problems if the last line of input in the file doesn't end with a newline character
        if (instruction[strlen(instruction)] != '\0')
            instruction[strlen(instruction)] = '\0';

        value = strtoll(instruction, &ch, 10);

        address = symbol_table[instr.operand3];
        memory[address] = value;
    }

    // write to output
    if (instr.opcode == -8)
    {
        // read the value from the source (operand1) and print the ouput to the terminal
        value = symbol_lookup(instr.operand1);
        printf("Code Output : %lld\n", value);
    }
}

void assign(instruction instr)
{
    long long int value = symbol_lookup(instr.operand1);
    int address = symbol_table[instr.operand3];

    memory[address] = value; // store the value in the destination
}

void fetch_decode_execute()
{
    // fetch the instruction from the memory and put it in the IP
    // decode the instruction
    // execute the instruction
    // increment the IP
    // check if the IP is in the range of the code memory
    // if not exit the program
    // if it's a read instruction +8 => read a line from the file, decode it and put it in the data memory
    int i = 1000;

    // fetch 
    IP = memory[i];


    do
    {
        instruction current_instruction;

        // copy the instruction from the memory to the PC

        // decode
        current_instruction = decode(IP);


        // check if the opcode is for arithmetic operations
        int opcode = current_instruction.opcode;

        if (opcode == 1 || opcode == -1 || opcode == 2 || opcode == -2)
        {
            arithmetic_operations(current_instruction);
            IP = memory[++i];
        }

        else if (opcode == 4 || opcode == -4 || opcode == 5 || opcode == -5)
        {
            // i is the index of the next instruction to store in the IP
            i = conditional_operation(current_instruction, i);
            IP = memory[i];
        }
        else if (opcode == 6 || opcode == -6)
        {
            array_operation(current_instruction);
            IP = memory[++i];
        }
        else if (opcode == 7)
        {
            i = loop(current_instruction, i);
            IP = memory[i];
        }
        else if (opcode == 8 || opcode == -8)
        {
            input_output(current_instruction);
            IP = memory[++i];
        }
        else if (opcode == 0)
        {
            assign(current_instruction);
            IP = memory[++i];
        }

        // i++;
    } while (IP != 9000000000);
}


void labels_to_address()
{
    // this function will loop over the code loaded and replaces labels with their memory addresses

    instruction code;

    for (int i = 1000; i < 1000 + code_bp; i++)
    {
        code = decode(memory[i]);

        if (code.opcode == 4 || code.opcode == -4 || code.opcode == 5 || code.opcode == -5 || code.opcode == 7)
        {
            code.operand3 = label_table[code.operand3] - 1000;
            memory[i] = encode(code);
        }
    }
}

int main(int argc, char *argv[])
{
    char file_path[100];

    if(argc < 2)
    {
        printf("Error: No input file provided\n");
        printf("Usage: gcc interpreter.cpp -o code.exe -lstdc++ && code.exe [CODE PATH]\n");
        printf("-v : Run the program in verbose mode\n\n");
        printf("Proceeding with default file path: ./code_samples/code2.txt \n\n");
        strcpy(file_path, "./code_samples/code2.txt");
    }
    else if(argc > 3)
    {
        printf("Error: Too many arguments provided\n");
        printf("Usage: gcc interpreter.cpp -o code.exe -lstdc++ && code.exe [CODE PATH]\n");
        printf("-v : Run the program in verbose mode\n");
        exit(1); // EXIT FAILURE
    }
    else
    {
        // copy the file path from the command line arguments
        strcpy(file_path, argv[1]);
    }

    if(argc == 3 && strcmp(argv[2], "-v") == 0)
        VERBOSE = TRUE;


    program_code = fopen(file_path, "r");

    if (program_code == NULL)
    {
        printf("Error opening file\n");
    }

    else
    {
        initialize_memory();        // initialize the memory to 0

        load_memory();              // load the code into the memory

        if (label_exist == TRUE)
        {
            labels_to_address();    // replace the labels with their memory addresses if they exist
        }

        // print data in data memory
        if(VERBOSE)
        {
            // print data memory
            printf("Data Memory (Only the occupied ones):\n");
            for (int i = 0; i < data_bp; i++)
            {
                printf("%lld\n", memory[i]);
            }

            printf("*********************************\n");

            // print symbol table
            printf("Symbol Table (Format : Label => Memory Address):\n");
            for (auto it = symbol_table.begin(); it != symbol_table.end(); ++it)
                std::cout << it->first << " => " << it->second << '\n';

            printf("*********************************\n");

            // print code memory
            printf("Code Memory (Only the occupied ones):\n");
            for (int i = 1000; i < 1020; i++)
            {
                printf("%lld\n", memory[i]);
            }
            
            printf("*********************************\n");

            if(label_exist)
            {
                // print label table
                printf("Label Table (Format : Label => Memory Address) :\n");
                for (auto it = label_table.begin(); it != label_table.end(); ++it)
                    std::cout << it->first << " => " << it->second << '\n';
            }
        }

        fetch_decode_execute();
    }

    return 0;
}