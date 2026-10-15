# Spinel Stack

Full-colour Python 3 neon platform-stacking arcade for ElbowOS.

Stack moving neon platforms before they drop. Perfect alignment glows gold and multiplies score. Miss the edge and the tower narrows.

Featured: https://x.com/ElbowOS

Drive reel: https://drive.google.com/file/d/1Lc65_ASNIuuuRca8Cu4j66K2TyZIngUn/view

## Play

```bash
pip install -r requirements.txt
python3 spinel_stack.py --play
```

Space / Down / Enter to drop the current platform.

## Record a 9:16 reel

```bash
python3 spinel_stack.py --record
```

Outputs SPINEL_STACK_ElbowOS.mp4 (1080x1920, 15s, 30fps).

Needs Python 3.10+ and pygame. Headless recording uses SDL dummy driver.
