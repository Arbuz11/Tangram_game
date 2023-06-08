import arcade
import arcade.gui
from arcade.gui import UIManager, UIAnchorWidget, UILabel
from arcade.experimental.uislider import UISlider
from arcade.gui.events import UIOnChangeEvent
from arcade.gui.widgets import UITextArea, UITexturePane
from arcade import load_texture
from pyglet.image import load as pyglet_load

WIDTH = 800
HEIGHT = 600

FADE_RATE = 15
faded = False

main_menu_pressed = False
game_mode_pressed = False
level_pressed = False
pause_pressed = False
settings_pressed = False

volume = 0.1

timer = "0"

selected_lvl = -1

rules = (
    "Правила игры Танграм заключаются в том, чтобы из 7 геометрических фигур собрать более сложную фигуру, при этом используя все 7 фигур так, чтобы они не накладывались друг на друга.\n\n"
    "Управление: для прокрутки данного текста вниз или вверх используйте колёсико мыши.\n\n"
    "Для перемещения фигуры необходимо навестись на необходимую фигуру, зажать левую или правую кнопку мыши и перемещать курсор.\n\n"
    "Для поворота фигуры нужно навестись на необходимую фигуру, зажать левую или правую кнопку мыши и нажимать на стрелки влево и вправо.\n\n"
    "Для настройки громкости звука необходимо зайти в меню 'Настройки' и затем двигать кружок на слайдере влево для уменьшения громкости или вправо для повышения громкости\n\n"
    "Для открытия паузы во время игры необходимо нажать клавишу ESCAPE на клавиатуре\n\n"
    "Для возвращения фигур на изначальное положение во время игры необходимо нажать на клавишу R на клавиатуре\n\n"
    "Для навигации в меню игры нужно использовать кнопки на экране, а для возвращения на прошлую часть меню кнопку ESCAPE."
)


class FadingView(arcade.View):
    def __init__(self):
        super().__init__()
        self.fade_out = None
        self.fade_in = 255

    def update_fade(self, next_view=None):
        if self.fade_out is not None:
            self.fade_out += FADE_RATE
            if self.fade_out is not None and self.fade_out > 255 and next_view is not None:
                game_view = next_view()
                game_view.setup()
                self.window.show_view(game_view)

        if self.fade_in is not None:
            self.fade_in -= FADE_RATE
            if self.fade_in <= 0:
                self.fade_in = None

    def draw_fading(self):
        if self.fade_out is not None:
            arcade.draw_rectangle_filled(self.window.width / 2, self.window.height / 2,
                                         self.window.width, self.window.height,
                                         (0, 0, 0, self.fade_out))

        if self.fade_in is not None:
            arcade.draw_rectangle_filled(self.window.width / 2, self.window.height / 2,
                                         self.window.width, self.window.height,
                                         (0, 0, 0, self.fade_in))


class MenuView(FadingView):

    def __init__(self):
        super().__init__()

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout()

        button_style = {
            "font_name": "Courier New",
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": arcade.color.WHITE,
            "bg_color": arcade.color.DARK_BLUE_GRAY,

            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.BLUE_GRAY,
            "font_color_pressed": arcade.color.BLACK
        }

        start_button = arcade.gui.UIFlatButton(text="Играть", width=200, style=button_style)
        self.v_box.add(start_button.with_space_around(bottom=20))

        settings_button = arcade.gui.UIFlatButton(text="Настройки", width=200, style=button_style)
        self.v_box.add(settings_button.with_space_around(bottom=20))

        rules_button = arcade.gui.UIFlatButton(text="Правила игры", width=200, style=button_style)
        self.v_box.add(rules_button.with_space_around(bottom=20))

        quit_button = arcade.gui.UIFlatButton(text="Выход", width=200, style=button_style)
        self.v_box.add(quit_button)

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

        self.background = arcade.Sprite(r"images/background.png")
        self.background.center_x = WIDTH / 2
        self.background.center_y = HEIGHT / 2

        self.click_sound = arcade.Sound("Sound/click_sound.mp3")

        start_button.on_click = self.on_click_start

        settings_button.on_click = self.on_click_settings

        rules_button.on_click = self.on_click_rules

        quit_button.on_click = self.on_click_quit

    def on_click_start(self, event):
        global main_menu_pressed, volume
        if not main_menu_pressed:
            self.click_sound.play(volume=volume)
            game_view = GameModeView()
            self.window.show_view(game_view)

    def on_click_settings(self, event):
        global main_menu_pressed, volume
        if not main_menu_pressed:
            self.click_sound.play(volume=volume)
            settings_view = SettingsView()
            self.window.show_view(settings_view)

    def on_click_rules(self, event):
        global main_menu_pressed, volume
        if not main_menu_pressed:
            self.click_sound.play(volume=volume)
            rules_view = RulesView()
            self.window.show_view(rules_view)

    def on_click_quit(self, event):
        global main_menu_pressed, volume
        if not main_menu_pressed:
            self.click_sound.play(volume=volume)
            arcade.exit()

    def on_show_view(self):
        global pause_pressed, game_mode_pressed, level_pressed, main_menu_pressed, settings_pressed
        arcade.set_background_color(arcade.color.WHITE)
        main_menu_pressed = False
        game_mode_pressed = True
        level_pressed = True
        pause_pressed = True
        settings_pressed = True

    def on_draw(self):
        """ Draw the menu """
        self.clear()
        self.background.draw()
        self.manager.draw()
        arcade.draw_text("Танграм", WIDTH / 2, HEIGHT - 100, arcade.color.GHOST_WHITE, 54, anchor_x="center", font_name="Courier New")
        self.draw_fading()

    def on_update(self, dt):
        self.update_fade()


