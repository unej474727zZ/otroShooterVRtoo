import cv2, numpy as np, os, math

print("Generating Professional High-Fidelity Futuristic Soldier Skin...")

W, H = 720, 720
skin = np.zeros((H, W, 3), dtype=np.uint8)

# 1. Base Colors (BGR)
C_VOID = (0, 0, 0)
C_UNDERSUIT = (18, 20, 24)       # Deep matte nano-weave black
C_CARBON_PLATE = (30, 34, 40)    # Dark composite ballistic armor plate
C_TITANIUM = (55, 62, 72)        # Titanium joint/frame
C_HAZARD_YELLOW = (0, 200, 255)  # Electric Hazard Yellow / Amber (BGR)
C_YELLOW_GLOW = (80, 235, 255)   # Visor & energy core glow
C_CYAN_CORE = (255, 230, 0)      # High-tech cyan accent (BGR)
C_SEAM = (10, 11, 13)            # Panel gap seam

# Load normal map to extract authentic anatomical/plate curvature
norm_map = cv2.imread('d:/otroShooter/scratch_tex/tex_1.webp')
if norm_map is not None:
    nx = (norm_map[:, :, 2].astype(float) - 128.0) / 128.0
    ny = (norm_map[:, :, 1].astype(float) - 128.0) / 128.0
    nz = (norm_map[:, :, 0].astype(float) - 128.0) / 128.0
    length = np.sqrt(nx**2 + ny**2 + nz**2)
    length[length == 0] = 1.0
    nx /= length; ny /= length; nz /= length
    
    # Key light + ambient
    light_dir = np.array([0.35, 0.45, 0.82])
    light_dir /= np.linalg.norm(light_dir)
    shading = np.clip(nx * light_dir[0] + ny * light_dir[1] + nz * light_dir[2], 0.0, 1.0)
    shading = 0.5 + 0.5 * shading # Normalize to 0.5 - 1.0 range
else:
    shading = np.ones((H, W), dtype=float)

# Load UV island mask
uv_map = cv2.imread('d:/otroShooter/scratch_tex/uv_map_colored.png')
gray_uv = cv2.cvtColor(uv_map, cv2.COLOR_BGR2GRAY)
_, uv_mask = cv2.threshold(gray_uv, 1, 255, cv2.THRESH_BINARY)
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(uv_mask)

# Fill base undersuit inside all UV islands
for i in range(1, num_labels):
    skin[labels == i] = C_UNDERSUIT

# High-resolution decal & armor layer
armor_layer = skin.copy()
yellow_layer = np.zeros((H, W, 3), dtype=np.uint8)
panel_seams = np.zeros((H, W), dtype=np.uint8)

# Helper: Draw smooth anti-aliased polygon
def draw_poly(img, pts, color):
    cv2.fillPoly(img, [np.array(pts, np.int32)], color, lineType=cv2.LINE_AA)

def draw_line(img, p1, p2, color, thickness=2):
    cv2.line(img, p1, p2, color, thickness, lineType=cv2.LINE_AA)

# =========================================================================
# 1. FRONT TORSO (Island 10: x=[203, 432], y=[453, 719], center ~ 318, 587)
# =========================================================================
mask_front = (labels == 10)
cx_f = 318

# A. Large Ballistic Chest Plates (Pectorals)
# Left Pec plate
draw_poly(armor_layer, [(cx_f - 10, 485), (cx_f - 95, 480), (cx_f - 105, 550), (cx_f - 10, 560)], C_CARBON_PLATE)
# Right Pec plate
draw_poly(armor_layer, [(cx_f + 10, 485), (cx_f + 95, 480), (cx_f + 105, 550), (cx_f + 10, 560)], C_CARBON_PLATE)

# B. Dynamic Hazard Yellow Chevrons on Chest
# Upper Chevron wing left & right
draw_poly(yellow_layer, [
    (cx_f - 15, 510), (cx_f - 85, 495), (cx_f - 85, 508), (cx_f - 15, 523)
], C_HAZARD_YELLOW)
draw_poly(yellow_layer, [
    (cx_f + 15, 510), (cx_f + 85, 495), (cx_f + 85, 508), (cx_f + 15, 523)
], C_HAZARD_YELLOW)

# Lower Chevron wing left & right
draw_poly(yellow_layer, [
    (cx_f - 18, 532), (cx_f - 75, 520), (cx_f - 75, 530), (cx_f - 18, 542)
], C_HAZARD_YELLOW)
draw_poly(yellow_layer, [
    (cx_f + 18, 532), (cx_f + 75, 520), (cx_f + 75, 530), (cx_f + 18, 542)
], C_HAZARD_YELLOW)

