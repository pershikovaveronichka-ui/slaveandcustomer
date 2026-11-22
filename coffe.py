import json
import os

DATA_FILE = "coffee_shop.json"

DEFAULT_MENU = [
    {"id": 1, "name": "Эспрессо", "price": 150, "stock": 100},
    {"id": 2, "name": "Капучино", "price": 250, "stock": 80},
    {"id": 3, "name": "Латте", "price": 280, "stock": 60},
]


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Проверка структуры
            if isinstance(data, dict) and "menu" in data and "orders" in data:
                return data
            print("⚠️ Файл данных повреждён. Создаю новые данные.")
        except (json.JSONDecodeError, OSError) as e:
            print(f"⚠️ Не удалось загрузить данные: {e}. Создаю новые.")
    return {"menu": [dict(d) for d in DEFAULT_MENU], "orders": [], "next_order_id": 1}


def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"⚠️ Не удалось сохранить данные: {e}")


def show_menu(data):
    print("\n=== МЕНЮ ===")
    if not data["menu"]:
        print("Меню пусто.")
        return
    print(f"{'ID':<4}{'Название':<15}{'Цена':<10}{'Остаток':<10}")
    for drink in data["menu"]:
        print(f"{drink['id']:<4}{drink['name']:<15}{drink['price']:<10}{drink['stock']:<10}")
    print()


def find_drink(data, drink_id):
    for drink in data["menu"]:
        if drink["id"] == drink_id:
            return drink
    return None


def calculate_discount(total):
    if total >= 3000:
        return 10
    if total >= 1000:
        return 5
    return 0


def create_order(data):
    print("\n=== СОЗДАНИЕ ЗАКАЗА ===")
    show_menu(data)

    items = []
    total = 0

    while True:
        raw_id = input("Введите ID напитка (или '0' для завершения заказа): ").strip()
        if raw_id == "0":
            break

        try:
            drink_id = int(raw_id)
        except ValueError:
            print("❌ Некорректный ID. Введите целое число.")
            continue

        drink = find_drink(data, drink_id)
        if drink is None:
            print("❌ Напиток с таким ID не найден.")
            continue

        raw_qty = input(f"Количество '{drink['name']}': ").strip()
        try:
            qty = int(raw_qty)
        except ValueError:
            print("❌ Количество должно быть целым числом.")
            continue

        if qty <= 0:
            print("❌ Количество должно быть положительным целым числом.")
            continue

        if qty > drink["stock"]:
            print(f"❌ Недостаточно порций. Остаток: {drink['stock']}.")
            continue

       
        already = sum(i["qty"] for i in items if i["id"] == drink_id)
        if already + qty > drink["stock"]:
            print(f"❌ С учётом уже выбранного ( {already} ) недостаточно порций. Остаток: {drink['stock']}.")
            continue

        items.append({
            "id": drink_id,
            "name": drink["name"],
            "price": drink["price"],
            "qty": qty,
            "sum": drink["price"] * qty,
        })
        total += drink["price"] * qty
        print(f"✅ Добавлено: {drink['name']} x{qty} = {drink['price'] * qty} ₽")

    if not items:
        print("Заказ пуст. Отмена.")
        return

    discount = calculate_discount(total)
    final_total = int(round(total * (100 - discount) / 100))
    order_id = data["next_order_id"]
    data["next_order_id"] += 1

    order = {
        "id": order_id,
        "items": items,
        "total": total,
        "discount": discount,
        "final_total": final_total,
        "status": "Новый",
    }

    for item in items:
        drink = find_drink(data, item["id"])
        drink["stock"] -= item["qty"]

    data["orders"].append(order)
    save_data(data)

    print("\n--- ЗАКАЗ ОФОРМЛЕН ---")
    print(f"Номер заказа: {order_id}")
    for item in items:
        print(f"  {item['name']} x{item['qty']} = {item['sum']} ₽")
    print(f"Сумма: {total} ₽")
    print(f"Скидка: {discount}%")
    print(f"Итого к оплате: {final_total} ₽")
    print("Статус: Новый\n")


