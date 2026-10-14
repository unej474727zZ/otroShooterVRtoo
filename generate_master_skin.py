import cv2, numpy as np, json, math, os

print("Generating Master-Quality Futuristic Soldier Armor Skin...")

# 1. Load GLB geometry
with open('d:/otroShooter/app/src/main/assets/Rifleidle-webp.glb', 'rb') as f:
    data = f.read()

chunk0_len = int.from_bytes(data[12:16], 'little')
gltf = json.loads(data[20:20+chunk0_len].decode('utf-8'))
bin_data = data[20 + chunk0_len + 8:]

def get_buffer(acc_idx):
    acc = gltf['accessors'][acc_idx]
    bv = gltf['bufferViews'][acc['bufferView']]
    offset = bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
    stride = bv.get('byteStride', 0)
    count = acc['count']
    ctype = acc['componentType']
    atype = acc['type']
    types_map = {5126: np.float32, 5123: np.uint16, 5121: np.uint8, 5125: np.uint32}
    counts_map = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}
    dtype = types_map[ctype]
    num = counts_map[atype]
    if stride == 0 or stride == num * np.dtype(dtype).itemsize:
        return np.frombuffer(bin_data[offset:offset+count*num*np.dtype(dtype).itemsize], dtype=dtype).reshape(count, num)
    else:
        res = [np.frombuffer(bin_data[offset+i*stride:offset+i*stride+num*np.dtype(dtype).itemsize], dtype=dtype) for i in range(count)]
        return np.array(res)

prim = gltf['meshes'][0]['primitives'][0]
pos = get_buffer(prim['attributes']['POSITION'])
norm = get_buffer(prim['attributes']['NORMAL'])
uvs = get_buffer(prim['attributes']['TEXCOORD_0'])
joints = get_buffer(prim['attributes']['JOINTS_0'])
weights = get_buffer(prim['attributes']['WEIGHTS_0'])

skin_joint_names = [gltf['nodes'][j]['name'] for j in gltf['skins'][0]['joints']]
primary_joint = joints[np.arange(len(joints)), np.argmax(weights, axis=1)]

indices_acc = gltf['accessors'][prim['indices']]
indices_bv = gltf['bufferViews'][indices_acc['bufferView']]
ind_offset = indices_bv.get('byteOffset', 0) + indices_acc.get('byteOffset', 0)
ind_count = indices_acc['count']
ind_type = np.uint16 if indices_acc['componentType'] == 5123 else np.uint32
indices = np.frombuffer(bin_data[ind_offset:ind_offset+ind_count*np.dtype(ind_type).itemsize], dtype=ind_type)

W, H = 720, 720

# Colors (BGR)
C_VOID = (0, 0, 0)
C_MATTE_CARBON = (16, 18, 22)       # Ultra-deep ballistic nano-weave
C_ARMOR_PLATE = (32, 36, 44)        # Heavy composite plate
C_TITANIUM_FRAME = (60, 68, 78)     # Gunmetal/Titanium structural trim
C_HAZARD_YELLOW = (0, 205, 255)     # Vibrant electric hazard yellow/amber
C_YELLOW_GLOW = (90, 235, 255)      # Intense core glow
C_CYAN_TECH = (255, 230, 0)         # Cyan digital sensor/core
C_PANEL_SEAM = (8, 9, 11)           # Seam groove

base_canvas = np.zeros((H, W, 3), dtype=np.uint8)
yellow_canvas = np.zeros((H, W, 3), dtype=np.uint8)
seam_canvas = np.zeros((H, W), dtype=np.uint8)