# C. Central Cybernetic Arc Reactor / Tech Hub at sternum
cv2.circle(armor_layer, (cx_f, 526), 18, C_TITANIUM, -1, lineType=cv2.LINE_AA)
cv2.circle(yellow_layer, (cx_f, 526), 13, C_HAZARD_YELLOW, -1, lineType=cv2.LINE_AA)
cv2.circle(yellow_layer, (cx_f, 526), 7, C_YELLOW_GLOW, -1, lineType=cv2.LINE_AA)
cv2.circle(yellow_layer, (cx_f, 526), 3, C_CYAN_CORE, -1, lineType=cv2.LINE_AA)

# D. Segmented Abdominal Armor Plates (Y: 570 - 665)
for y_ab in range(575, 650, 22):
    # Left ab plate
    draw_poly(armor_layer, [(cx_f - 65, y_ab), (cx_f - 8, y_ab + 2), (cx_f - 8, y_ab + 16), (cx_f - 65, y_ab + 14)], C_CARBON_PLATE)
    # Right ab plate
    draw_poly(armor_layer, [(cx_f + 65, y_ab), (cx_f + 8, y_ab + 2), (cx_f + 8, y_ab + 16), (cx_f + 65, y_ab + 14)], C_CARBON_PLATE)
    draw_line(panel_seams, (cx_f - 65, y_ab), (cx_f + 65, y_ab), 255, 2)

# E. Heavy Tactical Belt & Buckle (Y: 675 - 710)
draw_poly(armor_layer, [(cx_f - 100, 680), (cx_f + 100, 680), (cx_f + 100, 715), (cx_f - 100, 715)], C_TITANIUM)
# Buckle
draw_poly(yellow_layer, [(cx_f - 16, 686), (cx_f + 16, 686), (cx_f + 16, 708), (cx_f - 16, 708)], C_HAZARD_YELLOW)
cv2.circle(yellow_layer, (cx_f, 697), 4, C_CYAN_CORE, -1, lineType=cv2.LINE_AA)

# =========================================================================
# 2. BACK TORSO (Island 9: x=[0, 204], y=[428, 719], center ~ 100, 577)
# =========================================================================
mask_back = (labels == 9)
cx_b = 100

# A. Back Shoulder Armor Plates
draw_poly(armor_layer, [(cx_b - 80, 470), (cx_b - 12, 470), (cx_b - 15, 550), (cx_b - 85, 545)], C_CARBON_PLATE)
draw_poly(armor_layer, [(cx_b + 80, 470), (cx_b + 12, 470), (cx_b + 15, 550), (cx_b + 85, 545)], C_CARBON_PLATE)

# B. Tactical Hazard Warning Stripes on Shoulder Blades (// //)
for off_y in [490, 508, 526]:
    # Left shoulder stripes
    draw_poly(yellow_layer, [
        (cx_b - 75, off_y), (cx_b - 35, off_y - 12), (cx_b - 35, off_y - 4), (cx_b - 75, off_y + 8)
    ], C_HAZARD_YELLOW)
    # Right shoulder stripes
    draw_poly(yellow_layer, [
        (cx_b + 75, off_y), (cx_b + 35, off_y - 12), (cx_b + 35, off_y - 4), (cx_b + 75, off_y + 8)
    ], C_HAZARD_YELLOW)

# C. Cybernetic Spinal Exoskeleton Column (Center Spine)
# Vertical titanium housing
cv2.rectangle(armor_layer, (cx_b - 14, 460), (cx_b + 14, 690), C_TITANIUM, -1)
# Segmented glowing yellow vertebrae power cells
for y_sp in range(470, 680, 18):
    # Hexagonal / trapezoid vertebrae node
    draw_poly(yellow_layer, [
        (cx_b - 9, y_sp), (cx_b + 9, y_sp), (cx_b + 11, y_sp + 10), (cx_b - 11, y_sp + 10)
    ], C_HAZARD_YELLOW)
    cv2.circle(yellow_layer, (cx_b, y_sp + 5), 2, C_YELLOW_GLOW, -1, lineType=cv2.LINE_AA)

# =========================================================================
# 3. COMBAT HELMET / HEAD (Island 7: x=[342, 611], y=[250, 534], center ~ 481, 378)
# =========================================================================
cx_h = 481
cy_h = 378

# Entire helmet base is ballistic black composite
draw_poly(armor_layer, [(cx_h - 110, 260), (cx_h + 110, 260), (cx_h + 120, 520), (cx_h - 120, 520)], C_CARBON_PLATE)

