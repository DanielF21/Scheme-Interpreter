'''
This code implements a basic interpreter for Scheme (https://www.scheme.org/).
'''

import sys
sys.setrecursionlimit(1500)

def repl(raise_all=False):
    global_frame = Frame(builtin_frame)
    files = sys.argv[1:]
    for f in files:
        evaluate_file(f, global_frame)

    while True:
        # read the input.  pressing ctrl+d exits, as does typing "EXIT" at the
        # prompt.  pressing ctrl+c moves on to the next prompt, ignoring
        # current input
        try:
            inp = input("in> ")
            if inp.strip().lower() == "exit":
                print("  bye bye!")
                return
        except EOFError:
            print()
            print("  bye bye!")
            return
        except KeyboardInterrupt:
            print()
            continue

        try:
            # tokenize and parse the input
            tokens = tokenize(inp)
            ast = parse(tokens)
            # if global_frame has not been set, we want to call
            # result_and_frame without it (which will give us our new frame).
            # if it has been set, though, we want to provide that value
            # explicitly.
            args = [ast]
            if global_frame is not None:
                args.append(global_frame)
            result, global_frame = result_and_frame(*args)
            # finally, print the result
            print("  out> ", result)
        except SchemeError as e:
            # if raise_all was given as True, then we want to raise the
            # exception so we see a full traceback.  if not, just print some
            # information about it and move on to the next step.
            #
            # regardless, all Python exceptions will be raised.
            if raise_all:
                raise
            print(f"{e.__class__.__name__}:", *e.args)
        print()


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """
    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """
    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """
    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """
    pass


class Pair:
    """
    Linked-List class:
    """
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def get_car(self):
        return self.car

    def get_cdr(self):
        return self.cdr


class Function:
    """
    User defined objects
    """
    def __init__(self, param, exp, frame):
        self.param = param
        self.expression = exp
        self.frame = frame

    def __call__(self, params):
        # length of params
        if len(params) != len(self.param):
            raise SchemeEvaluationError(f"You gave {len(params)}, expected {len(self.param)}, parameters")
        # Make the function call
        function_frame = Frame(self.frame)
        # iterate through the parameters
        for p in range(len(self.param)):
            function_frame.create_map(self.param[p], params[p])
        return evaluate(self.expression, function_frame)


class Frame:
    """
    Creates frame
    Contains Variable Mapping and pointer to enclosing frame
    """
    def __init__(self, enclosing_frame):
        self.enclosing_frame = enclosing_frame
        self.mapping = {}

    def create_map(self, variable, value):
        """
        :return: assigns value to variable in mapping dict
        """
        if type(variable) == list:
            raise SchemeSyntaxError("You cannot assign a list to be a variable")
        self.mapping[variable] = value


# Helper Functions for Evaluate

def create_pair_copy(arg, arg2):
    """
    Recursively builds copy of pair objects
    """
    if arg == 'nil':
        return arg2
    else:
        if is_list(arg):
            return Pair(arg.car, create_pair_copy(arg.cdr, arg2))
        else:
            raise SchemeEvaluationError("Int has no attribute car")


def create_list(args, frame):
    """
    :param args: list of args
    :return: nested cons statements
    """
    if len(args) == 0:
        return 'nil'
    elif len(args) == 1:
        return Pair(evaluate(args[0], frame), 'nil')
    else:
        return Pair(evaluate(args[0], frame), create_list(args[1:], frame))


def search_for_binding(variable, frame):
    """
    :param variable: var
    :param frame: frame
    :return: variable or error
    """
    # Check frames until you hit builtin
    while frame.enclosing_frame is not None:
        if variable in frame.mapping.keys():
            return frame.mapping[variable], frame
        else:
            frame = frame.enclosing_frame
    # if it isn't in the builtin frame
    if frame.enclosing_frame is None:
        if variable in frame.mapping.keys():
            return frame.mapping[variable], frame
        else:
            raise SchemeNameError(f"There is no variable with this assignent: {variable}")


def result_and_frame(tree, frame = None):
    """
    :param tree: tree expressiom
    :param frame: optional: frame to pass in
    :return: tuple (evaluated expression and frame it was evaluated in)
    """
    # If there is no frame, create an empty one
    if frame is None:
        frame = Frame(builtin_frame)
    return evaluate(tree, frame), frame


