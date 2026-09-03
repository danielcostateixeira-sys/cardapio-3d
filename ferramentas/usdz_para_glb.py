"""Converte um USDZ (iPhone) num GLB (Android e computador).

Uso:  python ferramentas/usdz_para_glb.py modelos/panquecas.usdz modelos/panquecas.glb

Lê as malhas, as coordenadas de textura e a textura de cor base de cada material.
Escreve um GLB à escala real em metros, com cor, rugosidade e mapa de normais,
texturas reduzidas a 2048 px em JPEG para ficar leve no telemóvel.

Depende de: usd-core, pygltflib, numpy, pillow  (pip install usd-core pygltflib numpy pillow)
"""
import io
import sys
import zipfile

import numpy as np
from PIL import Image
from pxr import Gf, Usd, UsdGeom, UsdShade
import pygltflib as g

# O Scene Viewer da Google falha a carregar em telemóveis médios quando a memória de
# textura passa de umas dezenas de MB. Estes valores mantêm-se muito abaixo disso.
TAMANHO_TEXTURA = 1024   # cor base
TAMANHO_NORMAIS = 1024   # relevo
TAMANHO_RUGOSIDADE = 512  # brilho
QUALIDADE_JPEG = 88


def textura_base(material):
    """Devolve (caminho_cor, cor_constante, metalico, caminho_rugosidade, caminho_normais)."""
    caminho = None
    rug = None
    nrm = None
    cor = None
    metalico = 0.0
    for sh in material.GetPrim().GetChildren():
        shader = UsdShade.Shader(sh)
        ident = shader.GetIdAttr().Get() or ""
        if ident == "UsdUVTexture":
            f = shader.GetInput("file").Get()
            espaco = shader.GetInput("sourceColorSpace").Get()
            if not f:
                continue
            if espaco == "sRGB":
                caminho = f.path
            elif f.path.endswith("_n.png"):
                nrm = f.path
            elif f.path.endswith("_r.png"):
                rug = f.path
        if "UsdPreviewSurface" in ident:
            d = shader.GetInput("diffuseColor")
            if d and d.Get() is not None:
                cor = tuple(d.Get())
            m = shader.GetInput("metallic")
            if m and m.Get() is not None:
                metalico = float(m.Get())
    return caminho, cor, metalico, rug, nrm


def carregar_textura(zipf, caminho, modo="cor", tamanho=TAMANHO_TEXTURA):
    """modo: 'cor' | 'rugosidade' (empacota no canal verde, como o glTF exige) | 'normais'."""
    for nome in zipf.namelist():
        if nome.endswith(caminho.lstrip("./")):
            img = Image.open(io.BytesIO(zipf.read(nome)))
            if modo == "rugosidade":
                r = img.convert("L")
                zero = Image.new("L", r.size, 0)
                img = Image.merge("RGB", (Image.new("L", r.size, 255), r, zero))
            else:
                img = img.convert("RGB")
            if max(img.size) > tamanho:
                img.thumbnail((tamanho, tamanho), Image.LANCZOS)
            saida = io.BytesIO()
            img.save(saida, "JPEG", quality=QUALIDADE_JPEG if modo == "cor" else 80)
            return saida.getvalue()
    raise FileNotFoundError(caminho)


def malha_para_arrays(mesh, escala):
    """Triangula e desdobra a malha em arrays por vértice-de-face."""
    xf = UsdGeom.Xformable(mesh.GetPrim()).ComputeLocalToWorldTransform(Usd.TimeCode.Default())
    pontos = np.array(mesh.GetPointsAttr().Get(), dtype=np.float64)
    pontos = np.array([xf.Transform(Gf.Vec3d(*p)) for p in pontos], dtype=np.float64) * escala
    contagens = np.array(mesh.GetFaceVertexCountsAttr().Get())
    indices = np.array(mesh.GetFaceVertexIndicesAttr().Get())

    pv = UsdGeom.PrimvarsAPI(mesh.GetPrim()).GetPrimvar("st")
    st = np.array(pv.Get(), dtype=np.float64)
    interp = pv.GetInterpolation()
    st_idx = pv.GetIndices()
    if st_idx:
        st = st[np.array(st_idx)]

    nrm_usd = mesh.GetNormalsAttr().Get()
    nrm_interp = mesh.GetNormalsInterpolation()
    if nrm_usd is not None:
        # rodar as normais com a parte de rotação da matriz (sem translação)
        rot = xf.ExtractRotationMatrix()
        nrm_usd = np.array([rot * Gf.Vec3d(*v) for v in nrm_usd], dtype=np.float64)

    pos, uv, nrm = [], [], []
    k = 0  # posição no array de índices (= índice de face-vertex)
    for n in contagens:
        fv = indices[k:k + n]
        for i in range(1, n - 1):
            for j in (0, i, i + 1):
                v = fv[j]
                pos.append(pontos[v])
                uv.append(st[k + j] if interp == "faceVarying" else st[v])
                if nrm_usd is not None:
                    nrm.append(nrm_usd[k + j] if nrm_interp == "faceVarying" else nrm_usd[v])
        k += n
    pos = np.array(pos, dtype=np.float32)
    uv = np.array(uv, dtype=np.float32)
    uv[:, 1] = 1.0 - uv[:, 1]  # USD tem origem em baixo, glTF em cima

    if nrm:
        normais = np.array(nrm, dtype=np.float32)
    else:  # sem normais no ficheiro: planas por triângulo
        a, b, c = pos[0::3], pos[1::3], pos[2::3]
        n = np.cross(b - a, c - a)
        normais = np.repeat(n, 3, axis=0).astype(np.float32)
    normais /= np.maximum(np.linalg.norm(normais, axis=1, keepdims=True), 1e-9)
    return pos, normais, uv


