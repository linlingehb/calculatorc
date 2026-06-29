# -*- coding: utf-8 -*-
"""
科学计算器 — 基于 Kivy 框架
支持基本运算、三角函数、对数、幂运算、阶乘、百分比、常数(π/e)、DEG/RAD 切换
"""

import math
import re
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.utils import platform
from kivy.properties import StringProperty, BooleanProperty

# ── KV 布局定义 ────────────────────────────────────────────
KV = '''
<CustButton@Button>:
    font_size: "18sp"
    bold: True
    background_normal: ""
    background_color: self.bg_color

<NumButton@CustButton>:
    bg_color: 0.94, 0.94, 0.96, 1
    color: 0.15, 0.15, 0.2, 1

<OpButton@CustButton>:
    bg_color: 0.88, 0.88, 0.9, 1
    color: 0.15, 0.15, 0.2, 1

<FuncButton@CustButton>:
    bg_color: 0.82, 0.85, 0.9, 1
    color: 0.15, 0.15, 0.2, 1
    font_size: "15sp"

<EqButton@CustButton>:
    bg_color: 0.18, 0.55, 0.88, 1
    color: 1, 1, 1, 1

<ClrButton@CustButton>:
    bg_color: 0.92, 0.65, 0.6, 1
    color: 1, 1, 1, 1
    font_size: "16sp"

<ModeToggle@ToggleButton>:
    font_size: "13sp"
    bold: True
    background_normal: ""
    background_color: 0.75, 0.8, 0.85, 1 if self.state == "normal" else 0.55, 0.6, 0.7, 1
    color: 1, 1, 1, 1 if self.state == "down" else 0.25, 0.25, 0.25, 1

CalculatorWidget:
    orientation: "vertical"
    padding: 6
    spacing: 4

    # ── 显示区域 ──
    BoxLayout:
        orientation: "vertical"
        size_hint_y: 0.22
        padding: 10, 6
        canvas.before:
            Color:
                rgba: 0.96, 0.96, 0.99, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [12]

        Label:
            id: expression_label
            text: root.expression_display
            font_size: "16sp"
            halign: "right"
            valign: "bottom"
            text_size: self.width - 16, self.height * 0.4
            color: 0.5, 0.5, 0.55, 1

        Label:
            id: result_label
            text: root.display_text
            font_size: "38sp"
            halign: "right"
            valign: "bottom"
            text_size: self.width - 16, self.height * 0.6
            color: 0.1, 0.1, 0.15, 1
            bold: True
            shorten: True

    # ── 按钮区域 ──
    GridLayout:
        cols: 5
        spacing: 3
        size_hint_y: 0.78

        # Row 1 — 模式 & 常数 & 清除
        ModeToggle:
            text: "DEG" if root.deg_mode else "RAD"
            state: "down" if root.deg_mode else "normal"
            on_press: root.toggle_mode()
        FuncButton:
            text: "π"
            on_press: root.add_text("π")
        FuncButton:
            text: "e"
            on_press: root.add_text("e")
        ClrButton:
            text: "C"
            on_press: root.clear()
        ClrButton:
            text: "⌫"
            on_press: root.backspace()

        # Row 2 — 三角函数 & 括号
        FuncButton:
            text: "sin"
            on_press: root.add_text("sin(")
        FuncButton:
            text: "cos"
            on_press: root.add_text("cos(")
        FuncButton:
            text: "tan"
            on_press: root.add_text("tan(")
        FuncButton:
            text: "("
            on_press: root.add_text("(")
        FuncButton:
            text: ")"
            on_press: root.add_text(")")

        # Row 3 — 对数 & 根号 & 幂
        FuncButton:
            text: "log"
            on_press: root.add_text("log(")
        FuncButton:
            text: "ln"
            on_press: root.add_text("ln(")
        FuncButton:
            text: "√"
            on_press: root.add_text("√(")
        FuncButton:
            text: "x²"
            on_press: root.add_text("²")
        FuncButton:
            text: "xʸ"
            on_press: root.add_text("^")

        # Row 4 — 阶乘 & 倒数 & 百分号 & 乘除
        FuncButton:
            text: "n!"
            on_press: root.add_text("!")
        FuncButton:
            text: "1/x"
            on_press: root.reciprocal()
        FuncButton:
            text: "%"
            on_press: root.add_text("%")
        OpButton:
            text: "÷"
            on_press: root.add_text("÷")
        OpButton:
            text: "×"
            on_press: root.add_text("×")

        # Row 5 — 7 8 9 + −
        NumButton:
            text: "7"
            on_press: root.add_text("7")
        NumButton:
            text: "8"
            on_press: root.add_text("8")
        NumButton:
            text: "9"
            on_press: root.add_text("9")
        OpButton:
            text: "+"
            on_press: root.add_text("+")
        OpButton:
            text: "−"
            on_press: root.add_text("-")

        # Row 6 — 4 5 6 . ±
        NumButton:
            text: "4"
            on_press: root.add_text("4")
        NumButton:
            text: "5"
            on_press: root.add_text("5")
        NumButton:
            text: "6"
            on_press: root.add_text("6")
        NumButton:
            text: "."
            on_press: root.add_text(".")
        FuncButton:
            text: "±"
            on_press: root.negate()

        # Row 7 — 1 2 3 0 =
        NumButton:
            text: "1"
            on_press: root.add_text("1")
        NumButton:
            text: "2"
            on_press: root.add_text("2")
        NumButton:
            text: "3"
            on_press: root.add_text("3")
        NumButton:
            text: "0"
            on_press: root.add_text("0")
        EqButton:
            text: "="
            on_press: root.calculate()
'''


