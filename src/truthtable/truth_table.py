import pandas as pd


class TruthTable:
    def __init__(self, *statements: str):
        '''Constructor for TruthTable object
        
        statements: str
            *args of discrete statements, ex: *["P", "Q", "R"]
        '''
        self.statements = statements
        self.df = pd.DataFrame(self.__get_combinations(), columns=self.statements)

    def get_truth_table(self) -> pd.DataFrame:
        '''Returns current truth table
        '''
        return self.df

    def add_statement(self, lc:'LogicalConnective') -> 'TruthTable':
        '''Adds boolean expression from LogicalConnective object to the dataframe
        
        lc: LogicalConnective
            LogicalConnective obj with boolean expression
        '''
        def select_cols_from(row, params):
            # recursively get the params for nested statements to send into dataframe.loc
            if isinstance(params, str):
                # extract param string
                return row[params]
            else:
                return [select_cols_from(row, p) for p in params]

        params = lc.get_params()
        name = lc.get_name()
        self.df[name] = self.df.apply(lambda row: lc.compute(*select_cols_from(row, params)), axis=1)
        return self

    def __get_combinations(self) -> list:
        '''Recursively generates all (2^n) possible combinations from n independent statements

        surely there is a more efficient way...

        return: list
            nested list of booleans
        '''
        branches = []
        max_level = len(self.statements)
        def traverse(branch: list, level: int):
            if level > max_level:
                branches.append(branch)
            else:
                traverse(branch + [True], level+1)
                traverse(branch + [False], level+1)
        traverse([], 1)
        return branches

class StatementBuilder:
    def get_statement(self, left=None, mid=None, right=None, params: list = None) -> 'LogicalConnective':
        '''Creates LogicalConnective object with merged statement
        
        left: str or LogicalConnective
            if str, return a primitive statement (1-sided expression) such as (NOT X)
            else if LogicalConnective, return the combined 2-sided expression as a new LogicalConnective obj

        mid: None or LogicalConnective
            Middle expression
        
        right: None or LogicalConnective
            RHS expression
        
        params: list<str>
            list of (list of) strings of variables, for ex: [["P"], ["Q"]] for expression [P AND Q]

        return: LogicalConnective
            returns new LogicalConnective obj with merged statements
        '''
        factory = self.__logical_connective_factory

        if None in [mid, right]:
            # make primitive statement (only 1 variable)
            assert isinstance(left, str)
            combined_lc = factory(left).set_params(params)
        else:
            left_lc = factory(left) if isinstance(left, str) else left
            mid_lc = factory(mid) if isinstance(mid, str) else mid
            right_lc = factory(right) if isinstance(right, str) else right

            combined_lc = self.__merge(left_lc, mid_lc, right_lc, params=params)
        return combined_lc

    def __logical_connective_factory(self, operation:str) -> 'LogicalConnective':
        '''Factory method to produce LogicalConnective objects, given a logical operation
        
        operation: str
            Boolean operations allowed: AND, OR, XOR, IDENTITY, NOT, ->, <->

        return: LogicalConnective object
        '''
        connective_factory = {
            "AND": lambda s1, s2: s1 & s2,
            "OR": lambda s1, s2: s1 | s2,
            "XOR": lambda s1, s2: s1 ^ s2,
            "IDENTITY": lambda s1, s2=None: s1,
            "NOT": lambda s1, s2=None: not s1, # drop s2
            "->": lambda s1, s2: (not s1) or (s2),
            "<->": lambda s1, s2: s1 == s2,
        }

        f = connective_factory[operation]
        if operation == "IDENTITY":
            name_function = lambda name: f"{name}"
        elif operation == "NOT":
            name_function = lambda name: f"[{operation} {name}]"
        else:
            name_function = lambda left, right=None: f"({left} {operation} {right})"
        return LogicalConnective(f, name_function=name_function)

    def __merge(self, prefix: 'LogicalConnective', connector: 'LogicalConnective', suffix: 'LogicalConnective', params: list) -> 'LogicalConnective':
        '''Merges two boolean statements into a single one
        All boolean statements can be decomposed into pairwise statements, so this recursively applying this function can produce
        all statements, no matter how complex

        prefix: LogicalConnective
            LogicalConnective object, left side of expression
        
        connector: LogicalConnective
            LogicalConnective object, connects left and right statements

        suffix: LogicalConnective
            LogicalConnective object, right side of expression
        '''
        new_name_function = lambda *args: connector.get_name_function()(
                                                            prefix.get_name_function()(*args[0]),
                                                            suffix.get_name_function()(*args[1]),
                                                        )

        f = lambda left_args, right_args: connector.compute(prefix.compute(*left_args), suffix.compute(*right_args))
        return LogicalConnective(f, params=params, name_function=new_name_function)

class LogicalConnective:
    def __init__(self, func: 'function', params: list = [], name_function: 'function' = None):
        '''Constructor for LogicalConnective obj
        
        func: function
            f: *args<bool> -> bool
            returns the truth value of an expresion after taking in boolean inputs

        params: list of (list of) str
            parameters for the statement function, indicating the variables involved

        name_function: function: params -> str
            returns human-readable name of the statement function
        '''
        self.f = func
        self.params = params
        self.name_function = name_function # f: *args -> string

    def get_name_function(self) -> 'function':
        return self.name_function

    def get_name(self) -> str:
        return self.get_name_function()(*self.params)        

    def set_params(self, params: list) -> 'LogicalConnective':
        self.params = params
        return self

    def get_params(self) -> list:
        return self.params

    def compute(self, *args) -> bool:
        return self.f(*args)