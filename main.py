from models.parser import Parser
from models.calculator import Calculator
from models.country_data_model import CountryDataModel
from controllers.app_controller import AppController
from views.main_view import MainView
from db import get_db_connection
from dict import country_codes
from utils.formula_evaluator import FormulaEvaluator
from utils.exporter import DataExporter

if __name__ == "__main__":
    parser = Parser()
    calculator = Calculator(parser)
    model = CountryDataModel(get_db_connection, parser, calculator)
    evaluator = FormulaEvaluator(model.metrics)
    exporter = DataExporter()

    #  интерфейс
    view = MainView(controller=None, available_countries=list(country_codes.keys()))
    controller = AppController(model, view, evaluator, exporter)
    view.controller = controller

    # основной цикл
    view.build_main_ui()
    view.mainloop()
