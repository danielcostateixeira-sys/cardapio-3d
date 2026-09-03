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
    id: "panquecas",
    nome: "Panquecas com mirtilos e nozes",
    descricao: "Três panquecas, mirtilos frescos, nozes caramelizadas e xarope de ácer.",
    preco: "7,50 €",
    categoria: "Pequeno-almoço",
    foto: "fotos/panquecas.jpg",
    glb: "",
    usdz: "modelos/panquecas.usdz",
    nota: "Modelo real, digitalizado por fotografia. Só abre em iPhone.",
  },
  {
    id: "abacate",
    nome: "Abacate (demonstração)",
    descricao: "Modelo de amostra à escala real, para testar em Android e no computador.",
    preco: "2,00 €",
    categoria: "Demonstração",
    foto: "fotos/abacate.jpg",
    glb: "modelos/avocado.glb",
    usdz: "",
    nota: "Amostra técnica. Substituir por um prato do restaurante.",
  },
];
