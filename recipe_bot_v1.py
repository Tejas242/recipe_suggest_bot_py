import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea
from PyQt5.QtGui import QPixmap, QImage, QFont
import requests
from PIL import Image
from io import BytesIO

class RecipeSuggestionBot(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Recipe Suggestion Bot')
        self.setGeometry(100, 100, 600, 500)

        self.search_label = QLabel('Enter Ingredient:')
        self.entry_search = QLineEdit()
        self.search_button = QPushButton('Get Recipe')
        self.result_label = QLabel()
        self.image_label = QLabel()

        # Scroll area for the result label
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.result_label)

        # Layouts
        main_layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        result_layout = QVBoxLayout()

        input_layout.addWidget(self.search_label)
        input_layout.addWidget(self.entry_search)
        input_layout.addWidget(self.search_button)

        result_layout.addWidget(self.scroll_area)
        result_layout.addWidget(self.image_label)

        main_layout.addLayout(input_layout)
        main_layout.addLayout(result_layout)

        self.setLayout(main_layout)

        self.search_button.clicked.connect(self.get_recipe)

    def get_recipe(self):
        ingredient = self.entry_search.text()

        if ingredient:
            endpoint = f'https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}'
    
            try:
                response = requests.get(endpoint)
                response.raise_for_status()
                data = response.json()

                if 'meals' in data and data['meals']:
                    meal = data['meals'][0]
                    meal_id = meal.get('idMeal', '')
                    self.display_recipe_details(meal_id)
                else:
                    self.result_label.setText('No recipe found. Try another ingredient!')

            except requests.exceptions.RequestException as e:
                self.result_label.setText(f'Error: {e}')

    def display_recipe_details(self, meal_id):
        if not meal_id:
            return

        endpoint = f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}'
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()

            if 'meals' in data and data['meals']:
                meal = data['meals'][0]
                self.display_recipe(meal)
            else:
                self.result_label.setText('No details found for this recipe.')

        except requests.exceptions.RequestException as e:
            self.result_label.setText(f'Error: {e}')

    def display_recipe(self, meal):
        meal_title = meal.get('strMeal', 'No Title')
        meal_instructions = meal.get('strInstructions', 'No Instructions')

        self.result_label.setText(f'<font size="5">{meal_title}</font><br><br><b>Instructions:</b><br>{meal_instructions}')
        self.result_label.setWordWrap(True)

        self.display_image_from_url(meal.get('strMealThumb', ''))

    def display_image_from_url(self, url):
        try:
            response = requests.get(url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((300, 300), Image.LANCZOS)
            qt_img = QImage(img.tobytes(), img.width, img.height, img.width * 3, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_img)

            self.image_label.setPixmap(pixmap)

        except requests.exceptions.RequestException as e:
            self.result_label.setText(f'Error loading image: {e}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RecipeSuggestionBot()
    window.show()
    sys.exit(app.exec_())