class SettingsView(FadingView):
    def __init__(self):
        super().__init__()
        global volume

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout()

        self.background = arcade.Sprite(r"images/background.png")
        self.background.center_x = WIDTH / 2
        self.background.center_y = HEIGHT / 2

        ui_slider = UISlider(value=volume, width=300, height=50, min_value=0.00, max_value=5)
        label = UILabel(text=f"{ui_slider.value:00.1f}")

        @ui_slider.event()
        def on_change(event: UIOnChangeEvent):
            global volume, settings_pressed
            if not settings_pressed:
                label.text = f"{ui_slider.value:00.1f}"
                label.fit_content()
                volume = ui_slider.value

        self.manager.add(UIAnchorWidget(child=ui_slider))
        self.manager.add(UIAnchorWidget(child=label, align_y=100))

    def on_show_view(self):
        global main_menu_pressed
        global level_pressed
        global settings_pressed
        global game_mode_pressed
        global pause_pressed

        settings_pressed = False
        level_pressed = True
        game_mode_pressed = True
        main_menu_pressed = True
        pause_pressed = True

    def on_draw(self):
        self.clear()
        self.background.draw()
        self.manager.draw()

        arcade.draw_text("Настройки", WIDTH / 2, HEIGHT - 75, arcade.color.GHOST_WHITE, 54, anchor_x="center", font_name="Courier New")
        arcade.draw_text("Громкость звука", WIDTH / 2, HEIGHT - 400, arcade.color.GHOST_WHITE, 48, anchor_x="center",
                         font_name="Courier New")
        self.draw_fading()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            main_menu_view = MenuView()
            self.window.show_view(main_menu_view)

    def on_update(self, dt):
        self.update_fade()


class GameModeView(FadingView):

    def __init__(self):
        super().__init__()

        self.background = arcade.Sprite(r"images/background.png")
        self.background.center_x = WIDTH / 2
        self.background.center_y = HEIGHT / 2

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout()

        button_style = {
            "font_name": "Courier New",
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": arcade.color.WHITE,
            "bg_color": arcade.color.DARK_BLUE_GRAY,

            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.BLUE_GRAY,
            "font_color_pressed": arcade.color.BLACK
        }

        classic_button = arcade.gui.UIFlatButton(text="Классический", width=200, style=button_style)
        self.v_box.add(classic_button.with_space_around(bottom=20))

        free_button = arcade.gui.UIFlatButton(text="Творческий", width=200, style=button_style)
        self.v_box.add(free_button.with_space_around(bottom=20))

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

        self.click_sound = arcade.Sound("Sound/click_sound.mp3")

        classic_button.on_click = self.on_click_classic
        free_button.on_click = self.on_click_free

    def on_click_classic(self, event):
        global game_mode_pressed, volume
        if not game_mode_pressed:
            self.click_sound.play(volume=volume)
            level_view = LevelView()
            self.window.show_view(level_view)

    def on_click_free(self, event):
        global selected_lvl, volume, game_mode_pressed
        if not game_mode_pressed:
            self.click_sound.play(volume=volume)
            selected_lvl = 0
            tangram_game_view = TangrammGame()
            tangram_game_view.setup()
            self.window.show_view(tangram_game_view)

    def on_show_view(self):
        global level_pressed, settings_pressed, pause_pressed, game_mode_pressed, main_menu_pressed
        """ Called when switching to this view"""
        arcade.set_background_color(arcade.color.ORANGE_PEEL)
        game_mode_pressed = False
        main_menu_pressed = True
        level_pressed = True
        pause_pressed = True
        settings_pressed = True

    def on_draw(self):
        self.clear()
        self.background.draw()
        self.manager.draw()
        arcade.draw_text("Режим игры", WIDTH / 2, HEIGHT - 100, arcade.color.GHOST_WHITE, 54, anchor_x="center",
                         font_name="Courier New")
        self.draw_fading()

    def on_key_press(self, key, _modifiers):
        global main_menu_pressed
        if key == arcade.key.ESCAPE:
            menu_view = MenuView()
            self.window.show_view(menu_view)

    def on_update(self, dt):
        self.update_fade()


