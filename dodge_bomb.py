import os
import random
import sys
import pygame as pg
import time

def game_over(screen: pg.Surface, kk_rct: pg.Rect):
    """
    ゲームオーバー画面を表示する関数
    1. 黒い矩形を描画するためのSurfaceを作り，透明度を設定
    2. 「Game Over」の文字を描画
    3. 泣いているこうかとん画像を描画
    4. すべてをscreenにblitして更新
    5. 5秒間表示したまま停止
    """
    # 1. 黒い矩形Surfaceを作成
    blackout = pg.Surface((WIDTH, HEIGHT))
    blackout.fill((0, 0, 0))       # 黒で塗りつぶし
    blackout.set_alpha(200)        # 透明度（0:完全透明, 255:完全不透明）

    # 2. フォントを作って「Game Over」を描画
    font = pg.font.Font(None, 120)
    text = font.render("Game Over", True, (255, 255, 255))  # 白文字

    # 3. 泣いているこうかとん画像を読み込み
    cry_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    cry_rct = cry_img.get_rect(center=kk_rct.center)  # 元のこうかとん位置に配置

    # 4. blit処理
    screen.blit(blackout, (0, 0))  # 黒いSurfaceを貼る
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 100))  # 中央に文字
    screen.blit(cry_img, cry_rct)  # 泣いているこうかとん

    # 5. 更新 & 5秒停止
    pg.display.update()
    time.sleep(5)




WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRect or ばくだんRect
    戻り値：判定結果タプル（横方向，縦方向）
    画面内ならTrue／画面外ならFalse
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:  # 横方向にはみ出ていたら
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom: # 縦方向にはみ出ていたら
        tate = False
    return yoko, tate


def create_bomb_assets():
    """
    爆弾のサイズ・加速度を段階的に準備する
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    bb_accs = [a for a in range(1, 11)]  # 加速度リスト
    return bb_imgs, bb_accs


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")

    # こうかとんの向きごとの画像を準備
    kk_imgs = {
       (0, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), -90, 0.9),
       (0, 5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 90, 0.9),
       (-5, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9),
       (5, 0): pg.transform.flip(pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9), True, False),
    }
    kk_img = kk_imgs[(5, 0)]  # 初期向きは右
    kk_rct = kk_img.get_rect(center=(300, 200))

    # 爆弾リストを作成
    bb_imgs, bb_accs = create_bomb_assets()
    bb_rct = bb_imgs[0].get_rect(center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
    vx, vy = +5, +5  # 初期速度

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return

        screen.blit(bg_img, [0, 0])

        # 衝突判定
        if kk_rct.colliderect(bb_rct):
            game_over(screen, kk_rct)
            return

        # こうかとん移動
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])

        # 向き画像を切り替え
        if tuple(sum_mv) in kk_imgs and sum_mv != [0, 0]:
           kk_img = kk_imgs[tuple(sum_mv)]
        screen.blit(kk_img, kk_rct)

        # 爆弾の加速・拡大
        acc_idx = min(tmr//500, 9)
        avx = vx * bb_accs[acc_idx]
        avy = vy * bb_accs[acc_idx]

        # 追従型爆弾: こうかとんに近づくように移動
        dx, dy = kk_rct.centerx - bb_rct.centerx, kk_rct.centery - bb_rct.centery
        if dx != 0 or dy != 0:
            dist = max(1, (dx**2 + dy**2) ** 0.5)
            avx = int(avx * dx / dist)
            avy = int(avy * dy / dist)

        bb_rct.move_ip(avx, avy)
        

        # 画面外判定（跳ね返し不要にするならコメントアウト可）
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1

        # 爆弾描画
        screen.blit(bb_imgs[acc_idx], bb_rct)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()