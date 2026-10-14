import json, cv2, numpy as np, os, math

print("Loading GLB data...")
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

skin = gltf['skins'][0]
joint_names = [gltf['nodes'][j]['name'] for j in skin['joints']]
primary_joint = joints[np.arange(len(joints)), np.argmax(weights, axis=1)]

indices_acc = gltf['accessors'][prim['indices']]
indices_bv = gltf['bufferViews'][indices_acc['bufferView']]
ind_offset = indices_bv.get('byteOffset', 0) + indices_acc.get('byteOffset', 0)
ind_count = indices_acc['count']
ind_type = np.uint16 if indices_acc['componentType'] == 5123 else np.uint32
indices = np.frombuffer(bin_data[ind_offset:ind_offset+ind_count*np.dtype(ind_type).itemsize], dtype=ind_type)

W, H = 720, 720
texture = np.zeros((H, W, 3), dtype=np.uint8)

# Color Palette (BGR):
# Hazard Yellow vibrant
C_YELLOW = (0, 215, 255)       # Pure electric hazard yellow/amber
C_YELLOW_HOT = (30, 240, 255)   # Visor highlight
C_GOLD = (0, 165, 235)         # Warm gold accent
C_BLACK_CARBON = (16, 17, 19)  # Deep matte ballistic carbon
C_CHARCOAL = (32, 34, 38)      # Composite armor plate
C_TITANIUM = (55, 60, 68)      # Titanium alloy joint/frame
C_CYAN_TECH = (255, 220, 0)    # Cyan HUD element
C_SEAM = (8, 9, 10)            # Recessed panel gap