class LevelView(FadingView):

    def __init__(self):
        super().__init__()

        self.background = arcade.Sprite(r"images/background.png")
        self.background.center_x = WIDTH / 2
        self.background.center_y = HEIGHT / 2

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout()

        button_style = {
            "font_name": "Courier New",
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": arcade.color.WHITE,
            "bg_color": arcade.color.DARK_BLUE_GRAY,

            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.BLUE_GRAY,
            "font_color_pressed": arcade.color.BLACK
        }

        lvl1_button = arcade.gui.UIFlatButton(text="1", width=200, style=button_style)
        self.v_box.add(lvl1_button.with_space_around(bottom=20))

        lvl2_button = arcade.gui.UIFlatButton(text="2", width=200, style=button_style)
        self.v_box.add(lvl2_button.with_space_around(bottom=20))

        lvl3_button = arcade.gui.UIFlatButton(text="3", width=200, style=button_style)
        self.v_box.add(lvl3_button.with_space_around(bottom=20))

        lvl4_button = arcade.gui.UIFlatButton(text="4", width=200, style=button_style)
        self.v_box.add(lvl4_button.with_space_around(bottom=20))

        lvl5_button = arcade.gui.UIFlatButton(text="5", width=200, style=button_style)
        self.v_box.add(lvl5_button.with_space_around(bottom=20))

        lvl6_button = arcade.gui.UIFlatButton(text="6", width=200, style=button_style)
        self.v_box.add(lvl6_button.with_space_around(bottom=20))

        lvl7_button = arcade.gui.UIFlatButton(text="7", width=200, style=button_style)
        self.v_box.add(lvl7_button.with_space_around(bottom=20))

        lvl8_button = arcade.gui.UIFlatButton(text="8", width=200, style=button_style)
        self.v_box.add(lvl8_button.with_space_around(bottom=20))

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

        self.click_sound = arcade.Sound("Sound/click_sound.mp3")

        lvl1_button.on_click = self.on_click_1
        lvl2_button.on_click = self.on_click_2
        lvl3_button.on_click = self.on_click_3
        lvl4_button.on_click = self.on_click_4
        lvl5_button.on_click = self.on_click_5
        lvl6_button.on_click = self.on_click_6
        lvl7_button.on_click = self.on_click_7
        lvl8_button.on_click = self.on_click_8

    def on_click_1(self, event):
        global selected_lvl, volume, level_pressed
        if not level_pressed:
            self.click_sound.play(volume=volume)
            selected_lvl = 1
            tangram_game_view = TangrammGame()
            tangram_game_view.setup()
            self.window.show_view(tangram_game_view)

    def on_click_2(self, event):
        global selected_lvl, volume, level_pressed
        if not level_pressed:
            self.click_sound.play(volume=volume)
            selected_lvl = 2
            tangram_game_view = TangrammGame()
            tangram_game_view.setup()
            self.window.show_view(tangram_game_view)

    def on_click_3(self, event):
        global selected_lvl, volume, level_pressed
        if not level_pressed:
            self.click_sound.play(volume=volume)
            selected_lvl = 3
            tangram_game_view = TangrammGame()
            tangram_game_view.setup()
            self.window.show_view(tangram_game_view)

    def on_click_4(self, event):
        global selected_lvl, volume, level_pressed
        if not level_pressed:
            self.click_sound.play(volume=volume)
            selected_lvl = 4
            tangram_game_view = TangrammGame()
            tangram_game_view.setup()
            self.window.show_view(tangram_game_view)

    def on_click_5(self, event):
        global selected_lvl, volume, level_pressed
        if not level_pressed:
            self.click_sound.play(volume=volume)
            selected_lvl = 5
            tangram_game_view = TangrammGame()
            tangram_game_view.setup()
            self.window.show_view(tangram_game_view)

    def on_click_6(self, event):
        global selected_lvl, volume, level_pressed
        if not level_pressed:
            self.click_sound.play(volume=volume)
            selected_lvl = 6
            tangram_game_view = TangrammGame()
            tangram_game_view.setup()
            self.window.show_view(tangram_game_view)

    def on_click_7(self, event):
        global selected_lvl, volume, level_pressed
        if not level_pressed:
            self.click_sound.play(volume=volume)
            selected_lvl = 7
            tangram_game_view = TangrammGame()
            tangram_game_view.setup()
            self.window.show_view(tangram_game_view)

    def on_click_8(self, event):
        global selected_lvl, volume, level_pressed
        if not level_pressed:
            self.click_sound.play(volume=volume)
            selected_lvl = 8
            tangram_game_view = TangrammGame()
            tangram_game_view.setup()
            self.window.show_view(tangram_game_view)

    def on_show_view(self):
        global level_pressed, settings_pressed, pause_pressed, main_menu_pressed, game_mode_pressed
        arcade.set_background_color(arcade.color.BLACK)
        level_pressed = False
        game_mode_pressed = True
        main_menu_pressed = True
        pause_pressed = True
        settings_pressed = True

    def on_draw(self):
        self.clear()
        self.background.draw()
        self.manager.draw()
        arcade.draw_text("Выбор", WIDTH - 700, HEIGHT / 2, arcade.color.GHOST_WHITE, 54, anchor_y="center",
                         font_name="Courier New", rotation=90)
        arcade.draw_text("Уровня", WIDTH - 100, HEIGHT / 2, arcade.color.GHOST_WHITE, 54, anchor_y="center",
                         font_name="Courier New", rotation=-90)
        self.draw_fading()

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.ESCAPE:
            game_mode_view = GameModeView()
            self.window.show_view(game_mode_view)

    def on_update(self, dt):
        self.update_fade()


