import arcade

from platform_tutorial.constants import SCREEN_WIDTH, SCREEN_HEIGHT


class CutScene:
    def __init__(self, viewport, player):
        self.viewport = viewport
        self.player = player

    def start_animation(self):
        pass

    def stop_animation(self):
        pass

    def is_completed(self):
        return False

    def draw(self):
        pass

    def update(self, delta_time):
        pass


class TimeLineCutScene(CutScene):
    def __init__(self, viewport, player, end_timer=-1):
        super().__init__(viewport, player)
        self.events = []
        self.timer: float = 0
        self.end_timer: float = end_timer
        self.cur_update = None
        self.cur_draw = None

    def add_event(self, trigger_time, update_func, draw_func):
        self.events.append([trigger_time, update_func, draw_func])

    def update(self, delta_time):
        self.timer += delta_time
        self.cur_update = None
        self.cur_draw = None
        for trigger_time, update_func, draw_func in self.events:
            if trigger_time <= self.timer:
                self.cur_update = update_func
                self.cur_draw = draw_func
            else:
                break
        if self.cur_update:
            self.cur_update(delta_time)
        if self.is_completed():
            self.stop_animation()

    def draw(self):
        if self.cur_draw:
            self.cur_draw()

    def is_completed(self):
        return 0 < self.end_timer <= self.timer


class GameOver(CutScene):
    def __init__(self, viewport, player, damager=None):
        super().__init__(viewport, player)
        self.game_over_count_down: float = 0
        self.damager = damager
        self.game_over = arcade.load_sound("sounds/gameover1.wav")

    def start_animation(self):
        arcade.play_sound(self.game_over)
        self.game_over_count_down = 2
        self.player.start_dying_animation()

    def stop_animation(self):
        self.game_over_count_down = 0
        self.player.reset()
        self.viewport.reset()

    def is_completed(self):
        return self.game_over_count_down <= 0

    def draw(self):
        self.viewport.shade()
        self.viewport.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.csscolor.WHITE, 50,
                                anchor_x="center", anchor_y="center")

    def update(self, delta_time):
        """ Movement and game logic """
        if self.game_over_count_down > 0:
            self.game_over_count_down -= delta_time
            if self.is_completed():
                self.stop_animation()
            else:
                self.player.update_dying_animation(self.damager)


class Intro(TimeLineCutScene):
    def __init__(self, viewport, player):
        super().__init__(viewport, player, 9)
        self.add_event(0, None, self.draw_text_1)
        self.add_event(3, self.update_scrolling, None)
        self.add_event(6, self.update_text_2, self.draw_text_2)
        self.girl = arcade.Sprite("images/adventure_girl/Adventure.png")
        self.girl.left = 0
        self.girl.bottom = 0

    def draw_text_1(self):
        self.girl.draw()
        self.viewport.draw_bubble(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, 500, 50, arcade.csscolor.WHITE_SMOKE)
        self.viewport.draw_text("Le village est attaqué par des monstres !!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, arcade.csscolor.LIGHT_SKY_BLUE, 20,
                                anchor_x="center", anchor_y="center")

    def draw_text_2(self):
        self.viewport.draw_bubble(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, 400, 50, arcade.csscolor.WHITE_SMOKE)
        self.viewport.draw_text("Va chercher une arme !!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100, arcade.csscolor.LIGHT_SKY_BLUE, 20,
                                anchor_x="center", anchor_y="center")

    def update_scrolling(self, delta_time):
        self.viewport.set(self.viewport.view_left + 5, 0)
        self.player.update_animation()

    def update_text_2(self, delta_time):
        self.player.update_animation()

    def start_animation(self):
        self.viewport.set(0, 0)
        self.player.update_animation()