def classify_triangle(xc, yc, zc, nxc, nyc, nzc, body_part):
    # Returns (base_color, is_accent, seam_color)
    abs_x = abs(xc)
    dist_center = math.sqrt(xc*xc + zc*zc)
    
    # 1. HEAD / COMBAT HELMET (yc > 1.54)
    if yc > 1.54:
        # Visor: Front of face (zc > 0.04, yc in [1.59, 1.67], abs_x < 0.08)
        if zc > 0.04 and 1.59 <= yc <= 1.67 and abs_x < 0.08:
            # Visor center slit
            if 1.61 <= yc <= 1.65 and abs_x < 0.075:
                return C_YELLOW_HOT, True
            return C_YELLOW, True
        
        # Helmet center tactical stripe (forehead to crown)
        if yc > 1.66 and abs_x < 0.018:
            return C_YELLOW, True
            
        # Helmet temple/ear communications / vents
        if 1.58 <= yc <= 1.66 and abs_x > 0.075 and abs(zc) < 0.05:
            return C_GOLD, True
            
        # Mouth / Chin filtration vents
        if 1.54 <= yc <= 1.58 and zc > 0.05 and abs_x < 0.035:
            return C_TITANIUM, False
            
        # Helmet main dome plates
        if yc > 1.65:
            return C_BLACK_CARBON, False
        return C_CHARCOAL, False

    # 2. NECK (1.48 <= yc <= 1.54)
    if 1.48 <= yc <= 1.54:
        # Side conduits
        if abs_x > 0.04:
            return C_TITANIUM, False
        return C_BLACK_CARBON, False

    # 3. CHEST & BACK (1.20 <= yc < 1.48)
    if 1.20 <= yc < 1.48:
        # --- BACK VIEW (zc < -0.01) ---
        if zc < -0.01:
            # Cybernetic Spinal Exoskeleton (midline on back)
            if abs_x < 0.025:
                # Segmented vertebrae nodes
                segment = int((yc - 1.20) * 40) % 2
                if segment == 0:
                    return C_YELLOW, True
                return C_TITANIUM, False
                
            # Upper back angled shoulder-blade hazard stripes
            # Angled stripes on shoulder blades
            stripe_val = (yc * 15.0 - abs_x * 8.0)
            if 1.30 <= yc <= 1.44 and 0.05 <= abs_x <= 0.16 and (int(stripe_val) % 3 == 0):
                return C_YELLOW, True
                
            # Back heavy armor plate
            if abs_x < 0.18:
                return C_CHARCOAL, False
            return C_BLACK_CARBON, False

        # --- FRONT VIEW (zc >= -0.01) ---
        else:
            # Chest Chevron Hazard Stripes (on pectorals)
            # Chevron angle: yc + abs_x * 0.5
            chevron = (yc - 1.30) - (abs_x * 0.4)
            if 1.28 <= yc <= 1.42 and 0.03 <= abs_x <= 0.18:
                if 0.01 <= chevron <= 0.045:
                    return C_YELLOW, True
                if 0.06 <= chevron <= 0.085:
                    return C_YELLOW, True
                    
            # Central Core / Arc reactor mount at center sternum
            if 1.30 <= yc <= 1.37 and abs_x < 0.03:
                return C_YELLOW_HOT, True
                
            # Collarbone titanium frame
            if yc > 1.42 and abs_x < 0.14:
                return C_TITANIUM, False
                
            # Abdominal armor plates (1.20 to 1.28)
            if yc < 1.28:
                if abs_x < 0.12:
                    # Segmented abs
                    ab_tier = int((yc - 1.20) * 35) % 2
                    if ab_tier == 0:
                        return C_CHARCOAL, False
                    return C_BLACK_CARBON, False
                return C_BLACK_CARBON, False
                
            return C_CHARCOAL, False

    # 4. WAIST & HIPS (0.90 <= yc < 1.20)
    if 0.90 <= yc < 1.20:
        # Tactical utility belt (yc in [0.93, 1.01])
        if 0.94 <= yc <= 1.00:
            # Belt buckle status LED
            if zc > 0.05 and abs_x < 0.03:
                return C_YELLOW_HOT, True
            # Mag pouch fasteners / modules
            if abs_x > 0.08:
                return C_TITANIUM, False
            return C_BLACK_CARBON, False
            
        # Lower back spine continuation
        if zc < -0.01 and abs_x < 0.025:
            return C_YELLOW, True
            
        # Hip armor plates
        if abs_x > 0.12:
            if 1.02 <= yc <= 1.15 and abs(zc) < 0.08:
                # Yellow lateral hazard border on hip armor
                if abs_x > 0.15:
                    return C_YELLOW, True
                return C_CHARCOAL, False
        return C_BLACK_CARBON, False

    # 5. SHOULDERS & ARMS
    if 'arm' in body_part or 'shoulder' in body_part or 'hand' in body_part:
        # Pauldrons / Deltoids (abs_x > 0.20 and yc > 1.28)
        if yc > 1.28:
            # Pauldron cap
            if yc > 1.36 and abs_x > 0.22:
                # Dual hazard yellow stripes on shoulder outer cap
                stripe = int((abs_x - 0.22) * 25) % 2
                if stripe == 0 and abs_x < 0.32:
                    return C_YELLOW, True
                return C_CHARCOAL, False
            return C_BLACK_CARBON, False
            
        # Forearms / Bracers (0.75 <= yc <= 1.05 when arms relaxed, but let's check distance from body)
        if abs_x > 0.35:
            # Wrist cybernetic display (left wrist)
            if xc < -0.45 and abs(yc - 0.95) < 0.05 and zc > 0.0:
                return C_CYAN_TECH, True
            # Forearm outer armor plate
            if abs_x > 0.48:
                # Yellow racing stripe along bracer
                if 0.85 <= yc <= 1.10 and abs(zc) < 0.03:
                    return C_YELLOW, True
                return C_CHARCOAL, False
            # Hands / Gauntlets
            if abs_x > 0.65:
                # Knuckle armor
                if abs(zc) < 0.04:
                    return C_TITANIUM, False
                return C_BLACK_CARBON, False
            return C_BLACK_CARBON, False
        return C_BLACK_CARBON, False

    # 6. LEGS & FEET (yc < 0.90)
    # Thighs (0.55 <= yc < 0.90)
    if 0.55 <= yc < 0.90:
        # Outer thigh ballistic plates
        if abs_x > 0.10:
            # Diagonal tactical yellow stripe across thigh
            diag = (yc * 10.0 - abs_x * 8.0)
            if 0.60 <= yc <= 0.80 and (int(diag) % 4 == 0):
                return C_YELLOW, True
            if abs(zc) < 0.08:
                return C_CHARCOAL, False
        return C_BLACK_CARBON, False

    # Knees (0.43 <= yc < 0.55)
    if 0.43 <= yc < 0.55:
        # Front knee caps (zc > 0.02)
        if zc > 0.02 and abs_x > 0.05:
            # Bold yellow chevron down on knee cap
            if 0.46 <= yc <= 0.52:
                return C_YELLOW, True
            return C_CHARCOAL, False
        return C_BLACK_CARBON, False

    # Shins / Calves (0.16 <= yc < 0.43)
    if 0.16 <= yc < 0.43:
        # Shin guard plate (front)
        if zc > 0.01 and abs_x > 0.04:
            # Yellow lateral reinforcement strut
            if abs_x > 0.09:
                return C_YELLOW, True
            return C_CHARCOAL, False
        # Back calf composite plate
        if zc < -0.02 and abs_x > 0.04:
            return C_CHARCOAL, False
        return C_BLACK_CARBON, False

    # Combat Boots (yc < 0.16)
    if yc < 0.16:
        # Sole / Shock absorber base
        if yc < 0.03:
            return C_YELLOW, True
        # Toe cap
        if zc > 0.04:
            return C_TITANIUM, False
        # Heel / Ankle stabilizer
        if abs_x > 0.08:
            return C_GOLD, True
        return C_BLACK_CARBON, False

    return C_BLACK_CARBON, False

