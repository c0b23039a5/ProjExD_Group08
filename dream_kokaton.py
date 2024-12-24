import os
import random
import sys
import time
import math
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5  # 爆弾の個数
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.size = 0.9  # こうかとんのサイズ
        self.dictionary((+5, 0),xy)  # こうかとんが右に向く
        self.post_size = self.size  # 過去のサイズを記録する
        self.post_angle = (+5, 0)  # 過去のアングルを記録する

    def big_bird(self, num:float):
        """
        オブジェクトを食ったらこうかとんがでかくなる
        引数 num：こうかとんのサイズの増減量
        """
        if num < 0 and self.size < 0.5:  # こうかとんが小さくなりすぎてどこに居るのかが分からなくならないようにする
            pass
        elif min(WIDTH,HEIGHT) > self.size*self.rct.height/2:  # ウィンドウサイズより大きくならないようにする
            self.size += num  # numの増減に合わせてこうかとんのサイズを定義する

        if self.size < 0:  # こうかとんのサイズがマイナスにならないようにする
            self.size = 0.5

    def dictionary(self, mv_angle,xy=None):
        """
        こうかとんに関するパラメーター（回転、サイズ）の動的辞書
        引数1 my_angle：こうかとんが移動している角度
        引数2 xy：座標の指定（任意）
        戻り値：こうかとんの状況(回転、サイズ、位置等)を適用したこうかとんの画像
        """
        imgs = self.update_img()
        if mv_angle == (0,0):  # こうかとんが静止しているときにでもサイズを更新するようにする。
            self.img = imgs[self.post_angle]
            self.update_rect(imgs)
        else:  # こうかとんが移動しているとき
          self.img = imgs[mv_angle]
          if xy:
            self.rct: pg.Rect = self.img.get_rect()
            self.rct.center = xy
          else:
            self.update_rect(imgs)
          self.post_angle = mv_angle
          return self.img

    def update_img(self):
        """
        こうかとんのサイズを反映したこうかとんの回転辞書
        引数なし
        戻り値：こうかとんのサイズを反映したこうかとんの回転辞書
        """
        img0 = pg.image.load("fig/3.png")  # 左向き
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
        imgs = {  # 0度から反時計回りに定義
            (+5, 0): pg.transform.rotozoom(img, 0, self.size),  # 右
            (+5, -5): pg.transform.rotozoom(img, 45, self.size),  # 右上
            (0, -5): pg.transform.rotozoom(img, 90, self.size),  # 上
            (-5, -5): pg.transform.rotozoom(img0, -45, self.size),  # 左上
            (-5, 0): pg.transform.rotozoom(img0, 0, self.size),  # 左
            (-5, +5): pg.transform.rotozoom(img0, 45, self.size),  # 左下
            (0, +5): pg.transform.rotozoom(img, -90, self.size),  # 下
            (+5, +5): pg.transform.rotozoom(img, -45, self.size),  # 右下
        }
        return imgs

    def update_rect(self,imgs):
        """
        こうかとんのサイズを大きくしたときあたり判定を更新する
        引数 imgs: 画像を回転する辞書
        """
        cache_center = self.rct.center  # self.rctを代入するとself.rct.centerのデータが失われてしまうため
        self.rct: pg.Rect = imgs[(+5,0)].get_rect()  # こうかとんの画像が斜めのときあたり判定が広くなるため、斜めではないときの画像のあたり判定に固定する。
        self.rct.center = cache_center


    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, self.size)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        imgs = self.update_img()
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            if (self.post_angle == (+5, -5) or  # 右上
                self.post_angle == (-5, -5) or  # 左上
                self.post_angle == (-5, +5) or  # 左下
                self.post_angle == (+5, +5)):  # 右下
                    # こうかとんが斜めの状態だとheightとwidthが斜めではないときよりも長くなるため
                    if self.rct.top < imgs[(+5, -5)].get_rect().height/8:
                        self.rct.top = 0 - imgs[(+5, -5)].get_rect().height/8  # 画面内に強制移動
                    if HEIGHT - imgs[(+5, -5)].get_rect().height/8 < self.rct.bottom:
                        self.rct.bottom = HEIGHT - imgs[(+5, -5)].get_rect().height/8  # 画面内に強制移動
                    if self.rct.left < imgs[(+5, -5)].get_rect().width/8:
                        self.rct.left = 0 - imgs[(+5, -5)].get_rect().width/8  # 画面内に強制移動
                    if WIDTH - imgs[(+5, -5)].get_rect().width/8 < self.rct.right:
                        self.rct.right = WIDTH - imgs[(+5, -5)].get_rect().width/8   # 画面内に強制移動
            else:
                if self.rct.top < 0:
                    self.rct.top = 0  # 画面内に強制移動
                if HEIGHT < self.rct.bottom:
                    self.rct.bottom = HEIGHT  # 画面内に強制移動
                if self.rct.left <0:
                    self.rct.left = 0  # 画面内に強制移動
                if WIDTH < self.rct.right:
                    self.rct.right = WIDTH  # 画面内に強制移動

        if not self.size == self.post_size or not self.post_angle == (sum_mv):
            self.dictionary(tuple(sum_mv))
        self.post_size = self.size
        screen.blit(self.img, self.rct)


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Score:
    """
    スコアに関するクラス
    """
    def __init__(self):
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.color = (0, 0, 255)
        self.score = 0
        self.img = self.fonto.render(f"Score: {self.score}", True, self.color)
        self.rect = self.img.get_rect()
        self.rect.bottomleft = (100, HEIGHT - 50)

    def update(self, screen: pg.Surface):
        # スコアの文字列を更新
        self.img = self.fonto.render(f"Score: {self.score}", True, self.color)
        screen.blit(self.img, self.rect)




def main():
    score = Score()
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/sora.jpg")
    bird = Bird((300, 200))
    bomb = Bomb((255, 0, 0), 10)
    # bomb2 = Bomb((0, 0, 255), 20)
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        screen.blit(bg_img, [0, 0])

        for bomb in bombs:  # 仮 爆弾を魚だと仮定して
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                # bird.change_img(8, screen)
                # fonto = pg.font.Font(None, 80)
                # txt = fonto.render("Game Over", True, (255, 0, 0))
                # screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                bird.big_bird(0.02)
                # pg.display.update()
                # time.sleep(1)
                # return

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        # beam.update(screen)
        bombs = [bomb for bomb in bombs if bomb is not None]  # Noneでないものリスト
        for bomb in bombs:
            bomb.update(screen)
        # bomb2.update(screen)
        score.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
