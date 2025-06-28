import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import tkinter as tk
import tkinter.filedialog as filedialog

# окно для построения графиков на основе добавленных данных
class GraphBuilder(ctk.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.title("Построение графика")
        self.geometry("600x400")
        self.controller = controller
        self.selected_mode = tk.StringVar(value="by_years")  # режим отображения графика
        self.attributes("-topmost", True)
        self.focus_force()
        self.grab_set()

        self.build_ui()

    # инициализация всех элементов интерфейса
    def build_ui(self):
        # выбор режима построения графика
        mode_label = ctk.CTkLabel(self, text="Выберите режим сравнения:")
        mode_label.pack(pady=10)

        mode_frame = ctk.CTkFrame(self)
        mode_frame.pack(pady=5)

        ctk.CTkRadioButton(mode_frame, text="Показатели одной страны за годы",
                           variable=self.selected_mode, value="by_years",
                           command=self.update_ui).pack(anchor="w", padx=20)

        ctk.CTkRadioButton(mode_frame, text="Один показатель для разных стран",
                           variable=self.selected_mode, value="by_countries",
                           command=self.update_ui).pack(anchor="w", padx=20)

        # блок выбора страны, года и показателя
        self.selection_frame = ctk.CTkFrame(self)
        self.selection_frame.pack(pady=10, fill="x")
        self.update_ui()

        # кнопка построения графика
        self.plot_button = ctk.CTkButton(self, text="Построить график", command=self.plot_graph)
        self.plot_button.pack(pady=10)

    # обновление интерфейса в зависимости от выбранного режима
    def update_ui(self):
        for widget in self.selection_frame.winfo_children():
            widget.destroy()

        if self.selected_mode.get() == "by_years":
            # пользователь выбирает одну страну и один показатель
            self.country_box = ctk.CTkComboBox(self.selection_frame,
                                               values=self.controller.get_added_country_names())
            self.country_box.pack(pady=5)

            self.indicator_box = ctk.CTkComboBox(self.selection_frame,
                                                 values=self.controller.get_available_indicators())
            self.indicator_box.pack(pady=5)

        elif self.selected_mode.get() == "by_countries":
            # пользователь выбирает один год и один показатель
            self.indicator_box = ctk.CTkComboBox(self.selection_frame,
                                                 values=self.controller.get_available_indicators())
            self.indicator_box.pack(pady=5)

            self.year_entry = ctk.CTkEntry(self.selection_frame, placeholder_text="Год (например, 2021)")
            self.year_entry.pack(pady=5)

    # построение графика в зависимости от режима
    def plot_graph(self):
        mode = self.selected_mode.get()
        fig, ax = plt.subplots()

        if mode == "by_years":
            # график один показатель для одной страны за годы
            country = self.country_box.get()
            indicator = self.indicator_box.get()
            data = self.controller.get_country_data_by_year(country, indicator)

            if not data:
                ctk.CTkMessagebox(title="Ошибка", message="Недостаточно данных.")
                return

            years = sorted(data.keys())
            values = [data[year] for year in years]
            ax.plot(years, values, marker='o')
            ax.set_title(f"{indicator} — {country}")
            ax.set_xlabel("Год")
            ax.set_ylabel(indicator)

        elif mode == "by_countries":
            # график один показатель для всех стран за конкретный год
            indicator = self.indicator_box.get()
            try:
                year = int(self.year_entry.get())
            except ValueError:
                ctk.CTkMessagebox(title="Ошибка", message="Введите корректный год.")
                return

            data = {}
            for row in self.controller.country_data:
                row_year = row.get("Год")
                if (str(row_year) == str(year)) and indicator in row:
                    try:
                        value = float(row[indicator])
                        data[row["Страна"]] = value
                    except (ValueError, TypeError):
                        continue

            if not data:
                ctk.CTkMessagebox(title="Нет данных", message=f"Нет данных за {year} год.")
                return

            countries = list(data.keys())
            values = list(data.values())
            ax.bar(countries, values)
            ax.set_title(f"{indicator} по странам ({year})")
            ax.set_xlabel("Страна")
            ax.set_ylabel(indicator)

        # отображение графика в новом окне
        graph_window = ctk.CTkToplevel()
        graph_window.title("График")
        graph_window.geometry("800x600")
        graph_window.attributes("-topmost", True)

        canvas = FigureCanvasTkAgg(fig, master=graph_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # кнопка сохранения графика в картинку
        def save_graph():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                title="Сохранить график как PNG"
            )
            if file_path:
                fig.savefig(file_path)

        save_button = ctk.CTkButton(graph_window, text="Сохранить как PNG", command=save_graph)
        save_button.pack(pady=10)