def evaluate_3d_point(x, y, z, nx, ny, nz, joint_name):
    abs_x = abs(x)
    
    # 1. HEAD / COMBAT HELMET (y >= 1.54)
    if y >= 1.54:
        # Visor: Front of face (z > 0.04, y in [1.59, 1.66], abs_x < 0.075)
        if z > 0.04 and 1.59 <= y <= 1.66 and abs_x < 0.075:
            # Visor center slit
            if 1.61 <= y <= 1.645 and abs_x < 0.065:
                # Cyan core dots at edges
                if 0.045 <= abs_x <= 0.06:
                    return C_CYAN_TECH, True
                return C_YELLOW_GLOW, True
            return C_HAZARD_YELLOW, True
            
        # Helmet dorsal crest stripe (center top of head)
        if y > 1.66 and abs_x < 0.015:
            return C_HAZARD_YELLOW, True
            
        # Temple comms / ear intake
        if 1.58 <= y <= 1.64 and abs_x > 0.075 and abs(z) < 0.04:
            return C_HAZARD_YELLOW, True
            
        # Chin filtration vent
        if 1.54 <= y <= 1.58 and z > 0.05 and abs_x < 0.035:
            return C_TITANIUM_FRAME, False
            
        # Main helmet dome
        if y > 1.64:
            return C_MATTE_CARBON, False
        return C_ARMOR_PLATE, False

    # 2. NECK (1.47 <= y < 1.54)
    if 1.47 <= y < 1.54:
        if abs_x > 0.04:
            return C_TITANIUM_FRAME, False
        return C_MATTE_CARBON, False

    # 3. CHEST & BACK (1.18 <= y < 1.47)
    if 1.18 <= y < 1.47:
        # --- BACK VIEW (z < -0.01) ---
        if z < -0.01:
            # Cybernetic Spinal Exoskeleton (midline on back)
            if abs_x < 0.024:
                # Segmented vertebrae nodes
                segment = int((y - 1.18) * 38) % 2
                if segment == 0:
                    return C_HAZARD_YELLOW, True
                return C_TITANIUM_FRAME, False
                
            # Upper back angled hazard stripes on shoulder blades
            stripe_val = (y * 14.0 - abs_x * 8.0)
            if 1.30 <= y <= 1.43 and 0.05 <= abs_x <= 0.17 and (int(stripe_val) % 3 == 0):
                return C_HAZARD_YELLOW, True
                
            # Trapezius / Back armor plate
            if abs_x < 0.19:
                return C_ARMOR_PLATE, False
            return C_MATTE_CARBON, False

        # --- FRONT VIEW (z >= -0.01) ---
        else:
            # Central Arc Reactor / Energy Core at sternum
            dist_core = math.sqrt(x*x + (y - 1.33)**2)
            if dist_core < 0.038:
                if dist_core < 0.014:
                    return C_CYAN_TECH, True
                if dist_core < 0.026:
                    return C_YELLOW_GLOW, True
                return C_HAZARD_YELLOW, True
                
            # Chest Pectoral Chevron Wings
            # Angled chevron: (y - 1.30) - (abs_x * 0.45)
            chevron = (y - 1.29) - (abs_x * 0.45)
            if 1.27 <= y <= 1.42 and 0.03 <= abs_x <= 0.18:
                if 0.005 <= chevron <= 0.038:
                    return C_HAZARD_YELLOW, True
                if 0.055 <= chevron <= 0.082:
                    return C_HAZARD_YELLOW, True
                return C_ARMOR_PLATE, False
                
            # Abdominal Segmented Plates (1.18 to 1.27)
            if y < 1.27:
                if abs_x < 0.12:
                    ab_segment = int((y - 1.18) * 35) % 2
                    if ab_segment == 0:
                        return C_ARMOR_PLATE, False
                    return C_MATTE_CARBON, False
                return C_MATTE_CARBON, False
                
            return C_ARMOR_PLATE, False

    # 4. WAIST & HIPS (0.90 <= y < 1.18)
    if 0.90 <= y < 1.18:
        # Tactical Utility Belt (y in [0.94, 1.01])
        if 0.94 <= y <= 1.01:
            # Front belt buckle status LED
            if z > 0.05 and abs_x < 0.03:
                return C_CYAN_TECH, True
            if abs_x > 0.08:
                return C_TITANIUM_FRAME, False
            return C_MATTE_CARBON, False
            
        # Lower spine power conduit
        if z < -0.01 and abs_x < 0.024:
            return C_HAZARD_YELLOW, True
            
        # Hip composite armor plates
        if abs_x > 0.11:
            if 1.02 <= y <= 1.14 and abs_x > 0.14:
                return C_HAZARD_YELLOW, True
            return C_ARMOR_PLATE, False
            
        return C_MATTE_CARBON, False

    # 5. SHOULDERS & ARMS
    if abs_x > 0.18 and y > 1.20:
        # Pauldrons / Deltoids (abs_x in [0.22, 0.36])
        if 0.22 <= abs_x <= 0.36:
            # Dual hazard yellow stripes on shoulder outer cap
            stripe = int((abs_x - 0.22) * 30) % 2
            if stripe == 0 and y > 1.34:
                return C_HAZARD_YELLOW, True
            return C_ARMOR_PLATE, False
            
        # Biceps (abs_x in [0.36, 0.46])
        if 0.36 < abs_x <= 0.46:
            return C_MATTE_CARBON, False
            
        # Forearms & Bracers (abs_x in [0.46, 0.65])
        if 0.46 < abs_x <= 0.65:
            # Left Forearm: Cybernetic HUD display (x > 0.48, z > 0.0)
            if x > 0.48 and z > 0.01:
                if 0.52 <= x <= 0.60:
                    return C_CYAN_TECH, True
                return C_TITANIUM_FRAME, False
            # Tactical bracer band on right forearm
            if x < -0.48:
                if 0.53 <= abs_x <= 0.57:
                    return C_HAZARD_YELLOW, True
                return C_ARMOR_PLATE, False
            return C_ARMOR_PLATE, False
            
        # Hands & Gloves (abs_x > 0.65)
        if abs_x > 0.65:
            # Knuckle ballistic plate
            if abs(z) < 0.035:
                # Yellow knuckle dots
                if int(abs_x * 80) % 2 == 0:
                    return C_HAZARD_YELLOW, True
                return C_TITANIUM_FRAME, False
            return C_MATTE_CARBON, False

    # 6. LEGS & GREAVES (y < 0.90)
    # Thighs (0.54 <= y < 0.90)
    if 0.54 <= y < 0.90:
        # Outer Thigh Plates
        if abs_x > 0.09:
            # Diagonal tactical hazard stripe
            diag = (y * 11.0 - abs_x * 9.0)
            if 0.62 <= y <= 0.82 and (int(diag) % 3 == 0):
                return C_HAZARD_YELLOW, True
            if abs(z) < 0.08:
                return C_ARMOR_PLATE, False
        return C_MATTE_CARBON, False

    # Knees (0.43 <= y < 0.54)
    if 0.43 <= y < 0.54:
        # Front knee caps (z > 0.02)
        if z > 0.02 and abs_x > 0.05:
            # Downward yellow chevron ("V")
            chev_k = (y - 0.45) - (abs(abs_x - 0.10) * 0.8)
            if 0.01 <= chev_k <= 0.045:
                return C_HAZARD_YELLOW, True
            return C_ARMOR_PLATE, False
        return C_MATTE_CARBON, False

    # Shins & Calves (0.16 <= y < 0.43)
    if 0.16 <= y < 0.43:
        # Front shin plate
        if z > 0.01 and abs_x > 0.04:
            # Yellow lateral reinforcement strut
            if abs_x > 0.095:
                return C_HAZARD_YELLOW, True
            return C_ARMOR_PLATE, False
        # Back calf composite plate
        if z < -0.02 and abs_x > 0.04:
            return C_ARMOR_PLATE, False
        return C_MATTE_CARBON, False

    # Combat Boots (y < 0.16)
    if y < 0.16:
        # Sole / Shock absorber base
        if y < 0.03:
            return C_HAZARD_YELLOW, True
        # Toe cap titanium
        if z > 0.04:
            return C_TITANIUM_FRAME, False
        # Heel kinetic dampener
        if abs_x > 0.08:
            return C_HAZARD_YELLOW, True
        return C_ARMOR_PLATE, False

    return C_MATTE_CARBON, False

