import os

from kivy import platform

if platform in ["win", "linux", "macosx"]:
    os.environ["KIVY_AUDIO"] = "ffpyplayer"
elif platform == "android":
    from android import mActivity
    from jnius import autoclass, cast

from kivy import Config
from kivy.core.text import LabelBase
from kivy.metrics import sp

# Установка размеров корневого окна приложения.
Config.set("graphics", "width", "420")
Config.set("graphics", "height", "780")

# Импорт двух классов экранов приложения.
from views.music_list.music_list import MusicList
from views.music_play.music_play import MusicPlay

# Импорт классов библиотеки KivyMD.
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.utils.set_bars_colors import set_bars_colors
from kivy.utils import get_color_from_hex

# Импорт классов для работы с сервисом.
from oscpy.client import OSCClient
from oscpy.server import OSCThreadServer


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

    def on_start(self):
        """
        Метод вызывается при открытии (когда загрузился первый экран)
        приложения.
        """

        def callback(permission, results):
            """Вызывается после подтверждения/не подтверждения прав."""

            if all([res for res in results]):
                server = OSCThreadServer()
                server.listen(address=b"localhost", port=3002, default=True)
                server.bind(b"/track_state", self.track_state)
                self.client = OSCClient(b"localhost", 3000)
                self.query_service_state()
            else:
                print("Did not get all permissions", api_version)

        if platform == "android":
            from android.permissions import Permission, request_permissions
            from android import api_version

            # Запрашиваем права.
            permissions = [Permission.FOREGROUND_SERVICE]
            request_permissions(permissions, callback)

    def on_pause(self):
        """Метод вызывается, когда приложение сворачивается в трей."""

        self.client.send_message(b"/service_state", [])
        return True

    def on_resume(self):
        """
        Метод вызывается, когда приложение восстанавливают из трея
        (свернутое состояние приложения).
        """

        self.query_service_state()

    # ---------------------------- Track Metadata -----------------------------

    def track_state(self, *Args):
        print("track_state")

    # --------------------------- Состояние сервиса ---------------------------

    def get_service_name(self):
        context = mActivity.getApplicationContext()
        return str(context.getPackageName()) + ".Service" + "Mediaplayer"

    def service_is_running(self):
        print("service_is_running")
        service_name = self.get_service_name()
        context = mActivity.getApplicationContext()
        print("service_name", service_name)
        manager = cast(
            "android.app.ActivityManager",
            mActivity.getSystemService(context.ACTIVITY_SERVICE),
        )
        print("manager", manager)
        for service in manager.getRunningServices(100):
            print(
                "service.service.getClassName()",
                service_name,
                service.service.getClassName() == service_name,
            )
            if service.service.getClassName() == service_name:
                return True
        return False

    def start_service_if_not_running(self):
        service_is_running = self.service_is_running()
        print("start_service_if_not_running", service_is_running)

        if service_is_running:
            return
        service = autoclass(self.get_service_name())
        # service.start(
        #     mActivity, "round_music_note_white_24", "Music Service", "Started", ""
        # )
        service.start(mActivity, '')
        print("START SERVICE", service)

    def query_service_state(self):
        service_is_running = self.service_is_running()
        print("query_service_state", service_is_running)

        if service_is_running:
            print("query_service_state 1")
            self.client.send_message(b"/service_state", [])
        else:
            print("query_service_state 2")
            self.start_service_if_not_running()
            # self.set_play()
            # self.set_album_art(None)

    # -------------------------------------------------------------------------


MusicPlayer().run()


""""""