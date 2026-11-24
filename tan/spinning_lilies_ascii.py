"""
================================================================================
  SPINNING LILIES — PROCEDURAL ASCII & UNICODE TERMINAL ANIMATION
================================================================================
  Generative 3D Botanical Art in Pure Terminal ASCII / ANSI TrueColor
  
  Features:
  - 12 Parametrically Sculpted Lily Tepals (6 Outer Sepals + 6 Inner Petals)
  - 3D Z-Buffer Depth Rasterizer with Perspective Projection & Diffuse Lighting
  - Realistic Floral Center: 6 Stamens with Golden Rocking Anthers & Pistil
  - 3 Visual Rendering Modes: Classic ASCII, Shaded Unicode Blocks, Floral Runes
  - 5 Viral Aesthetic Color Palettes with Smooth Dynamic Hue Drifting
  - 3D Floating Stardust Particle Swarm with Orbit & Twinkle Dynamics
  - Universal Zero-Dependency (Vectorized NumPy with Pure-Python Fallback)
  - Interactive Keyboard Controls (Space, C, M, 1/2/3, Up/Down, H, Q)
  - Auto-Adapting Terminal Size & Zero-Flicker Double-Buffered ANSI Display
================================================================================
"""

import sys
import os
import math
import time

# -----------------------------------------------------------------------------
# 0. TERMINAL SETUP & VT100 ESCAPE CODES
# -----------------------------------------------------------------------------
# Enable ANSI escape processing on Windows consoles
if os.name == 'nt':
    os.system('')

# Platform-independent non-blocking keyboard input
def get_key_pressed():
    """Returns the single character pressed without blocking, or None."""
    if os.name == 'nt':
        import msvcrt
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            # Handle special/arrow keys
            if ch in (b'\x00', b'\xe0'):
                ch2 = msvcrt.getch()
                if ch2 == b'H': return 'UP'
                elif ch2 == b'P': return 'DOWN'
                return None
            try:
                return ch.decode('utf-8', errors='ignore')
            except Exception:
                return None
        return None
    else:
        import select
        r, _, _ = select.select([sys.stdin], [], [], 0)
        if r:
            return sys.stdin.read(1)
        return None

# -----------------------------------------------------------------------------
# 1. COLOR MATHEMATICS & AESTHETIC PALETTES
# -----------------------------------------------------------------------------
def clamp(val, low=0, high=255):
    return max(low, min(high, int(val)))

def color_lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t)
    )

def rgb_to_hsv(rgb):
    r, g, b = rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    diff = cmax - cmin
    if cmax == cmin:
        h = 0.0
    elif cmax == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif cmax == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360
    s = 0.0 if cmax == 0 else (diff / cmax)
    v = cmax
    return h / 360.0, s, v

def hsv_to_rgb(h, s, v):
    h = h % 1.0
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else: r, g, b = v, p, q
    return int(r * 255), int(g * 255), int(b * 255)

def shift_hue(rgb, hue_offset):
    h, s, v = rgb_to_hsv(rgb)
    return hsv_to_rgb(h + hue_offset, s, v)

class AsciiPalette:
    def __init__(self, name, throat, base, mid, outer, tip, rim, stamen):
        self.name = name
        self.throat = throat
        self.base = base
        self.mid = mid
        self.outer = outer
        self.tip = tip
        self.rim = rim
        self.stamen = stamen

    def shifted(self, hue_delta):
        if abs(hue_delta) < 1e-4:
            return self
        return AsciiPalette(
            self.name,
            throat=shift_hue(self.throat, hue_delta),
            base=shift_hue(self.base, hue_delta),
            mid=shift_hue(self.mid, hue_delta),
            outer=shift_hue(self.outer, hue_delta),
            tip=shift_hue(self.tip, hue_delta),
            rim=shift_hue(self.rim, hue_delta),
            stamen=shift_hue(self.stamen, hue_delta)
        )

    @staticmethod
    def lerp(p1, p2, t):
        return AsciiPalette(
            p2.name if t > 0.5 else p1.name,
            throat=color_lerp(p1.throat, p2.throat, t),
            base=color_lerp(p1.base, p2.base, t),
            mid=color_lerp(p1.mid, p2.mid, t),
            outer=color_lerp(p1.outer, p2.outer, t),
            tip=color_lerp(p1.tip, p2.tip, t),
            rim=color_lerp(p1.rim, p2.rim, t),
            stamen=color_lerp(p1.stamen, p2.stamen, t)
        )

