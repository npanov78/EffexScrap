import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time


# Замените путь к Chrome WebDriver на свой
chrome_driver_path = "chromedriver.exe"
username = "******@*****.ru"
password = "******"
value_list = {
    '00:00 - 03:00': '1',
    '03:00 - 06:00': '3',
    '06:00 - 09:00': '5',
    '09:00 - 12:00': '7',
    '12:00 - 15:00': '11',
    '15:00 - 18:00': '13',
    '18:00 - 21:00': '17',
    '21:00 - 24:00': '19'
}


def authorize(driver):
    driver.get("https://sel.effex.ru/")
    username_input = driver.find_element(By.NAME, 'login')
    password_input = driver.find_element(By.NAME, 'password')
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)


def open_slot_page(driver, target_name):
    driver.get("https://sel.effex.ru/ru/out//1")

    # Обновляем и очищаем элемент
    driver.refresh()
    search_slot = driver.find_element(By.NAME, 'search')
    search_slot.clear()

    search_slot.send_keys(f'{target_name}')
    search_slot.send_keys(Keys.ENTER)


def click_next_button(driver):
    # Найти кнопку "Далее" по тексту "Далее" и кликнуть на нее
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Далее')]"))
    )
    next_button.click()


def click_save_button(driver):
    # Найти кнопку "Сохранить" по тексту "Сохранить" и кликнуть на нее
    save_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Сохранить')]"))
    )
    save_button.click()


def mainLoop(driver, target_date, target_time, target_name):
    # Найти элемент <a> в третьей колонке таблицы
    target_link = driver.find_element("xpath", "//a//span[contains(text(), '" + target_name + "')]")

    # Кликнуть по элементу <a>
    target_link.click()

    # Нажать на кнопку "Далее" в первом модальном окне
    time.sleep(0.7)
    click_next_button(driver)

    # Второе модальное окно: выбрать дату
    date_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "beg_date"))
    )
    date_input.clear()
    date_input.send_keys(target_date + Keys.ENTER)

    # Нажать на кнопу перед выбором слота
    slot_button = driver.find_element("xpath", "//select[@name='slot']")
    driver.execute_script("arguments[0].click();", slot_button)

    time.sleep(0.15)

    # Второе модальное окно: выбрать слот
    slot_select = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "slot"))
    )

    time.sleep(0.15)

    try:
        # Выбираем нужный вариант непосредственно по его значению через атрибут "value"
        select = Select(slot_select)
        time.sleep(0.15)
        select.select_by_value(target_time)
    except:
        print("Недоступно")
        return 1

    # Нажать на кнопку "Сохранить"
    click_save_button(driver)
    time.sleep(5)
    return 0


def choose_date_and_time(driver, target_date, target_time, target_name):
    # Авторизовываемся на сайте
    authorize(driver)

    end = 1
    while end != 0:
        # Открыть веб-страницу
        open_slot_page(driver, target_name)

        # Пытаемся арендовать слот
        end = mainLoop(driver, target_date, target_time, target_name)


def on_start_execution():
    target_name = target_name_entry.get()
    target_date = target_date_entry.get()
    target_time = value_list.get(target_time_combobox.get())
    use_options = use_options_var.get()

    service = Service(executable_path=chrome_driver_path)
    if not use_options:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(service=service)

    try:
        choose_date_and_time(driver, target_date, target_time, target_name)
        messagebox.showinfo("Success", "УСПЕХ!!!")
    except:
        messagebox.showerror("Error", "Произошла ошибка при выполнении. Проверьте имя слота. Отключите VPN или Proxy.")

    driver.quit()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("EffexScrap bot")
    root.configure(bg="black")

    # Create and configure input fields and checkboxes
    target_name_label = ttk.Label(root, text="Введите имя слота:", foreground="white", background="black")
    target_name_label.grid(row=0, column=0, padx=5, pady=5)
    target_name_entry = ttk.Entry(root)
    target_name_entry.grid(row=0, column=1, padx=5, pady=5)

    target_date_label = ttk.Label(root, text="Введите желаемую дату:", foreground="white", background="black")
    target_date_label.grid(row=1, column=0, padx=5, pady=5)
    target_date_entry = DateEntry(root, date_pattern="dd.mm.yyyy", foreground="white", background="black")
    target_date_entry.grid(row=1, column=1, padx=5, pady=5)

    target_time_label = ttk.Label(root, text="Выберите желаемое время:", foreground="white", background="black")
    target_time_label.grid(row=2, column=0, padx=5, pady=5)
    target_time_combobox = ttk.Combobox(root, values=list(value_list.keys()), state="readonly")
    target_time_combobox.grid(row=2, column=1, padx=5, pady=5)

    use_options_var = tk.BooleanVar()
    use_options_check = ttk.Checkbutton(root, text="Показать работу в окне Chrome", variable=use_options_var)
    use_options_check.grid(row=3, columnspan=2, padx=5, pady=5)

    start_button = ttk.Button(root, text="Начать выполнение", command=on_start_execution)
    start_button.grid(row=4, columnspan=2, padx=5, pady=5)

    root.mainloop()
