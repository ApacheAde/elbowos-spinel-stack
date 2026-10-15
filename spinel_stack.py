#!/usr/bin/env python3
"""Spinel Stack — full-colour Python 3 neon platform-stacking arcade for ElbowOS.
Autoplay 9:16 MP4 reel. https://x.com/ElbowOS
"""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv

if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/SPINEL_STACK_ElbowOS.mp4")
TITLE, HANDLE = "SPINEL STACK", "x.com/ElbowOS"

VOID = (12, 6, 28)
INK = (22, 12, 48)
PINK = (255, 80, 180)
MAG = (220, 40, 160)
CYAN = (40, 230, 255)
GOLD = (255, 210, 70)
WHITE = (245, 250, 255)
AMBER = (255, 160, 60)
LIME = (120, 255, 140)

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font_lg = pygame.font.SysFont("arial", 92, bold=True)
        self.font_md = pygame.font.SysFont("arial", 48, bold=True)
        self.font_sm = pygame.font.SysFont("arial", 36)
        self.reset()

    def reset(self):
        self.score = 0
        self.combo = 0
        self.height = 0
        self.stack = []  # list of (x, w, y, color)
        base_w = 420
        base_x = (W - base_w) // 2
        self.stack.append((base_x, base_w, H - 280, CYAN))
        self.cur_w = base_w
        self.cur_x = random.randint(80, W - 80 - self.cur_w)
        self.cur_vx = random.choice([-6, -5, 5, 6])
        self.dropping = False
        self.drop_y = 180
        self.drop_vy = 0
        self.particles = []
        self.t = 0
        self.perfects = 0
        self.msg = ""
        self.msg_t = 0

    def spawn_next(self):
        self.cur_w = max(80, self.stack[-1][1] - random.choice([0, 0, 10, 20]))
        self.cur_x = random.randint(60, W - 60 - self.cur_w)
        self.cur_vx = random.choice([-7, -6, -5, 5, 6, 7])
        self.drop_y = 200
        self.dropping = False
        self.drop_vy = 0

    def autoplay(self):
        # auto drop when roughly aligned or randomly for motion
        if not self.dropping and self.t % 45 == 0:
            top = self.stack[-1]
            center = top[0] + top[1] // 2
            cur_c = self.cur_x + self.cur_w // 2
            if abs(cur_c - center) < 40 or random.random() < 0.3:
                self.dropping = True
                self.drop_vy = 18

    def tick(self):
        self.t += 1
        if not self.dropping:
            self.cur_x += self.cur_vx
            if self.cur_x < 40 or self.cur_x + self.cur_w > W - 40:
                self.cur_vx *= -1
                self.cur_x = max(40, min(W - 40 - self.cur_w, self.cur_x))
        else:
            self.drop_y += self.drop_vy
            self.drop_vy += 0.6
            top = self.stack[-1]
            land_y = top[2] - 48
            if self.drop_y >= land_y:
                # land
                overlap_l = max(self.cur_x, top[0])
                overlap_r = min(self.cur_x + self.cur_w, top[0] + top[1])
                new_w = max(0, overlap_r - overlap_l)
                if new_w < 40:
                    # fail, reset stack somewhat
                    self.msg = "MISS"
                    self.msg_t = 40
                    self.combo = 0
                    if len(self.stack) > 1:
                        self.stack.pop()
                    self.spawn_next()
                    return
                perfect = abs((self.cur_x + self.cur_w / 2) - (top[0] + top[1] / 2)) < 12
                new_x = overlap_l
                color = GOLD if perfect else random.choice([PINK, MAG, CYAN, AMBER])
                self.stack.append((new_x, new_w, land_y, color))
                self.height += 1
                pts = 100 + self.combo * 25 + (50 if perfect else 0)
                self.score += pts
                self.combo = self.combo + 1 if perfect else 0
                if perfect:
                    self.perfects += 1
                    self.msg = "PERFECT!"
                    self.msg_t = 30
                # particles
                for _ in range(12):
                    self.particles.append({
                        "x": new_x + new_w // 2,
                        "y": land_y,
                        "vx": random.uniform(-4, 4),
                        "vy": random.uniform(-8, -2),
                        "life": 25,
                        "c": color
                    })
                # rise stack a bit
                for i in range(len(self.stack)):
                    x, w, y, c = self.stack[i]
                    self.stack[i] = (x, w, y - 18, c)
                self.spawn_next()

        # particles
        alive = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.3
            p["life"] -= 1
            if p["life"] > 0:
                alive.append(p)
        self.particles = alive
        if self.msg_t > 0:
            self.msg_t -= 1

    def draw(self, surf):
        surf.fill(VOID)
        # ambient glow bars
        for i in range(6):
            yy = 300 + i * 250
            pygame.draw.rect(surf, INK, (0, yy, W, 4))
        # stack
        for x, w, y, c in self.stack:
            if y > -100 and y < H + 100:
                pygame.draw.rect(surf, c, (x, y, w, 42), border_radius=8)
                pygame.draw.rect(surf, WHITE, (x, y, w, 42), 3, border_radius=8)
        # current
        if not self.dropping:
            pygame.draw.rect(surf, MAG, (self.cur_x, self.drop_y, self.cur_w, 42), border_radius=8)
            pygame.draw.rect(surf, CYAN, (self.cur_x, self.drop_y, self.cur_w, 42), 4, border_radius=8)
        else:
            pygame.draw.rect(surf, PINK, (self.cur_x, self.drop_y, self.cur_w, 42), border_radius=8)
            pygame.draw.rect(surf, WHITE, (self.cur_x, self.drop_y, self.cur_w, 42), 3, border_radius=8)
        # particles
        for p in self.particles:
            a = max(0, min(255, int(255 * p["life"] / 25)))
            col = (*p["c"][:3], a) if len(p["c"]) == 3 else p["c"]
            pygame.draw.circle(surf, p["c"], (int(p["x"]), int(p["y"])), 6)
        # UI overlay
        title = self.font_lg.render(TITLE, True, GOLD)
        surf.blit(title, title.get_rect(center=(W // 2, 90)))
        sc = self.font_md.render(f"SCORE {self.score}", True, WHITE)
        surf.blit(sc, sc.get_rect(center=(W // 2, 180)))
        ht = self.font_sm.render(f"HEIGHT {self.height}  PERFECTS {self.perfects}", True, CYAN)
        surf.blit(ht, ht.get_rect(center=(W // 2, H - 180)))
        handle = self.font_sm.render(HANDLE, True, AMBER)
        surf.blit(handle, handle.get_rect(center=(W // 2, H - 90)))
        if self.msg_t > 0 and self.msg:
            m = self.font_md.render(self.msg, True, GOLD if "PERFECT" in self.msg else PINK)
            surf.blit(m, m.get_rect(center=(W // 2, 420)))

    def play_interactive(self):
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_SPACE, pygame.K_DOWN, pygame.K_RETURN):
                    if not self.dropping:
                        self.dropping = True
                        self.drop_vy = 16
            self.tick()
            self.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

    def record(self):
        frames = FPS * SECS
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
            "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
            "-i", "-", "-an", "-vcodec", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "fast", "-movflags", "+faststart",
            OUT
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        canvas = pygame.Surface((W, H))
        try:
            for i in range(frames):
                self.autoplay()
                self.tick()
                self.draw(canvas)
                raw = pygame.image.tostring(canvas, "RGB")
                proc.stdin.write(raw)
            proc.stdin.close()
            rc = proc.wait(timeout=60)
            if rc != 0:
                err = proc.stderr.read().decode()[-800:]
                raise SystemExit(f"ffmpeg failed ({rc}): {err}")
            print("wrote", OUT)
        finally:
            pygame.quit()

def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()

if __name__ == "__main__":
    main()
