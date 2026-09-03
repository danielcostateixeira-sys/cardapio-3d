// Cardápio de demonstração. Para acrescentar um prato, copia um bloco e muda os campos.
// glb  = modelo 3D para Android e computador (obrigatório para ver em 3D no ecrã)
// usdz = modelo 3D para iPhone/iPad (obrigatório para «ver na mesa» em iPhone)
// Se um prato só tiver usdz, no iPhone abre direto na mesa; noutros aparelhos mostra só a foto.
window.RESTAURANTE = {
  nome: "Tasca do Zé (demonstração)",
  morada: "Rua do Exemplo 123, Porto",
  telefone: "999 999 999",
  nota: "Aponte o telemóvel para a mesa e veja o prato em tamanho real.",
};

window.PRATOS = [
  {
    id: "bolo",
    nome: "Bolo de chocolate com morangos",
    descricao: "Bolo de chocolate de três camadas, com morangos frescos e ganache.",
    preco: "4,50 €",
    categoria: "Sobremesas",
    foto: "",
    glb: "modelos/bolo.glb",
    usdz: "",
    nota: "Modelo de amostra à escala real (Poly Haven, livre de direitos).",
  },
  {
    id: "panquecas",
    nome: "Panquecas com mirtilos e nozes",
    descricao: "Três panquecas, mirtilos frescos, nozes caramelizadas e xarope de ácer.",
    preco: "7,50 €",
    categoria: "Pequeno-almoço",
    foto: "",
    glb: "modelos/panquecas.glb",
    usdz: "modelos/panquecas.usdz",
    nota: "Modelo real, digitalizado por fotografia (amostra pública da Apple).",
  },
  {
    id: "folha-a4",
    nome: "Folha A4 (régua de teste)",
    descricao: "Uma folha A4 deitada na mesa, 21 por 29,7 cm. Serve para confirmar que o telemóvel está a pousar os objectos no tamanho certo.",
    preco: "—",
    categoria: "Teste de escala",
    foto: "",
    glb: "modelos/folha-a4.glb",
    usdz: "",
    nota: "Ponha uma folha A4 verdadeira ao lado. Se as duas tiverem o mesmo tamanho, a escala está certa.",
  },
  {
    id: "abacate",
    nome: "Abacate (demonstração)",
    descricao: "Modelo de amostra à escala real, para testar em Android e no computador.",
    preco: "2,00 €",
    categoria: "Demonstração",
    foto: "",
    glb: "modelos/avocado.glb",
    usdz: "",
    nota: "Amostra técnica. Substituir por um prato do restaurante.",
  },
];
