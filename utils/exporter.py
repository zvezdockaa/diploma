import pandas as pd

#экспорт подсчитанных данных в файл эксель
class DataExporter:
    def export(self, data):
        try:
            df = pd.DataFrame(data)
            df.to_excel("exported_data.xlsx", index=False)
        except Exception as e:
            print(f"[Exporter] Ошибка экспорта: {e}")
