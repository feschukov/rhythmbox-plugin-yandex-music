# Яндекс.Музыка в Rhythmbox
Данный репозиторий содержит плагин для музыкального плеера [Rhythmbox](https://wiki.gnome.org/Apps/Rhythmbox), предоставляющий возможность слушать музыку из сервиса Яндекс.Музыка.
![Скриншот](https://user-images.githubusercontent.com/11454622/171248479-ae6d03e1-8256-484e-96d3-e9c1bf904c55.png)

## Установка
Для работы плагина требуется установить [неофициальную Python библиотеку API Yandex Music](https://github.com/MarshalX/yandex-music-api).

    $ pip install yandex-music --upgrade

Затем удалить старый плагин, скачать новый и переместить его в папку с плагинами Rhythmbox.

    $ rm -R ~/.local/share/rhythmbox/plugins/yandex-music
    $ wget https://github.com/dobroweb/rhythmbox-plugin-yandex-music/archive/refs/tags/0.3-alpha.tar.gz
    $ tar -zxvf 0.3-alpha.tar.gz
    $ mkdir -p ~/.local/share/rhythmbox/plugins/
    $ mv rhythmbox-plugin-yandex-music-0.3-alpha ~/.local/share/rhythmbox/plugins/yandex-music

После чего активировать плагин в настройках Rhythmbox.

## Настройка
Все возможности будут доступны только после авторизации в сервисе Яндекс.Музыка и при наличии активной подписки.

Запустите Rhythmbox, выберите источник "Мне нравится" из группы "Яндекс.Музыка" и авторизуйтесь, используя ваш логин и пароль. Плагин хранит только token, который генерирует Яндекс, и использует его для дальнейшей авторизации.

## Отладка
В случае возникновления проблем при работе с плагином вы можете запустить Rhythmbox, используя следующую команду

    $ rhythmbox -D yandex-music

После чего повторите действия, которые привели к ошибке, и [сообщите о ней](https://github.com/dobroweb/rhythmbox-plugin-yandex-music/issues/new/choose).