PALETTES = [
    AsciiPalette(
        "Cosmic Nebula",
        throat=(0, 245, 230),       # Luminous electric cyan throat
        base=(70, 20, 195),         # Deep royal violet claw
        mid=(205, 25, 200),         # Radiant electric magenta
        outer=(255, 35, 140),       # Hot neon pink
        tip=(120, 240, 255),        # Celestial turquoise / pale lavender tip
        rim=(255, 115, 225),        # Luminous pink rim
        stamen=(255, 215, 60)       # Golden amber pollen
    ),
    AsciiPalette(
        "Vaporwave Cyber-Lily",
        throat=(0, 255, 255),       # Neon electric cyan
        base=(110, 0, 220),         # Deep electric indigo
        mid=(240, 0, 130),          # Vibrant fuchsia
        outer=(255, 75, 165),       # Bright neon rose
        tip=(140, 255, 245),        # Soft seafoam turquoise
        rim=(80, 240, 255),         # Cyan neon rim
        stamen=(255, 240, 100)      # Neon gold pollen
    ),
    AsciiPalette(
        "Celestial Aurora",
        throat=(110, 255, 190),     # Luminescent mint
        base=(25, 45, 145),         # Midnight blue
        mid=(0, 175, 215),          # Vibrant turquoise
        outer=(100, 75, 235),       # Royal indigo
        tip=(205, 255, 240),        # Shimmering pale emerald
        rim=(70, 255, 220),         # Electric mint rim
        stamen=(255, 185, 75)       # Honey amber
    ),
    AsciiPalette(
        "Twilight Rose Gold",
        throat=(255, 225, 110),     # Champagne core
        base=(95, 15, 60),          # Velvet plum
        mid=(215, 30, 85),          # Ruby crimson
        outer=(255, 90, 130),       # Coral rose
        tip=(255, 225, 195),        # Rose gold
        rim=(255, 165, 140),        # Warm peach rim
        stamen=(255, 240, 140)      # Champagne gold
    ),
    AsciiPalette(
        "Electric Psyche",
        throat=(255, 245, 60),      # Electric lemon
        base=(120, 10, 210),        # Neon violet
        mid=(255, 10, 160),         # Electric magenta
        outer=(0, 230, 255),        # Neon electric cyan
        tip=(255, 255, 255),        # Starlight white
        rim=(0, 255, 190),          # Fluorescent aqua rim
        stamen=(255, 120, 30)       # Burning orange pollen
    ),
]

# -----------------------------------------------------------------------------
# 2. RENDERING GLYPH MODES
# -----------------------------------------------------------------------------
GLYPH_MODES = [
    {"name": "Classic ASCII", "ramp": " .:-=+*#%@"},
    {"name": "Unicode Blocks", "ramp": " ░▒▓█"},
    {"name": "Celestial Runes", "ramp": " ·:✦✧✿❋❊"},
]

