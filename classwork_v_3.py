import sys
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt
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
        self.is_dark_theme = False
        self.init_ui()

    def init_ui(self) -> None:
        self.setWindowTitle("Записная книжка")
        self.resize(550, 650)

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)

        top_layout = QHBoxLayout()
        title_label = QLabel("Контакты")
        title_label.setObjectName("mainTitle")

        self.theme_button = QPushButton("Темная тема")
        self.theme_button.setObjectName("themeButton")
        self.theme_button.clicked.connect(self._toggle_theme)

        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(self.theme_button)
        main_layout.addLayout(top_layout)

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

        # Скрываем вертикальную нумерацию строк, чтобы убрать белую полосу слева
        self.table.verticalHeader().setVisible(False)

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

        self.hint_label = QLabel(
            "Подсказка: Кликните на контакт, чтобы подготовить его к удалению. Двойной клик заполнит поля для изменения.")
        self.hint_label.setWordWrap(True)
        self.hint_label.setObjectName("hintLabel")
        main_layout.addWidget(self.hint_label)

        self.setCentralWidget(main_widget)
        self._update_table()
        self._apply_theme()

    def _apply_theme(self) -> None:
        if self.is_dark_theme:
            self.theme_button.setText("Светлая тема")
            self.setStyleSheet("""
                QMainWindow { 
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                                      stop:0 #1a1c29, stop:1 #282c42); 
                }

                QLabel#mainTitle { color: #ffffff; font-size: 18px; font-weight: bold; background: transparent; }
                QLabel#hintLabel { color: #a0a5b5; font-size: 12px; line-height: 1.4; background: transparent; }

                QLineEdit { 
                    padding: 9px 12px; 
                    border: 1px solid rgba(255, 255, 255, 0.1); 
                    border-radius: 8px; 
                    background: rgba(255, 255, 255, 0.08); 
                    color: #ffffff; 
                }
                QLineEdit:focus { 
                    border: 1px solid #79bbff; 
                    background: rgba(255, 255, 255, 0.15); 
                }

                QPushButton { 
                    padding: 9px 16px; 
                    background-color: #007aff; 
                    color: white; 
                    border: none; 
                    border-radius: 8px; 
                    font-weight: bold; 
                }
                QPushButton:hover { background-color: #3395ff; }
                QPushButton:pressed { background-color: #0062cc; }
                QPushButton:disabled { background-color: rgba(0, 122, 255, 0.2); color: rgba(255, 255, 255, 0.4); }

                QPushButton#themeButton {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: #ffffff;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
                QPushButton#themeButton:hover { background-color: rgba(255, 255, 255, 0.2); }

                QPushButton#secondaryButton { 
                    background-color: rgba(255, 255, 255, 0.05); 
                    color: #79bbff; 
                    border: 1px solid rgba(121, 187, 255, 0.3); 
                }
                QPushButton#secondaryButton:hover { 
                    background-color: rgba(255, 255, 255, 0.1); 
                    border-color: #79bbff; 
                }

                QPushButton#deleteButton { background-color: #ff4d4f; }
                QPushButton#deleteButton:hover { background-color: #ff7875; }
                QPushButton#deleteButton:pressed { background-color: #d9363e; }
                QPushButton#deleteButton:disabled { background-color: rgba(255, 77, 79, 0.2); color: rgba(255, 255, 255, 0.3); }

                /* Фикс пустого пространства: красим и саму таблицу, и её внутреннюю область viewport */
                QTableWidget, QTableWidget QWidget { 
                    background-color: #1e2130; 
                }
                QTableWidget {
                    border: 1px solid rgba(255, 255, 255, 0.05); 
                    border-radius: 8px; 
                    gridline-color: rgba(255, 255, 255, 0.05); 
                }
                QTableWidget::item { padding: 8px; color: #e1e4ea; background-color: transparent; }
                QTableWidget::item:selected { background-color: rgba(0, 122, 255, 0.3); color: #ffffff; font-weight: bold; }

                QHeaderView::section { 
                    background-color: #212431; 
                    padding: 8px; 
                    border: none; 
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1); 
                    color: #a0a5b5; 
                    font-weight: bold; 
                }
            """)
        else:
            self.theme_button.setText("Темная тема")
            self.setStyleSheet("""
                QMainWindow { 
                    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                                      stop:0 #a1c4fd, stop:1 #c2e9fb); 
                }

                QLabel#mainTitle { color: #2c3e50; font-size: 18px; font-weight: bold; background: transparent; }
                QLabel#hintLabel { color: #7f8c8d; font-size: 12px; line-height: 1.4; background: transparent; }

                QLineEdit { 
                    padding: 9px 12px; 
                    border: 1px solid rgba(255, 255, 255, 0.4); 
                    border-radius: 8px; 
                    background: rgba(255, 255, 255, 0.85); 
                    color: #2c3e50; 
                }
                QLineEdit:focus { 
                    border: 1px solid #4a90e2; 
                    background: #ffffff; 
                }

                QPushButton { 
                    padding: 9px 16px; 
                    background-color: #4a90e2; 
                    color: white; 
                    border: none; 
                    border-radius: 8px; 
                    font-weight: bold; 
                }
                QPushButton:hover { background-color: #357abd; }
                QPushButton:pressed { background-color: #2a5a8f; }
                QPushButton:disabled { background-color: rgba(74, 144, 226, 0.4); color: rgba(255, 255, 255, 0.6); }

                QPushButton#themeButton {
                    background-color: rgba(255, 255, 255, 0.4);
                    color: #2a5a8f;
                    border: 1px solid rgba(74, 144, 226, 0.3);
                }
                QPushButton#themeButton:hover { background-color: rgba(255, 255, 255, 0.6); }

                QPushButton#secondaryButton { 
                    background-color: rgba(255, 255, 255, 0.6); 
                    color: #4a90e2; 
                    border: 1px solid rgba(74, 144, 226, 0.4); 
                }
                QPushButton#secondaryButton:hover { 
                    background-color: rgba(255, 255, 255, 0.9); 
                    border-color: #4a90e2; 
                }

                QPushButton#deleteButton { background-color: #ff5a5f; }
                QPushButton#deleteButton:hover { background-color: #e0484c; }
                QPushButton#deleteButton:pressed { background-color: #c0393b; }
                QPushButton#deleteButton:disabled { background-color: rgba(255, 90, 95, 0.4); color: rgba(255, 255, 255, 0.6); }

                QTableWidget, QTableWidget QWidget { 
                    background-color: rgba(255, 255, 255, 0.85); 
                }
                QTableWidget { 
                    border: 1px solid rgba(255, 255, 255, 0.3); 
                    border-radius: 8px; 
                    gridline-color: rgba(240, 240, 240, 0.5); 
                }
                QTableWidget::item { padding: 8px; color: #2c3e50; background-color: transparent; }
                QTableWidget::item:selected { background-color: rgba(74, 144, 226, 0.15); color: #2a5a8f; font-weight: bold; }

                QHeaderView::section { 
                    background-color: rgba(245, 247, 250, 0.9); 
                    padding: 8px; 
                    border: none; 
                    border-bottom: 1px solid rgba(228, 231, 237, 0.7); 
                    color: #7f8c8d; 
                    font-weight: bold; 
                }
            """)

    def _toggle_theme(self) -> None:
        self.is_dark_theme = not self.is_dark_theme
        self._apply_theme()

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

    service = ContactService()
    service.add_contact("Алексей", "+7 (999) 111-22-33")
    service.add_contact("Мария", "+7 (999) 444-55-66")

    window = ContactWindow(service)
    window.show()
    sys.exit(app.exec())