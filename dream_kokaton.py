import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5  # 爆弾の個数
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def start_screen(screen: pg.Surface):
    """
    ゲームのスタート画面を表示し、ユーザーの入力を待つ
    """
    # 背景画像やフォントの準備
    bg_img = pg.image.load("fig/sora.jpg")  # 背景画像
    kokaton_img = pg.image.load("fig/koukoton.png")  # 背景画像
    kokaton_img = pg.transform.scale(kokaton_img,(158, 168))
    font_title = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 100)  # タイトル用フォント
    font_start = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 50)   # 説明用フォント
    font_rule = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 50)   # 説明用フォント


    # テキストの描画
    title_text = font_title.render("ゲームタイトル", True, (255, 255, 255))
    start_text = font_start.render("スタート", True, (255, 255, 255))
    rule_text = font_rule.render("遊び方", True, (255, 255, 255))
    

    while True:
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        button_rect = start_text.get_rect(center=(WIDTH//3, (HEIGHT//5)*4))
        rule_rect = rule_text.get_rect(center=((WIDTH//3)*2, (HEIGHT//5)*4))

        screen.blit(bg_img, [0, 0])
        
        pg.draw.rect(screen, (142, 206, 254), button_rect.inflate(20, 20), border_radius=10)  # スタートボタン背景
        pg.draw.rect(screen, (142, 206, 254), rule_rect.inflate(20, 20), border_radius=10)   # 遊び方ボタン背景
        
        screen.blit(title_text, title_rect)  # タイトルを描画
        screen.blit(start_text, button_rect)  # 説明文を描画
        screen.blit(rule_text, rule_rect)  # 説明文を描画
        screen.blit(kokaton_img, ((WIDTH//2)-100, (HEIGHT//2)-50)) #画像の描画
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
    """
    # pg.mixer.music.load("sound/_Albatross.mp3") #音声ファイルの読み込み
    # pg.mixer.music.play(-1) #音声を再生（無限ループ）



    font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)  # 日本語フォントを指定
    # 色の設定
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BROWN = (160, 82, 45)
    GREEN = (0, 255, 0)
    BUTTON_COLOR = (200, 50, 50)

    # テキスト内容
    instructions = (
        "<遊び方>\n"
        "1. 矢印キーでこうかとんを上下左右に動かし、\n   自分よりも小さな鳥を食べると体が大きくなります。\n"
        "2. 自分より小さな魚を食べると得点となり、\n   自分よりも大きな魚にぶつかるとLIFEは減ります。\n"
        "3. たまに出現する飛行機にあたったり\n"
        "　 LIFEが全てなくなるか制限時間が終わるとゲームオーバーです。"
    )

    # 背景画像やフォントの準備
    bg_img = pg.image.load("fig/sora.jpg")  # 背景画像
    Howto_title = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 40)  # タイトル用フォント
    font_return = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 40)   # 説明用フォント
    
    # テキストの描画
    Howto_text = Howto_title.render("遊び方", True, WHITE)
    font_return = font_return.render("<閉じる>", True, BLACK)
    
    while True:
        # 半透明なテキストSurfaceを作成
        Howto_surf = Howto_text.convert_alpha()
        Howto_surf.set_alpha(125)  # 透明度設定：0（完全透明）～ 255（不透明）
        # テキストの位置調整
        title_rect = Howto_text.get_rect(center=(WIDTH//2, HEIGHT//4))
        return_rect = font_return.get_rect(center=(WIDTH//2, (HEIGHT//4)*3))
        screen.blit(bg_img, [0, 0])
        #screen.blit(Howto_text, title_rect)  # タイトルを描画
        screen.blit(font_return, return_rect)  # 戻るボタンを描画

        instruction_lines = instructions.split("\n")
        for i, line in enumerate(instruction_lines):
            line_surface = font.render(line, True, BLACK)
            screen.blit(line_surface, (100, 150 + i * 40))
        pg.display.update()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:  # マウスクリックの検知
                if return_rect.collidepoint(event.pos):  # クリック位置がボタン内かを判定
                    return "play" # スタート画面終了
        



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
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

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
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
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
    pg.mixer.music.load("sound/_Albatross.mp3") #音声ファイルの読み込み
    pg.mixer.music.play(-1) #音声を再生（無限ループ）
    screen_scene = 0
    pg.display.set_caption("ゲームタイトル")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    score = Score()
    bg_img = pg.image.load("fig/sora.jpg")
    bird = Bird((300, 200)) 
    bomb = Bomb((255, 0, 0), 10)
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)] 
    clock = pg.time.Clock()
    tmr = 0
    while True:
        if screen_scene == 0:
            if start_screen(screen) == "play":
                screen_scene = 1
            else:
                screen_scene = 2
                continue
        elif screen_scene == 2:
            Howto_screen(screen) #遊び方関数
            screen_scene = 0
            continue

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return         
        screen.blit(bg_img, [0, 0])

        
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
    pg.mixer.init()
    main()
    pg.quit()
    sys.exit()