# ── 计算器核心逻辑 ──────────────────────────────────────────
class CalculatorWidget(BoxLayout):
    """科学计算器主控件"""

    display_text = StringProperty("0")
    expression_display = StringProperty("")
    deg_mode = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expression = ""
        self._last_was_result = False

    # ── 输入处理 ─────────────────────────────────────────

    def add_text(self, text: str):
        """向表达式中追加文本"""
        if self._last_was_result:
            # 上次是计算结果 — 判断是覆盖还是续接
            if text.isdigit() or text in ("(", "sin(", "cos(", "tan(", "log(",
                                           "ln(", "√(", "π", "e"):
                self.expression = ""
            self._last_was_result = False

        # 防止连续运算符（用新运算符替换上一个）
        ops = ("+", "-", "×", "÷", "^")
        if text in ops and self.expression and self.expression[-1] in ops:
            self.expression = self.expression[:-1] + text
        # 防止多个小数点在同一数字中
        elif text == ".":
            # 取最后一个数字 token
            m = re.search(r"(\d+\.?\d*)$", self.expression)
            if m and "." in m.group(1):
                return  # 已有小数点，忽略
            self.expression += text
        else:
            self.expression += text

        self._refresh_display()

    def clear(self):
        """清空表达式"""
        self.expression = ""
        self.display_text = "0"
        self.expression_display = ""
        self._last_was_result = False

    def backspace(self):
        """删除最后一个字符 / token"""
        if self._last_was_result:
            self.clear()
            return
        if not self.expression:
            return

        # 检查末尾是否为多字符 token
        for token in ("sin(", "cos(", "tan(", "log(", "ln(", "√("):
            if self.expression.endswith(token):
                self.expression = self.expression[:-len(token)]
                break
        else:
            self.expression = self.expression[:-1]

        self._refresh_display()

    def toggle_mode(self):
        """切换 DEG / RAD"""
        self.deg_mode = not self.deg_mode

    def negate(self):
        """± 按钮：取反当前数值"""
        if not self.expression or self._last_was_result:
            self.expression = "-"
            self._last_was_result = False
            self._refresh_display()
            return

        # 匹配末尾的数字（含符号和小数）
        m = re.search(r"(-?\d+\.?\d*)$", self.expression)
        if m:
            num = m.group(1)
            if num.startswith("-"):
                new_num = num[1:]
            else:
                new_num = f"(-{num})" if self.expression[:m.start()] else f"-{num}"
            self.expression = self.expression[:m.start()] + new_num
        else:
            # 末尾不是数字，附加 "-"
            self.expression += "-"

        self._refresh_display()

    def reciprocal(self):
        """1/x：计算当前表达式的倒数"""
        if not self.expression:
            return
        try:
            val = self._evaluate()
            if val == 0:
                self.display_text = "Error: 除以零"
                self.expression = ""
                self.expression_display = ""
                return
            result = 1 / val
            self._set_result(result)
        except Exception:
            self._show_error()

    def calculate(self):
        """= 按钮：求值"""
        if not self.expression:
            return
        try:
            result = self._evaluate()
            self._set_result(result)
        except ZeroDivisionError:
            self.display_text = "Error: 除以零"
            self.expression = ""
            self.expression_display = ""
        except OverflowError:
            self.display_text = "Error: 数值溢出"
            self.expression = ""
            self.expression_display = ""
        except Exception:
            self._show_error()

    # ── 内部方法 ─────────────────────────────────────────

    def _refresh_display(self):
        """刷新显示"""
        self.display_text = self.expression if self.expression else "0"
        self.expression_display = self.expression if self.expression else ""

    def _set_result(self, value):
        """将计算结果设为当前值"""
        formatted = self._format_number(value)
        self.expression_display = self.expression + " ="
        self.expression = formatted
        self.display_text = formatted
        self._last_was_result = True

    def _show_error(self):
        self.display_text = "Error"
        self.expression = ""
        self.expression_display = ""

    def _evaluate(self) -> float:
        """将显示表达式转换为 Python 表达式并求值"""
        expr = self.expression

        # ── 1) 常数 ──
        expr = expr.replace("π", str(math.pi))
        expr = expr.replace("e", str(math.e))

        # ── 2) 运算符 ──
        expr = expr.replace("×", "*")
        expr = expr.replace("÷", "/")
        expr = expr.replace("^", "**")
        expr = expr.replace("²", "**2")

        # ── 3) 函数名 ──
        expr = expr.replace("sin(", "math.sin(")
        expr = expr.replace("cos(", "math.cos(")
        expr = expr.replace("tan(", "math.tan(")
        expr = expr.replace("log(", "math.log10(")
        expr = expr.replace("ln(", "math.log(")
        expr = expr.replace("√(", "math.sqrt(")

        # ── 4) 阶乘 n! ──
        expr = re.sub(r"(\d+)!", r"math.factorial(\1)", expr)

        # ── 5) 百分号 % ──
        expr = re.sub(r"(\d+\.?\d*)%", r"(\1/100)", expr)

        # ── 6) DEG 模式下包裹三角函数参数 ──
        if self.deg_mode:
            expr = self._wrap_trig_degrees(expr)

        # ── 7) 安全求值 ──
        safe_globals = {
            "__builtins__": {},
            "math": math,
        }
        return eval(expr, safe_globals, {})

    def _wrap_trig_degrees(self, expr: str) -> str:
        """将 math.sin/cos/tan(arg) 包裹为 math.sin/cos/tan(math.radians(arg))"""

        # 策略：匹配 "math.XXX(" 后跟一个平衡括号组
        result = []
        i = 0
        trig_funcs = ("sin", "cos", "tan")

        while i < len(expr):
            matched = False
            for func in trig_funcs:
                prefix = f"math.{func}("
                if expr[i:].startswith(prefix):
                    result.append(prefix)
                    result.append("math.radians(")
                    i += len(prefix)
                    # 找到匹配的右括号
                    depth = 1
                    start = i
                    while i < len(expr) and depth > 0:
                        if expr[i] == "(":
                            depth += 1
                        elif expr[i] == ")":
                            depth -= 1
                        i += 1
                    arg = expr[start:i - 1]  # 不含末尾 ')'
                    result.append(arg)
                    result.append("))")
                    matched = True
                    break
            if not matched:
                result.append(expr[i])
                i += 1

        return "".join(result)

    def _format_number(self, num) -> str:
        """格式化数值显示"""
        if isinstance(num, (int, float)):
            if isinstance(num, float):
                if math.isinf(num) or math.isnan(num):
                    return "Error"
                # 整数范围内的浮点数
                if num == int(num) and abs(num) < 1e15:
                    return str(int(num))
            # 科学计数法数值
            formatted = f"{num:.12g}"
            if len(formatted) > 16:
                formatted = f"{num:.8e}"
            return formatted
        return str(num)


# ── App 入口 ───────────────────────────────────────────────
class CalculatorApp(App):
    """科学计算器应用"""

    def build(self):
        self.title = "科学计算器"
        # 桌面端设置窗口尺寸
        if platform != "android":
            Window.size = (400, 680)
            Window.minimum_width = 360
            Window.minimum_height = 600
        return CalculatorWidget()


if __name__ == "__main__":
    CalculatorApp().run()