# A. Glowing Tactical HUD Visor (horizontal panoramic band)
# Curved aerodynamic visor shape
visor_pts = [
    (cx_h - 75, 345), (cx_h - 40, 340), (cx_h, 338), (cx_h + 40, 340), (cx_h + 75, 345),
    (cx_h + 70, 375), (cx_h + 35, 370), (cx_h, 368), (cx_h - 35, 370), (cx_h - 70, 375)
]
draw_poly(armor_layer, visor_pts, C_SEAM)
# Inside Visor Glow
visor_inner = [
    (cx_h - 65, 350), (cx_h, 344), (cx_h + 65, 350),
    (cx_h + 60, 368), (cx_h, 362), (cx_h - 60, 368)
]
draw_poly(yellow_layer, visor_inner, C_HAZARD_YELLOW)
# Center laser HUD line
draw_line(yellow_layer, (cx_h - 55, 357), (cx_h + 55, 357), C_YELLOW_GLOW, 2)
# Cyan HUD sensor dots on visor edges
cv2.circle(yellow_layer, (cx_h - 45, 357), 3, C_CYAN_CORE, -1, lineType=cv2.LINE_AA)
cv2.circle(yellow_layer, (cx_h + 45, 357), 3, C_CYAN_CORE, -1, lineType=cv2.LINE_AA)

# B. Dorsal Racing / Tactical Stripe on Helmet Top
draw_poly(yellow_layer, [
    (cx_h - 10, 255), (cx_h + 10, 255), (cx_h + 12, 332), (cx_h - 12, 332)
], C_HAZARD_YELLOW)

# C. Temple Ear Audio / Tactical Comms Ports
cv2.circle(armor_layer, (cx_h - 95, 365), 14, C_TITANIUM, -1, lineType=cv2.LINE_AA)
cv2.circle(yellow_layer, (cx_h - 95, 365), 7, C_HAZARD_YELLOW, -1, lineType=cv2.LINE_AA)
cv2.circle(armor_layer, (cx_h + 95, 365), 14, C_TITANIUM, -1, lineType=cv2.LINE_AA)
cv2.circle(yellow_layer, (cx_h + 95, 365), 7, C_HAZARD_YELLOW, -1, lineType=cv2.LINE_AA)

# D. Chin Rebreather / Filtration Intake (Y: 410 - 450)
draw_poly(armor_layer, [(cx_h - 35, 415), (cx_h + 35, 415), (cx_h + 25, 450), (cx_h - 25, 450)], C_TITANIUM)
for y_v in [422, 432, 442]:
    draw_line(panel_seams, (cx_h - 20, y_v), (cx_h + 20, y_v), 255, 2)

# =========================================================================
# 4. ARMS & SHOULDERS (Island 11: x=[423, 665], y=[552, 719]; Island 8: x=[619, 719])
# =========================================================================
# Pauldron dual yellow hazard stripes
for y_s in [570, 595]:
    draw_poly(yellow_layer, [(440, y_s), (640, y_s), (640, y_s + 12), (440, y_s + 12)], C_HAZARD_YELLOW)

# Cybernetic HUD Wrist Display on Left Arm
draw_poly(armor_layer, [(500, 640), (580, 640), (580, 690), (500, 690)], C_TITANIUM)
draw_poly(yellow_layer, [(510, 648), (570, 648), (570, 682), (510, 682)], C_CYAN_CORE)
draw_line(yellow_layer, (515, 665), (565, 665), C_HAZARD_YELLOW, 2)

# =========================================================================
# 5. LEGS & GREAVES (Islands 1 & 2: x=[0, 373], y=[1, 434])
# =========================================================================
# Outer Thigh Diagonal Hazard Stripes
for off in [80, 115, 150]:
    # Left Thigh
    draw_poly(yellow_layer, [(15, off), (85, off - 25), (85, off - 15), (15, off + 10)], C_HAZARD_YELLOW)
    # Right Thigh
    draw_poly(yellow_layer, [(165, off), (235, off - 25), (235, off - 15), (165, off + 10)], C_HAZARD_YELLOW)

# Reinforced Heavy Knee Guards with Inverted Chevron ("V")
for k_cx in [65, 250]:
    # Knee plate
    draw_poly(armor_layer, [
        (k_cx - 30, 215), (k_cx + 30, 215), (k_cx + 35, 275), (k_cx, 290), (k_cx - 35, 275)
    ], C_CARBON_PLATE)
    # Yellow Chevron V
    draw_poly(yellow_layer, [
        (k_cx - 24, 230), (k_cx, 265), (k_cx + 24, 230),
        (k_cx + 24, 242), (k_cx, 277), (k_cx - 24, 242)
    ], C_HAZARD_YELLOW)

