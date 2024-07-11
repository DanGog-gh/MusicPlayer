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

# Имя пакета приложения для запуска фоновой службы.
SERVICE_NAME = u'{packagename}.Service{servicename}'.format(
    packagename=u'org.lesson.musicplayer',
    servicename=u'Mediaplayerservice'
)

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

        def start_service():
            self.service = None
            self.server = server = OSCThreadServer()
            server.listen(
                address=b'localhost',
                port=3002,
                default=True,
            )
            # server.bind(b'/message', self.display_message)
            server.bind(b'/date', self.date)
            self.start_service()

        def callback(permission, results):
            """Вызывается после подтверждения/не подтверждения прав."""

            if all([res for res in results]):
                start_service()

                self.client = OSCClient(b'localhost', 3000)
            else:
                print("Did not get all permissions", api_version)

        if platform == "android":
            from android.permissions import Permission, request_permissions
            from android import api_version

            # Запрашиваем права.
            permissions = [Permission.FOREGROUND_SERVICE]
            request_permissions(permissions, callback)
        else:
            start_service()

    def on_pause(self):
        """Метод вызывается, когда приложение сворачивается в трей."""

        return True

    def on_resume(self):
        """
        Метод вызывается, когда приложение восстанавливают из трея
        (свернутое состояние приложения).
        """

    def start_service(self):
        """Запускает фоновую службу."""

        if platform == 'android':
            service = autoclass(SERVICE_NAME)
            self.mActivity = autoclass(u'org.kivy.android.PythonActivity').mActivity
            argument = ''
            service.start(self.mActivity, argument)
            self.service = service
        elif platform in ('linux', 'linux2', 'macosx', 'win'):
            from runpy import run_path
            from threading import Thread
            self.service = Thread(
                target=run_path,
                args=['service.py'],
                kwargs={'run_name': '__main__'},
                daemon=True
            )
            self.service.start()
        else:
            raise NotImplementedError(
                "service start not implemented on this platform"
            )

    def stop_service(self):
        """Останавливает фоновую службу."""

        if self.service:
            if platform == "android":
                self.service.stop(self.mActivity)
            elif platform in ('linux', 'linux2', 'macos', 'win'):
                # The below method will not work.
                # Need to develop a method like
                # https://www.oreilly.com/library/view/python-cookbook/0596001673/ch06s03.html
                self.service.stop()
            else:
            	raise NotImplementedError(
                	"service start not implemented on this platform"
            	)

            self.service = None

    def send(self, *args):
        self.client.send_message(b'/ping', [])

    def display_message(self, message):
        if self.root:
            self.root.ids.label.text += '{}\n'.format(message.decode('utf8'))

    def date(self, message):
        if self.root:
            self.root.ids.date.text = message.decode('utf8')


MusicPlayer().run()



# coding: utf8
# __version__ = '0.2'
#
# from kivy.app import App
# from kivy.lang import Builder
# from kivy.clock import Clock
# from kivy.utils import platform
#
# if platform == "android":
#     from jnius import autoclass
#
# from oscpy.client import OSCClient
# from oscpy.server import OSCThreadServer
#
#
# SERVICE_NAME = u'{packagename}.Service{servicename}'.format(
#     packagename=u'org.lesson.musicplayer',
#     servicename=u'Mediaplayerservice'
# )
#
# KV = '''
# BoxLayout:
#     orientation: 'vertical'
#     BoxLayout:
#         size_hint_y: None
#         height: '30sp'
#         Button:
#             text: 'start service'
#             on_press: app.start_service()
#         Button:
#             text: 'stop service'
#             on_press: app.stop_service()
#
#     ScrollView:
#         Label:
#             id: label
#             size_hint_y: None
#             height: self.texture_size[1]
#             text_size: self.size[0], None
#
#     BoxLayout:
#         size_hint_y: None
#         height: '30sp'
#         Button:
#             text: 'ping'
#             on_press: app.send()
#         Button:
#             text: 'clear'
#             on_press: label.text = ''
#         Label:
#             id: date
#
# '''
#
# class ClientServerApp(App):
#     def build(self):
#         self.service = None
#         # self.start_service()
#
#         self.server = server = OSCThreadServer()
#         server.listen(
#             address=b'localhost',
#             port=3002,
#             default=True,
#         )
#
#         server.bind(b'/message', self.display_message)
#         server.bind(b'/date', self.date)
#
#         self.client = OSCClient(b'localhost', 3000)
#         self.root = Builder.load_string(KV)
#         return self.root
#
#     def start_service(self):
#         if platform == 'android':
#             service = autoclass(SERVICE_NAME)
#             self.mActivity = autoclass(u'org.kivy.android.PythonActivity').mActivity
#             argument = ''
#             service.start(self.mActivity, argument)
#             self.service = service
#
#         elif platform in ('linux', 'linux2', 'macosx', 'win'):
#             from runpy import run_path
#             from threading import Thread
#             self.service = Thread(
#                 target=run_path,
#                 args=['service.py'],
#                 kwargs={'run_name': '__main__'},
#                 daemon=True
#             )
#             self.service.start()
#         else:
#             raise NotImplementedError(
#                 "service start not implemented on this platform"
#             )
#
#     def stop_service(self):
#         if self.service:
#             if platform == "android":
#                 self.service.stop(self.mActivity)
#             elif platform in ('linux', 'linux2', 'macos', 'win'):
#                 # The below method will not work.
#                 # Need to develop a method like
#                 # https://www.oreilly.com/library/view/python-cookbook/0596001673/ch06s03.html
#                 self.service.stop()
#             else:
#             	raise NotImplementedError(
#                 	"service start not implemented on this platform"
#             	)
#             self.service = None
#
#     def send(self, *args):
#         self.client.send_message(b'/ping', [])
#
#     def display_message(self, message):
#         if self.root:
#             self.root.ids.label.text += '{}\n'.format(message.decode('utf8'))
#
#     def date(self, message):
#         if self.root:
#             self.root.ids.date.text = message.decode('utf8')
#
#
# if __name__ == '__main__':
#     ClientServerApp().run()
