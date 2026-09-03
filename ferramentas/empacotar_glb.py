"""Junta um .gltf com ficheiros soltos (.bin e texturas) num único .glb.

Uso:  python ferramentas/empacotar_glb.py entrada.gltf saida.glb [largura_maxima_da_textura]

Serve para modelos descarregados de bibliotecas livres, que vêm em pasta com o
modelo e as imagens à parte. O cardápio precisa de um ficheiro só, porque cada
pedido extra é mais um segundo de espera na mesa do restaurante.

Depende de: pygltflib, pillow  (pip install pygltflib pillow)
"""
import io
import os
import sys

from PIL import Image
import pygltflib as g

QUALIDADE_JPEG = 88


def empacotar(entrada, saida, largura_maxima=1024):
    base = os.path.dirname(os.path.abspath(entrada))
    gltf = g.GLTF2().load(entrada)

    # o buffer de geometria vem de um .bin ao lado
    blob = bytearray(gltf.binary_blob() or b"")
    if not blob and gltf.buffers and gltf.buffers[0].uri:
        with open(os.path.join(base, gltf.buffers[0].uri), "rb") as f:
            blob = bytearray(f.read())

    def acrescentar(dados):
        while len(blob) % 4:
            blob.append(0)
        gltf.bufferViews.append(g.BufferView(buffer=0, byteOffset=len(blob), byteLength=len(dados)))
        blob.extend(dados)
        return len(gltf.bufferViews) - 1

    for imagem in gltf.images:
        if not imagem.uri:
            continue  # já está dentro do ficheiro
        caminho = os.path.join(base, imagem.uri.replace("/", os.sep))
        img = Image.open(caminho).convert("RGB")
        if max(img.size) > largura_maxima:
            img.thumbnail((largura_maxima, largura_maxima), Image.LANCZOS)
        saida_img = io.BytesIO()
        img.save(saida_img, "JPEG", quality=QUALIDADE_JPEG)
        imagem.bufferView = acrescentar(saida_img.getvalue())
        imagem.mimeType = "image/jpeg"
        imagem.uri = None

    gltf.buffers = [g.Buffer(byteLength=len(blob))]
    gltf.set_binary_blob(bytes(blob))
    gltf.save_binary(saida)
    print(f"{saida}: {len(blob)/1e6:.1f} MB, {len(gltf.images)} imagens embutidas")


if __name__ == "__main__":
    largura = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
    empacotar(sys.argv[1], sys.argv[2], largura)