class RulesView(FadingView):
    def __init__(self):
        super().__init__()

        self.manager = UIManager()
        self.manager.enable()

        bg_tex = load_texture("images/rules_background.png")
        text_area = UITextArea(x=WIDTH / 2 - 300,
                               y=HEIGHT / 2 - 250,
                               width=600,
                               height=400,
                               text=rules,
                               text_color=(255, 255, 255, 255),
                               font_name="Courier New",
                               font_size=25)
        self.manager.add(
            UITexturePane(
                text_area.with_space_around(right=20),
                tex=bg_tex,
                padding=(10, 10, 10, 10)
            )
        )

        self.background = arcade.Sprite(r"images/background.png")
        self.background.center_x = WIDTH / 2
        self.background.center_y = HEIGHT / 2

    def on_draw(self):
        self.clear()
        self.background.draw()
        self.manager.draw()
        arcade.draw_text("Правила игры", WIDTH / 2, HEIGHT - 85, arcade.color.GHOST_WHITE, 54, anchor_x="center", font_name="Courier New")
        self.draw_fading()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            menu_view = MenuView()
            self.window.show_view(menu_view)

    def on_show_view(self):
        global pause_pressed, settings_pressed
        global game_mode_pressed
        global level_pressed
        global main_menu_pressed
        main_menu_pressed = True
        game_mode_pressed = True
        level_pressed = True
        pause_pressed = True
        settings_pressed = True

    def on_update(self, dt):
        self.update_fade()


