from typing import Dict, Optional


class ContactService:

    def __init__(self) -> None:
        self._contacts: Dict[str, str] = {}

    def add_contact(self, name: str, phone: str) -> None:
        self._contacts[name] = phone

    def get_all_contacts(self) -> Dict[str, str]:
        return self._contacts.copy()

    def find_contact(self, name: str) -> Optional[str]:
        return self._contacts.get(name)

    def update_contact(self, name: str, new_phone: str) -> bool:
        if name in self._contacts:
            self._contacts[name] = new_phone
            return True
        return False

    def delete_contact(self, name: str) -> bool:
        if name in self._contacts:
            del self._contacts[name]
            return True
        return False


class ConsoleInterface:

    def __init__(self, service: ContactService) -> None:
        self.service = service

    def run(self) -> None:
        print("Рад приветствовать вас в телефонном справочнике!")

        while True:
            print("\n" + "=" * 35)
            print("  Что мы сейчас сделаем?")
            print("=" * 35)
            print("1. Добавим новый контакт")
            print("2. Посмотрим весь список")
            print("3. Найдем кого-то по имени")
            print("4. Изменим номер телефона")
            print("5. Удалим контакт")
            print("6. Завершим работу")
            print("=" * 35)

            choice = input("\nВведите номер нужного действия: ").strip()

            if choice == "1":
                self._handle_add()
            elif choice == "2":
                self._handle_view_all()
            elif choice == "3":
                self._handle_search()
            elif choice == "4":
                self._handle_update()
            elif choice == "5":
                self._handle_delete()
            elif choice == "6":
                print("\nСпасибо за работу! Всего вам доброго и до свидания!")
                break
            else:
                print("\nКажется, такой цифры в меню нет. Попробуйте еще раз, пожалуйста.")

    def _handle_add(self) -> None:
        print("\n--- Добавление нового человека в базу ---")
        name = input("Как зовут этого человека? ").strip()
        if not name:
            print("Вы не ввели имя. Без имени сохранить контакт не получится.")
            return

        existing_phone = self.service.find_contact(name)
        if existing_phone:
            print(f"Человек с именем '{name}' уже есть в вашем списке с номером: {existing_phone}")
            confirm = input("Вы хотите заменить его старый номер на новый? (да/нет): ").strip().lower()
            if confirm not in ['да', 'д', 'yes', 'y']:
                print("Хорошо, оставляем все как было.")
                return

        phone = input(f"Введите номер телефона для '{name}': ").strip()
        if not phone:
            print("Номер телефона обязателен для заполнения.")
            return

        self.service.add_contact(name, phone)
        print(f"Готово! '{name}' теперь в вашем списке контактов.")

    def _handle_view_all(self) -> None:
        contacts = self.service.get_all_contacts()
        if not contacts:
            print("\nВаша записная книжка пока совсем пуста.")
            return

        print(f"\nУ вас сохранено контактов: {len(contacts)}")
        print("-" * 35)
        for name in sorted(contacts.keys()):
            print(f"Имя: {name:<15} | Телефон: {contacts[name]}")
        print("-" * 35)

    def _handle_search(self) -> None:
        print("\n--- Поиск по имени ---")
        name = input("Чье имя вы хотите найти? ").strip()
        if not name:
            print("Пожалуйста, введите имя для поиска в следующий раз.")
            return

        phone = self.service.find_contact(name)
        if phone:
            print(f"Да, такой человек есть: {name} -> {phone}")
        else:
            print(f"К сожалению, человека с именем '{name}' в вашей книжке не нашлось.")

    def _handle_update(self) -> None:
        print("\n--- Изменение номера ---")
        name = input("Чей номер телефона мы будем менять? ").strip()

        current_phone = self.service.find_contact(name)
        if current_phone is None:
            print(f"Не удалось найти контакт с именем '{name}'.")
            return

        print(f"Сейчас у '{name}' записан номер: {current_phone}")
        new_phone = input("Введите вместо него новый номер: ").strip()
        if not new_phone:
            print("Изменение отменено, так как новый номер не может быть пустым.")
            return

        if current_phone == new_phone:
            print("Этот номер точно такой же, как и старый. Ничего не изменилось.")
            return

        self.service.update_contact(name, new_phone)
        print(f"Все прошло успешно. Новый номер для '{name}': {new_phone}")

    def _handle_delete(self) -> None:
        print("\n--- Удаление из списка ---")
        name = input("Кого вы хотите удалить из контактов? ").strip()

        current_phone = self.service.find_contact(name)
        if not current_phone:
            print(f"Контакта '{name}' и так нет в вашей записной книжке.")
            return

        confirm = input(
            f"Вы точно уверены, что хотите навсегда удалить '{name}' ({current_phone})? (да/нет): ").strip().lower()
        if confirm in ['да', 'д', 'yes', 'y']:
            self.service.delete_contact(name)
            print(f"Запись о '{name}' успешно удалена.")
        else:
            print("Удаление отменено, карточка контакта не тронута.")


if __name__ == "__main__":
    contact_service = ContactService()
    app = ConsoleInterface(contact_service)
    app.run()