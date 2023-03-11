#!/usr/bin/env python3

from ctypes import pointer
import os
from re import DEBUG
import sys
from kyzylborda_lib.secrets import get_flag
from datetime import datetime, timezone, timedelta
import time
import subprocess
import pwd


class Menu():
    def __init__(self, title, submenus = [], text=None, command=None, parent=None):
        self.title = title
        self.submenus = submenus
        self.text = text
        self.command = command
        self.parent = parent or self

    def add(self, *submenus):
        for submenu in submenus:
            submenu.parent = self
        self.submenus = submenus
        return self

    def interact(self):
        print(self)
        if self.command:
            self.command()
        print(self.navigate(), end='')
        try:
            choice = int(input())
            if choice == 0:
                return self.parent or self
            elif choice < (len(self.submenus) + 1):
                return self.submenus[choice - 1]
            else:
                print("ОШИБКА не задано номера")
                return self
        except ValueError:
            print("ОШИБКА ввода команды")
            return self

    def navigate(self):
        submenus = self.submenus
        if self.parent or submenus:
            formatted = [f"{n + 1}. {x.title}" for n, x in enumerate(self.submenus)]
            if self.parent != self:
                formatted.append("0. [НАЗАД]")
            options = "\n".join(formatted)
            return f"\nДля продолжения введите номер:\n{options}\n№> "
        else:
            return ""

    def __str__(self):
        title = self.title
        msg = self.text
        return f"\n{'='*len(title)}\n{title.upper()}\n\n{msg}"


def repl(menu_root):
    current_menu = menu_root
    while True:
        current_menu = current_menu.interact()


def weather_error():
    time.sleep(1)
    print("ОШИБКА нет соединения с базой душ")

def main():
    THE_MENU = Menu(
        title="Главная страница",
        text="Добро поРЖАловать на наш сервер!!"
    ).add(
        Menu(
            title="Текущие сведения",
            text="""На данном экране вы можете получить текущие сведения.
Эту информацию можно использовать в разных целях: получение, анализ, обработка.

Доступны множество источников. Выберите по настроению!""",
        ).add(
            Menu(
                title="Текущее время",
                text="Текущее время в Ижевск, Ро\x06\x392",
                command=lambda: print(datetime.now(timezone(timedelta(hours=4))))
            ),
            Menu(
                title="Текущая погода",
                text="Текущее погода в каком из городов?",
            ).add(
                *[Menu(x, text=f"Просмотрите погоду в {x} на экране! Свежая актуальная погода.", command=lambda: weather_error()) \
                  for x in ["Ижевск", "Ростов", "Сызрань", "Рудничный", "Кильмезь"]]
            ),
        ),
        Menu(
            title="Состояние системы",
            text="На данном экране доступные ключевые показатели работоспособности системы."
        ).add(
            *[Menu(x, text=f"ОШИБКА не удалось получить доступ к данным '{x}'") \
              for x in [
                      "Пользователи", "Группы", "Администраторы", "Делопроизводство",
                      "Отчётность", "Души", "Вознесение", "Реестр душ", "Чистилище",
              ]]
        ),
        Menu("Система", text="[Нет документации или запрещено (секретно).]").add(
            Menu(
                title="Служебный режим обслуживания",
                text="""Введите служебную команду ЕСЛИ:
- вы администратор
- вы ТОЧНО знаете ЧТО делаете
- это НЕ ПОВРЕДИТ душам.

Обнаржена попытка похищения душа! При выводе командой Имени Души с наибольшим числом отказов вам будет даровано ВОЗНАГРАЖДЕНИЕ.""",
                command=lambda: execute_command()
            ),
        )
    )

    repl(THE_MENU)


def execute_command():
    flag = get_flag()
    flag_user = os.environ.get("flag_user")
    flag_user = f'{flag_user}\n'.encode('utf-8')

    del os.environ["KYZYLBORDA_SECRET_flag"]
    del os.environ["flag_user"]
    pw_record = pwd.getpwnam('user')


    user = pw_record.pw_name
    uid = pw_record.pw_uid
    gid = pw_record.pw_gid
    home = pw_record.pw_dir

    env = os.environ.copy()
    env['HOME'] = home
    env['LOGNAME'] = user
    env['PWD'] = home
    env['USER'] = user
    env['PATH'] = "/run/bin"

    command = input("> ")

    process = subprocess.Popen(
        ["/bin/bash", "-r", "-c", command],
        preexec_fn=demote(uid, gid), cwd=home, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    line_counter = 0
    line_limit = 5

    while True:
        output = process.stdout.readline()
        if line_counter >= line_limit:
            print("ОШИБКА безопасник запретил выводить более 5 строк")
            break
        if not output:
            break
        if output:
            print(output.decode('utf-8'), end='')
            line_counter += 1
            if (output == flag_user):
                print("УСПЕХ очистки условие РЕКОРД ОТКАЗ? И ДУША? -> ИСТИНА")
                print(f'Чек-сумма освобождения Душа("{output.decode("utf-8").strip()}"): {flag}')
                print("Освобождено пространства: 13.3 кл/м2")
                sys.exit(0)
                break
    print("ОШИБКА очистки условие РЕКОРД ОТКАЗ? И ДУША? -> ЛОЖЬ")
    sys.exit(0)


def demote(uid, gid):
    def result():
        os.setgid(gid)
        os.setuid(uid)
    return result


if __name__ == '__main__':
    main()