print("Rasterizing triangles into UV texture...")
seam_lines = []

for t in range(0, len(indices), 3):
    i0, i1, i2 = indices[t], indices[t+1], indices[t+2]
    
    # 2D UV Points
    u0, v0 = uvs[i0]
    u1, v1 = uvs[i1]
    u2, v2 = uvs[i2]
    
    # Check boundary wrap
    if max(abs(u0-u1), abs(u1-u2), abs(u0-u2)) > 0.5: continue
    if max(abs(v0-v1), abs(v1-v2), abs(v0-v2)) > 0.5: continue
    
    p0 = (int(u0 * (W - 1)), int(v0 * (H - 1)))
    p1 = (int(u1 * (W - 1)), int(v1 * (H - 1)))
    p2 = (int(u2 * (W - 1)), int(v2 * (H - 1)))
    
    # 3D Center & Normal
    pos0, pos1, pos2 = pos[i0], pos[i1], pos[i2]
    xc = (pos0[0] + pos1[0] + pos2[0]) / 3.0
    yc = (pos0[1] + pos1[1] + pos2[1]) / 3.0
    zc = (pos0[2] + pos1[2] + pos2[2]) / 3.0
    
    n0, n1, n2 = norm[i0], norm[i1], norm[i2]
    nxc = (n0[0] + n1[0] + n2[0]) / 3.0
    nyc = (n0[1] + n1[1] + n2[1]) / 3.0
    nzc = (n0[2] + n1[2] + n2[2]) / 3.0
    
    j_idx = int(primary_joint[i0])
    b_name = joint_names[j_idx].lower() if j_idx < len(joint_names) else ''
    
    col, is_accent = classify_triangle(xc, yc, zc, nxc, nyc, nzc, b_name)
    
    pts = np.array([p0, p1, p2], np.int32)
    cv2.fillPoly(texture, [pts], col)
    
    # Store seams for outer edges or accents
    if is_accent:
        seam_lines.append(pts)

# Subtle panel seams
for pts in seam_lines:
    cv2.polylines(texture, [pts], True, C_SEAM, 1)

# Apply subtle carbon fiber noise / micro-texture to matte areas
print("Adding carbon weave micro-texture...")
noise = np.random.randint(-4, 5, (H, W, 3), dtype=np.int16)
# Checkerboard carbon twill
y_coords, x_coords = np.indices((H, W))
twill = (((x_coords // 2) + (y_coords // 2)) % 2) * 5 - 2
twill = np.repeat(twill[:, :, np.newaxis], 3, axis=2).astype(np.int16)

# Apply only where texture is dark (armor / undersuit, not bright yellow)
dark_mask = (texture[:, :, 0] < 80) & (texture[:, :, 1] < 80) & (texture[:, :, 2] < 80) & (texture.sum(axis=2) > 0)
tex_int = texture.astype(np.int16)
tex_int[dark_mask] = np.clip(tex_int[dark_mask] + twill[dark_mask] + noise[dark_mask], 8, 255)
texture = tex_int.astype(np.uint8)

# UV Bleed / dilation to prevent seam filtering artifacts
print("Dilating texture to eliminate seams...")
empty_mask = (texture.sum(axis=2) == 0).astype(np.uint8)
dilated = cv2.dilate(texture, np.ones((5, 5), np.uint8))
texture[empty_mask == 1] = dilated[empty_mask == 1]

# Save output webp and png
out_webp = 'd:/otroShooter/app/src/main/assets/futuristic_armor_skin.webp'
out_png = 'd:/otroShooter/scratch_tex/futuristic_armor_skin.png'
cv2.imwrite(out_png, texture)
cv2.imwrite(out_webp, texture, [cv2.IMWRITE_WEBP_QUALITY, 90])

print(f"Saved {out_webp} ({os.path.getsize(out_webp) / 1024:.1f} KB)")
