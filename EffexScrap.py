from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time

# Замените путь к Chrome WebDriver на свой
chrome_driver_path = "chromedriver.exe"
username = "******@******.ru"
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

    time.sleep(0.1)

    # Второе модальное окно: выбрать слот
    slot_select = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "slot"))
    )

    time.sleep(0.1)

    try:
        # Выбираем нужный вариант непосредственно по его значению через атрибут "value"
        select = Select(slot_select)
        time.sleep(0.1)
        select.select_by_value(target_time)
    except:
        print("Недоступно")
        return 1

    # Нажать на кнопку "Сохранить"
    click_save_button(driver)
    time.sleep(10)
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


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument(
        "--headless")  # Эта опция позволяет запустить Chrome в фоновом режиме (без графического интерфейса)
    service = Service(executable_path=chrome_driver_path)

    windows_show = int(input("Показать окно Google и работу программы? 1 - (Да), 0 - (Нет): "))
    if not windows_show:
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(service=service)

    target_name = input("Введите имя слота: ")
    target_date = input("Введите желаемую дату (формат строго: ДД.ММ.ГГГГ): ")
    # Меняем формат даты в понятный сайту
    target_time = input("Введите желаемое время (формат строго: ЧЧ:ММ - ЧЧ:ММ): ")
    target_time = value_list[target_time]

    # Такая конструкция не даст проге тупо упасть
    try:
        choose_date_and_time(driver, target_date, target_time, target_name)
    except:
        choose_date_and_time(driver, target_date, target_time, target_name)

    # Закрываем браузер после завершения работы
    print("УСПЕХ!!!")
    driver.quit()

