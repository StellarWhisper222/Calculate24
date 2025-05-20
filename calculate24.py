import itertools
import re
import ast
import math

# 定义四则运算符
ops = ['+', '-', '*', '/']

def factorial(n):
    """
    计算n的阶乘，仅支持非负整数，且n<=10（防止溢出）
    """
    if not isinstance(n, int) or n < 0 or n > 10:
        raise ValueError('阶乘只支持0~10的整数')
    return math.factorial(n)

def normalize(expr):
    """
    递归解析表达式为AST树，对加减链和乘除链递归归一化，生成结构签名用于去重。
    支持阶乘表达式。
    """
    def node_signature(node):
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, (ast.Add, ast.Sub)):
                add_list, sub_list = collect_addsub(node)
                add_list.sort()
                sub_list.sort()
                return f"addsub({'_'.join(add_list)}|{'_'.join(sub_list)})"
            elif isinstance(node.op, (ast.Mult, ast.Div)):
                mul_list, div_list = collect_muldiv(node)
                mul_list.sort()
                div_list.sort()
                return f"muldiv({'_'.join(mul_list)}|{'_'.join(div_list)})"
            else:
                op_type = type(node.op)
                op_str = {ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/'}[op_type]
                return f"{op_str}({node_signature(node.left)},{node_signature(node.right)})"
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            # 用!表示阶乘
            return f"fact({node_signature(node.operand)})"
        elif isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'fact':
            return f"fact({node_signature(node.args[0])})"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif hasattr(ast, 'Num') and isinstance(node, ast.Num):
            return str(node.n)
        return str(node)
    def collect_addsub(node):
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Add):
                left_add, left_sub = collect_addsub(node.left)
                right_add, right_sub = collect_addsub(node.right)
                return (left_add + right_add, left_sub + right_sub)
            elif isinstance(node.op, ast.Sub):
                left_add, left_sub = collect_addsub(node.left)
                right_add, right_sub = collect_addsub(node.right)
                return (left_add + right_sub, left_sub + right_add)
        return ([node_signature(node)], [])
    def collect_muldiv(node):
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Mult):
                left_mul, left_div = collect_muldiv(node.left)
                right_mul, right_div = collect_muldiv(node.right)
                return (left_mul + right_mul, left_div + right_div)
            elif isinstance(node.op, ast.Div):
                left_mul, left_div = collect_muldiv(node.left)
                right_mul, right_div = collect_muldiv(node.right)
                return (left_mul + right_div, left_div + right_mul)
        return ([node_signature(node)], [])
    try:
        tree = ast.parse(expr.replace('!','fact'), mode='eval')
        return node_signature(tree.body)
    except Exception:
        return expr

