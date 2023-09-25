from game_entities import Ball, AIPaddle, PlayerPaddle
from oven_engine.base_app import BaseApp
from oven_engine.utils.gl import *

"""
PONG
"""
class Assignment2(BaseApp):
    def __init__(self):
        super().__init__(win_title="Assignment 2 - 2D game")

        self.ball = Ball(position=self.screen_center, parent=self, speed=150.)
        self.pl_paddle = PlayerPaddle(parent=self, speed=200., name="Player_Paddle")
        self.ai_paddle = AIPaddle(parent=self, ball=self.ball, speed=150., name="AI_Paddle", speed_mult=.5)

        self.add_entity(self.ball)
        self.add_entity(self.pl_paddle)
        self.add_entity(self.ai_paddle)

        self.background_img = self.tm.load_texture("assets/background.png",
                                           filtering=GL_LINEAR, clamping=GL_CLAMP_TO_EDGE)
        assert self.background_img != -1

        font = "assets/fonts/upheavtt.ttf"
        self.ai_text = Text(text="0", fontFileName=font)
        self.pl_text = Text(text="0", fontFileName=font)

        self.initial_text = Text(text="Press any key to start", fontFileName=font)
        self.game_started = False
        self.draw_entities = False
        self.update_entities = False
        self.cm.enabled = False

        self.ai_score = 0
        self.pl_score = 0

    def display_back(self):
        border = .05
        draw_texture(self.background_img, self.screen_center, self.win_size/2,
                     img_tl=Vector2D(-border), img_br=Vector2D(1. + border))

        if not self.game_started:
            return

        tmp = Vector2D((self.ai_paddle.position.x + self.ai_paddle.size.x/2.)/2., self.screen_center.y)
        draw_text(self.ai_text, tmp, 1., filtering=GL_LINEAR)
        tmp = Vector2D(self.win_size.x - (self.ai_paddle.position.x + self.ai_paddle.size.x/2.)/2., self.screen_center.y)
        draw_text(self.pl_text, tmp, 1., filtering=GL_LINEAR)

    def display_front(self):
        if not self.game_started:
            draw_text(self.initial_text, self.screen_center, 1., filtering=GL_LINEAR)

    def handle_event(self, ev):
        if not self.game_started:
            if ev.type == pg.KEYDOWN:
                self.game_started = True
                self.draw_entities = True
                self.update_entities = True
                self.cm.enabled = True

    @staticmethod
    def update_text(text_obj, new_text):
        text_obj.text = new_text
        text_obj.reload_surface()

    def update(self):
        scored = True

        if self.ball.position.x >= self.pl_paddle.position.x - self.pl_paddle.size.x/2.:
            print("AI SCORED")
            self.ai_score += 1
            Assignment2.update_text(self.ai_text, f"{int(self.ai_score)}")
        elif self.ball.position.x <= self.ai_paddle.position.x + self.ai_paddle.size.x/2.:
            print("PLAYER SCORED")
            self.pl_score += 1
            Assignment2.update_text(self.pl_text, f"{int(self.pl_score)}")
            self.ai_paddle.speed_mult += .1
        else:
            scored = False

        if scored:
            self.reset()
            self.ball.direction.x *= -1
            self.ball.speed_mult += .1

            if self.ai_score >= 10 or self.pl_score >= 10:
                self.draw_entities = False
                self.update_entities = False
                self.cm.enabled = False
                self.game_started = False
                self.ai_score = 0
                self.pl_score = 0
                self.ai_paddle.position.y = self.screen_center.y
                self.pl_paddle.position.y = self.screen_center.y
                self.ai_paddle.speed_mult = .5
                self.ball.speed_mult = 1.
                Assignment2.update_text(self.ai_text, "0")
                Assignment2.update_text(self.pl_text, "0")

    def get_paddle(self, side: int):
        if side < 0:
            return self.ai_paddle
        elif side > 0:
            return self.pl_paddle

        return None

    def reset(self):
        self.ball.reset()
        self.pl_paddle.reset()
        self.ai_paddle.reset()


if __name__ == "__main__":
    g = Assignment2()
    
    exit_code = g.run()

    quit(code = exit_code)