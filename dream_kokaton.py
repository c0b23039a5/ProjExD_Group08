import os
import random
import sys
import time
import math
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def start_screen(screen: pg.Surface):
    """
    ゲームのスタート画面を表示し、ユーザーの入力を待つ
    引数 screen：画面Surface
    戻り値 スタート画面終了 "play" / ルール画面 null
    """
    # 背景画像やフォントの準備
    bg_image = pg.image.load("fig/sora.jpg")  # 背景画像
    kokaton_image = pg.image.load("fig/3.png")  # 背景画像
    kokaton_image = pg.transform.scale(kokaton_image,(158, 168))
    font_title = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 100)  # タイトル用フォント
    font_start = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 50)   # 説明用フォント
    font_rule = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 50)   # 説明用フォント
    # テキストの描画
    title_text = font_title.render("ゲームタイトル", True, (255, 255, 255))
    start_text = font_start.render("スタート", True, (2, 200, 0))
    rule_text = font_rule.render("遊び方", True, (2, 200, 0))
    while True:
        # 半透明なテキストSurfaceを作成
        start_surf = start_text.convert_alpha()
        start_surf.set_alpha(200)  # 透明度設定：0（完全透明）～ 255（不透明）
        # テキストの位置調整
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        button_rect = start_text.get_rect(center=(WIDTH//3, (HEIGHT//5)*4))
        rule_rect = rule_text.get_rect(center=((WIDTH//3)*2, (HEIGHT//5)*4))
        screen.blit(bg_image, [0, 0])
        screen.blit(title_text, title_rect)  # タイトルを描画
        screen.blit(start_surf, button_rect)  # 説明文を描画
        screen.blit(rule_text, rule_rect)  # 説明文を描画
        screen.blit(kokaton_image, ((WIDTH//2)-100, (HEIGHT//2)-50))  #画像の描画
        pg.display.update()
        # ユーザーの入力を待つ
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:  # マウスクリックの検知
                if button_rect.collidepoint(event.pos):  # クリック位置がボタン内かを判定
                    return "play" # スタート画面終了
                if rule_rect.collidepoint(event.pos):  # クリック位置がボタン内かを判定
                    return  # スタート画面終了


def Howto_screen(screen: pg.Surface):
    """
    ゲームの遊び方の画面を表示し、ユーザーの入力を待つ
    引数 screen：画面Surface
    戻り値 ルール画面終了 "play"
    """
    # pg.mixer.music.load("sound/_Albatross.mp3")  #音声ファイルの読み込み
    # pg.mixer.music.play(-1)  #音声を再生（無限ループ）

    # 背景画像やフォントの準備
    bg_image = pg.image.load("fig/sora.jpg")  # 背景画像
    Howto_title = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 100)  # タイトル用フォント
    font_return = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 50)   # 説明用フォント

    # テキストの描画
    Howto_text = Howto_title.render("遊び方を書くページだよ", True, (255, 255, 255))
    font_return = font_return.render("戻る", True, (2, 200, 0))

    while True:
        # 半透明なテキストSurfaceを作成
        Howto_surf = Howto_text.convert_alpha()
        Howto_surf.set_alpha(125)  # 透明度設定：0（完全透明）～ 255（不透明）
        # テキストの位置調整
        title_rect = Howto_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        return_rect = font_return.get_rect(center=(WIDTH//2, (HEIGHT//4)*3))
        screen.blit(bg_image, [0, 0])
        screen.blit(Howto_text, title_rect)  # タイトルを描画
        screen.blit(font_return, return_rect)  # 戻るボタンを描画
        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:  # マウスクリックの検知
                if return_rect.collidepoint(event.pos):  # クリック位置がボタン内かを判定
                    return "play" # スタート画面終了


def check_bound(obj_rect: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rect.left < 0 or WIDTH < obj_rect.right:
        yoko = False
    if obj_rect.top < 0 or HEIGHT < obj_rect.bottom:
        tate = False
    return yoko, tate


class Bird(pg.sprite.Sprite):
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
        self.size = 1
        self.post_size = self.size  # 過去のサイズを記録する
        self.post_angle = (+5, 0)  # 過去のアングルを記録する
        self.dictionary((+5, 0),xy)
        self.mask = pg.mask.from_surface(self.image)  # 透明な部分を無視するsurface「mask」を追加、当たり判定はこれを用いて行う
        self.rect: pg.Rect = self.image.get_rect()


    def change_image(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, self.size)
        self.mask = pg.mask.from_surface(self.image)
        screen.blit(self.image, self.rect)


    def big_bird(self, num:float):
        """
        オブジェクトを食ったらこうかとんがでかくなる
        引数 num：こうかとんのサイズの増減量
        """
        if num < 0 and self.size < 0.5:  # こうかとんが小さくなりすぎてどこに居るのかが分からなくならないようにする
            pass
        elif min(WIDTH,HEIGHT) > self.size*self.rect.height/2:  # ウィンドウサイズより大きくならないようにする
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
        imgs = self.update_image()
        if mv_angle == (0,0):  # こうかとんが静止しているときにでもサイズを更新するようにする。
            self.image = imgs[self.post_angle]
            self.update_rect(imgs)
        else:  # こうかとんが移動しているとき
            self.image = imgs[mv_angle]
            if xy:
                self.rect: pg.Rect = self.image.get_rect()
                self.rect.center = xy
            else:
                self.update_rect(imgs)
            self.post_angle = mv_angle
            return self.image

    def update_image(self):
        """
        こうかとんのサイズを反映したこうかとんの回転辞書
        引数なし
        戻り値：こうかとんのサイズを反映したこうかとんの回転辞書
        """
        image0 = pg.image.load("fig/3.png")  # 左向き
        image = pg.transform.flip(image0, True, False)  # デフォルトのこうかとん（右向き）
        imgs = {  # 0度から反時計回りに定義
            (+5, 0): pg.transform.rotozoom(image, 0, self.size),  # 右
            (+5, -5): pg.transform.rotozoom(image, 45, self.size),  # 右上
            (0, -5): pg.transform.rotozoom(image, 90, self.size),  # 上
            (-5, -5): pg.transform.rotozoom(image0, -45, self.size),  # 左上
            (-5, 0): pg.transform.rotozoom(image0, 0, self.size),  # 左
            (-5, +5): pg.transform.rotozoom(image0, 45, self.size),  # 左下
            (0, +5): pg.transform.rotozoom(image, -90, self.size),  # 下
            (+5, +5): pg.transform.rotozoom(image, -45, self.size),  # 右下
        }
        return imgs

    def update_rect(self,imgs):
        """
        こうかとんのサイズを大きくしたときあたり判定を更新する
        引数 imgs: 画像を回転する辞書
        """
        cache_center = self.rect.center  # self.rectを代入するとself.rect.centerのデータが失われてしまうため
        self.rect: pg.Rect = imgs[(+5,0)].get_rect()  # こうかとんの画像が斜めのときあたり判定が広くなるため、斜めではないときの画像のあたり判定に固定する。
        self.rect.center = cache_center

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        imgs = self.update_image()
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(sum_mv)
        if check_bound(self.rect) != (True, True):
            if (self.post_angle == (+5, -5) or  # 右上
                self.post_angle == (-5, -5) or  # 左上
                self.post_angle == (-5, +5) or  # 左下
                self.post_angle == (+5, +5)):  # 右下
                    # こうかとんが斜めの状態だとheightとwidthが斜めではないときよりも長くなるため
                    if self.rect.top < imgs[(+5, -5)].get_rect().height/8:
                        self.rect.top = 0 - imgs[(+5, -5)].get_rect().height/8  # 画面内に強制移動
                    if HEIGHT - imgs[(+5, -5)].get_rect().height/8 < self.rect.bottom:
                        self.rect.bottom = HEIGHT - imgs[(+5, -5)].get_rect().height/8  # 画面内に強制移動
                    if self.rect.left < imgs[(+5, -5)].get_rect().width/8:
                        self.rect.left = 0 - imgs[(+5, -5)].get_rect().width/8  # 画面内に強制移動
                    if WIDTH - imgs[(+5, -5)].get_rect().width/8 < self.rect.right:
                        self.rect.right = WIDTH - imgs[(+5, -5)].get_rect().width/8  # 画面内に強制移動
            else:
                if self.rect.top < 0:
                    self.rect.top = 0  # 画面内に強制移動
                if HEIGHT < self.rect.bottom:
                    self.rect.bottom = HEIGHT  # 画面内に強制移動
                if self.rect.left <0:
                    self.rect.left = 0  # 画面内に強制移動
                if WIDTH < self.rect.right:
                    self.rect.right = WIDTH  # 画面内に強制移動
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dictionary(tuple(sum_mv))
            self.mask = pg.mask.from_surface(self.image)
        if not self.size == self.post_size or not self.post_angle == (sum_mv):
            self.dictionary(tuple(sum_mv))
        self.post_size = self.size
        screen.blit(self.image, self.rect)


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
        self.image = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rect)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rect.move_ip(self.vx, self.vy)
        screen.blit(self.image, self.rect)


class Enemy(pg.sprite.Sprite):
    """
    敵バードに関するクラス
    """
    imgs = [pg.image.load(f"en_bird/bird{i}.png") for i in range(1, 9)]
    start_move_lst = [[0, +6], [WIDTH, -6]]  # 初期位置と移動速度をまとめたリスト
    def __init__(self):
        super().__init__()
        start_move_idx = random.randint(0, 1)  # start_move_lstのインデックスを決める変数(どちらからスタートし、どちらに動くか決める)
        self.size = random.randint(1, 8)  # 鳥の大きさを決める変数
        self.image = pg.transform.rotozoom(__class__.imgs[self.size-1], 0, 0.1*self.size)
        if start_move_idx == 0:  # スタート位置が左端のとき画像を反転させる
            self.image = pg.transform.flip(self.image, True, False)
        self.mask = pg.mask.from_surface(self.image)  # 透明な部分を無視するsurface「mask」を追加、当たり判定にはこれを使う
        self.rect = self.mask.get_rect()
        self.rect.center = __class__.start_move_lst[start_move_idx][0], random.randint(0, HEIGHT)  # 初期位置
        self.vx = __class__.start_move_lst[start_move_idx][1]  # どちらに動くかをきめる変数

    def update(self):
        self.rect.move_ip(self.vx, 0)
        if (self.vx > 0 and self.rect.center[0] > WIDTH) or (self.vx < 0 and self.rect.center[0] < 0):  # 初期位置でない画面端に到達したら削除
                self.kill()


class Score:
    """
    スコアに関するクラス
    """
    def __init__(self):
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.color = (0, 0, 255)
        self.score = 0
        self.image = self.fonto.render(f"Score: {self.score}", True, self.color)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (100, HEIGHT - 50)

    def update(self, screen: pg.Surface):
        # スコアの文字列を更新
        self.image = self.fonto.render(f"Score: {self.score}", True, self.color)
        screen.blit(self.image, self.rect)

def check_eat_or_ed(bird: Bird, en_birds: pg.sprite.Group):
    """
    こうかとんと敵バードが当たった時に値を返す関数
    引数1 bird: birdクラスのこうかとん
    引数2 en_birds Enemyクラスの敵バードを要素に持つ、Groupクラス
    返り値 こうかとんのsizeの方が大きい場合:1 ／ 敵のsizeの方が大きい場合:0
    """
    for en_bird in pg.sprite.spritecollide(bird, en_birds, False):  # こうかとんと敵バードの当たり判定について
            offset = (bird.rect.x - en_bird.rect.x, bird.rect.y - en_bird.rect.y)
            if en_bird.mask.overlap(bird.mask, offset):
                if bird.size < en_bird.size:
                    return 0
                else:
                    return 1


class Life:
    """
    ライフ
    """
    def __init__(self,bird,bombs):
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.color = (0, 0, 255)
        self.life = 30
        self.image = self.fonto.render(f"Life: {self.life}", True, self.color)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (300, HEIGHT - 50)
        self.bird = bird
        self.bombs = bombs


    def update(self, screen: pg.Surface):
        # ライフの文字列を更新
        self.image = self.fonto.render(f"Life: {self.life}", True, self.color)
        screen.blit(self.image, self.rect)

    def life_decrease(self):
        for bomb in self.bombs:
            if self.bird.rect.colliderect(bomb.rect):
                print("Collision detected!")  # デバッグ用プリント
                self.life -= 10
                print(f"Life decreased to: {self.life}")
                self.bombs.remove(bomb)
                break


def main():
    pg.mixer.music.load("sound/_Albatross.mp3")  #音声ファイルの読み込み
    pg.mixer.music.play(-1)  #音声を再生（無限ループ）
    screen_scene = 0
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    score = Score()
    pg.display.set_caption("たたかえ！こうかとん")
    bg_image = pg.image.load("fig/sora.jpg")
    bird = Bird((300, 200))
    en_birds = pg.sprite.Group()
    clock = pg.time.Clock()
    tmr = 0
    life = Life(bird, en_birds)
    while True:
        if screen_scene == 0:
            if start_screen(screen) == "play":
                screen_scene = 1
            else:
                screen_scene = 2
                continue
        elif screen_scene == 2:
            Howto_screen(screen)  #遊び方関数
            screen_scene = 0
            continue

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        screen.blit(bg_image, [0, 0])


        # for bomb in bombs:  # 仮 爆弾を魚だと仮定して
        #     if bird.rect.colliderect(bomb.rect):
        #     # if life.life <= 0:
        #         # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
        #         # bird.change_image(8, screen)
        #         # fonto = pg.font.Font(None, 80)
        #         # txt = fonto.render("Game Over", True, (255, 0, 0))
        #         # screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
        #         bird.big_bird(0.02)
        #         # pg.display.update()
        #         # time.sleep(1)
        #         # return

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        # beam.update(screen)
        #bombs = [bomb for bomb in bombs if bomb is not None]  # Noneでないものリスト
        #for bomb in bombs:
        #    bomb.update(screen)
        # bomb2.update(screen)
        if tmr %100 == 0:
            en_birds.add(Enemy())
        for en_bird in en_birds:
            en_bird.update()

        if check_eat_or_ed(bird, en_birds):
            bird.big_bird(0.06)
        else:
            life.life_decrease()


        en_birds.draw(screen)
        score.update(screen)
        life.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    pg.mixer.init()
    main()
    pg.quit()
    sys.exit()
