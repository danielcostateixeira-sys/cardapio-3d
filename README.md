# Cardápio 3D

Página de cardápio para restaurantes em que cada prato aparece em 3D no telemóvel e pode ser pousado na mesa em tamanho real, sem instalar nenhuma app. Abre a partir de um link ou de um QR code.

Não há servidor nem base de dados. São três ficheiros estáticos e uma pasta de modelos. Serve em qualquer alojamento gratuito (Vercel, Netlify, GitHub Pages, Cloudflare Pages).

## Ficheiros

- `index.html` — a lista de pratos (o cardápio).
- `prato.html?id=…` — o prato em 3D com o botão «Ver na mesa».
- `dados.js` — o nome do restaurante e a lista de pratos. É o único ficheiro que se edita para mudar a carta.
- `modelos/` — os ficheiros 3D. `.glb` para Android e computador, `.usdz` para iPhone.
- `fotos/` — fotografias dos pratos para a lista (opcional).

## Ver localmente

```bash
python -m http.server 3200
```

Depois abrir http://127.0.0.1:3200. O 3D no ecrã funciona localmente. O botão «Ver na mesa» **só funciona num telemóvel e com a página publicada em HTTPS**, porque a câmara e a realidade aumentada exigem-no.

## Modelos de amostra incluídos

- `modelos/panquecas.usdz` — panquecas reais digitalizadas por fotografia (amostra pública da Apple). Só iPhone.
- `modelos/avocado.glb` — abacate à escala real (amostra pública do Khronos Group). Android e computador.

São para testar. Um prato do restaurante substitui-os.

## Como digitalizar um prato

1. Instalar no telemóvel a **RealityScan** (Epic, grátis) ou a **Polycam** (tem versão grátis).
2. Pôr o prato numa mesa com boa luz, sem sol direto, num sítio onde se consiga dar a volta toda.
3. Tirar 50 a 80 fotografias à volta do prato, em dois ou três níveis de altura: à altura da mesa, a 45 graus e quase de cima. Sobrepor cada foto com a anterior. Não mexer no prato.
4. Deixar a app processar e exportar em **GLB** (para Android) e **USDZ** (para iPhone). A Polycam exporta os dois; a RealityScan exporta GLB e converte-se depois.
5. Confirmar a escala: as apps de fotogrametria com LiDAR já dão a escala certa. Sem LiDAR, medir o prato (diâmetro) e comparar com o que a app diz; corrigir se for preciso.
6. Copiar os ficheiros para `modelos/` e acrescentar o prato em `dados.js`.

Cuidado com comida brilhante, transparente ou com molho líquido: a fotogrametria lida mal com isso. Sopas e bebidas não se digitalizam bem; pratos sólidos, sobremesas e sandes ficam ótimos.

## Tamanho dos ficheiros

Um modelo de telemóvel deve ficar abaixo de 10 MB para carregar depressa na mesa do restaurante, com rede fraca. Se ficar maior, reduzir as texturas para 2048 px na exportação.
