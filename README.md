# Ugra CTF School 2023

11 марта 2023 | [Сайт](https://2023.ugractf.ru/)

## Таски

[Краткость — сестра таланта](tasks/brevity/) (baksist, ppc 100)  
[Циркулирование](tasks/circulation/) (baksist, forensics 200)  
[Классическая дискета](tasks/classic/) (ksixty, forensics 200)  
[[ДАННЫЕ УДАЛЕНЫ]](tasks/classified/) (ivanq, ppc 250)  
[Очередь](tasks/endlessline/) (astrra, web 150)  
[Очень удалённый доступ](tasks/moonshot/) (ivanq, pwn 300)  
[Minimum system requirements](tasks/msr/) (rozetkin, reverse 400)  
[Nucached](tasks/nucached/) (ivanq, web 200)  
[Nucached 2.0](tasks/nucached2/) (ivanq, ctb 200)  
[Решите капчу за нас](tasks/payoff/) (gudn, web 150)

## Команда разработки

Олимпиада была подготовлена командой [team Team].

[Никита Сычев](https://github.com/nsychev) — руководитель команды, разработчик платформы и системы регистрации  
[Калан Абе](https://github.com/enhydra) — разработчик тасков  
[Коля Амиантов](https://github.com/abbradar) — инженер по надёжности  
[Астра Андриенко](https://github.com/astrrra) — разработчица тасков  
[Ваня Клименко](https://github.com/ksixty) — разработчик тасков, сайта и платформы, дизайнер  
[Иван «Ivanq» Мачуговский](https://github.com/imachug) — разработчик тасков и платформы  
[Даниил Новоселов](https://github.com/gudn) — разработчик тасков  
[Матвей Сердюков](https://github.com/baksist) — разработчик тасков  
[Евгений Черевацкий](https://github.com/rozetkinrobot) — разработчик тасков

## Организаторы и спонсоры

Организаторы Ugra CTF — Югорский НИИ информационных технологий, Департамент информационных технологий и цифрового развития ХМАО–Югры и Департамент образования и науки ХМАО–Югры. Олимпиаду разрабатывает команда [team Team].

Спонсор призового фонда — АНО «Лаборатория цифровой трансформации».

## Площадки

В этом году олимпиада прошла на 13 площадках по всей России. Благодарим организации, на базе которых работали площадки, а также всех организаторов на площадках:

* Владивосток — [IT-колледж ВВГУ (IThub Владивосток)](https://vvsu.ithub.ru)
* Воронеж — [Точка кипения ВГТУ](https://leader-id.ru/places/1294)
* Екатеринбург — [Уральский клуб нового образования](https://www.ukno.ru/)
* Казань — [ИТ-парк](https://itpark.tech/?city=kazan)
* Москва — [Колледж IThub](https://ithub.ru)
* Нижневартовск — [Нижневартовский государственный университет](https://nvsu.ru/)
* Новосибирск — [Новосибирский государственный университет](https://www.nsu.ru/)
* Новосибирск — [Сибирский государственный университет телекоммуникаций и информатики](https://sibsutis.ru)
* Пермь — [Пермский политех](https://pstu.ru/)
* Сургут — [Сургутский государственный университет](https://surgu.ru/)
* Тюмень — [Центр робототехники и автоматизированных систем управления](https://rio-centr.ru/projects/main/robotech/)
* Ханты-Мансийск — [Югорский НИИ информационных тенхологий](https://uriit.ru/)

## Генерация заданий

Некоторые таски создаются динамически — у каждого участника своя, уникальная версия задания. В таких заданиях вам необходимо запустить генератор — обычно он находится в файле `generate.py` в директории задания. Обычно генератор принимает три аргумента — уникальный идентификатор, директорию для сохранения файлов для участника и названия генерируемых тасков (последний, как правило, не используется). Например, генератор можно запустить так:

```bash
./tasks/hello/generate.py 1337 /tmp/hello
```

Уникальный идентификатор используется для инициализации генератора псевдослучайных чисел, если такой используется. Благодаря этому, повторные запуски генератора выдают одну и ту же версию задания.

Генератор выведет на стандартный поток вывода JSON-объект, содержащий флаг к заданию и информацию для участника, а в директории `/tmp/hello` появятся вложения, если они есть.

## Лицензия

Материалы соревнования можно использовать для тренировок, сборов и других личных целей, но запрещено использовать на своих соревнованиях. Подробнее — [в лицензии](LICENSE).