class TangrammGame(arcade.View):
    def __init__(self):
        super().__init__()

        arcade.set_background_color([255, 255, 255])

        self.figures = []
        self.figures.append(arcade.Sprite("images/game_background.png", 1))

        if selected_lvl == 0:
            self.figures.append(arcade.Sprite("images/nobg.png", 0.0001))
        elif selected_lvl == 1:
            self.figures.append(arcade.Sprite("images/lvls/1.png", 0.32, hit_box_algorithm="Detailed"))
        elif selected_lvl == 2:
            self.figures.append(arcade.Sprite("images/lvls/2.png", 0.3, hit_box_algorithm="Detailed"))
        elif selected_lvl == 3:
            self.figures.append(arcade.Sprite("images/lvls/3.png", 0.43, hit_box_algorithm="Detailed"))
        elif selected_lvl == 4:
            self.figures.append(arcade.Sprite("images/lvls/4.png", 0.55, hit_box_algorithm="Detailed"))
        elif selected_lvl == 5:
            self.figures.append(arcade.Sprite("images/lvls/5.png", 0.32, hit_box_algorithm="Detailed"))
        elif selected_lvl == 6:
            self.figures.append(arcade.Sprite("images/lvls/6.png", 0.39, hit_box_algorithm="Detailed"))
        elif selected_lvl == 7:
            self.figures.append(arcade.Sprite("images/lvls/7.png", 0.38, hit_box_algorithm="Detailed"))
        elif selected_lvl == 8:
            self.figures.append(arcade.Sprite("images/lvls/8.png", 0.409, hit_box_algorithm="Detailed"))

        self.figures.append(arcade.Sprite("images/big_tr_1.png", 0.15))
        self.figures.append(arcade.Sprite("images/big_tr_2.png", 0.15))
        self.figures.append(arcade.Sprite("images/sqr.png", 0.15))
        self.figures.append(arcade.Sprite("images/prl.png", 0.15))
        self.figures.append(arcade.Sprite("images/mid_tr.png", 0.15))
        self.figures.append(arcade.Sprite("images/sml_tr_1.png", 0.15))
        self.figures.append(arcade.Sprite("images/sml_tr_2.png", 0.15))

        self.reset_figures()

        self.total_time = 0.0
        self.timer_text = arcade.Text(
            text="00:00:00",
            start_x=WIDTH - 400,
            start_y=HEIGHT - 50,
            color=arcade.color.WHITE,
            font_size=30,
            anchor_x="center")

        self.FigureSoundPickUp = arcade.Sound(r"Sound\FigureSoundPickUp.mp3")
        self.FigureSoundPutDown = arcade.Sound(r"Sound\FigureSoundPutDown.mp3")

        self.media_player = None
        if selected_lvl % 2 == 0:
            self.background_music_1 = arcade.Sound(r"Sound\background_music_1.mp3")
        else:
            self.background_music_1 = arcade.Sound(r"Sound\background_music_2.mp3")

        self.victory_sound = arcade.Sound(r"Sound\victory_sound.mp3")

        self.level_completed = False

        self.mouse_clicked = False

    def setup(self):
        self.total_time = 0.0

    def on_show_view(self):
        global volume
        global main_menu_pressed, settings_pressed
        global pause_pressed
        global selected_lvl
        global game_mode_pressed
        global level_pressed
        main_menu_pressed = True
        game_mode_pressed = True
        level_pressed = True
        pause_pressed = True
        settings_pressed = True
        if selected_lvl > 0:
            level_pressed = True
        if selected_lvl == 0:
            game_mode_pressed = True
        self.media_player = self.background_music_1.play(volume=volume, loop=True)

    def check_level_completed(self):
        # условие 1: Все маленькие фигуры находятся внутри большой фигуры
        for i in range(2, 9):
            sprite = self.figures[i]
            if not (self.figures[1].collides_with_point([sprite.center_x, sprite.center_y]) and any(
                    sprite.collides_with_sprite(self.figures[j]) for j in range(2, 9) if j != i)):
                print("1")
                return False

        # условие 2: Все маленькие фигуры не накладываются друг на друга
        proximity_threshold = 51

        for i in range(2, 9):
            for j in range(i + 2, 9):
                if (
                        abs(self.figures[i].center_x - self.figures[j].center_x) < proximity_threshold
                        and abs(self.figures[i].center_y - self.figures[j].center_y) < proximity_threshold
                ):
                    print("2")
                    return False

        for i in range(2, 9):
            for j in range(2, 9):
                if j != i:
                    if self.figures[i].collides_with_point([self.figures[j].center_x, self.figures[j].center_y]):
                        print("3")
                        return False

        return True

    def reset_figures(self):
        for i in range(2, 9):
            self.figures[i].center_x = 15 + i * 90
            self.figures[i].center_y = 100
            self.figures[i].dragging = False
            self.figures[i].angle = 0
        self.figures[1].center_x = 400
        self.figures[1].center_y = 300
        self.figures[0].center_x = WIDTH / 2
        self.figures[0].center_y = HEIGHT / 2
        self.figures[2].angle = 180
        self.figures[3].angle = 180
        self.figures[5].angle = 90
        self.figures[6].angle = -135

    def on_draw(self):
        self.clear()
        arcade.start_render()
        for figure in self.figures:
            figure.draw()
        self.timer_text.draw()

    def on_update(self, delta_time):
        global timer
        if self.mouse_clicked:
            if not self.level_completed:
                self.total_time += delta_time

                minutes = int(self.total_time) // 60

                seconds = int(self.total_time) % 60

                seconds_100s = int((self.total_time - seconds) * 100)

                self.timer_text.text = f"{minutes:02d}:{seconds:02d}:{int(seconds_100s) % 100:02d}"
                timer = self.timer_text.text

    def on_mouse_press(self, x, y, button, modifiers):
        global volume
        for i in range(8, 1, -1):
            if self.figures[i].collides_with_point((x, y)):
                self.mouse_clicked = True
                self.FigureSoundPickUp.play(volume=volume)
                self.figures[i].dragging = True
                self.figures[i].offset_x = self.figures[i].center_x - x
                self.figures[i].offset_y = self.figures[i].center_y - y
                break

    def on_mouse_release(self, x, y, button, modifiers):
        global volume
        for i in range(2, 9):
            if self.figures[i].dragging:
                self.FigureSoundPutDown.play(volume=volume)
                self.figures[i].dragging = False
                if self.figures[i].center_x > WIDTH - 100:
                    self.figures[i].center_x = WIDTH - 100
                if self.figures[i].center_y > HEIGHT - 100:
                    self.figures[i].center_y = HEIGHT - 100
                if self.figures[i].center_x < 100:
                    self.figures[i].center_x = 100
                if self.figures[i].center_y < 100:
                    self.figures[i].center_y = 100

        if self.check_level_completed() and not self.level_completed:
            game_over_view = GameOverView()
            game_over_view.timer = self.timer_text
            self.window.show_view(game_over_view)
            self.background_music_1.stop(self.media_player)
            self.victory_sound.play(volume=volume)
            self.level_completed = True

    def on_mouse_motion(self, x, y, dx, dy):
        for i in range(2, 9):
            if self.figures[i].dragging:
                self.figures[i].center_x = x + self.figures[i].offset_x
                self.figures[i].center_y = y + self.figures[i].offset_y

    def on_key_press(self, key, modifiers):

        if key == arcade.key.R:
            self.reset_figures()

        if key == arcade.key.LEFT:
            for i in range(2, 9):
                if self.figures[i].dragging:
                    self.figures[i].angle += 45

        if key == arcade.key.RIGHT:
            for i in range(2, 9):
                if self.figures[i].dragging:
                    self.figures[i].angle -= 45

        if key == arcade.key.ESCAPE:
            for i in range(2, 9):
                if self.figures[i].dragging:
                    self.figures[i].dragging = False
            self.media_player.pause()
            pause_view = PauseView(self)
            self.window.show_view(pause_view)