def show_orders(data):
    print("\n=== ВСЕ ЗАКАЗЫ ===")
    if not data["orders"]:
        print("Заказов пока нет.")
        return
    for order in data["orders"]:
        print(f"\nЗаказ №{order['id']} | Статус: {order['status']}")
        for item in order["items"]:
            print(f"  {item['name']} x{item['qty']} = {item['sum']} ₽")
        print(f"  Сумма: {order['total']} ₽ | Скидка: {order['discount']}% | Итого: {order['final_total']} ₽")
    print()


def change_status(data):
    print("\n=== ИЗМЕНЕНИЕ СТАТУСА ===")
    if not data["orders"]:
        print("Заказов нет.")
        return

    show_orders(data)

    raw_id = input("Введите номер заказа: ").strip()
    try:
        order_id = int(raw_id)
    except ValueError:
        print("❌ Некорректный номер заказа.")
        return

    order = next((o for o in data["orders"] if o["id"] == order_id), None)
    if order is None:
        print("❌ Заказ не найден.")
        return

    print(f"Текущий статус заказа №{order_id}: {order['status']}")
    print("Доступные статусы: 1 — Новый, 2 — Выполнен, 3 — Отменен")
    choice = input("Выберите новый статус: ").strip()

    status_map = {"1": "Новый", "2": "Выполнен", "3": "Отменен"}
    new_status = status_map.get(choice)
    if new_status is None:
        print("❌ Некорректный выбор.")
        return

    old_status = order["status"]
    if old_status == new_status:
        print("ℹ️ Статус не изменился.")
        return


    if old_status == "Отменен":
        print("❌ Отменённый заказ нельзя изменить.")
        return

    if new_status == "Отменен" and old_status != "Отменен":
        for item in order["items"]:
            drink = find_drink(data, item["id"])
            if drink:
                drink["stock"] += item["qty"]
        print("ℹ️ Порции возвращены на склад.")

    order["status"] = new_status
    save_data(data)
    print(f"✅ Статус заказа №{order_id} изменён: {old_status} → {new_status}\n")


def show_report(data):
    print("\n=== ОТЧЁТ ===")
    orders = data["orders"]
    total_orders = len(orders)
    new_count = sum(1 for o in orders if o["status"] == "Новый")
    done_count = sum(1 for o in orders if o["status"] == "Выполнен")
    cancelled_count = sum(1 for o in orders if o["status"] == "Отменен")

    revenue = sum(o["final_total"] for o in orders if o["status"] == "Выполнен")

    sold = {}
    for order in orders:
        if order["status"] != "Выполнен":
            continue
        for item in order["items"]:
            sold[item["name"]] = sold.get(item["name"], 0) + item["qty"]

    if sold:
        popular_name, popular_qty = max(sold.items(), key=lambda x: x[1])
        popular_str = f"{popular_name} ({popular_qty} порций)"
    else:
        popular_str = "Нет данных"

    print(f"Всего заказов: {total_orders}")
    print(f"  Новых: {new_count}")
    print(f"  Выполненных: {done_count}")
    print(f"  Отменённых: {cancelled_count}")
    print(f"Выручка по выполненным заказам: {revenue} ₽")
    print(f"Самый популярный напиток: {popular_str}")
    print("\nТекущие остатки порций:")
    for drink in data["menu"]:
        print(f"  {drink['name']}: {drink['stock']}")
    print()


def main():
    data = load_data()

    while True:
        print("=== КОФЕЙНЯ ===")
        print("1. Показать меню")
        print("2. Создать заказ")
        print("3. Показать все заказы")
        print("4. Изменить статус заказа")
        print("5. Показать отчёт")
        print("6. Завершить работу")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_menu(data)
        elif choice == "2":
            create_order(data)
        elif choice == "3":
            show_orders(data)
        elif choice == "4":
            change_status(data)
        elif choice == "5":
            show_report(data)
        elif choice == "6":
            print("До свидания!")
            break
        else:
            print("❌ Некорректный выбор. Введите число от 1 до 6.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nРабота программы прервана.")