# Shin Greave Lateral Kinetic Struts
for s_cx in [55, 240]:
    draw_poly(yellow_layer, [(s_cx - 25, 320), (s_cx - 15, 320), (s_cx - 15, 410), (s_cx - 25, 410)], C_HAZARD_YELLOW)
    draw_poly(yellow_layer, [(s_cx + 15, 320), (s_cx + 25, 320), (s_cx + 25, 410), (s_cx + 15, 410)], C_HAZARD_YELLOW)

# =========================================================================
# 6. COMBAT BOOTS (Islands 4 & 5: x=[498, 711], y=[5, 299])
# =========================================================================
for b_cx in [560, 645]:
    # Heavy boot armor
    draw_poly(armor_layer, [(b_cx - 45, 20), (b_cx + 45, 20), (b_cx + 50, 140), (b_cx - 50, 140)], C_CARBON_PLATE)
    # High-traction yellow sole rim & heel dampener
    draw_poly(yellow_layer, [(b_cx - 40, 120), (b_cx + 40, 120), (b_cx + 40, 138), (b_cx - 40, 138)], C_HAZARD_YELLOW)
    # Toe cap titanium
    cv2.circle(armor_layer, (b_cx, 60), 20, C_TITANIUM, -1, lineType=cv2.LINE_AA)

# =========================================================================
# 7. COMBAT GLOVES / GAUNTLETS (Islands 3 & 6: x=[352, 533], y=[2, 253])
# =========================================================================
for g_cx in [440, 435]:
    g_y = 50 if g_cx == 440 else 195
    # Knuckle guard plate
    draw_poly(armor_layer, [(g_cx - 40, g_y), (g_cx + 40, g_y), (g_cx + 35, g_y + 35), (g_cx - 35, g_y + 35)], C_TITANIUM)
    # Yellow Knuckle Pads
    for kx in [-25, -8, 8, 25]:
        cv2.circle(yellow_layer, (g_cx + kx, g_y + 15), 5, C_HAZARD_YELLOW, -1, lineType=cv2.LINE_AA)

# =========================================================================
# 8. COMPOSITING, NORMAL MAP SHADING, CARBON TWILL, AND DILATION
# =========================================================================
print("Compositing layers and applying baked normal map shading...")

# Combine armor base
final = armor_layer.copy()

# Add carbon fiber weave texture to dark areas
y_idx, x_idx = np.indices((H, W))
twill = (((x_idx // 2) + (y_idx // 2)) % 2) * 6 - 3
twill = np.repeat(twill[:, :, np.newaxis], 3, axis=2).astype(np.int16)

# Apply baked normal map shading
final_float = final.astype(float)
shading_3ch = np.repeat(shading[:, :, np.newaxis], 3, axis=2)
final_shaded = np.clip(final_float * shading_3ch, 0, 255).astype(np.int16)

# Add twill noise
dark_mask = (final_shaded[:, :, 0] < 80) & (final_shaded[:, :, 1] < 80) & (final_shaded[:, :, 2] < 80) & (uv_mask > 0)
final_shaded[dark_mask] = np.clip(final_shaded[dark_mask] + twill[dark_mask], 10, 255)
final = final_shaded.astype(np.uint8)

# Subtle panel seams
seams_mask = (panel_seams > 0) & (uv_mask > 0)
final[seams_mask] = C_SEAM

# Add vibrant yellow accents with bloom / soft glow
yellow_mask = (yellow_layer.sum(axis=2) > 0) & (uv_mask > 0)
# Create bloom for yellow elements
yellow_blur = cv2.GaussianBlur(yellow_layer, (7, 7), 2.0)
final = np.where(yellow_blur > 30, np.clip(final.astype(int) + (yellow_blur.astype(int) // 3), 0, 255).astype(np.uint8), final)
final[yellow_mask] = yellow_layer[yellow_mask]

# Dilation to eliminate UV seams completely
print("Eliminating UV seams with edge dilation...")
empty_mask = (uv_mask == 0)
dilated = cv2.dilate(final, np.ones((7, 7), np.uint8))
final[empty_mask] = dilated[empty_mask]

# Save WebP and PNG
out_webp = 'd:/otroShooter/app/src/main/assets/futuristic_armor_skin.webp'
out_png = 'd:/otroShooter/scratch_tex/pro_futuristic_skin.png'
cv2.imwrite(out_png, final)
cv2.imwrite(out_webp, final, [cv2.IMWRITE_WEBP_QUALITY, 92])

print(f"Success! Saved {out_webp} ({os.path.getsize(out_webp) / 1024:.1f} KB)")
