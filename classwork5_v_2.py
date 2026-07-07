import sys
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QLabel
)
from PyQt6.QtGui import QFont


class ContactService:

    def __init__(self) -> None:
        self._contacts: Dict[str, str] = {}

    def add_contact(self, name: str, phone: str) -> None:
        self._contacts[name] = phone

    def get_all_contacts(self) -> Dict[str, str]:
        return self._contacts.copy()

    def find_contact(self, name: str) -> Optional[str]:
        return self._contacts.get(name)

    def find_by_phone(self, phone: str) -> Optional[str]:
        for name, p in self._contacts.items():
            if p == phone:
                return name
        return None

    def delete_contact(self, name: str) -> bool:
        if name in self._contacts:
            del self._contacts[name]
            return True
        return False


class ContactWindow(QMainWindow):

    def __init__(self, service: ContactService) -> None:
        super().__init__()
        self.service = service
        self.init_ui()

    def init_ui(self) -> None:
        self.setWindowTitle("Записная книжка")
        self.resize(550, 650)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        form_layout = QHBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя...")

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Телефон...")

        form_layout.addWidget(self.name_input, stretch=2)
        form_layout.addWidget(self.phone_input, stretch=2)

        main_layout.addLayout(form_layout)

        buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Сохранить")
        self.add_button.clicked.connect(self._handle_add_or_update)

        self.clear_button = QPushButton("Очистить поля")
        self.clear_button.setObjectName("secondaryButton")
        self.clear_button.clicked.connect(self._handle_clear_fields)

        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.clear_button)

        main_layout.addLayout(buttons_layout)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по имени или номеру телефона...")
        self.search_input.textChanged.connect(self._handle_search)
        main_layout.addWidget(self.search_input)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Имя", "Номер телефона"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.table.itemClicked.connect(self._handle_table_click)
        self.table.itemDoubleClicked.connect(self._handle_table_double_click)
        self.table.selectionModel().selectionChanged.connect(self._update_delete_button_state)

        main_layout.addWidget(self.table)

        actions_layout = QHBoxLayout()
        self.delete_button = QPushButton("Удалить выбранный контакт")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self._handle_delete)
        actions_layout.addWidget(self.delete_button)

        main_layout.addLayout(actions_layout)

        hint_label = QLabel(
            "Подсказка: Кликните на контакт, чтобы подготовить его к удалению. Двойной клик заполнит поля для изменения.")
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet("color: #8e8e93; font-size: 12px; line-height: 1.4;")
        main_layout.addWidget(hint_label)

        self.setCentralWidget(main_widget)
        self._update_table()

    def _update_table(self, filter_text: str = "") -> None:
        self.table.setRowCount(0)
        contacts = self.service.get_all_contacts()
        sorted_names = sorted(contacts.keys())

        for name in sorted_names:
            phone = contacts[name]

            if filter_text:
                text_lower = filter_text.lower()
                if text_lower not in name.lower() and text_lower not in phone.lower():
                    continue

            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            self.table.setItem(row_position, 0, QTableWidgetItem(name))
            self.table.setItem(row_position, 1, QTableWidgetItem(phone))

    def _handle_add_or_update(self) -> None:
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()

        if not name or not phone:
            QMessageBox.warning(self, "Пустые поля", "Чтобы сохранить контакт, заполните имя и номер телефона.")
            return

        existing_phone = self.service.find_contact(name)
        if existing_phone:
            if existing_phone == phone:
                QMessageBox.information(self, "Уже сохранено",
                                        f"Контакт '{name}' с этим номером телефона уже есть в списке.")
                return

            confirm = QMessageBox.question(
                self,
                "Обновление контакта",
                f"Человек с именем '{name}' уже записан с номером {existing_phone}.\n\nВы хотите обновить его телефон на {phone}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm == QMessageBox.StandardButton.No:
                return
        else:
            existing_name_by_phone = self.service.find_by_phone(phone)
            if existing_name_by_phone:
                confirm = QMessageBox.question(
                    self,
                    "Дубликат номера",
                    f"Этот номер телефона уже записан на имя '{existing_name_by_phone}'.\n\nВы уверены, что хотите добавить его еще и для '{name}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if confirm == QMessageBox.StandardButton.No:
                    return

        self.service.add_contact(name, phone)
        self._update_table()
        self._handle_clear_fields()

    def _handle_search(self) -> None:
        search_text = self.search_input.text().strip()
        self._update_table(filter_text=search_text)

    def _handle_table_click(self, item: QTableWidgetItem) -> None:
        self.table.selectRow(item.row())

    def _handle_table_double_click(self, item: QTableWidgetItem) -> None:
        row = item.row()
        name = self.table.item(row, 0).text()
        phone = self.table.item(row, 1).text()

        self.name_input.setText(name)
        self.phone_input.setText(phone)
        self.phone_input.setFocus()

    def _handle_clear_fields(self) -> None:
        self.name_input.clear()
        self.phone_input.clear()
        self.search_input.clear()
        self.table.clearSelection()
        self.name_input.setFocus()

    def _update_delete_button_state(self) -> None:
        self.delete_button.setEnabled(len(self.table.selectedRanges()) > 0)

    def _handle_delete(self) -> None:
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return

        row = selected_ranges[0].topRow()
        name = self.table.item(row, 0).text()
        phone = self.table.item(row, 1).text()

        confirm = QMessageBox.question(
            self,
            "Удаление контакта",
            f"Вы уверены, что хотите навсегда удалить '{name}' ({phone})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.service.delete_contact(name)
            self._update_table()
            self._handle_clear_fields()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    app.setStyleSheet("""
        QMainWindow { background-color: #f8f9fa; }
        QLineEdit { padding: 8px 12px; border: 1px solid #dcdfe6; border-radius: 6px; background: white; color: #303133; }
        QLineEdit:focus { border: 1px solid #409eff; }

        QPushButton { padding: 8px 16px; background-color: #409eff; color: white; border: none; border-radius: 6px; font-weight: bold; }
        QPushButton:hover { background-color: #66b1ff; }
        QPushButton:pressed { background-color: #3a8ee6; }
        QPushButton:disabled { background-color: #c0c4cc; color: #ffffff; }

        QPushButton#secondaryButton { background-color: #ffffff; color: #606266; border: 1px solid #dcdfe6; }
        QPushButton#secondaryButton:hover { background-color: #ecf5ff; color: #409eff; border-color: #c6e2ff; }

        QPushButton#deleteButton { background-color: #f56c6c; }
        QPushButton#deleteButton:hover { background-color: #f78989; }
        QPushButton#deleteButton:pressed { background-color: #dd6161; }
        QPushButton#deleteButton:disabled { background-color: #fab6b6; }

        QTableWidget { background-color: white; border: 1px solid #e4e7ed; border-radius: 6px; gridline-color: #f2f6fc; }
        QTableWidget::item { padding: 6px; color: #303133; }
        QTableWidget::item:selected { background-color: #ecf5ff; color: #409eff; }
        QHeaderView::section { background-color: #f5f7fa; padding: 8px; border: none; border-bottom: 1px solid #e4e7ed; color: #909399; font-weight: bold; }
    """)

    service = ContactService()
    service.add_contact("Алексей", "+7 (999) 111-22-33")
    service.add_contact("Мария", "+7 (999) 444-55-66")

    window = ContactWindow(service)
    window.show()
    sys.exit(app.exec())