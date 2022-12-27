import ast

class SimpleCalcEnsurance(ast.NodeVisitor):
    def __init__(self):
        self.is_illegal_syntax: bool = False
        self.allow_float: bool = True
        self.param_name: tuple = tuple()

    def wrapper_visit(self, node: ast.AST, allow_float: bool, param_name: tuple) -> bool:
        self.is_illegal_syntax = False
        self.allow_float = allow_float
        self.param_name = param_name

        self.visit(node)
        return self.is_illegal_syntax
    
    def generic_visit(node):
        self.is_illegal_syntax = True

    def visit_Expression(self, node: ast.Expression):
        self.visit(node.body)

    def visit_BinOp(self, node: ast.BinOp):
        if isinstance(node.op, ast.Add) or isinstance(node.op, ast.Sub) or isinstance(node.op, ast.Mult) or isinstance(node.op, ast.Div):
            self.visit(node.left)
            self.visit(node.right)
        else:
            self.is_illegal_syntax = True
        
    def visit_UnaryOp(self, node: ast.UnaryOp):
        if isinstance(node.op, ast.USub):
            self.visit(node.operand)
        else:
            self.is_illegal_syntax = True
    
    def visit_Constant(self, node: ast.Constant):
        if (self.allow_float and isinstance(node.value, float)) or isinstance(node.value, int):
            pass
        else:
            self.is_illegal_syntax = True

    
    def visit_Name(self, node: ast.Name):
        if node.id in self.param_name and isinstance(node.ctx, ast.Load):
            pass
        else:
            self.is_illegal_syntax = True

def _do_calc(szEval: str, allow_float: bool, d: dict):
    ast_tree = ast.parse(szEval, mode='eval')
    walker = SimpleCalcEnsurance()
    if walker.wrapper_visit(ast_tree, allow_float, d.keys()):
        raise Exception("Illegal AST Tree. Tree contain illegal syntax. Please check BMERevenge.")
    
    return eval(compile(ast_tree, '', mode='eval'), {}, d)

def do_vec_calc(szEval: str, raw_d1: float, raw_d2: float, raw_d3: float) -> float:
    return float(_do_calc(szEval, True, {
        "d1": raw_d1,
        "d2": raw_d2,
        "d3": raw_d3
    }))

def do_expand_calc(szEval: str, d1: int, d2: int) -> int:
    return int(_do_calc(szEval, False, {
        "d1": d1,
        "d2": d2
    }))
