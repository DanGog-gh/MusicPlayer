from __future__ import annotations

import ast
import os
import random

from kivy import platform
from kivy.clock import Clock
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

_platform = "desktop"

# В зависимости от платформы используем различные классы для воспроизведения
# музыки.
if platform in ["win", "linux", "macosx"]:
    from kivy.core.audio import SoundLoader
elif platform == "android":
    from kvdroid.tools.audio import Player
    from kvdroid.tools.path import sdcard
    from modules.androidstorage import SharedStorage

    _platform = "android"

from kivy.metrics import dp
from kivy.uix.widget import Widget

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDFabButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel
from kivymd.uix.progressindicator import MDLinearProgressIndicator
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.slider import MDSlider, MDSliderHandle, MDSliderValueLabel

from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3

from modules.get_mp3_metadata import get_mp3_metadata


class MusicPlay(MDScreen):
    """Класс реализует экран проигрывания трека."""

    def __init__(self, *args, **kwargs):
        """Вызывается при создании экземпляра класса MusicPlay."""

        super().__init__(*args, **kwargs)
        self.add_widget(
            MDScrollView(
                MDBoxLayout(
                    # Обложка трека.
                    FitImage(
                        id="cover image",
                        source="data/images/bg-default.jpg",
                        size_hint=(0.7, None),
                        height=dp(320),
                        pos_hint={"center_x": 0.5},
                        radius=dp(32),
                    ),
                    MDBoxLayout(
                        # Название трека.
                        MDLabel(
                            id="name track label",
                            text="Выберите папку с музыкой",
                            theme_text_color="Custom",
                            text_color="white",
                            halign="center",
                            adaptive_height=True,
                            font_style="TransformBold",
                            role="large",
                        ),
                        # Название исполнителя.
                        MDLabel(
                            id="name artist label",
                            text="или трек вручную",
                            theme_text_color="Custom",
                            text_color="white",
                            halign="center",
                            adaptive_height=True,
                            font_style="TransformMedium",
                            role="medium",
                        ),
                        pos_hint={"center_x": 0.5},
                        orientation="vertical",
                        adaptive_height=True,
                        spacing=dp(8),
                        size_hint_x=0.9,
                        padding=[
                            0,  # отступ слева
                            dp(8),  # отступ сверху
                            0,  # отступ справа
                            dp(8),  # отступ снизу
                        ],
                    ),
                    # Слайдер длинны и прогресса трека с счетчиком длины трека.
                    MDBoxLayout(
                        MDLinearProgressIndicator(
                            id="music indicator",
                            value=0,
                        ),
                        MDBoxLayout(
                            MDLabel(
                                id="current time label",
                                text="0:00",
                                theme_text_color="Custom",
                                text_color="white",
                                adaptive_size=True,
                                font_style="TransformMedium",
                                role="small",
                            ),
                            Widget(),
                            MDLabel(
                                id="total time label",
                                text="0:00",
                                theme_text_color="Custom",
                                text_color="white",
                                adaptive_size=True,
                                font_style="TransformMedium",
                                role="small",
                            ),
                            adaptive_height=True,
                        ),
                        orientation="vertical",
                        spacing=dp(8),
                        adaptive_height=True,
                        size_hint_x=0.9,
                        pos_hint={"center_x": 0.5},
                    ),
                    # Контейнер с управляющими музыкой кнопками.
                    MDBoxLayout(
                        MDIconButton(
                            id="loop-button",
                            icon="restart",
                            theme_text_color="Custom",
                            text_color="#d3d3d3",
                            pos_hint={"center_y": 0.5},
                            # Присваиваем событие клика на кнопку.
                            on_release=self.on_tap_loop_button,
                        ),
                        Widget(),
                        MDIconButton(
                            icon="skip-previous",
                            theme_icon_color="Custom",
                            icon_color="#d3d3d3",
                            pos_hint={"center_y": 0.5},
                            on_release=self.on_tap_skip_previous_button,
                        ),
                        Widget(),
                        MDFabButton(
                            id="pause-button",
                            style="large",
                            icon="play",
                            theme_bg_color="Custom",
                            md_bg_color="#fc0fc0",
                            theme_icon_color="Custom",
                            icon_color="#d3d3d3",
                            on_release=self.on_tap_pause_button,
                        ),
                        Widget(),
                        MDIconButton(
                            icon="skip-next",
                            theme_icon_color="Custom",
                            icon_color="#d3d3d3",
                            pos_hint={"center_y": 0.5},
                            on_release=self.on_tap_skip_next_button,
                        ),
                        Widget(),
                        MDIconButton(
                            id="shuffle-button",
                            icon="shuffle",
                            theme_icon_color="Custom",
                            icon_color="#d3d3d3",
                            pos_hint={"center_y": 0.5},
                            on_release=self.on_tap_shuffle_button,
                        ),
                        size_hint_x=0.9,
                        pos_hint={"center_x": 0.5},
                        adaptive_height=True,
                        padding=dp(18),
                        md_bg_color="#1e0438",
                    ),
                    # Контейнер с кнопками для управления библиотекой и треками
                    # музыки.
                    # TODO: Добавить кнопку, которая переключает экран со
                    #  списком треков из директории, которая воспроизводится
                    #  в данный момент.
                    #  Сделать проверку: если переменная self.list_tracks_music
                    #  - это пустой список, вывести сообщение
                    #  (использовать виджет MDSnackbar) "Выберите директорию
                    #  для воспроизведения."
                    MDBoxLayout(
                        MDIconButton(
                            icon="archive-music",
                            on_release=self.on_tap_archive_music_button,
                        ),
                        Widget(),
                        MDIconButton(
                            icon="playlist-music",
                            on_release=self.on_tap_playlist_music_button,
                        ),
                        Widget(),
                        MDIconButton(
                            id="heart-button",
                            icon="heart",
                            on_release=self.on_tap_heart_button,
                        ),
                        size_hint_x=0.7,
                        pos_hint={"center_x": 0.5},
                        adaptive_height=True,
                        padding=dp(18),
                        radius=dp(32),
                        md_bg_color="#2a0d44",
                    ),
                    orientation="vertical",
                    md_bg_color="#1e0438",
                    padding=dp(18),
                    spacing=dp(18),
                    adaptive_height=True,
                ),
                bar_width=0,
                md_bg_color="#1e0438",
                do_scroll_x=False,
            ),
        )

        # Инстансы выджетов.
        self.shuffle_button = self.get_ids()["shuffle-button"]
        self.cover_image = self.get_ids()["cover image"]
        self.instance_music_indicator = self.get_ids()["music indicator"]
        self.current_time_label = self.get_ids()["current time label"]
        self.total_time_label = self.get_ids()["total time label"]
        self.name_track_label = self.get_ids()["name track label"]
        self.name_artist_label = self.get_ids()["name artist label"]
        self.loop_button = self.get_ids()["loop-button"]
        self.pause_button = self.get_ids()["pause-button"]
        # Инстанс SoundLoader.
        self.sound = None
        # Текущее тремя трека от 0 до 100%.
        self.current_time_track = 0
        # Зациклили ли пользователь воспроизведение трека.
        self.loop = False
        # Путь к текущему треку.
        self.path_to_current_track = ""
        # Слайдер громкости.
        self.volume_slider = MDSlider(
            MDSliderHandle(),
            MDSliderValueLabel(),
            step=10,
            value=50,
            size_hint_y=None,
            height=dp(200),
            orientation="vertical",
        )
        self.volume_slider.bind(value=self.on_value_volume_slider)
        # Флаг, открыт ли слайдер для установки громкости трека.
        self.is_volume_set = False
        # Текущая позиция трека при нажатии кнопки паузы.
        self.paused_position = 0
        # Выбран ли отдельный трек либо директория с музыкой.
        self.track_or_directory_music = "track"
        # Список треков из выбранной пользователем директория для
        # воспроизведения.
        self.list_tracks_music = []
        # текущий индекс трека из списка треков выбранной пользователем
        # директория для воспроизведения.
        self.index_tracks_music = 0
        self.heart_button = self.get_ids()["heart-button"]
        # Переключает ли пользователь треки вручную.x
        self.switch_tracks_manually = False
        # Если пользователь перемешал треки.
        self.shuffle = False

        self.instance_music_indicator.bind(
            on_touch_down=self.on_touch_down_music_indicator
        )

    def set_list_tracks_music(self, uri_list: list | str):
        """Устанавливает массив треков для воспроизведения."""

        ext = [".mp3"]
        self.list_tracks_music = []

        # Создает список файлов для воспроизведение из выбранной директории.
        if _platform == "desktop":
            for name_file in os.listdir(uri_list):
                if os.path.splitext(name_file)[1] in ext:
                    self.list_tracks_music.append(
                        os.path.join(uri_list, name_file)
                    )
        elif _platform == "android":
            for name_file in uri_list:
                if os.path.splitext(name_file)[1] in ext:
                    self.list_tracks_music.append(
                        os.path.join(sdcard("music"), name_file)
                    )

    def on_touch_down_music_indicator(self, instance_indicator, touch):
        """Метод вызывается при тапе по любому месту экрана."""

        # Если тап пришелся по индикатору прогресса трека.
        if instance_indicator.collide_point(*touch.pos) and self.sound:
            # Преобразовать значение позиции клика мыши в соответствующее
            # процентное значение от длинны слайдера длинны.
            click_percentage = (
                (touch.x - (self.width - instance_indicator.width) / 2)
                / instance_indicator.width
            ) * 100

            if _platform == "desktop":
                length = int(self.sound.length)
            elif _platform == "android":
                length = int(self.sound.get_duration() // 1000)

            # Время в секундах от процента клика по слайдеру.
            time_in_seconds = (click_percentage / 100) * length
            # Обновляем текущее значения длинны трека.
            self.current_time_track = length - time_in_seconds
            # Устанавливаем позицию воспроизведения трека.
            self.sound.seek(time_in_seconds)

    def on_value_volume_slider(self, instance_slider, value_slider):
        """
        Метод вызывается при изменении значения уровня громкости слайдера
        громкости.
        """

        if self.sound:
            self.sound.volume = value_slider / 100

    def on_tap_loop_button(self, path_to_track):
        """Метод вызывается при клике по кнопке 'loop'."""

        self.loop = not self.loop

        # Если пользователь зациклил трек:
        if self.loop:
            self.loop_button.color = "#fc0fc0"
        else:
            self.loop_button.color = "#d3d3d3"

    def on_tap_skip_previous_button(self, *args):
        """Метод вызывается при клике по кнопке 'skip-previous'."""

        print("on_tap_skip_previous_button", self.index_tracks_music)
        if self.track_or_directory_music == "archive":
            if self.index_tracks_music == 0:
                self.index_tracks_music = len(self.list_tracks_music) - 1
            else:
                self.index_tracks_music -= 1

            self.switch_tracks_manually = True
            self.play_music(self.list_tracks_music[self.index_tracks_music])

    def on_tap_skip_next_button(self, *args):
        """Метод вызывается при клике по кнопке 'skip-next'."""

        print("on_tap_skip_next_button")
        if self.track_or_directory_music == "archive":
            self.index_tracks_music += 1
            # if self.index_tracks_music >= 0:
            self.switch_tracks_manually = True
            self.play_music(self.list_tracks_music[self.index_tracks_music])

    def on_tap_pause_button(self, *args):
        """Метод вызывается при клике по кнопке 'pause'."""

        # Проверить выбран ли трек (если атрибут self.path_to_current_track)
        # пустая строка, перекинуть пользователя в файловый менеджер для
        # выбора трека - вызвать метод on_tap_playlist_music_button.
        # В зависимости от состояния трека self.sound.state - "play/stop")
        # изменить иконку объекта self.pause_button ("play/pause").
        # Остановить/продолжить воспроизведение трека.
        if not self.path_to_current_track:
            self.on_tap_playlist_music_button()
        else:
            if _platform == "desktop":
                state = self.sound.state  # "play"/"stop"
            elif _platform == "android":
                state = self.sound.is_playing()  # True/False

            if state == "play" or state is True:
                self.pause_button.icon = "pause"
                if _platform == "desktop":
                    self.paused_position = self.sound.get_pos()
                elif _platform == "android":
                    self.paused_position = self.sound.current_position() // 1000

                if _platform == "desktop":
                    self.sound.stop()
                elif _platform == "android":
                    self.sound.pause()
                Clock.unschedule(self.track_position)
            elif state == "stop" or not state:
                self.pause_button.icon = "play"
                if _platform == "desktop":
                    self.sound.seek(self.paused_position)
                    self.sound.play()

                elif _platform == "android":
                    self.sound.resume()

                Clock.schedule_interval(self.track_position, 1)

    def on_tap_archive_music_button(self, *args):
        """
        Метод вызывается при клике по кнопке 'archive-music'.
        Открывает интен для выбора директории с музыкой.
        """

        def exit_manager(*args):
            """
            Закрывает файловый менеждер, который был открыт для выбора
            директории с музыкой.
            """

            file_manager.close()

        def on_select_directory(uri_list: list | str):
            """Вызывается при выборе директории с музыкой."""

            def on_select_directory(*args):
                if self.list_tracks_music:
                    self.play_music(self.list_tracks_music[self.index_tracks_music])
                    screen_manager = MDApp.get_running_app().screen_manager
                    screen_manager.current = "music list"
                    instance_music_list = screen_manager.get_screen("music list")
                    instance_music_list.create_music_list(self.list_tracks_music)
                else:
                    MDSnackbar(
                        MDSnackbarText(
                            text="В директории нет музыкальных файлов",
                        ),
                        y=dp(24),
                        pos_hint={"center_x": 0.5},
                        size_hint_x=0.5,
                    ).open()

                if _platform == "desktop":
                    file_manager.close()

            self.track_or_directory_music = "archive"
            self.set_list_tracks_music(uri_list)
            Clock.schedule_once(on_select_directory, 0.2)

        is_tracks_selected = bool(self.list_tracks_music)

        # TODO: Ввести переменную is_tracks_selected и присвоить ей логическое значение не пуст ли
        #  список self.list_tracks_music.

        # Если платформа Android - запрашиваем права на чтение SD-карты
        # и воспроизведения аудио.
        if _platform == "android":

            def callback(permission, results):
                """Вызывается после подтверждения/не подтверждения прав."""

                if all([res for res in results]):
                    from modules.androidstorage import ChooserDir

                    chooser = ChooserDir(on_select_directory)
                    chooser.choose_dir()
                else:
                    print("Did not get all permissions", api_version)

            from android.permissions import Permission, request_permissions
            from android import api_version

            # TODO: Если is_tracks_selected это ложь, тогда открываем диалог для выбора директории музыки.
            #  Если истина, переключаем экран со списком треков.
            if not is_tracks_selected:
                # Запрашиваем права.
                permissions = [
                    (
                        Permission.READ_EXTERNAL_STORAGE
                        if api_version < 33
                        else Permission.READ_MEDIA_AUDIO
                    )
                ]
                request_permissions(permissions, callback)
            else:
                screen_manager = MDApp.get_running_app().screen_manager
                screen_manager.current = "music list"
        elif _platform == "desktop":
            # TODO: Если is_tracks_selected это ложь, тогда открываем диалог для выбора директории музыки.
            #  Если истина, переключаем экран со списком треков.
            if not is_tracks_selected:
                file_manager = MDFileManager(
                    exit_manager=exit_manager,
                    select_path=on_select_directory,
                    search="dirs",
                )
                file_manager.show(MDApp.get_running_app().user_data_dir)
            else:
                screen_manager = MDApp.get_running_app().screen_manager
                screen_manager.current = "music list"

    def on_tap_shuffle_button(self, instance, *args):
        if not self.list_tracks_music:
            MDSnackbar(
                MDSnackbarText(
                    text="Директория не выбрана",
                ),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.5,
            ).open()
        else:
            self.shuffle = not self.shuffle
            # Если пользователь перемешал треки:
            if self.shuffle:
                self.shuffle_button.color = "#fc0fc0"
                random.shuffle(self.list_tracks_music)
            else:
                self.shuffle_button.color = "#d3d3d3"

    def on_tap_playlist_music_button(self, *args):
        """Метод вызывается при клике по кнопке 'playlist-music'."""

        def exit_manager(*args):
            file_manager.close()

        def on_select_file(file_list: list | str):
            path_to_track = ""

            if _platform == "android":
                for uri in file_list:
                    shared_storage = SharedStorage()
                    path_to_track = shared_storage.copy_from_shared(uri)
            elif _platform == "desktop":
                path_to_track = file_list

            self.track_or_directory_music = "track"
            self.play_music(path_to_track)
            if _platform == "desktop":
                file_manager.close()

        # Если платформа Android - запрашиваем права на чтение SD-карты
        # и воспроизведения аудио.
        if _platform == "android":

            def callback(permission, results):
                """Вызывается после подтверждения/не подтверждения прав."""

                if all([res for res in results]):
                    from modules.androidstorage import Chooser

                    chooser = Chooser(on_select_file)
                    chooser.choose_content("audio/*")
                else:
                    print("Did not get all permissions", api_version)

            from android.permissions import Permission, request_permissions
            from android import api_version

            # Запрашиваем права.
            permissions = [
                (
                    Permission.READ_EXTERNAL_STORAGE
                    if api_version < 33
                    else Permission.READ_MEDIA_AUDIO
                )
            ]
            request_permissions(permissions, callback)
        elif _platform == "desktop":
            file_manager = MDFileManager(
                exit_manager=exit_manager,
                select_path=on_select_file,
                ext=[".mp3", ".ogg", ".wav"],
            )
            file_manager.show(MDApp.get_running_app().user_data_dir)

    def get_likes_list(self, *args):
        """
        Возвращает список путей к трекам, которыйе пользователь добавил в
        избранное.
        """

        config = MDApp.get_running_app().config
        likes = ast.literal_eval(config.get("General", "likes"))
        return likes

    def on_tap_heart_button(self, *args):
        """Метод вызывается при клике по кнопке 'heart'."""

        config = MDApp.get_running_app().config
        likes = ast.literal_eval(config.get("General", "likes"))

        # Проверить, находится ли текущий трек в списке избранных.
        if self.path_to_current_track in likes:
            # Удалить трек из списка избранных.
            likes.remove(self.path_to_current_track)
            self.heart_button.color = "#d3d3d3"
        else:
            # Добавить трек в список избранных.
            likes.append(self.path_to_current_track)
            self.heart_button.color = "#fc0fc0"

        # Установить и записать значение для параметра "likes" в
        # конфигурационном файле.
        config.set("General", "likes", str(likes))
        config.write()

    def reset_previous_values_track(self, stop_track=True):
        """
        Метод сбрасывает значения индикатора и времени воспроизводимого трека.
        """

        if stop_track:
            self.sound.stop()
            print("STOP")
        Clock.unschedule(self.track_position)
        self.instance_music_indicator.value = 0
        self.current_time_track = 0
        self.current_time_label.text = "0:00"

    def stop_music(self, *args):
        """Вызывается при остановке трека."""

        if self.loop and self.track_or_directory_music == "track":
            self.reset_previous_values_track()
            self.play_music(self.path_to_current_track)

        # Если воспроизводится директория с музыкой.
        if self.track_or_directory_music == "archive":
            self.reset_previous_values_track(False)
            if not self.switch_tracks_manually:
                self.index_tracks_music += 1
            # Проверяем не превышает ли индекс длинну списка треков.
            if self.index_tracks_music < len(self.list_tracks_music):
                self.play_music(self.list_tracks_music[self.index_tracks_music])
            # Если включено зациклевание, устанавливаем счетчик текущего трека
            # в 0.
            else:
                if not self.switch_tracks_manually:
                    self.index_tracks_music = 0
                if self.loop:
                    self.play_music(self.list_tracks_music[self.index_tracks_music])
        self.switch_tracks_manually = False

    def play_music(self, path_to_track):
        """Метод вызывается при выборе пользователем трека."""

        if self.sound:
            if _platform == "desktop":
                state = self.sound.state  # "play"/"stop"
            elif _platform == "android":
                state = self.sound.is_playing()  # True/False

        # Если трек уже воспроизводится, останавливаем воспроизведение.
        if self.sound and (state == "play" or state is True):
            self.reset_previous_values_track()
        # Загружаем новый трек.
        if _platform == "desktop":
            self.sound = SoundLoader.load(path_to_track)
        elif _platform == "android":
            self.sound = Player()

        if _platform == "desktop":
            # Если удалось загрузить трек.
            if self.sound:
                Clock.schedule_once(lambda x: self.sound.play(), 0.2)
            else:
                print("Не удалось загрузить трек")
        elif _platform == "android":
            # TODO: сделать проверку на ошибки воспроизведения.
            #  Найти возможность привязать окончание трека к методу
            #  self.stop_music.
            self.sound.play(path_to_track)

        self.path_to_current_track = path_to_track

        # TODO: Если self.path_to_current_track находится в списке избранного,
        #  измеить цвет кнопки "heart" на розовый. Если нет, изменить на
        #  дефолтный цвет (дефолтный цвет всять у кнопки "archive-music").

        # Устанавливаем обложку трека в плеере.
        # FIXME: При зацикленном треке обложка всегда извлекается и
        #  перезаписывается (исправими на следующем уроке).
        is_create_cover_album = self.save_album_art(path_to_track)
        if is_create_cover_album:
            self.cover_image.source = (
                f"{MDApp.get_running_app().user_data_dir}/album_art.jpg"
            )
        else:
            self.cover_image.source = "data/images/bg-default.jpg"

        # Перезагружаем изображение обложки.
        self.cover_image.reload()

        # Устанавливаем текст для метки self.total_time_label
        # (общее время трека в минутах).
        if _platform == "desktop":
            total_seconds = int(self.sound.length)
        elif _platform == "android":
            total_seconds = int(self.sound.get_duration() // 1000)

        minutes, seconds = divmod(total_seconds, 60)
        self.total_time_label.text = f"{minutes}:{str(seconds).zfill(2)}"

        # Устанавливаем название трека, имя атриста и название альбома.
        metadata = get_mp3_metadata(path_to_track)
        self.name_track_label.text = f"{metadata['artist']}, {metadata['title']}"
        self.name_artist_label.text = f"Альбом {metadata['album']}"

        # Запускаем метод self.track_position с интервалом в одну секунду.
        Clock.schedule_interval(self.track_position, 1)

    def track_position(self, interval):
        """
        Метод вызывается каждую секунду и устанавливает значение прогресса
        индикатора текущей длины трека в процентном соотношении.
        """

        if self.current_time_track == 0:
            if _platform == "desktop":
                self.current_time_track = self.sound.length - 1
            elif _platform == "android":
                self.current_time_track = int(self.sound.get_duration() // 1000) - 1
        else:
            self.current_time_track -= interval

        # Трек закончился.
        if self.current_time_track < 0:
            self.current_time_track = 0
            Clock.unschedule(self.track_position)
            self.stop_music()
            # TODO: Вызвать метод mark_current_track класса MusicList.

        # Устанавливаем позицию индикатора в процентах согласно длинны текущего
        # трека.
        if _platform == "desktop":
            percent_position = (self.current_time_track / self.sound.length) * 100
        elif _platform == "android":
            duration = self.sound.get_duration()
            if duration:
                percent_position = (
                    self.current_time_track / int(duration // 1000)
                ) * 100
            else:
                percent_position = 0
        self.instance_music_indicator.value = 100 - percent_position

        # Устанавливаем текст для метки self.current_time_label
        # (текущее время трека в минутах).
        current_minutes, current_seconds = divmod(int(self.current_time_track), 60)
        self.current_time_label.text = (
            f"-{current_minutes}:{str(current_seconds).zfill(2)}"
        )

    def save_album_art(self, mp3_file):
        """
        Метод сохраняет обложку альбома, если она существует в музыкальном
        файле.
        """

        # Переменная флаг найдена ои обложка альбома.
        exists_album = False

        try:
            audio = MP3(mp3_file, ID3=ID3)

            for tag in audio.tags.values():
                # Если обложка существует, сохраняем ее в файл album_art.jpg.
                if isinstance(tag, APIC):
                    with open(
                        f"{MDApp.get_running_app().user_data_dir}/album_art.jpg", "wb"
                    ) as f:
                        f.write(tag.data)
                        exists_album = True
                        break

            return exists_album
        except Exception:
            return exists_album