def evaluate_file(file, frame = None):
    """
    :param file: string containing file name
    :return:
    """
    with open(file, mode = 'r') as f:
        text = f.read() # Store in variable
    tk_text = tokenize(text) # Tokenize
    ps_text = parse(tk_text) # Parse
    return evaluate(ps_text, frame) # Eval


############################
# Tokenization and Parsing #
############################


def number_or_symbol(x):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression

        1. init return list
        2. strip the source by \n (output is a list of strings split by line
        3. go through each item in the list, check for ;
        (iterate through each item in the list, if ; -> replace idx with everything up to the ;)
        4. iterate through the comment stripped code, (list of lists)
    """
    tokenized, new_lines = [], []
    lines = source.split("\n")
    # Strip comments / whitespace
    for line in lines:
        semicolon = False
        for char in enumerate(line):
            if char[1] == ";":
                s_line = line[:char[0]]
                new_lines.append(s_line)
                semicolon = True
        if not semicolon:
            new_lines.append(line)

    # Go through each line and tokenize it
    for line in new_lines:
        old, current = 0, 0
        for char in line:
            current += 1
            if current == len(line):
                if char == ")":
                    tokenized.append(line[old:current - 1])
                    tokenized.append(char)
                else:
                    tokenized.append(line[old:current])
            elif char == "(" or char == ")":
                # append the stuff before the paren
                if line[old:current-1] != "":
                    tokenized.append(line[old:current - 1])
                tokenized.append(char)
                old = current
            elif char == " ":
                # append the stuff before the space
                if line[old:current-1] != "":
                    tokenized.append(line[old:current-1])
                old = current

    # Clean up tokens
    tokens = []
    for tk in tokenized:
        if tk != "" and tk != " ":
            tokens.append(tk.replace(" ", ""))
    return tokens


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    # if the exp is greater than 1, check if first is ( and last is )
    if len(tokens) > 1:
        if tokens[0] != "(" or tokens[-1] != ")":
            raise SchemeSyntaxError("The first and last items are not parens")
    # Mismatched number of parenthesis
    l, r = 0, 0
    for t in tokens:
        if t == "(":
            l += 1
        elif t == ")":
            r += 1
    if l != r:
        raise SchemeSyntaxError(f"Mismatched number of parenthesis: {l,r}")
    def parse_expression(index):
        """
        :param index: token index
        :return: parsed exp
        Helper function as suggested by the lab writeup
        """
        token = tokens[index]
        # Token is a parenthesis
        if token == "(":
            # Recursive call
            parsed = []
            next = index + 1
            while tokens[next] != ")":
                p, next = parse_expression(next)
                parsed.append(p)

            return parsed, next + 1

        # Token is a number or symbol
        else:
            parsed, next = number_or_symbol(token), index + 1
            return parsed, next

    if tokens == []:
        return None

    parsed_expression, next_index = parse_expression(0)
    return parsed_expression


######################
# Built-in Functions #
######################


def mult(args):
    """
    :param args: list of args
    :return: multiplied args
    """
    if len(args) == 1:
        return args[0]
    else:
        product = args[0]
        for arg in range(1, len(args)):
            product *= args[arg]
        return product


def div(args):
    """
    :param args: list or arguments
    :return: divide all of these
    """
    if len(args) == 1:
        return args[0]
    else:
        quotient = args[0]
        for arg in range(1, len(args)):
            quotient /= args[arg]
        return quotient


def equal_to(args):
    """
    :param args: list
    :return: True if all args are equal, False otherwise
    """
    if len(args) == 1:
        return True
    else:
        first_arg = args[0]
        for arg in range(1, len(args)):
            if first_arg == args[arg]:
                equal = True
            else:
                equal = False
                break
        return equal


def greater_than(args):
    """
    :param args: list
    :return: True if all args are in decreasing order
    """
    if len(args) == 1:
        return True
    else:
        for arg in range(len(args) - 1):
            if args[arg] > args[arg + 1]:
                gt = True
            else:
                gt = False
                break
        return gt


def greater_or_equal_to(args):
    """
    :param args: list
    :return: True if all args are in >= order, False otherwise
    """
    if len(args) == 1:
        return True
    else:
        for arg in range(len(args) - 1):
            if args[arg] >= args[arg + 1]:
                gte = True
            else:
                gte = False
                break
        return gte


def less_than(args):
    """
    :param args: list
    :return: True if items are in ascending order
    """
    if len(args) == 1:
        return False
    else:
        for arg in range(len(args) - 1):
            if args[arg] < args[arg + 1]:
                lt = True
            else:
                lt = False
                break
        return lt


def less_or_equal_to(args):
    """
    :param args: list
    :return: True if items are in ascending order
    """
    if len(args) == 1:
        return True
    else:
        for arg in range(len(args) - 1):
            if args[arg] <= args[arg + 1]:
                lte = True
            else:
                lte = False
                break
        return lte


def and_logic(args):
    """
    :param args: list
    :return: True if everything anded is True
    """
    answer = True
    for arg in args:
        answer = answer and arg
        if answer is False:
            break
    return answer


def or_logic(args):
    """
    :param args: list
    :return: True if everything ORed is True
    """
    answer = False
    for arg in args:
        answer = answer or arg
        if answer is True:
            break
    return answer


def not_logic(arg):
    """
    :param args: list
    :return: not arg
    """
    if len(arg) != 1:
        raise SchemeEvaluationError(f"Not has {len(arg)} inputs, Expected 1 input")
    else:
        return not arg[0]


# List Operations


def is_list(arg):
    """
    :param arg:
    :return: bool
    """
    # If its the first call, index in to the list
    if type(arg) == list:
        potential_pair = arg[0]
    else:
        potential_pair = arg

    if type(potential_pair) == Pair and is_list(potential_pair.cdr):
        return True
    elif potential_pair == 'nil':
        return True
    return False


def length(args):
    """
    :param args: list
    :return: length of linked-list
    """
    if not is_list(args):
        raise SchemeEvaluationError("The provided argument is not a list.")

    if type(args) == list:
        potential_pair = args[0]
    else:
        potential_pair = args

    if potential_pair == 'nil':
        return 0
    else:
        l = 1
        while potential_pair.cdr != 'nil':
            l += 1
            potential_pair = potential_pair.cdr
        return l


def indexing(args):
    """
    :param args: list
    :return: Pair object
    """
    if type(args) == list:
        potential_pair = args[0]
        idx = args[1]

    if not is_list(args):
        if idx == 0:
            return potential_pair.car
        raise SchemeEvaluationError("The provided argument is not a list.")

    elif potential_pair == 'nil':
        raise SchemeEvaluationError("Cannot index inside an empty list")

    if idx == 0:
        return potential_pair.car

    # Iterative indexing
    while idx != 0:
        potential_pair = potential_pair.cdr
        idx -= 1
        if potential_pair == 'nil' and idx != 0:
            raise SchemeEvaluationError("Asked for an index that is too high")
    return potential_pair.car


def append(args):
    """
    :param args: nested pair objects
    :return: appened list
    """
    new_args = []
    for arg in args:
        if arg != 'nil':
            new_args.append(arg)

    new_list = 'nil'
    for arg in new_args[::-1]:
        new_list = create_pair_copy(arg, new_list)
    return new_list


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": mult,
    "/": div,
    "#t": True,
    "#f": False,
    "equal?": equal_to,
    ">": greater_than,
    ">=": greater_or_equal_to,
    "<": less_than,
    "<=": less_or_equal_to,
    "and": and_logic,
    "or": or_logic,
    "not": not_logic,
    "list?": is_list,
    'append': append,
    'length': length,
    'list-ref': indexing,
    'nil': None,
}

conditionals = [">", ">=", "<", "<=", "equal?"]

keywords = ['define', 'lambda', 'if', 'cons', 'car', 'cdr', 'nil', 'list', 'begin', 'del', 'let', 'set!']

# CREATE Builtin Frame
builtin_frame = Frame(None)
for builtin in scheme_builtins.keys():
    builtin_frame.create_map(builtin, scheme_builtins[builtin])

##############
# Evaluation #
##############


def evaluate(tree, frame = None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    # create new frame if None is passed in
    if frame is None:
        new_frame = Frame(builtin_frame)
        frame = new_frame

    # If the expression is a symbol in scheme_builtins
    if type(tree) == str:
        # Check for Keywords
        if tree in keywords:
            return tree

        # Check for variable binding
        elif frame is not None:
            binding = search_for_binding(tree, frame)
            return binding[0]

    # If the expression is a number
    elif type(tree) == int or type(tree) == float:
        return tree

    # If the expression is a list
    elif type(tree) == list:

        # evaluate the list operator and after
        if len(tree) == 0:
            raise SchemeEvaluationError(f"Not a correct expression, got {tree}")

        func = evaluate(tree[0], frame)

        # Check for Special Keywords
        if func == "define":
            # Handling the shorthand function definitions, (rewrite exp and evaluate that)
            if type(tree[1]) == list:
                func_name, func_params, func_expression = tree[1][0], tree[1][1:], tree[2]
                new_expression = ['define', func_name, ["lambda", func_params, func_expression]]
                return evaluate(new_expression, frame)
            else:
                assignment = evaluate(tree[2], frame)
                frame.create_map(tree[1], evaluate(tree[2], frame))
                return assignment
        elif func == "lambda":
            # Instantiate a Function object
            new_function = Function(tree[1], tree[2], frame)
            return new_function
        elif func == "if":
            # Evaluate the condition
            condition = evaluate(tree[1], frame)
            if condition:
                return evaluate(tree[2], frame)
            else:
                return evaluate(tree[3], frame)
        elif func == 'cons':
            if len(tree[1:]) != 2:
                raise SchemeEvaluationError(f"Cons received {len(tree[1:])} elements, Expected 2")
            # Make a pair object
            pair = Pair(evaluate(tree[1], frame), evaluate(tree[2], frame))
            return pair
        elif func == 'car':
            if len(tree[1:]) != 1:
                raise SchemeEvaluationError(f"Car is taking in more than one element: {tree[1:]}")
            obj = evaluate(tree[1], frame)
            if type(obj) != Pair:
                raise SchemeEvaluationError("Not a pair object")
            return obj.get_car()
        elif func == 'cdr':
            if len(tree[1:]) != 1:
                raise SchemeEvaluationError(f"Car is taking in more than one element: {tree[1:]}")
            obj = evaluate(tree[1], frame)
            if type(obj) != Pair:
                raise SchemeEvaluationError("Not a pair object")
            return obj.get_cdr()
        elif func == 'list':
            return create_list(tree[1:], frame)
        elif func == 'begin':
            # Evaluate everything in the line
            for exp in tree[1:-1]:
                evaluate(exp, frame)
            return evaluate(tree[-1], frame)
        elif func == 'del':
            if tree[1] in frame.mapping.keys():
                v = frame.mapping[tree[1]]
                del frame.mapping[tree[1]]
                return v
            else:
                raise SchemeNameError("Can't find what to delete")
        elif func == 'let':
            lets = tree[1]
            let_frame = Frame(frame)
            for exp in lets:
                # Evaluate each expression
                let_assignment = evaluate(exp[1], let_frame)
                let_frame.create_map(exp[0], let_assignment)
            return evaluate(tree[2], let_frame)
        elif func == 'set!':
            binding_frame = search_for_binding(tree[1], frame)[1]
            assignment = evaluate(tree[2], frame)
            binding_frame.create_map(tree[1], assignment)
            return assignment

        # Check if it is callable
        elif not callable(func):
            raise SchemeEvaluationError(f"The operator is not an actual function: {func}")

        elif tree[0] in conditionals:
            for arg in range(1, len(tree) - 1):
                args = [evaluate(tree[arg], frame), evaluate(tree[arg + 1], frame)]
                sofar = func(args)
                # Short circuit condition
                if not sofar:
                    return False
            return True

        elif tree[0] == 'and' or tree[0] == 'or':
            if tree[0] == 'and':
                result = True
                for arg in range(1,len(tree)):
                    result = result and evaluate(tree[arg], frame)
                    # Short circuit condition
                    if not result:
                        return result
                return result
            elif tree[0] == 'or':
                result = False
                for arg in range(1, len(tree)):
                    result = result or evaluate(tree[arg], frame)
                    if result:
                        return result
                return result

        # else, Evaluate the function on its args
        args = []
        for arg in range(1, len(tree)):
            args.append(evaluate(tree[arg], frame))
        return func(args)


if __name__ == "__main__":
    repl()

