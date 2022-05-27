# Yandex Music Rhythmbox plugin
Плагин для работы с музыкальным сервисом Яндекс.Музыка в Rhythmbox.
![Screenshot](https://user-images.githubusercontent.com/11454622/161440160-655114ee-87ec-4929-af50-da43ee5dc56b.png)
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
