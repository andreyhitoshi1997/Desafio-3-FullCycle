CATEGORIAS_VALIDAS = [
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
]

NOME_MIN_LENGTH = 2
NOME_MAX_LENGTH = 200

DESCONTO_FAIXAS = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]

STATUSES_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]

PAGINACAO_DEFAULT_PAGE = 1
PAGINACAO_DEFAULT_PER_PAGE = 20
PAGINACAO_MAX_PER_PAGE = 100
