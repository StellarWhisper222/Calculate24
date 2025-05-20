import tkinter as tk
from tkinter import messagebox
from caculate24 import calc24

class Caculate24GUI:
    def __init__(self, master):
        self.master = master
        master.title("24点计算器")
        master.geometry("400x250")
        master.resizable(False, False)

        self.label = tk.Label(master, text="请输入4个1~13的整数（用空格分开）：", font=("微软雅黑", 12))
        self.label.pack(pady=10)

        self.entry = tk.Entry(master, font=("微软雅黑", 14), justify='center')
        self.entry.pack(pady=5)

        self.calc_button = tk.Button(master, text="计算24点", font=("微软雅黑", 12), command=self.calculate)
        self.calc_button.pack(pady=10)

        self.result_label = tk.Label(master, text="结果：", font=("微软雅黑", 12))
        self.result_label.pack(pady=5)

        self.result_text = tk.Text(master, height=3, width=40, font=("Consolas", 13))
        self.result_text.pack(pady=5)
        self.result_text.config(state=tk.DISABLED)

    def calculate(self):
        input_str = self.entry.get().strip()
        try:
            nums = list(map(int, input_str.split()))
            if len(nums) != 4:
                raise ValueError
            for n in nums:
                if n < 1 or n > 13:
                    raise ValueError
        except Exception:
            messagebox.showerror("输入错误", "请输入4个1~13的整数，用空格分开！")
            return
        results = calc24(nums)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        if results:
            # 只输出一种算法：优先只用四则运算且括号最少的
            arith_only = [expr for expr in results if '!' not in expr]
            if arith_only:
                simple_expr = min(arith_only, key=lambda expr: expr.count('('))
            else:
                simple_expr = min(results, key=lambda expr: expr.count('('))
            self.result_text.insert(tk.END, simple_expr)
        else:
            self.result_text.insert(tk.END, "无解")
        self.result_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = Caculate24GUI(root)
    root.mainloop() 