def converter(entrada, saida):
    stage = Usd.Stage.Open(entrada)
    escala = UsdGeom.GetStageMetersPerUnit(stage) or 1.0
    zipf = zipfile.ZipFile(entrada)

    gltf = g.GLTF2()
    gltf.scene = 0
    gltf.scenes = [g.Scene(nodes=[])]
    blob = bytearray()
    materiais = {}

    def acrescentar_buffer(dados, alvo=None):
        while len(blob) % 4:
            blob.append(0)
        off = len(blob)
        blob.extend(dados)
        gltf.bufferViews.append(g.BufferView(buffer=0, byteOffset=off, byteLength=len(dados), target=alvo))
        return len(gltf.bufferViews) - 1

    def material_para(mat):
        chave = str(mat.GetPath())
        if chave in materiais:
            return materiais[chave]
        caminho, cor, metalico, rug, nrm = textura_base(mat)
        pbr = g.PbrMetallicRoughness(metallicFactor=metalico, roughnessFactor=0.75 if metalico < 0.5 else 0.35)

        def textura(cam, modo, tamanho=TAMANHO_TEXTURA):
            bv = acrescentar_buffer(carregar_textura(zipf, cam, modo, tamanho))
            gltf.images.append(g.Image(bufferView=bv, mimeType="image/jpeg"))
            gltf.textures.append(g.Texture(source=len(gltf.images) - 1, sampler=0))
            return len(gltf.textures) - 1

        if caminho:
            pbr.baseColorTexture = g.TextureInfo(index=textura(caminho, "cor"))
        elif cor:
            pbr.baseColorFactor = [cor[0], cor[1], cor[2], 1.0]
        material = g.Material(name=mat.GetPrim().GetName(), pbrMetallicRoughness=pbr, doubleSided=True)
        if rug:
            pbr.roughnessFactor = 1.0
            pbr.metallicRoughnessTexture = g.TextureInfo(index=textura(rug, "rugosidade", TAMANHO_RUGOSIDADE))
        if nrm:
            material.normalTexture = g.NormalMaterialTexture(index=textura(nrm, "normais", TAMANHO_NORMAIS))
        gltf.materials.append(material)
        materiais[chave] = len(gltf.materials) - 1
        return materiais[chave]

    gltf.samplers = [g.Sampler(magFilter=g.LINEAR, minFilter=g.LINEAR_MIPMAP_LINEAR, wrapS=g.REPEAT, wrapT=g.REPEAT)]

    for prim in stage.Traverse():
        if prim.GetTypeName() != "Mesh":
            continue
        mesh = UsdGeom.Mesh(prim)
        pos, nrm, uv = malha_para_arrays(mesh, escala)
        # juntar vértices iguais (posição + normal + coordenada de textura)
        junto = np.concatenate([pos, nrm, uv], axis=1)
        _, primeiros, indices_tri = np.unique(junto, axis=0, return_index=True, return_inverse=True)
        ordem = np.argsort(primeiros)          # manter a ordem original, mais amiga da cache
        novo_lugar = np.empty_like(ordem)
        novo_lugar[ordem] = np.arange(len(ordem))
        indices_tri = novo_lugar[indices_tri.ravel()].astype(np.uint32)
        pos, nrm, uv = pos[primeiros[ordem]], nrm[primeiros[ordem]], uv[primeiros[ordem]]
        mat = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()[0]
        idx_mat = material_para(mat) if mat else None

        def acessor(arr, tipo, alvo=g.ARRAY_BUFFER, minmax=False):
            bv = acrescentar_buffer(arr.tobytes(), alvo)
            acc = g.Accessor(bufferView=bv, componentType=g.FLOAT, count=len(arr), type=tipo)
            if minmax:
                acc.min = arr.min(axis=0).tolist()
                acc.max = arr.max(axis=0).tolist()
            gltf.accessors.append(acc)
            return len(gltf.accessors) - 1

        a_pos = acessor(pos, g.VEC3, minmax=True)
        a_nrm = acessor(nrm, g.VEC3)
        a_uv = acessor(uv, g.VEC2)

        curto = len(pos) <= 65535
        indices_tri = indices_tri.astype(np.uint16 if curto else np.uint32)
        bv_i = acrescentar_buffer(indices_tri.tobytes(), g.ELEMENT_ARRAY_BUFFER)
        gltf.accessors.append(g.Accessor(
            bufferView=bv_i,
            componentType=g.UNSIGNED_SHORT if curto else g.UNSIGNED_INT,
            count=len(indices_tri), type=g.SCALAR))
        a_idx = len(gltf.accessors) - 1

        prim_gl = g.Primitive(attributes=g.Attributes(POSITION=a_pos, NORMAL=a_nrm, TEXCOORD_0=a_uv),
                              indices=a_idx, material=idx_mat)
        gltf.meshes.append(g.Mesh(name=prim.GetName(), primitives=[prim_gl]))
        gltf.nodes.append(g.Node(name=prim.GetName(), mesh=len(gltf.meshes) - 1))
        gltf.scenes[0].nodes.append(len(gltf.nodes) - 1)

    gltf.buffers = [g.Buffer(byteLength=len(blob))]
    gltf.set_binary_blob(bytes(blob))
    gltf.save_binary(saida)
    print(f"{saida}: {len(gltf.meshes)} malhas, {len(gltf.materials)} materiais, {len(blob)/1e6:.1f} MB")


if __name__ == "__main__":
    converter(sys.argv[1], sys.argv[2])
