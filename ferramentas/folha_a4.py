"""Gera modelos/folha-a4.glb: uma folha A4 (21 x 29,7 cm) deitada, com as medidas escritas.

Serve de régua na realidade aumentada. Se na mesa a folha não tiver o tamanho de uma
folha real, o telemóvel está a medir mal a mesa; se tiver, os pratos também estão certos.

Uso:  python ferramentas/folha_a4.py
"""
import io

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pygltflib as g

L, C = 0.210, 0.297  # metros

# textura
W, H = 1024, 1448
img = Image.new("RGB", (W, H), (250, 250, 247))
d = ImageDraw.Draw(img)
d.rectangle([8, 8, W - 9, H - 9], outline=(60, 60, 60), width=6)
try:
    f1 = ImageFont.truetype("arialbd.ttf", 150)
    f2 = ImageFont.truetype("arial.ttf", 64)
except OSError:
    f1 = f2 = ImageFont.load_default()
d.text((W / 2, H * 0.36), "A4", font=f1, fill=(40, 40, 40), anchor="mm")
d.text((W / 2, H * 0.52), "21 × 29,7 cm", font=f2, fill=(40, 40, 40), anchor="mm")
d.text((W / 2, H * 0.62), "Folha de referência", font=f2, fill=(120, 120, 120), anchor="mm")
# marcas de 1 cm nas bordas
for i in range(0, 22):
    x = int(i / 21 * (W - 18)) + 9
    d.line([x, 9, x, 9 + (40 if i % 5 == 0 else 20)], fill=(60, 60, 60), width=4)
for i in range(0, 30):
    y = int(i / 29.7 * (H - 18)) + 9
    d.line([9, y, 9 + (40 if i % 5 == 0 else 20), y], fill=(60, 60, 60), width=4)
tex = io.BytesIO()
img.save(tex, "JPEG", quality=88)
tex = tex.getvalue()

# geometria: quadrado no plano XZ, 1 mm acima do chão, normal para cima
pos = np.array([[-L / 2, 0.001, -C / 2], [L / 2, 0.001, -C / 2], [L / 2, 0.001, C / 2], [-L / 2, 0.001, C / 2]], dtype=np.float32)
nrm = np.array([[0, 1, 0]] * 4, dtype=np.float32)
uv = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float32)
idx = np.array([0, 2, 1, 0, 3, 2], dtype=np.uint16)

blob = bytearray()
views = []


def add(dados, alvo=None):
    while len(blob) % 4:
        blob.append(0)
    views.append(g.BufferView(buffer=0, byteOffset=len(blob), byteLength=len(dados), target=alvo))
    blob.extend(dados)
    return len(views) - 1


bv_pos = add(pos.tobytes(), g.ARRAY_BUFFER)
bv_nrm = add(nrm.tobytes(), g.ARRAY_BUFFER)
bv_uv = add(uv.tobytes(), g.ARRAY_BUFFER)
bv_idx = add(idx.tobytes(), g.ELEMENT_ARRAY_BUFFER)
bv_tex = add(tex)

gltf = g.GLTF2(
    scene=0,
    scenes=[g.Scene(nodes=[0])],
    nodes=[g.Node(mesh=0, name="FolhaA4")],
    meshes=[g.Mesh(primitives=[g.Primitive(attributes=g.Attributes(POSITION=0, NORMAL=1, TEXCOORD_0=2), indices=3, material=0)])],
    accessors=[
        g.Accessor(bufferView=bv_pos, componentType=g.FLOAT, count=4, type=g.VEC3, min=pos.min(0).tolist(), max=pos.max(0).tolist()),
        g.Accessor(bufferView=bv_nrm, componentType=g.FLOAT, count=4, type=g.VEC3),
        g.Accessor(bufferView=bv_uv, componentType=g.FLOAT, count=4, type=g.VEC2),
        g.Accessor(bufferView=bv_idx, componentType=g.UNSIGNED_SHORT, count=6, type=g.SCALAR),
    ],
    materials=[g.Material(pbrMetallicRoughness=g.PbrMetallicRoughness(baseColorTexture=g.TextureInfo(index=0), metallicFactor=0, roughnessFactor=0.9), doubleSided=True)],
    textures=[g.Texture(source=0)],
    images=[g.Image(bufferView=bv_tex, mimeType="image/jpeg")],
    bufferViews=views,
    buffers=[g.Buffer(byteLength=len(blob))],
)
gltf.set_binary_blob(bytes(blob))
gltf.save_binary("modelos/folha-a4.glb")
print("modelos/folha-a4.glb", len(blob) / 1e3, "kB")
