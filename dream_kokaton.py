import os
import random
import sys
import time
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
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        super().__init__()
        self.image = __class__.imgs[(+5, 0)]
        self.mask = pg.mask.from_surface(self.image) # 透明な部分を無視するsurface「mask」を追加、当たり判定はこれを用いて行う
        self.rect: pg.Rect = self.image.get_rect()
        self.rect.center = xy
        self.size = 1

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        self.mask = pg.mask.from_surface(self.image)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(sum_mv)
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.image = __class__.imgs[tuple(sum_mv)]
            self.mask = pg.mask.from_surface(self.image)
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

class Enemy(pg.sprite.Sprite):
    """
    敵バードに関するクラス
    """
    imgs = [pg.image.load(f"en_bird/bird{i}.png") for i in range(1, 9)]
    start_move_lst = [[0, +6], [WIDTH, -6]] # 初期位置と移動速度をまとめたリスト
    def __init__(self):
        super().__init__()
        start_move_idx = random.randint(0, 1) # start_move_lstのインデックスを決める変数(どちらからスタートし、どちらに動くか決める)
        self.size = random.randint(1, 8) # 鳥の大きさを決める変数
        self.image = pg.transform.rotozoom(__class__.imgs[self.size-1], 0, 0.1*self.size)
        if start_move_idx == 0: # スタート位置が左端のとき画像を反転させる
            self.image = pg.transform.flip(self.image, True, False)
        self.mask = pg.mask.from_surface(self.image) # 透明な部分を無視するsurface「mask」を追加、当たり判定にはこれを使う
        self.rect = self.mask.get_rect()
        self.rect.center = __class__.start_move_lst[start_move_idx][0], random.randint(0, HEIGHT) # 初期位置
        self.vx = __class__.start_move_lst[start_move_idx][1] # どちらに動くかをきめる変数

    def update(self):
        self.rect.move_ip(self.vx, 0)
        if (self.vx > 0 and self.rect.center[0] > WIDTH) or (self.vx < 0 and self.rect.center[0] < 0): # 初期位置でない画面端に到達したら削除
                self.kill()


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

def check_eat_or_ed(bird: Bird, en_birds: pg.sprite.Group):
    """
    こうかとんと敵バードが当たった時に値を返す関数
    返り値:
    こうかとんのsizeの方が大きい場合:1
    敵のsizeの方が大きい場合:0
    引数1 bird: birdクラスのこうかとん
    引数2 en_birds Enemyクラスの敵バードを要素に持つ、Groupクラス
    """
    for en_bird in pg.sprite.spritecollide(bird, en_birds, False): # こうかとんと敵バードの当たり判定について
            offset = (bird.rect.x - en_bird.rect.x, bird.rect.y - en_bird.rect.y)
            if en_bird.mask.overlap(bird.mask, offset):
                if bird.size < en_bird.size:
                    return 0
                else:
                    return 1
        
def main():
    score = Score()
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/sora.jpg")
    bird = Bird((300, 200)) 
    bomb = Bomb((255, 0, 0), 10)
    # bomb2 = Bomb((0, 0, 255), 20)   
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)] 
    en_birds = pg.sprite.Group()
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return         
        screen.blit(bg_img, [0, 0])
        
        """
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                pg.display.update()
                time.sleep(1)
                return 
        """            
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
        check_eat_or_ed(bird, en_birds)

        en_birds.draw(screen)
        score.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
