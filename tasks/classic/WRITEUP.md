# Классическая дискета: Write-up

Нам дают образ дискеты для «Макинтоша». Убедиться в этом можно с помощью утилиты *file:*

```
$ file 'Ugra Classic.dsk'
Ugra Classic.dsk: Macintosh HFS data block size: 512, number of blocks: 2874, volume name: Ugra Classic
```

Как же извлечь данные из этого образа?

## Способ решения первый: виртуализация

Существует множество способов запустить классическую *Mac OS* на современном компьютере. Нужно лишь понять, насколько классическую.

Диск имеет файловую систему *HFS.* В начале 90-х вместе с *Mac OS 8* «Макинтоши» перешли на *HFS Plus* — то есть, диск из немного более ранней эпохи. Разберём на примере *Mac OS 7.5.3*.

> На самом деле, подойдёт любая версия, начиная с шестой.

Установим [Basilisk II](https://basilisk.cebix.net/) — это эмулятор компьютеров серии *Macintosh II* и *Quarda*. Для его работы нужен образ ROM-памяти соответствующего компьютера и диск с операционной системой. Оба файлика небольшие и прекрасно скачиваются из, например, «Интернет-архива»: [ROM](https://archive.org/details/mac_rom_archive_-_as_of_8-19-2011), [ОС](https://archive.org/details/AppleMacintoshSystem753).

> В «Интернет-архиве» также доступна и эмуляция — прямо в браузере! Перейдите на страницу загрузки [образа ОС](https://archive.org/details/AppleMacintoshSystem753), наведите курсок на большую картинку и нажмите на зелёную круглую кнопку. Через некоторое время экран оживёт! Правда, примонтировать наш образ с дискетой таким образом не получится.

> Есть и другие эмуляторы, работающие прямо из браузера. На сайте [infinitemac.org](https://infinitemac.org) можно запустить абсолютно любую версию *Mac OS,* начиная с самой-самой первой. В этом же сайте можно и монтировать произвольные образы, перетаскивая их в окно браузера.

Запустим *Basilisk II*: `$ BasiliskII`. Во вкладке *Volumes* добавим образ диска с ОС и нашей дискеты. Во вкладке *Memory/Misc* укажем тип машины и путь к файлу с ROM:

![Настройки Basilisk II](./writeup/basilisk-settings.png)

Можно нажимать Start! Должен появиться рабочий стол и наша примонтированная дискета, которая в результате эмуляции превратилась в жёсткий диск… На дискете всего один файл — программа «Ugra Classic» с незамысловатой иконкой. Можно запустить его, но, увы, дальше экрана загрузки продвинуться нереально. Происходит ошибка:

![Ошибка стоп хнуль ноль нуль](./writeup/ugra.png)

Что такое RESOURCE FORK? Новая зацепка. [В Википедии сказано](https://en.wikipedia.org/wiki/Resource_fork), что файлы в *HFS* на самом деле двойственные. У них есть *data fork* — часть с данными — и *resource fork* — часть с ресурсами. Там же упоминается программа *ResEdit*, которая позволяет работать с *resource fork*. Звучит как то, что надо!

Поищем в интернете `resedit img`, примонтируем загруженный образ в параметрах *Basilisk II* и порадуемся новой установленной программе. Чтобы открыть файл «Ugra Classic», достаточно перетащить его значок на значок программы *ResEdit*:

![Перетаскиваем](./writeup/drag-n-drop.png)

Если всё получилось, мы увидим окошко со всеми ресурсами приложения. Там будут, например, ассемблерный код, строки из программы, диалоговые окна…

![Диалоговое окно с ошибкой. Можно его подредактировать, сохранить и запустить программу. Порадоваться и продолжить](./writeup/alert.png)

Но где же флаг? В картинках, конечно! В программе есть три ресурса типа `PICT`, и один из них, с ID 1337, содержит надпись с желанной строкой:

![Флаг](./writeup/flag.png)

Флаг: **ugra_you_are_a_power_macintosh_user_81de016d**

## Способ решения второй: настоящая форензика

Попробуем почитать тексты:

```
$ strings 'Ugra Classic.dsk'
Ugra Classic
Ugra Classic
APPLUGRA!
APPLUGRA!
Ugra Classic
1Programma dlya uchyota i provedenia meropriyatij.*Ispol'zovanie 3 licami VOSPRESHCHAETSYA!!!
V programme est sekrety.
(c) 2023 . XAHTbI-MAHCU`UCK
3AGPY3KA...
DDDDDDDD@
SOwu6ka :
RESOURCE FORK s PODPICbI-0 HE HAUDEH ! Eto konec, obratites k IT-omDe/\y.
```

Видим зацепку про resource fork, а также понимаем, что данные в образе, в целом, считываются как есть: ни сжатие, ни шифрование не используются. Существуют две библиотеки для «Питона» от одного и того же разработчика: *[machfs](https://github.com/elliotnunn/machfs)* и *[macresources](https://github.com/elliotnunn/macresources)*.

Откроем и почитаем файл ими:
```python
import macresources
import machfs

volume = machfs.Volume()

with open('/home/k60/Downloads/Ugra Classic.dsk', 'rb') as img:
    volume.read(img.read())

print(volume)
print(volume['Ugra Classic'])
print(volume['Ugra Classic'].rsrc[:100])
```

Файл читается, *resource fork* присутствует, но он в двоичном формате и не особо понятный:
```
Ugra Classic: [APPL/UGRA] data=0b rsrc=238011b
[APPL/UGRA] data=0b rsrc=238011b
b'\x00\x00\x01\x00\x00\x03\x9d\x86\x00\x03\x9c\x86\x00\x00\x045\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0cUgra Classic\x00\x02\x00\x02\x00APPLUGRA!\x00\x00\x00\x00\x00\x02\x00APPLUGRA!\x00\x00\x00\x00\x00\x00\x00\x00\x00'
```

Скормим форк как есть библиотеке *macresources*:

```python
# (продолжение)

rsrc_bin = volume['Ugra Classic'].rsrc
rsrc = macresources.parse_file(rsrc_bin)
rsrc = list(rsrc)  # parse_file возвращает генератор, превратим его в список
print(rsrc)
```

Библиотека правильно разбирает двоичный формат и формирует список ресурсов с типами и ID:
```
[Resource(type=b'DATA', id=0, name=None, attribs=40, data=b'\x00\x00\x002'...184b), Resource(type=b'ZERO', id=0, name=None, attribs=8, data=b'\x00\xce\x00\x02'), Resource(type=b'DREL', id=0, name=None, attribs=40, data=b''), Resource(type=b'CODE', id=2, name=None, attribs=56, data=b'\x00P\x00\x01'...558b), ..., Resource(type=b'ALRT', id=128, name=None, attribs=0, data=b'\x002\x00>'), Resource(type=b'PICT', id=128, name=None, attribs=0, data=b'\x86\xe8\x00\x00'...100072b), Resource(type=b'PICT', id=129, name=None, attribs=0, data=b'\x04\xba\x00\x00'...1210b), Resource(type=b'PICT', id=1337, name=None, attribs=0, data=b'\x02\x00\x00\x00'...132204b)]
```

Ресурс типа `PICT` с ID 1337 явно выбивается из ряда. Попробуем извлечь его из образа и записать на диск.
```python
# (продолжение)

leet_pict = rsrc[-1]

with open('1337.pict', 'wb') as pict:
    pict.write(leet_pict.data)
```

Преобразовать файл формата PICT можно с помощью утилиты *ImageMagick*. Полученный файл, однако, в ней не открывается. Более того, он даже не определяется утилитой *file*:

```
$ magick 1337.pict 1337.png
magick: improper image header `1337.pict' @ error/pict.c/ReadPICTImage/918.

$ file 1337.pict
1337.pict: data
```

Обстоятельно покопавшись в интернете, можно найти [упоминание причины](https://github.com/labbott/pictparser):

> This is litterally a PICT file minus the 512 byte header.
>
> [...]
>
> 3. add a 512 byte header of zeros, stick it in a binary file with .pct

Можно также открыть исходники метода `ReadPICTImage`, ошибка в котором и возникает у *ImageMagick.* В нём [явно сказано](https://github.com/ImageMagick/ImageMagick/blob/393c95ed0f1d7c5320f60d51785143f02b20825b/coders/pict.c#L905), что первые 512 байт файла программа пропускает, не читая:

```
coders/pict.c:904:
/*
  Skip header : 512 for standard PICT and 4, ie "PICT" for OLE2.
*/
```

Ну что ж. Допишем пустой заголовок размером 512 байт к началу файла:
```python
# (продолжение)

with open('1337-with-header.pict', 'wb') as pict:
    data = b'\x00' * 512 + leet_pict.data
    pict.write(data)
```

Теперь файл открывается в ImageMagick. Мы можем сконвертировать его в PNG и открыть. Нас встретит всё та же надпись с желанной строкой.

Флаг: **ugra_you_are_a_power_macintosh_user_81de016d**