def remove_redundant_parentheses(expr):
    import ast
    precedence = {'+':1, '-':1, '*':2, '/':2, '!':3}
    def flatten_add(node):
        # 递归收集加法链
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return flatten_add(node.left) + flatten_add(node.right)
        else:
            return [node]
    def flatten_mul(node):
        # 递归收集乘法链
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            return flatten_mul(node.left) + flatten_mul(node.right)
        else:
            return [node]
    def to_str(node):
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Add):
                # 合并加法链
                add_nodes = flatten_add(node)
                return '+'.join(to_str(n) for n in add_nodes)
            if isinstance(node.op, ast.Mult):
                # 合并乘法链
                mul_nodes = flatten_mul(node)
                return '*'.join(to_str(n) for n in mul_nodes)
            left = to_str(node.left)
            right = to_str(node.right)
            op = {ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/'}[type(node.op)]
            # 括号判断
            if isinstance(node.left, ast.BinOp):
                l_op = {ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/'}[type(node.left.op)]
                if precedence[l_op] < precedence[op]:
                    left = f'({left})'
            if isinstance(node.right, ast.BinOp):
                r_op = {ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/'}[type(node.right.op)]
                if precedence[r_op] < precedence[op] or (precedence[r_op] == precedence[op] and op in ['-', '/']):
                    right = f'({right})'
            return f'{left}{op}{right}'
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return f'{to_str(node.operand)}!'
        elif isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'fact':
            # 阶乘外层括号优化
            arg = node.args[0]
            # 如果是加法链或乘法链，直接合并
            if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                add_nodes = flatten_add(arg)
                return f"{' + '.join(to_str(n) for n in add_nodes)}!"
            if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mult):
                mul_nodes = flatten_mul(arg)
                return f"{'*'.join(to_str(n) for n in mul_nodes)}!"
            return f'{to_str(arg)}!'
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif hasattr(ast, 'Num') and isinstance(node, ast.Num):
            return str(node.n)
        return ''
    try:
        tree = ast.parse(expr.replace('!','fact'), mode='eval')
        return to_str(tree.body)
    except Exception:
        return expr

def safe_eval(expr):
    """
    安全计算表达式，支持阶乘
    """
    expr = expr.replace('!','fact')
    def fact(x):
        return math.factorial(x)
    return eval(expr, {"__builtins__":None, 'fact':fact})

def generate_all_expressions(nums):
    """
    递归生成所有可能的表达式（字符串），每一步结果也可取阶乘
    返回[(表达式字符串, 计算值)]
    """
    if len(nums) == 1:
        n = nums[0]
        results = []
        # 原数
        results.append((str(n), n))
        # 阶乘
        if isinstance(n, int) and 0 <= n <= 10:
            try:
                f = factorial(n)
                if f != n:
                    results.append((f"{n}!", f))
            except Exception:
                pass
        return results
    exprs = []
    for i in range(1, len(nums)):
        lefts = generate_all_expressions(nums[:i])
        rights = generate_all_expressions(nums[i:])
        for l_expr, l_val in lefts:
            for r_expr, r_val in rights:
                for op in ops:
                    try:
                        if op == '+':
                            val = l_val + r_val
                        elif op == '-':
                            val = l_val - r_val
                        elif op == '*':
                            val = l_val * r_val
                        elif op == '/':
                            if abs(r_val) < 1e-8:
                                continue
                            val = l_val / r_val
                        expr = f'({l_expr}{op}{r_expr})'
                        exprs.append((expr, val))
                        # 合并结果可取阶乘
                        if isinstance(val, int) and 0 <= val <= 10:
                            try:
                                f = factorial(val)
                                exprs.append((f'{expr}!', f))
                            except Exception:
                                pass
                    except Exception:
                        continue
    return exprs

def calc24(nums):
    """
    计算所有能用四个数字通过加减乘除和阶乘得到24的表达式。
    :param nums: 长度为4的数字列表
    :return: 所有能算出24的表达式（字符串列表）
    """
    results = set()
    normalized_set = set()
    # 所有数字的全排列
    for num_perm in set(itertools.permutations(nums)):
        exprs = generate_all_expressions(list(num_perm))
        for expr, val in exprs:
            try:
                if abs(val - 24) < 1e-6:
                    norm = normalize(expr)
                    if norm not in normalized_set:
                        results.add(expr)
                        normalized_set.add(norm)
            except Exception:
                continue
    return list(results)

def main():
    print("欢迎使用24点计算器！请输入4个整数（用空格分开）：")
    try:
        nums = list(map(int, input().strip().split()))
        if len(nums) != 4:
            print("请输入4个整数！")
            return
    except Exception:
        print("输入有误，请输入4个整数！")
        return
    results = calc24(nums)
    if results:
        # 先筛选只用四则运算的解法
        arith_only = [expr for expr in results if '!' not in expr]
        if arith_only:
            # 在只用四则运算的解法中选括号最少的
            simple_expr = min(arith_only, key=lambda expr: expr.count('('))
        else:
            # 没有只用四则运算的解法，在所有解法中选括号最少的
            simple_expr = min(results, key=lambda expr: expr.count('('))
        print(simple_expr)
    else:
        print("无解")

if __name__ == "__main__":
    main() 