class PauseView(arcade.View):
    def __init__(self, tangram_game_view):
        super().__init__()
        self.tangram_game_view = tangram_game_view

        self.background = arcade.Sprite(r"images/background.png")
        self.background.center_x = WIDTH / 2
        self.background.center_y = HEIGHT / 2

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout()

        button_style = {
            "font_name": "Courier New",
            "font_size": 15,
            "font_color": arcade.color.WHITE,
            "border_width": 2,
            "border_color": arcade.color.WHITE,
            "bg_color": arcade.color.DARK_BLUE_GRAY,

            "bg_color_pressed": arcade.color.WHITE,
            "border_color_pressed": arcade.color.BLUE_GRAY,
            "font_color_pressed": arcade.color.BLACK
        }

        continue_button = arcade.gui.UIFlatButton(text="Продолжить", width=200, style=button_style)
        self.v_box.add(continue_button.with_space_around(bottom=20))

        restart_button = arcade.gui.UIFlatButton(text="Перезапуск", width=200, style=button_style)
        self.v_box.add(restart_button.with_space_around(bottom=20))

        exit_button = arcade.gui.UIFlatButton(text="Выход", width=200, style=button_style)
        self.v_box.add(exit_button.with_space_around(bottom=20))

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

        self.click_sound = arcade.Sound("Sound/click_sound.mp3")

        continue_button.on_click = self.on_click_continue
        restart_button.on_click = self.on_click_restart
        exit_button.on_click = self.on_click_exit

    def on_click_continue(self, event):
        global pause_pressed, volume
        if not pause_pressed:
            self.click_sound.play(volume=volume)
            self.window.show_view(self.tangram_game_view)

    def on_click_exit(self, event):
        global pause_pressed, volume
        global selected_lvl
        if not pause_pressed:
            if selected_lvl > 0:
                self.click_sound.play(volume=volume)
                level_view = LevelView()
                self.window.show_view(level_view)
            if selected_lvl == 0:
                self.click_sound.play(volume=volume)
                game_mode_view = GameModeView()
                self.window.show_view(game_mode_view)

    def on_click_restart(self, event):
        global pause_pressed, volume
        if not pause_pressed:
            self.click_sound.play(volume=volume)
            tangram_game_view = TangrammGame()
            tangram_game_view.setup()
            self.window.show_view(tangram_game_view)

    def on_show_view(self):
        global pause_pressed, settings_pressed
        global main_menu_pressed
        global level_pressed
        global game_mode_pressed
        pause_pressed = False
        main_menu_pressed = True
        game_mode_pressed = True
        level_pressed = True
        settings_pressed = True
        arcade.set_background_color(arcade.color.ORANGE)

    def on_draw(self):
        self.clear()

        self.background.draw()

        arcade.draw_text("Пауза", WIDTH / 2, HEIGHT - 75,
                         arcade.color.GHOST_WHITE, font_size=50, anchor_x="center", font_name="Courier New")

        self.manager.draw()