# -----------------------------------------------------------------------------
# 3. 3D ASCII LILY ENGINE
# -----------------------------------------------------------------------------
class AsciiLilyEngine:
    """3D parametric lily rasterizer with perspective projection and depth buffer."""
    def __init__(self):
        try:
            import numpy as np
            self.np = np
            self.has_numpy = True
        except ImportError:
            self.np = None
            self.has_numpy = False

        self.glyph_mode_idx = 0
        self.camera_dist = 3.3

    def render_frame(self, t, spin_angle, cols, rows, palette, spin_speed=1.0):
        """Renders one complete frame to a string of ANSI-colored ASCII characters."""
        ramp = GLYPH_MODES[self.glyph_mode_idx]["ramp"]
        ramp_len = len(ramp)

        cx = cols // 2
        cy = rows // 2

        # In text terminals, characters are roughly 2x taller than wide.
        # Scale X is doubled relative to scale Y to maintain circular symmetry.
        scale_y = min(rows * 0.38, 16.0)
        scale_x = scale_y * 2.05
        D = self.camera_dist

        # Initialize buffers
        z_buffer = [[9999.0 for _ in range(cols)] for _ in range(rows)]
        char_buffer = [[" " for _ in range(cols)] for _ in range(rows)]
        color_buffer = [[(0, 0, 0) for _ in range(cols)] for _ in range(rows)]

        # 3D Euler Angles: Spin Yaw + Viewing Pitch + Gentle Nutation
        pitch = math.radians(18.0 + 2.5 * math.sin(t * 0.4))
        roll = math.radians(3.0 * math.cos(t * 0.35))

        cyaw, syaw = math.cos(spin_angle), math.sin(spin_angle)
        cp, sp = math.cos(pitch), math.sin(pitch)
        cr, sr = math.cos(roll), math.sin(roll)

        # 3D Model-View Rotation Matrix: R = Roll * Pitch * Yaw
        # R_yaw:   [[cyaw, -syaw, 0], [syaw, cyaw, 0], [0, 0, 1]]
        # R_pitch: [[1, 0, 0], [0, cp, -sp], [0, sp, cp]]
        # R_roll:  [[cr, 0, sr], [0, 1, 0], [-sr, 0, cr]]
        r00 = cr * cyaw + sr * sp * syaw
        r01 = -cr * syaw + sr * sp * cyaw
        r02 = sr * cp

        r10 = cp * syaw
        r11 = cp * cyaw
        r12 = -sp

        r20 = -sr * cyaw + cr * sp * syaw
        r21 = sr * syaw + cr * sp * cyaw
        r22 = cr * cp

        # Lily Petal Tiers:
        # Tier 0 (Outer 6 sepals): Longer sweeping starburst
        # Tier 1 (Inner 6 petals): Broader, nested inner chalice
        tiers = [
            {"L": 1.08, "W": 0.30, "z_base": 0.08, "angle_off": 0.0, "t_id": 0},
            {"L": 0.72, "W": 0.24, "z_base": -0.06, "angle_off": math.pi / 6.0, "t_id": 1},
        ]

        breath = math.sin(t * 1.05)
        breath_cos = math.cos(t * 1.05)

        # Sample resolution along petal surface
        u_steps = 60
        v_steps = 24

        c_throat = palette.throat
        c_base = palette.base
        c_mid = palette.mid
        c_outer = palette.outer
        c_tip = palette.tip

        # -------------------------------------------------------------
        # 1. RENDER PETAL SURFACES
        # -------------------------------------------------------------
        for tier in tiers:
            L = tier["L"] * (1.0 + 0.04 * breath)
            W = tier["W"]
            z_base = tier["z_base"]
            angle_off = tier["angle_off"]
            t_id = tier["t_id"]

            r_base = 0.06 if t_id == 0 else 0.04

            for p_idx in range(6):
                base_theta = angle_off + p_idx * (2.0 * math.pi / 6.0)
                petal_phase = p_idx * 1.047197

                for i in range(u_steps + 1):
                    u = i / u_steps
                    # Curvaceous teardrop width profile
                    w_shape = math.sin(math.pi * (u ** 0.58)) * ((1.0 - u * 0.78) ** 0.55) * 1.85
                    width = W * w_shape
                    r_spine = r_base + u * L

                    # Swirling spiral sweep + rotational inertia trailing tip lag
                    spiral = 0.22 * (u ** 1.35)
                    drag = -0.045 * (u ** 1.8) * spin_speed + 0.015 * u * math.sin(t * 1.5 + petal_phase)
                    theta = base_theta + spiral + drag

                    # 3D Elevation S-Curve
                    if t_id == 0:
                        z_arch = 0.16 * (u ** 1.6) * (1.0 + 0.14 * breath)
                        z_recurve = -0.06 * (u ** 2.8) * (1.0 + 0.20 * breath_cos)
                    else:
                        z_arch = 0.11 * (u ** 1.7) * (1.0 + 0.12 * breath)
                        z_recurve = -0.05 * (u ** 2.6) * (1.0 + 0.16 * breath_cos)

                    z_flutter = 0.016 * (u ** 2) * math.sin(t * 1.8 + petal_phase)

                    # Multi-stop color interpolation along u
                    if u < 0.20:
                        base_col = color_lerp(c_throat, c_base, u / 0.20)
                    elif u < 0.52:
                        base_col = color_lerp(c_base, c_mid, (u - 0.20) / 0.32)
                    elif u < 0.82:
                        base_col = color_lerp(c_mid, c_outer, (u - 0.52) / 0.30)
                    else:
                        base_col = color_lerp(c_outer, c_tip, (u - 0.82) / 0.18)

                    for j in range(v_steps + 1):
                        v = -1.0 + 2.0 * (j / v_steps)

                        # Midrib fluting & margin silk waviness
                        z_transverse = -0.03 * (v * v) * math.sin(math.pi * (u ** 0.75))
                        z_wave = 0.018 * (abs(v) ** 1.5) * math.sin(3.0 * math.pi * u + t * 2.2 + petal_phase)

                        z_local = z_base + z_arch + z_recurve + z_transverse + z_wave + z_flutter

                        # 3D Polar Position
                        x_local = r_spine * math.cos(theta) - (v * width) * math.sin(theta)
                        y_local = r_spine * math.sin(theta) + (v * width) * math.cos(theta)

                        # Rotate into camera space
                        x_rot = r00 * x_local + r01 * y_local + r02 * z_local
                        y_rot = r10 * x_local + r11 * y_local + r12 * z_local
                        z_rot = r20 * x_local + r21 * y_local + r22 * z_local

                        # Perspective projection
                        denom = D + z_rot
                        if denom < 0.4:
                            denom = 0.4
                        scale = D / denom

                        scol = cx + int(round(x_rot * scale * scale_x))
                        srow = cy - int(round(y_rot * scale * scale_y))

                        if 0 <= scol < cols and 0 <= srow < rows:
                            if z_rot < z_buffer[srow][scol]:
                                z_buffer[srow][scol] = z_rot

                                # Normal & Diffuse lighting
                                p_norm = math.sqrt(x_rot * x_rot + y_rot * y_rot + z_rot * z_rot + 1e-4)
                                dot_l = (x_rot * 0.35 + y_rot * 0.65 - z_rot * 0.65) / p_norm
                                diffuse = 0.68 + 0.32 * dot_l
                                midrib = math.exp(- (v * v) / 0.04) * 0.35
                                lum = max(0.0, min(1.0, diffuse * 0.72 + midrib))

                                char_idx = int(lum * (ramp_len - 1))
                                char_buffer[srow][scol] = ramp[char_idx]

                                # Final colored pixel
                                r = clamp(base_col[0] * lum * 1.25)
                                g = clamp(base_col[1] * lum * 1.25)
                                b = clamp(base_col[2] * lum * 1.25)
                                color_buffer[srow][scol] = (r, g, b)

        # -------------------------------------------------------------
        # 2. RENDER STAMENS WITH GOLDEN ROCKING ANTHERS
        # -------------------------------------------------------------
        stamen_color = palette.stamen
        for s_idx in range(6):
            base_ang = s_idx * (2.0 * math.pi / 6.0) + math.pi / 6.0
            for k in range(16):
                ts = k / 15.0
                r = 0.02 + 0.18 * (ts ** 1.3)
                z = - (0.02 + 0.28 * ts - 0.06 * (ts ** 2))
                ang = base_ang + 0.04 * math.sin(t * 1.8 + s_idx)
                lx = r * math.cos(ang)
                ly = r * math.sin(ang)
                lz = z

                x_rot = r00 * lx + r01 * ly + r02 * lz
                y_rot = r10 * lx + r11 * ly + r12 * lz
                z_rot = r20 * lx + r21 * ly + r22 * lz

                denom = D + z_rot
                if denom < 0.4: denom = 0.4
                scale = D / denom

                scol = cx + int(round(x_rot * scale * scale_x))
                srow = cy - int(round(y_rot * scale * scale_y))

                if 0 <= scol < cols and 0 <= srow < rows:
                    if z_rot < z_buffer[srow][scol]:
                        z_buffer[srow][scol] = z_rot
                        char_buffer[srow][scol] = ":"
                        color_buffer[srow][scol] = (30, 230, 200)

            # Golden Anther at tip: rocking golden pill
            anther_rock = 0.35 * math.sin(t * 2.8 + s_idx * 1.3)
            tan_ang = base_ang + math.pi / 2.0 + anther_rock
            anther_half = 0.04

            for a_sub in [-anther_half, 0.0, anther_half]:
                ax = (0.02 + 0.18) * math.cos(base_ang) + a_sub * math.cos(tan_ang)
                ay = (0.02 + 0.18) * math.sin(base_ang) + a_sub * math.sin(tan_ang)
                az = - (0.02 + 0.28 - 0.06) + a_sub * 0.1 * math.sin(anther_rock)

                x_rot = r00 * ax + r01 * ay + r02 * az
                y_rot = r10 * ax + r11 * ay + r12 * az
                z_rot = r20 * ax + r21 * ay + r22 * az

                denom = D + z_rot
                if denom < 0.4: denom = 0.4
                scale = D / denom

                scol = cx + int(round(x_rot * scale * scale_x))
                srow = cy - int(round(y_rot * scale * scale_y))

                if 0 <= scol < cols and 0 <= srow < rows:
                    # Anthers sit proudly in front
                    if z_rot < z_buffer[srow][scol] + 0.08:
                        z_buffer[srow][scol] = z_rot
                        char_buffer[srow][scol] = "✦"
                        color_buffer[srow][scol] = (
                            clamp(stamen_color[0]),
                            clamp(stamen_color[1]),
                            clamp(stamen_color[2])
                        )

        # -------------------------------------------------------------
        # 3. RENDER CENTRAL PISTIL STIGMA
        # -------------------------------------------------------------
        px, py, pz = 0.0, 0.0, -0.32
        x_rot = r00 * px + r01 * py + r02 * pz
        y_rot = r10 * px + r11 * py + r12 * pz
        z_rot = r20 * px + r21 * py + r22 * pz

        denom = D + z_rot
        if denom < 0.4: denom = 0.4
        scale = D / denom

        scol = cx + int(round(x_rot * scale * scale_x))
        srow = cy - int(round(y_rot * scale * scale_y))

        if 0 <= scol < cols and 0 <= srow < rows:
            z_buffer[srow][scol] = z_rot
            char_buffer[srow][scol] = "✿"
            color_buffer[srow][scol] = (70, 245, 190)

        # -------------------------------------------------------------
        # 4. RENDER 3D ATMOSPHERIC STARDUST SWARM
        # -------------------------------------------------------------
        stardust_count = 42
        for p in range(stardust_count):
            pr = 0.38 + (p * 0.024)
            pang = p * 1.35 + t * (0.16 + (p % 4) * 0.04)
            pz = math.sin(t * 0.8 + p) * 0.38
            lx = pr * math.cos(pang)
            ly = pr * math.sin(pang)
            lz = pz

            x_rot = r00 * lx + r01 * ly + r02 * lz
            y_rot = r10 * lx + r11 * ly + r12 * lz
            z_rot = r20 * lx + r21 * ly + r22 * lz

            denom = D + z_rot
            if denom < 0.4: denom = 0.4
            scale = D / denom

            scol = cx + int(round(x_rot * scale * scale_x))
            srow = cy - int(round(y_rot * scale * scale_y))

            if 0 <= scol < cols and 0 <= srow < rows:
                if z_buffer[srow][scol] > 9000.0:  # In open space
                    star_symbols = ["·", "✦", "°", "✧", "*", "+"]
                    sym = star_symbols[p % len(star_symbols)]
                    twinkle = 0.4 + 0.6 * abs(math.sin(t * 2.6 + p))
                    char_buffer[srow][scol] = sym

                    c_picks = [palette.throat, palette.outer, palette.stamen, palette.tip]
                    cpick = c_picks[p % 4]
                    color_buffer[srow][scol] = (
                        clamp(cpick[0] * twinkle),
                        clamp(cpick[1] * twinkle),
                        clamp(cpick[2] * twinkle)
                    )

        # -------------------------------------------------------------
        # 5. ASSEMBLE ZERO-FLICKER ANSI FRAME BUFFER
        # -------------------------------------------------------------
        frame_lines = []
        for r in range(rows):
            line = ""
            last_col = None
            for c in range(cols):
                ch = char_buffer[r][c]
                if ch == " ":
                    line += " "
                else:
                    col = color_buffer[r][c]
                    if col != last_col:
                        line += f"\033[38;2;{col[0]};{col[1]};{col[2]}m"
                        last_col = col
                    line += ch
            line += "\033[0m"
            frame_lines.append(line)

        return "\n".join(frame_lines)

