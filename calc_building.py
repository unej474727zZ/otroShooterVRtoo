import json, numpy as np

with open('d:/otroShooter/app/src/main/assets/low-poly_industrial_building.glb', 'rb') as f:
    data = f.read()

chunk0_len = int.from_bytes(data[12:16], 'little')
gltf = json.loads(data[20:20+chunk0_len].decode('utf-8'))
bin_data = data[20 + chunk0_len + 8:]

def get_buffer(acc_idx):
    acc = gltf['accessors'][acc_idx]
    bv = gltf['bufferViews'][acc['bufferView']]
    offset = bv.get('byteOffset', 0) + acc.get('byteOffset', 0)
    count = acc['count']
    return np.frombuffer(bin_data[offset:offset+count*12], dtype=np.float32).reshape(count, 3)

nodes = gltf['nodes']
def get_matrix(n):
    if 'matrix' in n:
        return np.array(n['matrix'], dtype=np.float32).reshape((4, 4), order='F')
    return np.eye(4, dtype=np.float32)

m0 = get_matrix(nodes[0])
m1 = get_matrix(nodes[1])
m2 = get_matrix(nodes[2])
m3 = get_matrix(nodes[3])
m6 = get_matrix(nodes[6])

M_bld1 = m0 @ m1 @ m2 @ m3
M_bld2 = m0 @ m1 @ m2 @ m6

pts1 = np.vstack([get_buffer(gltf['meshes'][0]['primitives'][0]['attributes']['POSITION']),
                  get_buffer(gltf['meshes'][1]['primitives'][0]['attributes']['POSITION'])])
pts1_h = np.hstack([pts1, np.ones((len(pts1), 1))])
w1 = (M_bld1 @ pts1_h.T).T[:, :3]

pts2 = np.vstack([get_buffer(gltf['meshes'][2]['primitives'][0]['attributes']['POSITION']),
                  get_buffer(gltf['meshes'][3]['primitives'][0]['attributes']['POSITION']),
                  get_buffer(gltf['meshes'][4]['primitives'][0]['attributes']['POSITION'])])
pts2_h = np.hstack([pts2, np.ones((len(pts2), 1))])
w2 = (M_bld2 @ pts2_h.T).T[:, :3]

w_all = np.vstack([w1, w2])
w_all[:, 0] -= 50
w_all[:, 2] += 8

print("World Building Bounds:")
print(f"X: [{w_all[:,0].min():.1f}, {w_all[:,0].max():.1f}]")
print(f"Y: [{w_all[:,1].min():.1f}, {w_all[:,1].max():.1f}]")
print(f"Z: [{w_all[:,2].min():.1f}, {w_all[:,2].max():.1f}]")

# Let's see ground points where Y is between -3.5 and -2.5
ground = w_all[(w_all[:, 1] >= -3.5) & (w_all[:, 1] <= -2.5)]
print(f"Ground count: {len(ground)}")
print(f"Ground X: [{ground[:,0].min():.1f}, {ground[:,0].max():.1f}]")
print(f"Ground Z: [{ground[:,2].min():.1f}, {ground[:,2].max():.1f}]")
