import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QVBoxLayout, QWidget, QStatusBar
from PyQt6.QtWidgets import QAbstractItemView
from PyQt6 import QtCore
import main
import addEditCoffeeForm_ui

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.ui = main.Ui_MainWindow()
        self.ui.setupUi(self)

        layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(layout)

        self.ui.label.setFixedHeight(40)
        self.ui.pushButton.setFixedHeight(40)
        self.ui.pushButton_2.setFixedHeight(40)

        layout.addWidget(self.ui.label)
        layout.addWidget(self.ui.tableWidget)
        layout.addWidget(self.ui.pushButton)
        layout.addWidget(self.ui.pushButton_2)
        self.setCentralWidget(container)

        self.ui.pushButton.clicked.connect(self.showData)
        self.ui.pushButton_2.clicked.connect(self.openAddEditForm)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def showData(self):
        try:
            conn = sqlite3.connect('data/coffee.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM grade")
            rows = cursor.fetchall()
            conn.close()
        except sqlite3.Error as e:
            self.statusBar.showMessage(f"Ошибка базы данных: {e}")
            return
        try:
            self.ui.tableWidget.setRowCount(len(rows))
            self.ui.tableWidget.setColumnCount(len(rows[0]))
            self.ui.tableWidget.setHorizontalHeaderLabels(['ID', 'Name', 'Roast', 'Format', 'Taste', 'Price'])

            for row_num, row in enumerate(rows):
                for col_num, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.ui.tableWidget.setItem(row_num, col_num, item)

            self.ui.tableWidget.resizeColumnsToContents()
            self.statusBar.showMessage(f"Нашлось {len(rows)} сортов кофе")
        except Exception as e:
            self.statusBar.showMessage(f"Ошибка отображения данных: {e}")

    def openAddEditForm(self):
        try:
            self.addEditWindow = AddEditCoffeeForm(self)
            self.addEditWindow.show()
        except Exception as e:
            print(f"Ошибка открытия окна добавления/редактирования: {e}")


class AddEditCoffeeForm(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.ui = addEditCoffeeForm_ui.Ui_MainWindow()
        self.ui.setupUi(self)

        layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(layout)

        self.ui.label.setFixedHeight(40)
        self.ui.pushButton_3.setFixedHeight(40)
        self.ui.addButton.setFixedHeight(40)

        layout.addWidget(self.ui.label)
        layout.addWidget(self.ui.tableWidget_2)
        layout.addWidget(self.ui.addButton)
        layout.addWidget(self.ui.pushButton_3)
        self.setCentralWidget(container)

        self.ui.tableWidget_2.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
        self.ui.tableWidget_2.itemChanged.connect(self.saveToDatabase)

        self.ui.addButton.clicked.connect(self.addRecord)
        self.ui.pushButton_3.clicked.connect(self.close)
        self.loadAddEditData()

    def loadAddEditData(self):
        try:
            conn = sqlite3.connect('data/coffee.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM grade")
            rows = cursor.fetchall()
            conn.close()
        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
            return

        try:
            self.ui.tableWidget_2.setRowCount(len(rows))
            self.ui.tableWidget_2.setColumnCount(len(rows[0]))
            self.ui.tableWidget_2.setHorizontalHeaderLabels(['ID', 'Name', 'Roast', 'Format', 'Taste', 'Price'])

            for row_num, row in enumerate(rows):
                for col_num, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.ui.tableWidget_2.setItem(row_num, col_num, item)
                    if col_num == 0:
                        item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            self.ui.tableWidget_2.resizeColumnsToContents()
        except Exception as e:
            print(f"Ошибка отображения данных: {e}")

    def addRecord(self):
        try:
            row = self.ui.tableWidget_2.rowCount()
            self.ui.tableWidget_2.insertRow(row)
            conn = sqlite3.connect('data/coffee.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(ID) FROM grade")
            max_id = cursor.fetchone()[0]
            if max_id is None:
                new_id = 1
            else:
                new_id = max_id + 1
            conn.close()

            item_id = QTableWidgetItem(str(new_id))
            item_id.setFlags(item_id.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
            self.ui.tableWidget_2.setItem(row, 0, item_id)

            item_name = QTableWidgetItem("new_name")
            self.ui.tableWidget_2.setItem(row, 1, item_name)

            item_roast = QTableWidgetItem("1")
            self.ui.tableWidget_2.setItem(row, 2, item_roast)

            item_format = QTableWidgetItem("0")
            self.ui.tableWidget_2.setItem(row, 3, item_format)

            item_taste = QTableWidgetItem("new_taste")
            self.ui.tableWidget_2.setItem(row, 4, item_taste)

            item_price = QTableWidgetItem("90.0")
            self.ui.tableWidget_2.setItem(row, 5, item_price)
            conn = sqlite3.connect('data/coffee.sqlite')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO grade (ID, name, roast, format, taste, price) VALUES (?, ?, ?, ?, ?, ?)",
                           (new_id, "new_name", 1, 0, "new_taste", 90.0))
            conn.commit()
            conn.close()

            self.parent.showData()

        except Exception as e:
            print(f"Ошибка добавления новой записи: {e}")
    def saveToDatabase(self, item):
        try:
            row = item.row()
            column = item.column()
            value = item.text()

            conn = sqlite3.connect('data/coffee.sqlite')
            cursor = conn.cursor()

            cursor.execute("SELECT ID FROM grade WHERE ID = ?", (self.ui.tableWidget_2.item(row, 0).text(),))
            id_row = cursor.fetchone()
            if id_row:
                id_value = id_row[0]
                if column == 1:
                    cursor.execute("UPDATE grade SET name = ? WHERE ID = ?", (value, id_value))
                elif column == 2:
                    cursor.execute("UPDATE grade SET roast = ? WHERE ID = ?", (value, id_value))
                elif column == 3:
                    cursor.execute("UPDATE grade SET format = ? WHERE ID = ?", (value, id_value))
                elif column == 4:
                    cursor.execute("UPDATE grade SET taste = ? WHERE ID = ?", (value, id_value))
                elif column == 5:
                    cursor.execute("UPDATE grade SET price = ? WHERE ID = ?", (value, id_value))
                conn.commit()
            conn.close()
            self.parent.showData()
        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.resize(800, 600)
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")