class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()

        global timer

        self.background = arcade.Sprite(r"images/background.png")
        self.background.center_x = WIDTH / 2
        self.background.center_y = HEIGHT / 2

    def on_show_view(self):
        global level_pressed
        global main_menu_pressed
        global game_mode_pressed
        global pause_pressed
        global settings_pressed
        arcade.set_background_color(arcade.color.BLACK)
        pause_pressed = True
        main_menu_pressed = True
        game_mode_pressed = True
        level_pressed = True
        settings_pressed = True

    def on_draw(self):
        self.clear()

        self.background.draw()

        arcade.draw_text("Вы победили !", WIDTH / 2, HEIGHT - 125, arcade.color.LIGHT_SKY_BLUE, 54, anchor_x="center", font_name="Courier New")
        arcade.draw_text("Нажмите ESCAPE для выхода в меню", WIDTH / 2, HEIGHT / 1.5, arcade.color.GHOST_WHITE, 20, anchor_x="center", font_name="Courier New")
        arcade.draw_text("или", WIDTH / 2, HEIGHT / 1.72, arcade.color.GHOST_WHITE, 20, anchor_x="center", font_name="Courier New")
        arcade.draw_text("нажмите на кнопку мыши для перезапуска", WIDTH / 2, HEIGHT / 2, arcade.color.GHOST_WHITE, 20, anchor_x="center", font_name="Courier New")
        arcade.draw_text(timer, WIDTH / 2, HEIGHT / 3, arcade.color.LIGHT_SKY_BLUE, 46, anchor_x="center", font_name="Courier New")
        arcade.draw_text("Время прохождения уровня", WIDTH / 2, HEIGHT / 4, arcade.color.GHOST_WHITE, 26, anchor_x="center", font_name="Courier New")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        tangram_game_view = TangrammGame()
        tangram_game_view.setup()
        self.window.show_view(tangram_game_view)

    def on_key_press(self, key, modifiers):
        global selected_lvl
        if key == arcade.key.ESCAPE:
            if selected_lvl > 0:
                level_view = LevelView()
                self.window.show_view(level_view)
            if selected_lvl == 0:
                game_mode_view = GameModeView()
                self.window.show_view(game_mode_view)


def main():
    window = arcade.Window(WIDTH, HEIGHT, "Танграм")
    window.set_icon(pyglet_load("images/icon.ico"))
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()