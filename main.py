import os

from kivy import platform

if platform in ["win", "linux", "macosx"]:
    os.environ['KIVY_AUDIO'] = 'ffpyplayer'

from kivy import Config
from kivy.core.text import LabelBase
from kivy.metrics import sp

# Установка размеров корневого окна приложения.
Config.set("graphics", "width", "420")
Config.set("graphics", "height", "780")

# Импорт двух классов экранов приложения.
from views.music_list.music_list import MusicList
from views.music_play.music_play import MusicPlay

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.utils.set_bars_colors import set_bars_colors
from kivy.utils import get_color_from_hex


# Главный класс приложения.
class MusicPlayer(MDApp):
    def build(self):
        """Запускаться при старте приложения."""

        # Устанавливаем цвет системных верхней и нижней панелей инструментов.
        set_bars_colors(
            get_color_from_hex("#1e0438"),
            get_color_from_hex("#1e0438"),
            "Light",
        )

        # Регистрация стилей шрифта.
        LabelBase.register(
            name="TransformBold",
            fn_regular="data/fonts/TransformaSans/TransformaSans_Trial-Bold.ttf",
        )
        LabelBase.register(
            name="TransformMedium",
            fn_regular="data/fonts/TransformaSans/TransformaSans_Trial-Medium.ttf",
        )
        self.theme_cls.font_styles["TransformBold"] = {
            "large": {
                "line-height": 1,
                "font-name": "TransformBold",
                "font-size": sp(24),
            },
            "medium": {
                "line-height": 1,
                "font-name": "TransformBold",
                "font-size": sp(20),
            },
            "small": {
                "line-height": 1,
                "font-name": "TransformBold",
                "font-size": sp(14),
            },
        }
        self.theme_cls.font_styles["TransformMedium"] = {
            "large": {
                "line-height": 1,
                "font-name": "TransformMedium",
                "font-size": sp(24),
            },
            "medium": {
                "line-height": 1,
                "font-name": "TransformMedium",
                "font-size": sp(20),
            },
            "small": {
                "line-height": 1,
                "font-name": "TransformMedium",
                "font-size": sp(14),
            },
        }

        # Создаем экранный менеджер приложения и добавляем в него два экрана
        # (экран проигрывания музыки и экран списка треков).
        self.screen_manager = MDScreenManager(
            MusicPlay(
                name="music play",
            ),
            MusicList(
                name="music list",
            ),
        )
        # Возвращаем экранный менеджер, который отобразится на девайсе
        # пользователя и покажет первый добавленный в него экран.
        return self.screen_manager

    def get_application_config(self) -> str:
        """Возвращает путь к файлу конфигурации."""

        try:
            my_app_conf = super().get_application_config(
                "{}/%(appname)s.ini".format(self.user_data_dir)
            )
        except PermissionError:
            my_app_conf = super().get_application_config(
                "{}/%(appname)s.ini".format(self.directory)
            )

        return my_app_conf

    def build_config(self, config):
        """Создает файл настроек musicplayer.ini."""

        config.adddefaultsection("General")
        config.setdefault("General", "likes", [])


MusicPlayer().run()
