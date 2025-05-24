import re
import sympy
from sympy import sympify

# класс для проверки и вычисления пользовательских формул
class FormulaEvaluator:
    def __init__(self, allowed_variables=None):
        # сохраняем список допустимых переменных, заменяя пробелы на подчёркивания для совместимости с sympy
        self.allowed_variables = [v.replace(" ", "_") for v in allowed_variables] if allowed_variables else []

    # функция проверяет корректность формулы
    def validate(self, formula: str) -> tuple[bool, str]:
        # проверка на подряд идущие математические знаки
        cleaned = formula.replace(" ", "")
        if re.search(r'[\+\-\*/]{2,}', cleaned):
            return False, "Формула содержит два подряд идущих оператора. Проверьте знаки"

        # проверка на деление на ноль (в том числе в скобках)
        if re.search(r'/\s*\(?\s*0(\s*[\+\-\*/]\s*0)*\s*\)?', formula):
            return False, "Формула содержит деление на ноль"

        # попытка разобрать выражение через sympy
        try:
            safe_formula = formula.replace(" ", "_")
            expr = sympify(safe_formula)

            # проверка есть ли в формуле неизвестные переменные
            used_symbols = {str(s) for s in expr.free_symbols}
            unknown = used_symbols - set(self.allowed_variables)
            if unknown:
                readable = ", ".join(var.replace("_", " ") for var in unknown)
                return False, f"Формула содержит неизвестные показатели: {readable}"

            return True, ""

        except sympy.SympifyError:
            return False, "Формула содержит синтаксическую ошибку"
        except Exception as e:
            return False, f"Ошибка в формуле: {str(e)}"

    # функция вычисляет значение формулы с подставленными значениями показателей
    def evaluate(self, formula: str, data: dict) -> float:
        try:
            # подставляем значения показателей с заменой пробелов
            safe_data = {k.replace(" ", "_"): v for k, v in data.items()}
            expr = sympify(formula.replace(" ", "_"))
            return round(float(expr.evalf(subs=safe_data)), 4)
        except Exception:
            return 0.0
