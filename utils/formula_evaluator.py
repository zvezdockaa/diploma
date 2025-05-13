class FormulaEvaluator:
    def evaluate(self, formula: str, data: dict) -> float:
        try:
            safe_data = {k.replace(" ", "_"): v for k, v in data.items()}
            code = compile(formula.replace(" ", "_"), "<string>", "eval")
            return round(eval(code, {"__builtins__": {}}, safe_data), 4)
        except Exception:
            return 0.0
