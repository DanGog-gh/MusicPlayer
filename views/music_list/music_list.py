import ast
import os

from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.appbar import (
    MDTopAppBar,
    MDTopAppBarLeadingButtonContainer,
    MDActionTopAppBarButton,
    MDTopAppBarTitle,
)
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    MDListItem,
    MDListItemLeadingIcon,
    MDListItemHeadlineText,
    MDListItemSupportingText,
    MDListItemTrailingIcon,
)
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView

from modules.get_mp3_metadata import get_mp3_metadata


class MusicList(MDScreen):
    """Класс реализует экран со списком треков выбранной директории."""

    def __init__(self, *args, **kwargs):
        """Вызывается при создании экземпляра класса MusicList."""

        super().__init__(*args, **kwargs)
        self.add_widget(
            MDBoxLayout(
                MDRelativeLayout(
                    FitImage(
                        # id="cover image",
                        source="data/images/bg-default.jpg",
                        radius=(0, 0, dp(70), dp(70)),
                    ),
                    MDTopAppBar(
                        MDTopAppBarLeadingButtonContainer(
                            MDActionTopAppBarButton(
                                on_release=self.back_to_music_play,
                                icon="arrow-left",
                                pos_hint={"center_y": 1.4},
                                theme_icon_color="Custom",
                                icon_color="white",
                            )
                        ),
                        MDTopAppBarTitle(
                            id="current tracks directory",
                            pos_hint={"center_x": 0.4, "center_y": 1.4},
                            theme_text_color="Custom",
                            text_color="white",
                        ),
                        type="small",
                        theme_bg_color="Custom",
                        md_bg_color=[0, 0, 0, 0],
                        theme_shadow_color="Custom",
                        shadow_color=[0, 0, 0, 0],
                    ),
                    MDLabel(
                        id="number track label",
                        padding=[dp(20), 0, 0, 0],
                        theme_text_color="Custom",
                        text_color=[1, 1, 1, 0.6],
                        halign="center",
                        adaptive_size=True,
                        pos_hint={"center_y": 0.40},
                        font_style="TransformBold",
                        role="small",
                    ),
                    size_hint_y=None,
                    height=dp(145),
                    md_bg_color="#1e0438",
                ),
                # TODO: использовать RecycleView вместо ScrollView.
                MDScrollView(
                    MDBoxLayout(
                        id="box track",
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
                orientation="vertical",
            ),
        )

        # Инстансы виджетов.
        self.box_track: MDBoxLayout = self.get_ids()["box track"]
        self.number_track_label: MDBoxLayout = self.get_ids()["number track label"]
        # Объект MDListItem (трек, который воспроизводится в данный момент).
        self.current_play_track = None

    def on_tap_heart_button(self, instance, touch):
        """Метод вызывается при тапе по иконке в элемент трека"""

        if instance.collide_point(*touch.pos):
            track_id = instance.id
            self.toggle_like(instance, track_id.replace("heart like ", ""))

    def toggle_like(self, instance, track_id):
        """Метод для добавления/удаления трека из избранного"""

        config = MDApp.get_running_app().config
        likes = ast.literal_eval(config.get("General", "likes"))

        if track_id in likes:
            likes.remove(track_id)
            self.update_heart_button_color(instance, "#412060")
        else:
            likes.append(track_id)
            self.update_heart_button_color(instance, "#fc0fc0")

        config.set("General", "likes", str(likes))
        config.write()

    def update_heart_button_color(self, instance, color):
        """Метод для обновления цвета иконки"""

        instance.color = color

    def on_tap_music_track(self, instance_track):
        """Метод вызывается при тапе по элементу трека из списка треков."""

        self.manager.get_screen("music play").play_music(instance_track.id)
        self.current_play_track.md_bg_color = "#1e0438"
        self.mark_current_track()

    def back_to_music_play(self, *args):
        screen_manager = MDApp.get_running_app().screen_manager
        screen_manager.current = "music play"

    def create_music_list(self, music_list):
        """Метод добавляет элементы треков в список на экране."""

        config = MDApp.get_running_app().config
        likes = ast.literal_eval(config.get("General", "likes"))
        self.get_ids()[
            "number track label"
        ].text = f"Количество треков: {len(music_list)}"

        # Получаем путь к директории из которой воспроизводятся треки.
        dirname = os.path.dirname(music_list[0])
        # Устанавливаем имя директории из которой воспроизводятся треки.
        self.get_ids()["current tracks directory"].text = os.path.split(dirname)[-1]
        # Перед созданием списка треков очищаем контейнер от элементов.
        self.box_track.clear_widgets()

        for i, path_to_track in enumerate(music_list):
            # Устанавливаем название трека, имя артиста и название альбома.
            metadata = get_mp3_metadata(path_to_track)
            name_track = f"{metadata['artist']}, {metadata['title']}"
            name_artist = f"Альбом {metadata['album']}"

            self.box_track.add_widget(
                MDListItem(
                    MDListItemLeadingIcon(
                        icon="music",
                        theme_icon_color="Custom",
                        icon_color=[1, 1, 1, 0.6],
                    ),
                    MDListItemHeadlineText(
                        text=name_track, theme_text_color="Custom", text_color="white"
                    ),
                    MDListItemSupportingText(
                        text=name_artist,
                        theme_text_color="Custom",
                        text_color=[1, 1, 1, 0.6],
                    ),
                    MDListItemTrailingIcon(
                        id=f"heart like {path_to_track}",
                        icon="heart",
                        theme_icon_color="Custom",
                        icon_color="#412060" if path_to_track not in likes else "red",
                        on_touch_down=self.on_tap_heart_button,
                    ),
                    id=path_to_track,
                    theme_bg_color="Custom",
                    md_bg_color=self.md_bg_color,
                    on_release=self.on_tap_music_track,
                    radius=[
                        dp(12),
                    ],
                )
            )

        self.mark_current_track()

    def mark_current_track(self):
        """Подсвечивает трек, который воспроизводится в данный момент."""

        for id in self.get_ids().keys():
            if self.manager.get_screen("music play").path_to_current_track in id:
                self.get_ids()[id].parent.parent.md_bg_color = "#483D8B"
                self.current_play_track = self.get_ids()[id].parent.parent
                break
