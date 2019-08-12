import ast
import numpy as np

def Hash (keys):
    res = 0
    for key in keys:
        r = hash(key)
        res+=r
    return res



def Z_ScoreNormalization(x):
    mu = np.average(x)
    sigma = np.std(x)
    for i in range(0,len(x)):
        x[i] = (x[i]-mu)/sigma


class NodeVisitorLevel(ast.NodeVisitor):
    def __init__(self, root):
        self._root = root
        self._levelTran = []
        self._new_levels = []
        self.d = {}
        self.nodesNum = 0
        self.others_values = []
        self.others_dict = {}
        self.same_nodes = 0

    def visit(self, node):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        for item in self.others_values[self.d[node][0]]:
            if self.d[node][1] == self.others_dict[item][1]:
                self.same_nodes = self.same_nodes + 2 * self.d[node][0]
                self.others_values[self.d[node][0]].remove(item)
                return None
        return visitor(node)

    def generic_visit_level(self):
        stack = [self._root]
        self._levelTran = []
        while len(stack) != 0:
            tmp = []
            res_each = []
            for i in stack:
                res_each.append(i)
                self.d[i] = [0]
                for field, value in ast.iter_fields(i):
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, ast.AST):
                                tmp.append(item)
                    elif isinstance(value, ast.AST):
                        tmp.append(value)
            stack = tmp
            self._levelTran.insert(0, res_each)

    def process_tree(self):
        for one_level in self._levelTran:
            for node in one_level:
                self.cal_num(node)
                self.cal_hash(node)

    def cal_num(self, node):
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        self.d[node][0] = self.d[node][0] + self.d[item][0] + 1
            elif isinstance(value, ast.AST):
                self.d[node][0] = self.d[node][0] + self.d[value][0] + 1
        if self.d[node][0] > self.nodesNum:
            self.nodesNum = self.d[node][0]

    def cal_hash(self, node):
        hash = Hash(node._fields)
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.AST):
                        hash = self.d[item][1] + hash
            elif isinstance(value, ast.AST):
                hash = hash + self.d[value][1]
        self.d[node].append(hash)


class FuncNodeCollector(ast.NodeTransformer):
    """
    Clean node attributes, delete the attributes that are not helpful for recognition repetition.
    Then collect all function nodes.
    """

    def __init__(self):
        super(FuncNodeCollector, self).__init__()
        self._curr_class_names = []
        self._func_nodes = []
        self._last_node_lineno = -1
        self._node_count = 0
        self._expr = 0
        self._call = 0
        self._classdef = 0
        self._funcdef = 0
        self._name = 0
        self._attribute = 0

    @staticmethod
    def _mark_docstring_sub_nodes(node):
        """
        Inspired by ast.get_docstring, mark all docstring sub nodes.

        Case1:
        regular docstring of function/class/module

        Case2:
        def foo(self):
            '''pure string expression'''
            for x in self.contents:
                '''pure string expression'''
                print x
            if self.abc:
                '''pure string expression'''
                pass

        Case3:
        def foo(self):
            if self.abc:
                print('ok')
            else:
                '''pure string expression'''
                pass

        :param node: every ast node
        :return:
        """

        def _mark_docstring_nodes(body):
            if body and isinstance(body, collections.Sequence):
                for n in body:
                    if isinstance(n, ast.Expr) and isinstance(n.value, ast.Str):
                        n.is_docstring = True

        node_body = getattr(node, 'body', None)
        _mark_docstring_nodes(node_body)
        node_orelse = getattr(node, 'orelse', None)
        _mark_docstring_nodes(node_orelse)

    @staticmethod
    def _is_docstring(node):
        return getattr(node, 'is_docstring', False)

    def generic_visit(self, node):
        self._node_count = self._node_count + 1
        self._last_node_lineno = max(getattr(node, 'lineno', -1), self._last_node_lineno)
        self._mark_docstring_sub_nodes(node)
        return super(FuncNodeCollector, self).generic_visit(node)

    def visit_Str(self, node):
        del node.s
        self.generic_visit(node)
        return node

    def visit_Expr(self, node):
        self._expr+=1
        if not self._is_docstring(node):
            self.generic_visit(node)
            if hasattr(node, 'value'):
                return node

    def visit_arg(self, node):
        """
        remove arg name & annotation for python3
        :param node: ast.arg
        :return:
        """
        del node.arg
        del node.annotation
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        self._name+=1
        del node.id
        del node.ctx
        self.generic_visit(node)
        return node

    def visit_Attribute(self, node):
        self._attribute+=1
        del node.attr
        del node.ctx
        self.generic_visit(node)
        return node

    def visit_Call(self, node):
        self._call +=1
        func = getattr(node, 'func', None)
        if func and isinstance(func, ast.Name) and func.id == 'print':
            return  # remove print call and its sub nodes for python3
        return node

    def visit_ClassDef(self, node):
        self._classdef+=1
        self._curr_class_names.append(node.name)
        self.generic_visit(node)
        self._curr_class_names.pop()
        return node

    def visit_FunctionDef(self, node):
        self._funcdef+=1
        node.name = '.'.join(itertools.chain(self._curr_class_names, [node.name]))
        self._func_nodes.append(node)
        count = self._node_count
        self.generic_visit(node)
        node.endlineno = self._last_node_lineno
        node.nsubnodes = self._node_count - count
        return node

    def visit_Compare(self, node):

        def _simple_nomalize(*ops_type_names):
            if node.ops and len(node.ops) == 1 and type(node.ops[0]).__name__ in ops_type_names:
                if node.left and node.comparators and len(node.comparators) == 1:
                    left, right = node.left, node.comparators[0]
                    if type(left).__name__ > type(right).__name__:
                        left, right = right, left
                        node.left = left
                        node.comparators = [right]
                        return True
            return False

        if _simple_nomalize('Eq'):
            pass

        if _simple_nomalize('Gt', 'Lt'):
            node.ops = [{ast.Lt: ast.Gt, ast.Gt: ast.Lt}[type(node.ops[0])]()]

        if _simple_nomalize('GtE', 'LtE'):
            node.ops = [{ast.LtE: ast.GtE, ast.GtE: ast.LtE}[type(node.ops[0])]()]

        self.generic_visit(node)
        return node

    def visit_Print(self, node):
        # remove print expr for python2
        pass

    def clear(self):
        self._func_nodes = []

    def get_function_nodes(self):
        return self._func_nodes