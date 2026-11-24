"""
================================================================================
  SPINNING LILIES — MESMERIZING PROCEDURAL AESTHETIC ANIMATION
================================================================================
  Generative 3D Botanical Art & Mathematical Motion Design
  
  Features:
  - 12 Parametrically Sculpted Lily Tepals (6 Outer Sepals + 6 Inner Petals)
  - Organic S-Curve Arch, Transverse Fluting, and Silky Margin Ruffling
  - Rotational Inertia Trailing & Harmonic Breathing Blooming Motion
  - Realistic Floral Center: 6 Stamens with Rocking Golden Anthers & Pistil
  - Viral TikTok Generative Color Palettes (Electric Violet, Magenta, Cyan, Gold)
  - Dynamic Hue Shifting & Smooth Real-Time Palette Cross-Fading
  - Soft Multi-Layer Gaussian Bloom & Core Aura Emission
  - 3D Atmospheric Stardust Swarm with Twinkling Particles
  - Interactive 3D Orbit Camera (Mouse Drag / Zoom)
  - Fullscreen (F11), Resizable Window, FPS Counter & Minimal Glassmorphic HUD
================================================================================
"""

import sys
import os
import math
import time
import subprocess

# -----------------------------------------------------------------------------
# 0. AUTOMATIC DEPENDENCY MANAGEMENT & PRE-CHECK
# -----------------------------------------------------------------------------
def check_and_install_dependencies():
    """Checks for required dependencies (pygame-ce/pygame, numpy) and offers guidance."""
    missing = []
    try:
        import numpy
    except ImportError:
        missing.append("numpy")

    try:
        import pygame
    except ImportError:
        missing.append("pygame-ce")

    if missing:
        print("\n" + "=" * 70)
        print("  SPINNING LILIES — PROCEDURAL AESTHETIC ANIMATION")
        print("=" * 70)
        print("  Missing required Python libraries:")
        for pkg in missing:
            print(f"    - {pkg}")
        print("\n  To install them manually, run:")
        print(f"    pip install {' '.join(missing)}")
        print("=" * 70 + "\n")

        # Attempt automatic installation if in an interactive terminal
        if sys.stdin and sys.stdin.isatty():
            try:
                choice = input("Would you like to install missing dependencies automatically now? (y/n): ").strip().lower()
                if choice in ('y', 'yes'):
                    print(f"\nInstalling {', '.join(missing)} via pip...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
                    print("Installation successful! Starting animation...\n")
                    return
            except Exception as e:
                print(f"Automatic installation failed: {e}")
        
        print("Please install the dependencies above and re-run the script.")
        sys.exit(1)

check_and_install_dependencies()

import numpy as np
import pygame

# -----------------------------------------------------------------------------
# 1. COLOR PALETTES & PROCEDURAL COLOR MATH
# -----------------------------------------------------------------------------
def clamp(val, low=0, high=255):
    """Clamps a numeric value into an integer byte range [low, high]."""
    return max(low, min(high, int(val)))

def color_lerp(c1, c2, t):
    """Linear interpolation between two RGB color tuples."""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t)
    )

def rgb_to_hsv(rgb):
    """Converts RGB (0-255) to HSV (0-1)."""
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
    """Converts HSV (0-1) to RGB (0-255)."""
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
    """Shifts the hue of an RGB color by hue_offset (0-1)."""
    h, s, v = rgb_to_hsv(rgb)
    return hsv_to_rgb(h + hue_offset, s, v)

