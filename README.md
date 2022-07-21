# Яндекс.Музыка в Rhythmbox
Данный репозиторий содержит плагин для музыкального плеера [Rhythmbox](https://wiki.gnome.org/Apps/Rhythmbox), предоставляющий возможность слушать музыку из сервиса Яндекс.Музыка.
![Скриншот](https://user-images.githubusercontent.com/11454622/171248479-ae6d03e1-8256-484e-96d3-e9c1bf904c55.png)

## Установка
### Arch Linux
В случае использования репозитория AUR, вы можете установить пакет [rhythmbox-plugin-yandex-music](https://aur.archlinux.org/packages/rhythmbox-plugin-yandex-music) из AUR через ваш пакетный менеджер или терминал. В ином случае требуется действовать согласно инструкции для других дистрибутивов.

### Другие дистрибутивы
Для работы плагина требуется установить [неофициальную Python библиотеку API Yandex Music](https://github.com/MarshalX/yandex-music-api).

    $ pip install yandex-music --upgrade

Далее закройте музыкальный плеер Rhythmbox, если он у вас запущен, и выполните установку релизной или тестовой версии плагина.

Релизная версия плагина является более стабильной и включает функционал, который завершён полностью или с незначительными замечаниями. Тестовая версия плагина включает весь функционал, написанный на данный момент, даже в незавершенном виде, но может работать с ошибками.

### Релизная версия
Теперь необходимо скачать плагин из репозитория, распаковать его и переместить в папку с плагинами Rhythmbox.

    $ wget https://github.com/dobroweb/rhythmbox-plugin-yandex-music/archive/refs/tags/0.4-alpha.tar.gz
    $ tar -zxvf 0.4-alpha.tar.gz
    $ mkdir -p ~/.local/share/rhythmbox/plugins/
    $ mv rhythmbox-plugin-yandex-music-0.4-alpha ~/.local/share/rhythmbox/plugins/yandex-music

### Тестовая версия
Вам достаточно клонировать репозиторий в папку с плагинами Rhythmbox.

    $ git clone git@github.com:feschukov/rhythmbox-plugin-yandex-music.git ~/.local/share/rhythmbox/plugins/yandex-music

## Обновление
### Arch Linux
В случае использования репозитория AUR, вам достаточно обновить пакет [rhythmbox-plugin-yandex-music](https://aur.archlinux.org/packages/rhythmbox-plugin-yandex-music) из AUR через ваш пакетный менеджер или терминал. В ином случае требуется действовать согласно инструкции для других дистрибутивов.

### Другие дистрибутивы
Для начала требуется обновить [неофициальную Python библиотеку API Yandex Music](https://github.com/MarshalX/yandex-music-api) такой же командой, как и при установке плагина.

Далее закройте музыкальный плеер Rhythmbox, если он у вас запущен, и выполните обновление релизной или тестовой версии плагина.

### Релизная версия
Теперь необходимо удалить старый плагин, скачать новый и переместить его в папку с плагинами Rhythmbox.

    $ rm -R ~/.local/share/rhythmbox/plugins/yandex-music
    $ wget https://github.com/dobroweb/rhythmbox-plugin-yandex-music/archive/refs/tags/0.4-alpha.tar.gz
    $ tar -zxvf 0.4-alpha.tar.gz
    $ mv rhythmbox-plugin-yandex-music-0.4-alpha ~/.local/share/rhythmbox/plugins/yandex-music

### Тестовая версия
Вам достаточно обновить репозиторий в папке с установленным плагином.

    git -C ~/.local/share/rhythmbox/plugins/yandex-music pull

## Настройка
После установки плагина необходимо его активировать в настройках Rhythmbox. Все возможности будут доступны только после авторизации в сервисе Яндекс.Музыка и при наличии активной подписки.

Запустите Rhythmbox, выберите источник "Мне нравится" из группы "Яндекс.Музыка" и авторизуйтесь, используя ваш логин и пароль. Плагин хранит только token, который генерирует Яндекс, и использует его для дальнейшей авторизации.

## Отладка
В случае возникновления проблем при работе с плагином вы можете запустить Rhythmbox, используя следующую команду

    $ rhythmbox -D yandex-music

После чего повторите действия, которые привели к ошибке, и [сообщите о ней](https://github.com/dobroweb/rhythmbox-plugin-yandex-music/issues/new/choose).