print("Rasterizing full 3D geometry onto UV canvas...")

for t in range(0, len(indices), 3):
    i0, i1, i2 = indices[t], indices[t+1], indices[t+2]
    
    u0, v0 = uvs[i0]; u1, v1 = uvs[i1]; u2, v2 = uvs[i2]
    if max(abs(u0-u1), abs(u1-u2), abs(u0-u2)) > 0.5: continue
    if max(abs(v0-v1), abs(v1-v2), abs(v0-v2)) > 0.5: continue
    
    p0 = (int(u0 * (W - 1)), int(v0 * (H - 1)))
    p1 = (int(u1 * (W - 1)), int(v1 * (H - 1)))
    p2 = (int(u2 * (W - 1)), int(v2 * (H - 1)))
    
    pos0, pos1, pos2 = pos[i0], pos[i1], pos[i2]
    xc = (pos0[0] + pos1[0] + pos2[0]) / 3.0
    yc = (pos0[1] + pos1[1] + pos2[1]) / 3.0
    zc = (pos0[2] + pos1[2] + pos2[2]) / 3.0
    
    n0, n1, n2 = norm[i0], norm[i1], norm[i2]
    nxc = (n0[0] + n1[0] + n2[0]) / 3.0
    nyc = (n0[1] + n1[1] + n2[1]) / 3.0
    nzc = (n0[2] + n1[2] + n2[2]) / 3.0
    
    j_idx = int(primary_joint[i0])
    j_name = skin_joint_names[j_idx].lower() if j_idx < len(skin_joint_names) else ''
    
    color, is_yellow = evaluate_3d_point(xc, yc, zc, nxc, nyc, nzc, j_name)
    
    pts = np.array([p0, p1, p2], np.int32)
    cv2.fillPoly(base_canvas, [pts], color)
    if is_yellow:
        cv2.fillPoly(yellow_canvas, [pts], color)