class Palette:
    """Represents a coordinated celestial color scheme for flower petals and atmosphere."""
    def __init__(self, name, throat, base, mid, outer, tip, rim, stamen):
        self.name = name
        self.throat = throat      # Luminous throat/nectary core
        self.base = base          # Petal claw / base
        self.mid = mid            # Main broad petal body
        self.outer = outer        # Upper petal flair
        self.tip = tip            # Petal apex highlight
        self.rim = rim            # Edge fluorescent highlight
        self.stamen = stamen      # Anther pollen glow

    def shifted(self, hue_delta):
        """Returns a new Palette with smoothly shifted hues."""
        if abs(hue_delta) < 1e-5:
            return self
        return Palette(
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
        """Smoothly blends between two palettes."""
        return Palette(
            p2.name if t > 0.5 else p1.name,
            throat=color_lerp(p1.throat, p2.throat, t),
            base=color_lerp(p1.base, p2.base, t),
            mid=color_lerp(p1.mid, p2.mid, t),
            outer=color_lerp(p1.outer, p2.outer, t),
            tip=color_lerp(p1.tip, p2.tip, t),
            rim=color_lerp(p1.rim, p2.rim, t),
            stamen=color_lerp(p1.stamen, p2.stamen, t)
        )

# Handcrafted viral aesthetic color palettes
PRESET_PALETTES = [
    Palette(
        "Cosmic Nebula",
        throat=(0, 245, 230),       # Luminous electric cyan throat
        base=(70, 20, 195),         # Deep royal violet claw
        mid=(195, 25, 205),         # Radiant electric orchid / magenta
        outer=(255, 35, 140),       # Hot neon pink flair
        tip=(120, 240, 255),        # Celestial turquoise / pale lavender tip
        rim=(255, 115, 225),        # Luminous pink edge glow
        stamen=(255, 215, 60)       # Golden amber pollen
    ),
    Palette(
        "Vaporwave Cyber-Lily",
        throat=(0, 255, 255),       # Neon electric cyan
        base=(110, 0, 220),         # Deep electric indigo
        mid=(240, 0, 130),          # Vibrant fuchsia
        outer=(255, 75, 165),       # Bright neon rose
        tip=(140, 255, 245),        # Soft seafoam turquoise
        rim=(80, 240, 255),         # Cyan neon rim
        stamen=(255, 240, 100)      # Neon gold pollen
    ),
    Palette(
        "Celestial Aurora",
        throat=(110, 255, 190),     # Luminescent mint
        base=(25, 45, 145),         # Midnight abyss blue
        mid=(0, 175, 215),          # Vibrant turquoise
        outer=(100, 75, 235),       # Electric royal indigo
        tip=(205, 255, 240),        # Shimmering pale emerald
        rim=(70, 255, 220),         # Electric mint rim
        stamen=(255, 185, 75)       # Warm honey amber
    ),
    Palette(
        "Twilight Rose Gold",
        throat=(255, 225, 110),     # Warm champagne core
        base=(95, 15, 60),          # Deep velvet plum
        mid=(215, 30, 85),          # Rich ruby crimson
        outer=(255, 90, 130),       # Coral rose
        tip=(255, 225, 195),        # Iridescent rose gold
        rim=(255, 165, 140),        # Warm peach rim
        stamen=(255, 240, 140)      # Champagne gold
    ),
    Palette(
        "Electric Psyche",
        throat=(255, 245, 60),      # Radiant electric lemon
        base=(120, 10, 210),        # Vivid neon violet
        mid=(255, 10, 160),         # Electric magenta
        outer=(0, 230, 255),        # Neon electric cyan
        tip=(255, 255, 255),        # Pure starlight white
        rim=(0, 255, 190),          # Fluorescent aqua rim
        stamen=(255, 120, 30)       # Burning orange pollen
    ),
]

# -----------------------------------------------------------------------------
# 2. BLOOM & GAUSSIAN GLOW ENGINE
# -----------------------------------------------------------------------------
class GlowEngine:
    """Generates and caches smooth Gaussian radial glow surfaces for additive bloom."""
    def __init__(self):
        self._cache = {}

    def get_glow_disc(self, radius, color, max_alpha=100):
        """
        Creates an additive glow surface where RGB values fall off exponentially.
        In Pygame BLEND_ADD mode, this produces perfectly smooth volumetric light halos.
        """
        # Round radius to reduce cache churn
        r_key = int(radius)
        c_key = (int(color[0]), int(color[1]), int(color[2]), int(max_alpha))
        key = (r_key, c_key)
        if key in self._cache:
            return self._cache[key]

        size = r_key * 2
        surf = pygame.Surface((size, size))
        surf.fill((0, 0, 0))

        y, x = np.ogrid[-r_key:r_key, -r_key:r_key]
        dist_sq = x * x + y * y
        r_sq = float(r_key * r_key)

        norm_dist = np.sqrt(dist_sq) / float(r_key)
        falloff = np.exp(-3.2 * (norm_dist ** 1.8))
        falloff[dist_sq > r_sq] = 0.0

        factor = (max_alpha / 255.0) * falloff
        r_arr = np.clip(color[0] * factor, 0, 255).astype(np.uint8)
        g_arr = np.clip(color[1] * factor, 0, 255).astype(np.uint8)
        b_arr = np.clip(color[2] * factor, 0, 255).astype(np.uint8)

        rgb = np.dstack((r_arr, g_arr, b_arr))
        pygame.surfarray.blit_array(surf, rgb)

        # Cache if not overflowing
        if len(self._cache) < 60:
            self._cache[key] = surf
        return surf

# -----------------------------------------------------------------------------
# 3. 3D ATMOSPHERIC STARDUST PARTICLE SWARM
# -----------------------------------------------------------------------------
class ParticleSystem:
    """3D stardust particles swirling in the wake of the spinning flower."""
    def __init__(self, count=160):
        self.count = count
        np.random.seed(1337)
        self.radii = np.random.uniform(70.0, 520.0, count).astype(np.float32)
        self.angles = np.random.uniform(0.0, 2.0 * math.pi, count).astype(np.float32)
        self.z_coords = np.random.uniform(-180.0, 180.0, count).astype(np.float32)
        # Inner particles swirl slightly faster (vortex dynamics)
        self.orbit_speeds = (0.28 / (self.radii ** 0.35)) * np.random.choice([1.0, 1.0, 0.8, -0.4], count).astype(np.float32)
        self.sizes = np.random.uniform(2.0, 5.0, count).astype(np.float32)
        self.twinkle_speeds = np.random.uniform(1.4, 3.8, count).astype(np.float32)
        self.phases = np.random.uniform(0.0, 2.0 * math.pi, count).astype(np.float32)
        self.color_slots = np.random.randint(0, 4, count)

    def get_particles(self, t, R, palette):
        """Transforms particles to 3D camera space and returns depth-sortable objects."""
        palette_colors = [palette.throat, palette.mid, palette.outer, palette.tip]
        particles = []

        for i in range(self.count):
            ang = self.angles[i] + self.orbit_speeds[i] * t * 0.6
            r = self.radii[i] + 16.0 * math.sin(t * 0.7 + self.phases[i])
            z = self.z_coords[i] + 22.0 * math.cos(t * 0.5 + self.phases[i])

            lx = r * math.cos(ang)
            ly = r * math.sin(ang)
            lz = z

            pt3d = np.array([lx, ly, lz], dtype=np.float32) @ R.T
            twinkle = 0.35 + 0.65 * abs(math.sin(t * self.twinkle_speeds[i] + self.phases[i]))
            base_col = palette_colors[self.color_slots[i]]
            col = (
                clamp(base_col[0] * twinkle),
                clamp(base_col[1] * twinkle),
                clamp(base_col[2] * twinkle)
            )

            particles.append({
                "type": "particle",
                "pt": pt3d,
                "depth": pt3d[2],
                "color": col,
                "size": self.sizes[i],
                "twinkle": twinkle
            })
        return particles

# -----------------------------------------------------------------------------
# 4. 3D PARAMETRIC LILY FLOWER MATHEMATICS
# -----------------------------------------------------------------------------
class LilyFlower3D:
    """
    Parametric botanical model of a 12-tepal Oriental Lily.
    Features dual-tier architecture, S-curve profiles, transverse fluting,
    trailing tip lag, stamens with golden rocking anthers, and center pistil.
    """
    def __init__(self):
        self.camera_dist = 850.0
        # Mesh discretization: high quality yet rock-solid 60+ FPS
        self.u_segs = 18
        self.v_segs = 7

    def get_petal_vertex(self, u, v, tier_cfg, petal_idx, num_petals, t, spin_speed):
        """
        Calculates the 3D position (X, Y, Z) of point (u, v) on a petal.
        u in [0, 1] : longitudinal parameter (0=base claw, 1=tip apex)
        v in [-1, 1] : transverse parameter (-1=left margin, 0=spine, 1=right margin)
        """
        L = tier_cfg["L"]
        W = tier_cfg["W"]
        angle_offset = tier_cfg["angle_offset"]
        tier_id = tier_cfg["tier_id"]

        # Base radial angle
        base_theta = angle_offset + petal_idx * (2.0 * math.pi / num_petals)

        # Hypnotic breathing pulsation: slow, lifelike floral expansion and contraction
        breath = math.sin(t * 1.05)
        breath_cos = math.cos(t * 1.05)

        # Dynamic petal length and organic phase offset
        L_dyn = L * (1.0 + 0.04 * breath)
        petal_phase = petal_idx * 1.047197  # pi / 3

        # Swirling logarithmic spiral sweep + rotational inertia trailing lag
        spiral_sweep = 0.22 * (u ** 1.35)
        drag = -0.045 * (u ** 1.8) * spin_speed + 0.015 * u * math.sin(t * 1.5 + petal_phase)
        theta = base_theta + spiral_sweep + drag

        # Lily Petal Width envelope:
        # Narrow base attachment (claw), broad curvaceous body, sharp recurved tip
        w_shape = math.sin(math.pi * (u ** 0.58)) * ((1.0 - u * 0.78) ** 0.55) * 1.85
        width = W * w_shape

        # 3D Starburst Architecture:
        # Petals emerge from central receptacle, flare outward, arch gently back
        if tier_id == 0:  # Outer petals (longer sweeping star)
            z_base = 12.0
            z_arch = 45.0 * (u ** 1.6) * (1.0 + 0.14 * breath)
            z_recurve = -18.0 * (u ** 2.8) * (1.0 + 0.20 * breath_cos)
            r_base = 26.0
        else:  # Inner petals (broader, nestled inside outer sepals)
            z_base = -10.0
            z_arch = 32.0 * (u ** 1.7) * (1.0 + 0.12 * breath)
            z_recurve = -14.0 * (u ** 2.6) * (1.0 + 0.16 * breath_cos)
            r_base = 18.0

        # Transverse fluting / crease along midrib & winged margins
        z_transverse = -8.0 * (v * v) * math.sin(math.pi * (u ** 0.75))
        # Delicate undulating silk waves along margins
        z_wave = 5.0 * (abs(v) ** 1.5) * math.sin(3.0 * math.pi * u + t * 2.2 + petal_phase)
        # Gentle organic petal flutter
        z_flutter = 5.0 * (u ** 2) * math.sin(t * 1.8 + petal_phase)

        z = z_base + z_arch + z_recurve + z_transverse + z_wave + z_flutter

        # Radial distance from stem center
        r_spine = r_base + u * L_dyn

        # Combine into petal 3D polar coordinate offset
        x = r_spine * math.cos(theta) - (v * width) * math.sin(theta)
        y = r_spine * math.sin(theta) + (v * width) * math.cos(theta)

        return np.array([x, y, z], dtype=np.float32)

    def generate_mesh(self, t, spin, pitch_offset, yaw_offset, spin_speed):
        """Generates all 3D triangles and edge outlines with smooth interpolated normals."""
        tiers = [
            {"L": 410.0, "W": 115.0, "angle_offset": 0.0, "count": 6, "tier_id": 0},
            {"L": 270.0, "W": 90.0, "angle_offset": math.pi / 6.0, "count": 6, "tier_id": 1},
        ]

        # 3D Camera Rotation Matrix (Euler: Yaw -> Pitch -> Roll)
        yaw = spin + yaw_offset
        # Gentle natural nutation & viewing inclination
        pitch = math.radians(16.0 + 2.5 * math.sin(t * 0.4)) + pitch_offset
        roll = math.radians(3.0 * math.cos(t * 0.35))

        cy, sy = math.cos(yaw), math.sin(yaw)
        R_yaw = np.array([
            [cy, -sy, 0],
            [sy,  cy, 0],
            [ 0,   0, 1]
        ], dtype=np.float32)

        cp, sp = math.cos(pitch), math.sin(pitch)
        R_pitch = np.array([
            [1,  0,   0],
            [0, cp, -sp],
            [0, sp,  cp]
        ], dtype=np.float32)

        cr, sr = math.cos(roll), math.sin(roll)
        R_roll = np.array([
            [ cr, 0, sr],
            [  0, 1,  0],
            [-sr, 0, cr]
        ], dtype=np.float32)

        R = R_roll @ (R_pitch @ R_yaw)

        triangles = []
        outlines = []

        u_segs = self.u_segs
        v_segs = self.v_segs

        for tier in tiers:
            count = tier["count"]
            tier_id = tier["tier_id"]

            for p_idx in range(count):
                grid_verts = np.zeros((u_segs + 1, v_segs + 1, 3), dtype=np.float32)
                for i in range(u_segs + 1):
                    u = i / u_segs
                    for j in range(v_segs + 1):
                        v = -1.0 + 2.0 * (j / v_segs)
                        pt = self.get_petal_vertex(u, v, tier, p_idx, count, t, spin_speed)
                        grid_verts[i, j] = pt

                flat_verts = grid_verts.reshape(-1, 3)
                rot_verts = flat_verts @ R.T
                rot_grid = rot_verts.reshape(u_segs + 1, v_segs + 1, 3)

                # Precompute smooth continuous vertex normals via central differences
                vertex_normals = np.zeros((u_segs + 1, v_segs + 1, 3), dtype=np.float32)
                for i in range(u_segs + 1):
                    i_prev = max(0, i - 1)
                    i_next = min(u_segs, i + 1)
                    for j in range(v_segs + 1):
                        j_prev = max(0, j - 1)
                        j_next = min(v_segs, j + 1)
                        du = rot_grid[i_next, j] - rot_grid[i_prev, j]
                        dv = rot_grid[i, j_next] - rot_grid[i, j_prev]
                        n = np.cross(du, dv)
                        nlen = np.linalg.norm(n)
                        if nlen > 1e-6:
                            vertex_normals[i, j] = n / nlen
                        else:
                            vertex_normals[i, j] = np.array([0, 0, 1], dtype=np.float32)

                # Assemble strictly planar triangles with smooth normals
                for i in range(u_segs):
                    u_mid = (i + 0.5) / u_segs
                    for j in range(v_segs):
                        v_mid = -1.0 + 2.0 * ((j + 0.5) / v_segs)

                        p00 = rot_grid[i, j]
                        p10 = rot_grid[i + 1, j]
                        p11 = rot_grid[i + 1, j + 1]
                        p01 = rot_grid[i, j + 1]

                        norm_quad = (vertex_normals[i, j] + vertex_normals[i+1, j] +
                                     vertex_normals[i+1, j+1] + vertex_normals[i, j+1]) * 0.25
                        nlen = np.linalg.norm(norm_quad)
                        if nlen > 1e-6:
                            norm_quad /= nlen

                        # Triangle 1
                        depth1 = (p00[2] + p10[2] + p11[2]) / 3.0
                        triangles.append({
                            "type": "tri",
                            "pts": [p00, p10, p11],
                            "depth": depth1,
                            "normal": norm_quad,
                            "u": u_mid,
                            "v": v_mid,
                            "tier": tier_id
                        })

                        # Triangle 2
                        depth2 = (p00[2] + p11[2] + p01[2]) / 3.0
                        triangles.append({
                            "type": "tri",
                            "pts": [p00, p11, p01],
                            "depth": depth2,
                            "normal": norm_quad,
                            "u": u_mid,
                            "v": v_mid,
                            "tier": tier_id
                        })

                # Petal perimeter edge outline for luminous neon rim
                left_edge = [rot_grid[i, 0] for i in range(u_segs + 1)]
                right_edge = [rot_grid[i, v_segs] for i in range(u_segs, -1, -1)]
                outline_3d = left_edge + right_edge
                outline_depth = np.mean([pt[2] for pt in outline_3d])
                outlines.append({
                    "type": "outline",
                    "pts": outline_3d,
                    "depth": outline_depth,
                    "tier": tier_id
                })

        return triangles, outlines, R

    def generate_center_elements(self, t, R):
        """Generates stamens with rocking golden anthers, central pistil, and throat receptacle."""
        elements = []
        num_stamens = 6

        # 6 Graceful Stamens with rocking golden pollen anthers
        for s_idx in range(num_stamens):
            base_angle = s_idx * (2.0 * math.pi / num_stamens) + math.pi / 6.0
            stamen_pts = []
            steps = 12
            for k in range(steps + 1):
                ts = k / steps
                # Filament arches out from throat and bends toward viewer (-Z)
                r = 4.0 + 60.0 * (ts ** 1.3)
                z = - (6.0 + 85.0 * ts - 15.0 * (ts ** 2))
                ang = base_angle + 0.05 * math.sin(t * 1.8 + s_idx)
                lx = r * math.cos(ang)
                ly = r * math.sin(ang)
                lz = z
                stamen_pts.append(np.array([lx, ly, lz], dtype=np.float32))

            stamen_pts_np = np.array(stamen_pts) @ R.T

            # Anther at the tip: large, prominent, golden oblong mounted perpendicularly
            tip_pre_rot = stamen_pts[-1]
            anther_rock = 0.35 * math.sin(t * 2.8 + s_idx * 1.3)
            tan_ang = base_angle + math.pi / 2.0 + anther_rock
            anther_half_len = 16.0

            anther_p1 = tip_pre_rot + np.array([
                anther_half_len * math.cos(tan_ang),
                anther_half_len * math.sin(tan_ang),
                - 5.0 * math.sin(anther_rock)
            ], dtype=np.float32)
            anther_p2 = tip_pre_rot - np.array([
                anther_half_len * math.cos(tan_ang),
                anther_half_len * math.sin(tan_ang),
                - 5.0 * math.sin(anther_rock)
            ], dtype=np.float32)

            anther_p1_rot = anther_p1 @ R.T
            anther_p2_rot = anther_p2 @ R.T
            anther_depth = (anther_p1_rot[2] + anther_p2_rot[2]) * 0.5

            # Filament segments
            for seg in range(len(stamen_pts_np) - 1):
                p_a = stamen_pts_np[seg]
                p_b = stamen_pts_np[seg + 1]
                elements.append({
                    "type": "stamen_seg",
                    "p1": p_a,
                    "p2": p_b,
                    "depth": (p_a[2] + p_b[2]) * 0.5
                })

            # Anther element
            elements.append({
                "type": "anther",
                "p1": anther_p1_rot,
                "p2": anther_p2_rot,
                "depth": anther_depth,
                "idx": s_idx
            })

        # Central Pistil (Tall Column + Glowing 3-Lobed Stigma)
        pistil_pts = []
        for k in range(10):
            ts = k / 9.0
            r = 3.0 * (1.0 - ts * 0.25)
            z = - (6.0 + 105.0 * ts)
            ang = 0.03 * math.sin(t * 1.4)
            lx = r * math.cos(ang)
            ly = r * math.sin(ang)
            lz = z
            pistil_pts.append(np.array([lx, ly, lz], dtype=np.float32))

        pistil_pts_np = np.array(pistil_pts) @ R.T
        for seg in range(len(pistil_pts_np) - 1):
            p_a = pistil_pts_np[seg]
            p_b = pistil_pts_np[seg + 1]
            elements.append({
                "type": "pistil_seg",
                "p1": p_a,
                "p2": p_b,
                "depth": (p_a[2] + p_b[2]) * 0.5
            })

        stigma_tip = pistil_pts_np[-1]
        elements.append({
            "type": "stigma",
            "pt": stigma_tip,
            "depth": stigma_tip[2]
        })

        # Central Floral Receptacle / Throat Disc (smooth chalice anchoring petals)
        num_core_pts = 24
        core_r = 22.0
        core_z = -12.0
        center_pt = np.array([0.0, 0.0, core_z], dtype=np.float32) @ R.T
        ring_pts = []
        for k in range(num_core_pts):
            ang = k * (2.0 * math.pi / num_core_pts)
            pt = np.array([core_r * math.cos(ang), core_r * math.sin(ang), core_z + 3.0], dtype=np.float32) @ R.T
            ring_pts.append(pt)

        for k in range(num_core_pts):
            p_curr = ring_pts[k]
            p_next = ring_pts[(k + 1) % num_core_pts]
            d = (center_pt[2] + p_curr[2] + p_next[2]) / 3.0
            elements.append({
                "type": "receptacle_tri",
                "pts": [center_pt, p_curr, p_next],
                "depth": d
            })

        return elements

    def project_point(self, pt3d, cx, cy, zoom=1.0):
        """Perspective 3D to 2D projection with dynamic camera focal distance."""
        x, y, z = pt3d[0], pt3d[1], pt3d[2]
        denom = (self.camera_dist / zoom) + z
        if denom < 40.0:
            denom = 40.0
        scale = (self.camera_dist / zoom) / denom
        sx = cx + x * scale
        sy = cy - y * scale
        return (int(sx), int(sy))

    def shade_quad(self, u, v, normal, tier_id, palette):
        """Computes vibrant multi-color gradient with soft studio diffuse, midrib and rim glow."""
        c_throat = palette.throat
        c_base = palette.base
        c_mid = palette.mid
        c_outer = palette.outer
        c_tip = palette.tip

        # Spline-smooth 5-stop color progression along length u
        if u < 0.20:
            base_col = color_lerp(c_throat, c_base, u / 0.20)
        elif u < 0.52:
            base_col = color_lerp(c_base, c_mid, (u - 0.20) / 0.32)
        elif u < 0.82:
            base_col = color_lerp(c_mid, c_outer, (u - 0.52) / 0.30)
        else:
            base_col = color_lerp(c_outer, c_tip, (u - 0.82) / 0.18)

        # Soft studio lighting: 68% ambient for silky colors + 32% directional
        light_dir = np.array([0.35, 0.65, 0.65], dtype=np.float32)
        light_dir /= np.linalg.norm(light_dir)
        view_dir = np.array([0.0, 0.0, 1.0], dtype=np.float32)

        dot_l = float(np.dot(normal, light_dir))
        diffuse = 0.68 + 0.32 * dot_l

        # Specular glint along glossy curves
        h = light_dir + view_dir
        h /= np.linalg.norm(h)
        spec_dot = max(0.0, float(np.dot(normal, h)))
        spec = (spec_dot ** 8) * 0.28

        # Luminous Fresnel rim glow (velvety edges)
        dot_v = abs(float(np.dot(normal, view_dir)))
        fresnel = ((1.0 - dot_v) ** 1.8) * 0.38

        # Luminous Midrib Spine (smooth exponential streak down center)
        midrib = math.exp(- (v * v) / 0.035) * 0.42

        # Glowing Petal Margins (outer rim glow)
        margin_dist = abs(v)
        margin_glow = (margin_dist ** 2.2) * 0.32

        # Longitudinal vein striations
        vein = 0.04 * math.sin(16.0 * math.pi * v) * math.sqrt(u)

        # Combine channels with rich additive glow
        r = base_col[0] * (diffuse + vein) + 255.0 * (spec + fresnel) + palette.rim[0] * (midrib + margin_glow)
        g = base_col[1] * (diffuse + vein) + 255.0 * (spec + fresnel) + palette.rim[1] * (midrib + margin_glow)
        b = base_col[2] * (diffuse + vein) + 255.0 * (spec + fresnel) + palette.rim[2] * (midrib + margin_glow)

        return (clamp(r), clamp(g), clamp(b))

# -----------------------------------------------------------------------------
# 5. BACKGROUND ATMOSPHERE & VIGNETTE
# -----------------------------------------------------------------------------
def render_background(surface, w, h, time_val):
    """Draws a deep dark cosmic radial background with breathing vignette."""
    cx, cy = w // 2, h // 2
    max_r = int(math.hypot(cx, cy))
    surface.fill((4, 2, 10))
    for r in range(max_r, 0, -35):
        ratio = r / max_r
        pulse = 0.05 * math.sin(time_val * 0.8)
        c_r = int(22 * (1.0 - ratio) * (1.0 + pulse))
        c_g = int(10 * (1.0 - ratio))
        c_b = int(52 * (1.0 - ratio) * (1.0 + pulse))
        pygame.draw.circle(surface, (c_r, c_g, c_b), (cx, cy), r)

# -----------------------------------------------------------------------------
# 6. MAIN APPLICATION CONTROLLER
# -----------------------------------------------------------------------------
class SpinningLiliesApp:
    """Master controller managing game loop, user interactions, rendering, and HUD."""
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Procedural Spinning Lilies — Hypnotic Generative Art")

        # Display Setup: Resizable, 1280x800 default
        self.width = 1280
        self.height = 800
        self.flags = pygame.RESIZABLE
        self.screen = pygame.display.set_mode((self.width, self.height), self.flags)
        self.clock = pygame.time.Clock()
        self.is_fullscreen = False

        # Generative Models
        self.flower = LilyFlower3D()
        self.particles = ParticleSystem(count=160)
        self.glow_engine = GlowEngine()

        # Palettes & Transitions
        self.palette_idx = 0
        self.current_palette = PRESET_PALETTES[0]
        self.target_palette = PRESET_PALETTES[0]
        self.palette_transition_t = 1.0  # 1.0 = fully transitioned
        self.auto_morph = True
        self.last_morph_time = time.time()
        self.morph_interval = 14.0  # seconds between auto-morphing themes

        # Dynamic Hue Flow
        self.hue_shift_speed = 0.015  # Continuous subtle hue drift
        self.current_hue_offset = 0.0

        # Animation & Physics state
        self.time = 0.0
        self.spin_angle = 0.0
        self.spin_speed = 1.0
        self.is_paused = False

        # Interactive 3D Camera
        self.pitch_offset = 0.0
        self.yaw_offset = 0.0
        self.zoom = 1.0
        self.is_dragging = False
        self.last_mouse_pos = (0, 0)

        # UI & HUD state
        self.show_hud = True
        self.font = pygame.font.SysFont("Segoe UI", 16) or pygame.font.Font(None, 20)
        self.title_font = pygame.font.SysFont("Segoe UI", 22, bold=True) or pygame.font.Font(None, 26)
        self.fps = 60.0

    def toggle_fullscreen(self):
        """Toggles between windowed and fullscreen modes."""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((self.width, self.height), self.flags)
        self.width, self.height = self.screen.get_size()

    def next_palette(self):
        """Initiates a smooth animated cross-fade to the next palette preset."""
        self.palette_idx = (self.palette_idx + 1) % len(PRESET_PALETTES)
        self.target_palette = PRESET_PALETTES[self.palette_idx]
        self.palette_transition_t = 0.0

    def handle_events(self):
        """Processes all keyboard, mouse, and window events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.VIDEORESIZE:
                if not self.is_fullscreen:
                    self.width, self.height = event.w, event.h
                    self.screen = pygame.display.set_mode((self.width, self.height), self.flags)

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False

                elif event.key == pygame.K_SPACE:
                    self.is_paused = not self.is_paused

                elif event.key == pygame.K_c:
                    self.next_palette()

                elif event.key == pygame.K_m:
                    self.auto_morph = not self.auto_morph

                elif event.key in (pygame.K_h, pygame.K_TAB):
                    self.show_hud = not self.show_hud

                elif event.key in (pygame.K_f, pygame.K_F11):
                    self.toggle_fullscreen()

                elif event.key == pygame.K_UP:
                    self.spin_speed = min(3.0, self.spin_speed + 0.2)

                elif event.key == pygame.K_DOWN:
                    self.spin_speed = max(0.1, self.spin_speed - 0.2)

                elif event.key == pygame.K_r:
                    # Reset camera & speed
                    self.pitch_offset = 0.0
                    self.yaw_offset = 0.0
                    self.zoom = 1.0
                    self.spin_speed = 1.0

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click: start 3D drag
                    self.is_dragging = True
                    self.last_mouse_pos = event.pos
                elif event.button == 4:  # Wheel up: zoom in
                    self.zoom = min(2.2, self.zoom + 0.08)
                elif event.button == 5:  # Wheel down: zoom out
                    self.zoom = max(0.4, self.zoom - 0.08)
                elif event.button == 3:  # Right click: reset camera
                    self.pitch_offset = 0.0
                    self.yaw_offset = 0.0
                    self.zoom = 1.0

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.is_dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if self.is_dragging:
                    dx = event.pos[0] - self.last_mouse_pos[0]
                    dy = event.pos[1] - self.last_mouse_pos[1]
                    self.yaw_offset += dx * 0.008
                    self.pitch_offset += dy * 0.008
                    # Clamp pitch to avoid full flip
                    self.pitch_offset = max(-1.2, min(1.2, self.pitch_offset))
                    self.last_mouse_pos = event.pos

        return True

    def update(self, dt):
        """Updates animation timelines, palette morphing, and camera physics."""
        if not self.is_paused:
            self.time += dt
            self.spin_angle += dt * 0.45 * self.spin_speed
            self.current_hue_offset = (self.current_hue_offset + dt * self.hue_shift_speed) % 1.0

        # Palette Cross-Fade Interpolation
        if self.palette_transition_t < 1.0:
            self.palette_transition_t = min(1.0, self.palette_transition_t + dt * 1.2)
            self.current_palette = Palette.lerp(self.current_palette, self.target_palette, self.palette_transition_t)
        else:
            self.current_palette = self.target_palette

        # Auto-Morphing schedule
        if self.auto_morph and (time.time() - self.last_morph_time > self.morph_interval):
            self.next_palette()
            self.last_morph_time = time.time()

        # Smooth return to center when not dragging
        if not self.is_dragging:
            self.pitch_offset *= 0.985
            self.yaw_offset *= 0.985

    def draw_hud(self, active_palette):
        """Renders an aesthetic minimal HUD with FPS, active theme, and controls."""
        fps_text = f"{self.fps:.1f} FPS"
        theme_text = f"Theme: {active_palette.name}" + (" [Auto-Morph: ON]" if self.auto_morph else "")
        speed_text = f"Speed: {self.spin_speed:.1f}x"
        zoom_text = f"Zoom: {int(self.zoom * 100)}%"

        # Subtle dark glassmorphism card in top-left
        card_w, card_h = 370, 115
        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((10, 8, 22, 195))
        pygame.draw.rect(card_surf, (80, 70, 130, 140), (0, 0, card_w, card_h), 1, border_radius=10)

        # Title
        t_surf = self.title_font.render("L I L I U M  ·  C O S M I C A", True, (220, 240, 255))
        card_surf.blit(t_surf, (16, 12))

        # Stats
        s1 = self.font.render(f"{fps_text}  ·  {speed_text}  ·  {zoom_text}", True, (0, 240, 210))
        card_surf.blit(s1, (16, 44))

        s2 = self.font.render(theme_text, True, (255, 145, 225))
        card_surf.blit(s2, (16, 72))

        self.screen.blit(card_surf, (20, 20))

        # Bottom hint bar with translucent capsule
        hint_str = "[SPACE] Pause  ·  [C] Theme  ·  [M] Auto-Morph  ·  [F11] Fullscreen  ·  [H] Toggle HUD  ·  [ESC] Exit"
        h_surf = self.font.render(hint_str, True, (200, 190, 225))
        pad_x, pad_y = 18, 6
        capsule_w = h_surf.get_width() + pad_x * 2
        capsule_h = h_surf.get_height() + pad_y * 2
        hx = (self.width - capsule_w) // 2
        hy = self.height - 38

        cap_surf = pygame.Surface((capsule_w, capsule_h), pygame.SRCALPHA)
        cap_surf.fill((8, 6, 18, 180))
        pygame.draw.rect(cap_surf, (60, 50, 95, 120), (0, 0, capsule_w, capsule_h), 1, border_radius=14)
        cap_surf.blit(h_surf, (pad_x, pad_y))
        self.screen.blit(cap_surf, (hx, hy))

    def render(self):
        """Renders one complete frame: background, blooms, 3D sorted flower, particles, and HUD."""
        cx, cy = self.width // 2, self.height // 2 + 10
        t = self.time

        # Active palette shifted smoothly by current hue flow
        active_palette = self.current_palette.shifted(self.current_hue_offset)

        # 1. Dark cosmic radial vignette
        render_background(self.screen, self.width, self.height, t)

        # 2. Additive Background Aura Bloom discs
        aura_r_far = int(450 * self.zoom)
        bg_aura_far = self.glow_engine.get_glow_disc(aura_r_far, active_palette.mid, max_alpha=28)
        self.screen.blit(bg_aura_far, (cx - aura_r_far, cy - aura_r_far), special_flags=pygame.BLEND_ADD)

        aura_r_mid = int(270 * self.zoom)
        bg_aura_mid = self.glow_engine.get_glow_disc(aura_r_mid, active_palette.throat, max_alpha=50)
        self.screen.blit(bg_aura_mid, (cx - aura_r_mid, cy - aura_r_mid), special_flags=pygame.BLEND_ADD)

        # 3. Generate 3D geometry and elements
        triangles, outlines, R = self.flower.generate_mesh(
            t, self.spin_angle, self.pitch_offset, self.yaw_offset, self.spin_speed
        )
        center_elems = self.flower.generate_center_elements(t, R)
        part_elems = self.particles.get_particles(t, R, active_palette)

        # Combine into unified list for Painter's depth sorting
        all_renderables = []
        for tri in triangles:
            all_renderables.append({"depth": tri["depth"], "type": "tri", "data": tri})
        for elem in center_elems:
            all_renderables.append({"depth": elem["depth"], "type": elem["type"], "data": elem})
        for outl in outlines:
            all_renderables.append({"depth": outl["depth"], "type": "outline", "data": outl})
        for p in part_elems:
            all_renderables.append({"depth": p["depth"], "type": "particle", "data": p})

        # Sort descending by depth: farthest drawn first (+Z), closest drawn last (-Z)
        all_renderables.sort(key=lambda item: item["depth"], reverse=True)

        # 4. Draw all elements back-to-front
        for item in all_renderables:
            itype = item["type"]
            data = item["data"]

            if itype == "tri":
                pts3d = data["pts"]
                poly2d = [self.flower.project_point(p, cx, cy, self.zoom) for p in pts3d]
                col = self.flower.shade_quad(data["u"], data["v"], data["normal"], data["tier"], active_palette)
                pygame.draw.polygon(self.screen, col, poly2d)

            elif itype == "outline":
                pts3d = data["pts"]
                poly2d = [self.flower.project_point(p, cx, cy, self.zoom) for p in pts3d]
                pygame.draw.lines(self.screen, active_palette.rim, False, poly2d, 1)

            elif itype == "receptacle_tri":
                pts3d = data["pts"]
                poly2d = [self.flower.project_point(p, cx, cy, self.zoom) for p in pts3d]
                pygame.draw.polygon(self.screen, active_palette.throat, poly2d)

            elif itype == "stamen_seg":
                p1_2d = self.flower.project_point(data["p1"], cx, cy, self.zoom)
                p2_2d = self.flower.project_point(data["p2"], cx, cy, self.zoom)
                # Filament: glowing aqua / electric mint
                pygame.draw.line(self.screen, (30, 210, 180), p1_2d, p2_2d, 3)
                pygame.draw.line(self.screen, (210, 255, 240), p1_2d, p2_2d, 1)

            elif itype == "anther":
                p1_2d = self.flower.project_point(data["p1"], cx, cy, self.zoom)
                p2_2d = self.flower.project_point(data["p2"], cx, cy, self.zoom)
                stamen_col = active_palette.stamen
                # Anther pill glow layers
                pygame.draw.line(self.screen, (clamp(stamen_col[0] * 0.8), clamp(stamen_col[1] * 0.5), 20), p1_2d, p2_2d, 11)
                pygame.draw.line(self.screen, stamen_col, p1_2d, p2_2d, 7)
                pygame.draw.line(self.screen, (255, 255, 210), p1_2d, p2_2d, 3)
                pygame.draw.circle(self.screen, (255, 255, 220), p1_2d, 5)
                pygame.draw.circle(self.screen, (255, 255, 220), p2_2d, 5)

            elif itype == "pistil_seg":
                p1_2d = self.flower.project_point(data["p1"], cx, cy, self.zoom)
                p2_2d = self.flower.project_point(data["p2"], cx, cy, self.zoom)
                pygame.draw.line(self.screen, (30, 190, 140), p1_2d, p2_2d, 4)
                pygame.draw.line(self.screen, (190, 255, 220), p1_2d, p2_2d, 2)

            elif itype == "stigma":
                tip_2d = self.flower.project_point(data["pt"], cx, cy, self.zoom)
                pygame.draw.circle(self.screen, (70, 240, 190), tip_2d, 9)
                pygame.draw.circle(self.screen, (245, 255, 250), tip_2d, 5)

            elif itype == "particle":
                pt_2d = self.flower.project_point(data["pt"], cx, cy, self.zoom)
                sz = int(max(1, data["size"] * self.zoom))
                col = data["color"]
                pygame.draw.circle(self.screen, col, pt_2d, sz)
                if sz > 2 and data["twinkle"] > 0.6:
                    glow_col = (col[0] // 2, col[1] // 2, col[2] // 2)
                    pygame.draw.circle(self.screen, glow_col, pt_2d, sz + 3, 1)

        # 5. Central Core Radiant Bloom Emission
        core_r1 = int(105 * self.zoom)
        core_bloom1 = self.glow_engine.get_glow_disc(core_r1, active_palette.throat, max_alpha=85)
        self.screen.blit(core_bloom1, (cx - core_r1, cy - core_r1), special_flags=pygame.BLEND_ADD)

        core_r2 = int(45 * self.zoom)
        core_bloom2 = self.glow_engine.get_glow_disc(core_r2, (255, 255, 255), max_alpha=75)
        self.screen.blit(core_bloom2, (cx - core_r2, cy - core_r2), special_flags=pygame.BLEND_ADD)

        # 6. Render HUD Overlay if enabled
        if self.show_hud:
            self.draw_hud(active_palette)

        # Flip screen buffer
        pygame.display.flip()

    def run(self):
        """Main real-time animation execution loop."""
        running = True
        last_time = time.perf_counter()

        while running:
            # Calculate delta time for rock-solid frame pacing
            current_time = time.perf_counter()
            dt = current_time - last_time
            last_time = current_time
            # Cap dt to avoid huge leaps on window drag or pause
            dt = min(0.1, dt)

            running = self.handle_events()
            self.update(dt)
            self.render()

            # Target 60 FPS
            self.clock.tick(60)
            self.fps = self.clock.get_fps()

        pygame.quit()
        sys.exit(0)

# -----------------------------------------------------------------------------
# 7. SCRIPT ENTRY POINT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    app = SpinningLiliesApp()
    app.run()
