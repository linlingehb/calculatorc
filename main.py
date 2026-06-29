# -*- coding: utf-8 -*-
"""
科学计算器 — 基于 Kivy 框架
支持基本运算、三角函数、反三角函数、对数、幂运算、阶乘、百分比、常数(π/e)、DEG/RAD 切换
"""

import math
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty
from kivy.graphics import Color, RoundedRectangle


class CalculatorWidget(BoxLayout):
    """科学计算器主控件"""
    display_text = StringProperty("0")
    expression_display = StringProperty("")
    deg_mode = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expression = ""
        self._last_was_result = False
        self.orientation = "vertical"
        self.padding = 6
        self.spacing = 4

        # 构建UI
        self._build_ui()

    def _build_ui(self):
        """构建用户界面"""
        # 显示区域
        display_box = BoxLayout(
            orientation="vertical",
            size_hint_y=0.22,
            padding=[10, 6]
        )

        # 显示区域背景
        with display_box.canvas.before:
            Color(0.96, 0.96, 0.99, 1)
            self.display_bg = RoundedRectangle(
                pos=display_box.pos,
                size=display_box.size,
                radius=[12]
            )

        # 绑定更新背景位置
        display_box.bind(pos=self._update_bg, size=self._update_bg)

        # 表达式标签
        self.expr_label = Label(
            text=self.expression_display,
            font_size="16sp",
            halign="right",
            valign="bottom",
            color=[0.5, 0.5, 0.55, 1],
            size_hint_y=0.4
        )
        self.expr_label.bind(size=self.expr_label.setter('text_size'))

        # 结果标签
        self.result_label = Label(
            text=self.display_text,
            font_size="38sp",
            halign="right",
            valign="bottom",
            color=[0.1, 0.1, 0.15, 1],
            bold=True,
            shorten=True,
            size_hint_y=0.6
        )
        self.result_label.bind(size=self.result_label.setter('text_size'))

        display_box.add_widget(self.expr_label)
        display_box.add_widget(self.result_label)
        self.add_widget(display_box)

        # 按钮区域
        buttons_grid = GridLayout(
            cols=5,
            spacing=3,
            size_hint_y=0.78
        )

        # 定义按钮数据：(文本, 回调, 样式类)
        buttons = [
            # 第一行 - 模式切换
            ("DEG", self.toggle_mode, "mode"),
            ("π", lambda: self.add_text("π"), "func"),
            ("e", lambda: self.add_text("e"), "func"),
            ("C", self.clear, "clear"),
            ("⌫", self.backspace, "clear"),

            # 第二行 - 三角函数
            ("sin", lambda: self.add_text("sin("), "func"),
            ("cos", lambda: self.add_text("cos("), "func"),
            ("tan", lambda: self.add_text("tan("), "func"),
            ("(", lambda: self.add_text("("), "func"),
            (")", lambda: self.add_text(")"), "func"),

            # 第三行 - 反三角函数
            ("sin⁻¹", lambda: self.add_text("asin("), "func"),
            ("cos⁻¹", lambda: self.add_text("acos("), "func"),
            ("tan⁻¹", lambda: self.add_text("atan("), "func"),
            ("cot⁻¹", lambda: self.add_text("acot("), "func"),
            ("√", lambda: self.add_text("√("), "func"),

            # 第四行 - 对数和幂
            ("log", lambda: self.add_text("log("), "func"),
            ("ln", lambda: self.add_text("ln("), "func"),
            ("x²", lambda: self.add_text("²"), "func"),
            ("xʸ", lambda: self.add_text("^"), "func"),
            ("n!", lambda: self.add_text("!"), "func"),

            # 第五行 - 运算
            ("1/x", self.reciprocal, "func"),
            ("%", lambda: self.add_text("%"), "func"),
            ("÷", lambda: self.add_text("÷"), "op"),
            ("×", lambda: self.add_text("×"), "op"),
            ("±", self.negate, "func"),

            # 第六行 - 数字 7-9
            ("7", lambda: self.add_text("7"), "num"),
            ("8", lambda: self.add_text("8"), "num"),
            ("9", lambda: self.add_text("9"), "num"),
            ("+", lambda: self.add_text("+"), "op"),
            ("−", lambda: self.add_text("-"), "op"),

            # 第七行 - 数字 4-6
            ("4", lambda: self.add_text("4"), "num"),
            ("5", lambda: self.add_text("5"), "num"),
            ("6", lambda: self.add_text("6"), "num"),
            (".", lambda: self.add_text("."), "num"),
            ("=", self.calculate, "eq"),

            # 第八行 - 数字 1-3 和 0
            ("1", lambda: self.add_text("1"), "num"),
            ("2", lambda: self.add_text("2"), "num"),
            ("3", lambda: self.add_text("3"), "num"),
            ("0", lambda: self.add_text("0"), "num"),
            ("0", lambda: self.add_text("0"), "num"),  # 占位
        ]

        for text, callback, style in buttons:
            btn = self._create_button(text, callback, style)
            if text == "DEG":
                btn.state = "down" if self.deg_mode else "normal"
            buttons_grid.add_widget(btn)

        self.add_widget(buttons_grid)

    def _update_bg(self, instance, value):
        """更新显示区域背景"""
        self.display_bg.pos = instance.pos
        self.display_bg.size = instance.size

    def _create_button(self, text, callback, style):
        """创建按钮"""
        btn = Button(
            text=text,
            font_size=self._get_font_size(text, style),
            bold=True,
            background_normal="",
            background_color=[1, 1, 1, 1]
        )

        if style == "num":
            btn.background_color = [0.94, 0.94, 0.96, 1]
            btn.color = [0.15, 0.15, 0.2, 1]
        elif style == "op":
            btn.background_color = [0.88, 0.88, 0.9, 1]
            btn.color = [0.15, 0.15, 0.2, 1]
        elif style == "func":
            btn.background_color = [0.82, 0.85, 0.9, 1]
            btn.color = [0.15, 0.15, 0.2, 1]
        elif style == "clear":
            btn.background_color = [0.92, 0.65, 0.6, 1]
            btn.color = [1, 1, 1, 1]
        elif style == "eq":
            btn.background_color = [0.18, 0.55, 0.88, 1]
            btn.color = [1, 1, 1, 1]
        elif style == "mode":
            btn.background_color = [0.75, 0.8, 0.85, 1]
            btn.color = [0.25, 0.25, 0.25, 1]
            btn.font_size = "13sp"

        btn.bind(on_press=lambda x: callback())

        if text == "DEG":
            self.deg_button = btn

        return btn

    def _get_font_size(self, text, style):
        """获取字体大小"""
        if style == "func" or style == "clear":
            return "14sp"
        elif style == "mode":
            return "13sp"
        else:
            return "18sp"

    # ── 输入处理 ─────────────────────────────────────────

    def add_text(self, text: str):
        """向表达式中追加文本"""
        if self._last_was_result:
            if text.isdigit() or text in ("(", "sin(", "cos(", "tan(",
                                          "asin(", "acos(", "atan(", "acot(",
                                          "log(", "ln(", "√(", "π", "e"):
                self.expression = ""
            self._last_was_result = False

        ops = ("+", "-", "×", "÷", "^")
        if text in ops and self.expression and self.expression[-1] in ops:
            self.expression = self.expression[:-1] + text
        elif text == ".":
            m = re.search(r"(\d+\.?\d*)$", self.expression)
            if m and "." in m.group(1):
                return
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
        self._refresh_display()

    def backspace(self):
        """删除最后一个字符"""
        if self._last_was_result:
            self.clear()
            return
        if not self.expression:
            return

        for token in ("asin(", "acos(", "atan(", "acot(",
                      "sin(", "cos(", "tan(", "log(", "ln(", "√("):
            if self.expression.endswith(token):
                self.expression = self.expression[:-len(token)]
                break
        else:
            self.expression = self.expression[:-1]

        self._refresh_display()

    def toggle_mode(self):
        """切换 DEG / RAD"""
        self.deg_mode = not self.deg_mode
        if hasattr(self, 'deg_button'):
            self.deg_button.text = "DEG" if self.deg_mode else "RAD"
            self.deg_button.state = "down" if self.deg_mode else "normal"

    def negate(self):
        """± 按钮：取反当前数值"""
        if not self.expression or self._last_was_result:
            self.expression = "-"
            self._last_was_result = False
            self._refresh_display()
            return

        m = re.search(r"(-?\d+\.?\d*)$", self.expression)
        if m:
            num = m.group(1)
            if num.startswith("-"):
                new_num = num[1:]
            else:
                new_num = f"(-{num})" if self.expression[:m.start()] else f"-{num}"
            self.expression = self.expression[:m.start()] + new_num
        else:
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
                self._refresh_display()
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
            self._refresh_display()
        except OverflowError:
            self.display_text = "Error: 数值溢出"
            self.expression = ""
            self.expression_display = ""
            self._refresh_display()
        except Exception as e:
            print(f"Error: {e}")
            self._show_error()

    # ── 内部方法 ─────────────────────────────────────────

    def _refresh_display(self):
        """刷新显示"""
        self.display_text = self.expression if self.expression else "0"
        self.expression_display = self.expression if self.expression else ""
        self.expr_label.text = self.expression_display
        self.result_label.text = self.display_text

    def _set_result(self, value):
        """将计算结果设为当前值"""
        formatted = self._format_number(value)
        self.expression_display = self.expression + " ="
        self.expression = formatted
        self.display_text = formatted
        self._last_was_result = True
        self.expr_label.text = self.expression_display
        self.result_label.text = self.display_text

    def _show_error(self):
        self.display_text = "Error"
        self.expression = ""
        self.expression_display = ""
        self.expr_label.text = ""
        self.result_label.text = "Error"

    def _evaluate(self) -> float:
        """将显示表达式转换为 Python 表达式并求值"""
        expr = self.expression

        # ── 常数 ──
        expr = expr.replace("π", str(math.pi))
        expr = expr.replace("e", str(math.e))

        # ── 运算符 ──
        expr = expr.replace("×", "*")
        expr = expr.replace("÷", "/")
        expr = expr.replace("^", "**")
        expr = expr.replace("²", "**2")

        # ── 先处理反三角函数（使用特殊标记） ──
        # 使用占位符避免与三角函数冲突
        expr = expr.replace("asin(", "¶ASIN(")
        expr = expr.replace("acos(", "¶ACOS(")
        expr = expr.replace("atan(", "¶ATAN(")
        expr = expr.replace("acot(", "¶ACOT(")

        # ── 处理三角函数 ──
        expr = expr.replace("sin(", "math.sin(")
        expr = expr.replace("cos(", "math.cos(")
        expr = expr.replace("tan(", "math.tan(")

        # ── 处理反三角函数（恢复并转换） ──
        expr = expr.replace("¶ASIN(", "math.asin(")
        expr = expr.replace("¶ACOS(", "math.acos(")
        expr = expr.replace("¶ATAN(", "math.atan(")
        expr = expr.replace("¶ACOT(", "self._acot(")

        # ── 对数 ──
        expr = expr.replace("log(", "math.log10(")
        expr = expr.replace("ln(", "math.log(")

        # ── 根号 ──
        expr = expr.replace("√(", "math.sqrt(")

        # ── 阶乘 ──
        expr = re.sub(r"(\d+)!", r"math.factorial(\1)", expr)

        # ── 百分号 ──
        expr = re.sub(r"(\d+\.?\d*)%", r"(\1/100)", expr)

        # ── DEG/RAD 模式处理 ──
        if self.deg_mode:
            # 对三角函数：将角度转为弧度
            expr = self._wrap_trig_degrees(expr)
            # 对反三角函数：将结果弧度转为角度
            expr = self._wrap_inverse_trig_degrees(expr)

        # ── 安全求值 ──
        safe_globals = {
            "__builtins__": {},
            "math": math,
            "self": self,
        }

        try:
            result = eval(expr, safe_globals, {})
            return result
        except Exception as e:
            print(f"Evaluation error: {e}")
            print(f"Expression: {expr}")
            raise

    def _acot(self, x):
        """反余切函数"""
        if x == 0:
            return math.pi / 2
        return math.atan(1 / x)

    def _wrap_trig_degrees(self, expr: str) -> str:
        """将 math.sin/cos/tan(arg) 包裹为 math.sin(math.radians(arg))"""
        result = []
        i = 0
        trig_funcs = ["math.sin(", "math.cos(", "math.tan("]

        while i < len(expr):
            matched = False
            for func in trig_funcs:
                if expr[i:].startswith(func):
                    # 找到函数调用的结束位置
                    start = i + len(func)
                    depth = 1
                    j = start
                    while j < len(expr) and depth > 0:
                        if expr[j] == "(":
                            depth += 1
                        elif expr[j] == ")":
                            depth -= 1
                        j += 1

                    # 提取参数
                    arg = expr[start:j - 1]
                    # 构建新的表达式: math.sin(math.radians(arg))
                    result.append(func)
                    result.append("math.radians(")
                    result.append(arg)
                    result.append(")")
                    # 添加原来的右括号
                    result.append(")")
                    i = j
                    matched = True
                    break

            if not matched:
                result.append(expr[i])
                i += 1

        return "".join(result)

    def _wrap_inverse_trig_degrees(self, expr: str) -> str:
        """将 math.asin/acos/atan/self._acot(arg) 包裹为 math.degrees()"""
        result = []
        i = 0
        inv_funcs = [
            ("math.asin(", "math.asin"),
            ("math.acos(", "math.acos"),
            ("math.atan(", "math.atan"),
            ("self._acot(", "self._acot")
        ]

        while i < len(expr):
            matched = False
            for func_prefix, func_name in inv_funcs:
                if expr[i:].startswith(func_prefix):
                    # 找到函数调用的结束位置
                    start = i + len(func_prefix)
                    depth = 1
                    j = start
                    while j < len(expr) and depth > 0:
                        if expr[j] == "(":
                            depth += 1
                        elif expr[j] == ")":
                            depth -= 1
                        j += 1

                    # 提取参数
                    arg = expr[start:j - 1]
                    # 构建新的表达式: math.degrees(math.asin(arg))
                    result.append("math.degrees(")
                    result.append(func_prefix)
                    result.append(arg)
                    result.append(")")
                    # 关闭 math.degrees
                    result.append(")")
                    i = j
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
                if num == int(num) and abs(num) < 1e15:
                    return str(int(num))
            formatted = f"{num:.12g}"
            if len(formatted) > 16:
                formatted = f"{num:.8e}"
            return formatted
        return str(num)


class CalculatorApp(App):
    """科学计算器应用"""

    def build(self):
        self.title = "科学计算器"
        from kivy.utils import platform
        if platform != "android":
            Window.size = (420, 750)
            Window.minimum_width = 380
            Window.minimum_height = 650
        return CalculatorWidget()


if __name__ == "__main__":
    CalculatorApp().run()