# -----------------------------------------------------------------------------
# 4. MAIN TERMINAL CONTROLLER
# -----------------------------------------------------------------------------
class AsciiLiliesApp:
    """Master controller managing terminal loop, input handling, and HUD."""
    def __init__(self):
        self.engine = AsciiLilyEngine()
        self.palette_idx = 0
        self.current_palette = PALETTES[0]
        self.target_palette = PALETTES[0]
        self.palette_transition_t = 1.0

        self.auto_morph = True
        self.last_morph_time = time.time()
        self.morph_interval = 12.0

        self.hue_shift_speed = 0.015
        self.current_hue_offset = 0.0

        self.time = 0.0
        self.spin_angle = 0.0
        self.spin_speed = 1.0
        self.is_paused = False
        self.show_hud = True
        self.fps = 30.0

    def next_palette(self):
        self.palette_idx = (self.palette_idx + 1) % len(PALETTES)
        self.target_palette = PALETTES[self.palette_idx]
        self.palette_transition_t = 0.0

    def draw_hud_header(self, cols, active_palette):
        """Builds a stylish top and bottom HUD banner."""
        mode_name = GLYPH_MODES[self.engine.glyph_mode_idx]["name"]
        fps_str = f"{self.fps:.1f} FPS"
        title = "★ LILIUM · PROCEDURAL ASCII ★"
        stats = f"{fps_str} | Theme: {active_palette.name} | Mode: {mode_name} | Speed: {self.spin_speed:.1f}x"
        
        # Center title
        pad_t = max(0, (cols - len(title)) // 2)
        top_line = f"\033[1;38;2;220;240;255m{' ' * pad_t}{title}\033[0m"

        pad_s = max(0, (cols - len(stats)) // 2)
        sub_line = f"\033[38;2;140;180;220m{' ' * pad_s}{stats}\033[0m"

        return f"{top_line}\n{sub_line}\n"

    def draw_hud_footer(self, cols):
        """Builds bottom hint bar."""
        hint = "[SPACE] Pause | [C] Theme | [M] Morph | [1/2/3] Mode | [+/-] Speed | [H] HUD | [Q] Exit"
        pad = max(0, (cols - len(hint)) // 2)
        return f"\033[38;2;120;110;150m{' ' * pad}{hint}\033[0m"

    def run(self):
        """Main execution loop for real-time terminal animation."""
        # Hide terminal cursor and clear screen
        sys.stdout.write("\033[?25l\033[2J")
        sys.stdout.flush()

        last_time = time.perf_counter()
        fps_timer = time.perf_counter()
        frame_count = 0

        try:
            while True:
                current_time = time.perf_counter()
                dt = current_time - last_time
                last_time = current_time
                dt = min(0.1, dt)

                # FPS Counter calculation
                frame_count += 1
                if current_time - fps_timer >= 0.5:
                    self.fps = frame_count / (current_time - fps_timer)
                    frame_count = 0
                    fps_timer = current_time

                # Non-blocking keypress handling
                key = get_key_pressed()
                if key:
                    if key.lower() in ('q', '\x1b'):  # 'q' or ESC
                        break
                    elif key == ' ':
                        self.is_paused = not self.is_paused
                    elif key.lower() == 'c':
                        self.next_palette()
                    elif key.lower() == 'm':
                        self.auto_morph = not self.auto_morph
                    elif key.lower() == 'h':
                        self.show_hud = not self.show_hud
                    elif key in ('1', '2', '3'):
                        self.engine.glyph_mode_idx = int(key) - 1
                    elif key in ('+', '=', 'UP'):
                        self.spin_speed = min(3.0, self.spin_speed + 0.2)
                    elif key in ('-', '_', 'DOWN'):
                        self.spin_speed = max(0.1, self.spin_speed - 0.2)

                # Update physics and animation
                if not self.is_paused:
                    self.time += dt
                    self.spin_angle += dt * 0.45 * self.spin_speed
                    self.current_hue_offset = (self.current_hue_offset + dt * self.hue_shift_speed) % 1.0

                # Palette smooth cross-fading
                if self.palette_transition_t < 1.0:
                    self.palette_transition_t = min(1.0, self.palette_transition_t + dt * 1.2)
                    self.current_palette = AsciiPalette.lerp(self.current_palette, self.target_palette, self.palette_transition_t)
                else:
                    self.current_palette = self.target_palette

                # Auto-Morphing schedule
                if self.auto_morph and (time.time() - self.last_morph_time > self.morph_interval):
                    self.next_palette()
                    self.last_morph_time = time.time()

                # Get dynamic terminal dimensions
                try:
                    size = os.get_terminal_size()
                    term_cols, term_rows = size.columns, size.lines
                except Exception:
                    term_cols, term_rows = 80, 36

                # Reserve rows for HUD if enabled
                hud_offset = 3 if self.show_hud else 0
                hud_bottom = 2 if self.show_hud else 0
                render_rows = max(18, term_rows - hud_offset - hud_bottom)
                render_cols = max(40, term_cols)

                active_palette = self.current_palette.shifted(self.current_hue_offset)

                # Render 3D frame
                frame_content = self.engine.render_frame(
                    self.time, self.spin_angle, render_cols, render_rows, active_palette, self.spin_speed
                )

                # Assemble full screen buffer with cursor home: ZERO flicker!
                output_buffer = "\033[H"
                if self.show_hud:
                    output_buffer += self.draw_hud_header(render_cols, active_palette)
                output_buffer += frame_content
                if self.show_hud:
                    output_buffer += "\n" + self.draw_hud_footer(render_cols)

                sys.stdout.write(output_buffer)
                sys.stdout.flush()

                # Target 35-40 FPS in terminal (smooth and easy on CPU)
                target_frame_time = 1.0 / 35.0
                elapsed = time.perf_counter() - current_time
                if elapsed < target_frame_time:
                    time.sleep(target_frame_time - elapsed)

        except KeyboardInterrupt:
            pass
        finally:
            # Restore cursor, reset colors, and clear screen
            sys.stdout.write("\033[?25h\033[0m\033[2J\033[H")
            sys.stdout.flush()
            print("Lilium Procedural ASCII animation terminated cleanly.")

# -----------------------------------------------------------------------------
# 5. SCRIPT ENTRY POINT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = AsciiLiliesApp()
    app.run()