# Load normal map shading
print("Applying normal map anatomical cavity & lighting...")
norm_map = cv2.imread('d:/otroShooter/scratch_tex/tex_1.webp')
if norm_map is not None:
    nx = (norm_map[:, :, 2].astype(float) - 128.0) / 128.0
    ny = (norm_map[:, :, 1].astype(float) - 128.0) / 128.0
    nz = (norm_map[:, :, 0].astype(float) - 128.0) / 128.0
    length = np.sqrt(nx**2 + ny**2 + nz**2)
    length[length == 0] = 1.0
    nx /= length; ny /= length; nz /= length
    
    light_dir = np.array([0.3, 0.45, 0.84])
    light_dir /= np.linalg.norm(light_dir)
    shading = np.clip(nx * light_dir[0] + ny * light_dir[1] + nz * light_dir[2], 0.0, 1.0)
    shading = 0.55 + 0.45 * shading
else:
    shading = np.ones((H, W), dtype=float)

# Modulate base canvas with shading
shading_3ch = np.repeat(shading[:, :, np.newaxis], 3, axis=2)
shaded_base = np.clip(base_canvas.astype(float) * shading_3ch, 0, 255).astype(np.uint8)

# Add micro-twill carbon fiber weave
y_idx, x_idx = np.indices((H, W))
twill = (((x_idx // 2) + (y_idx // 2)) % 2) * 5 - 2
twill = np.repeat(twill[:, :, np.newaxis], 3, axis=2).astype(np.int16)

dark_mask = (shaded_base[:, :, 0] < 70) & (shaded_base[:, :, 1] < 70) & (shaded_base[:, :, 2] < 70) & (shaded_base.sum(axis=2) > 0)
shaded_base_int = shaded_base.astype(np.int16)
shaded_base_int[dark_mask] = np.clip(shaded_base_int[dark_mask] + twill[dark_mask], 10, 255)
shaded_base = shaded_base_int.astype(np.uint8)

# Yellow accents with soft electroluminescent glow
print("Generating cybernetic bloom and glow...")
is_yellow_mask = (yellow_canvas.sum(axis=2) > 0)
yellow_bloom = cv2.GaussianBlur(yellow_canvas, (9, 9), 2.5)

# Composite: base + bloom + sharp yellow
final = np.where(
    yellow_bloom > 20,
    np.clip(shaded_base.astype(int) + (yellow_bloom.astype(int) // 3), 0, 255).astype(np.uint8),
    shaded_base
)
final[is_yellow_mask] = yellow_canvas[is_yellow_mask]

# Eliminate all UV seam gaps with dilation
print("Dilating UV seams...")
empty_mask = (final.sum(axis=2) == 0)
dilated = cv2.dilate(final, np.ones((7, 7), np.uint8))
final[empty_mask] = dilated[empty_mask]

out_webp = 'd:/otroShooter/app/src/main/assets/futuristic_armor_skin.webp'
out_png = 'd:/otroShooter/scratch_tex/master_futuristic_skin.png'
cv2.imwrite(out_png, final)
cv2.imwrite(out_webp, final, [cv2.IMWRITE_WEBP_QUALITY, 92])

print(f"Master skin created! Saved {out_webp} ({os.path.getsize(out_webp) / 1024:.1f} KB)")
