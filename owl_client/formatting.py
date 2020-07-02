import ast
from string import Formatter
from typing import Set, Type


class _FormatNodeTransformer(ast.NodeTransformer):
    def __init__(self, source: str, owner: 'ArithmeticFormatter', kwargs) -> None:
        super().__init__()
        self.source = source
        self.owner = owner
        self.kwargs = kwargs

    def visit(self, node: ast.AST) -> ast.AST:
        if any([isinstance(node, t) for t in self.owner.whitelist]):
            return self.generic_visit(node)
        field = ast.get_source_segment(self.source, node, padded=False)
        value = self.owner.get_field_s(field, self.kwargs)[0]
        try:
            node = ast.Constant(value=value, **{k: node.__getattribute__(k) for k in node._attributes})
            compile(node, "", mode="eval")
            return node
        except TypeError:
            self.kwargs[field] = value
            return ast.parse(f"kwargs['{field}']", mode='eval').body


class ArithmeticFormatter(Formatter):
    """
    Formatter that allows for simple arithmetic to be done in formatting
    eg. ArithmeticFormatter().format("2x+1={2x+1:05d}", x=5) -> "2x+1=00011"
    Positional arguments are ignored as they would conflict with using integers as integers
    eg. ArithmeticFormatter().format("hello {1}", "world") -> "hello 1"
    """
    whitelist: Set[Type[ast.AST]] = {ast.operator, ast.BinOp, ast.Expression, ast.Constant}

    def get_field(self, field_name, args, kwargs):
        tree = ast.parse(field_name, mode='eval')
        fnt = _FormatNodeTransformer(field_name, self, kwargs)
        pruned_tree = fnt.visit(tree)
        return eval(compile(pruned_tree, "<field>", 'eval')), field_name

    def get_field_s(self, field_name, kwargs):
        return super().get_field(field_name, [], kwargs)
