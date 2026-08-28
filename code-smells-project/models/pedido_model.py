from config.constants import DESCONTO_FAIXAS


def calcular_desconto(faturamento):
    for limite, taxa in DESCONTO_FAIXAS:
        if faturamento > limite:
            return round(faturamento * taxa, 2)
    return 0


def _build_pedidos_com_itens(db, pedido_rows):
    if not pedido_rows:
        return []

    pedido_ids = [row["id"] for row in pedido_rows]
    placeholders = ",".join("?" for _ in pedido_ids)

    cursor = db.cursor()
    cursor.execute(
        "SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, "
        "p.nome as produto_nome "
        "FROM itens_pedido ip "
        "LEFT JOIN produtos p ON p.id = ip.produto_id "
        f"WHERE ip.pedido_id IN ({placeholders})",
        pedido_ids,
    )
    itens_rows = cursor.fetchall()

    itens_por_pedido = {}
    for item in itens_rows:
        pid = item["pedido_id"]
        if pid not in itens_por_pedido:
            itens_por_pedido[pid] = []
        itens_por_pedido[pid].append(
            {
                "produto_id": item["produto_id"],
                "produto_nome": item["produto_nome"]
                if item["produto_nome"]
                else "Desconhecido",
                "quantidade": item["quantidade"],
                "preco_unitario": item["preco_unitario"],
            }
        )

    result = []
    for row in pedido_rows:
        result.append(
            {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": itens_por_pedido.get(row["id"], []),
            }
        )
    return result


def criar(db, usuario_id, itens):
    cursor = db.cursor()

    produto_ids = [item["produto_id"] for item in itens]
    placeholders = ",".join("?" for _ in produto_ids)
    cursor.execute(
        f"SELECT * FROM produtos WHERE id IN ({placeholders})",
        produto_ids,
    )
    produtos_by_id = {row["id"]: row for row in cursor.fetchall()}

    total = 0
    for item in itens:
        produto = produtos_by_id.get(item["produto_id"])
        if produto is None:
            return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": "Estoque insuficiente para " + produto["nome"]}
        total += produto["preco"] * item["quantidade"]

    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
        (usuario_id, "pendente", total),
    )
    pedido_id = cursor.lastrowid

    for item in itens:
        produto = produtos_by_id[item["produto_id"]]
        cursor.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
        )
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (item["quantidade"], item["produto_id"]),
        )

    db.commit()
    return {"pedido_id": pedido_id, "total": total}


def get_por_usuario(db, usuario_id, limit=20, offset=0):
    cursor = db.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM pedidos WHERE usuario_id = ?", (usuario_id,)
    )
    total = cursor.fetchone()[0]
    cursor.execute(
        "SELECT * FROM pedidos WHERE usuario_id = ? LIMIT ? OFFSET ?",
        (usuario_id, limit, offset),
    )
    rows = cursor.fetchall()
    return _build_pedidos_com_itens(db, rows), total


def get_todos(db, limit=20, offset=0):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT * FROM pedidos LIMIT ? OFFSET ?", (limit, offset))
    rows = cursor.fetchall()
    return _build_pedidos_com_itens(db, rows), total


def atualizar_status(db, pedido_id, novo_status):
    cursor = db.cursor()
    cursor.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id),
    )
    db.commit()


def relatorio_vendas(db):
    cursor = db.cursor()
    cursor.execute(
        """
        SELECT
            COUNT(*) as total_pedidos,
            COALESCE(SUM(total), 0) as faturamento,
            SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END) as pendentes,
            SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END) as aprovados,
            SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END) as cancelados
        FROM pedidos
        """
    )
    row = cursor.fetchone()

    total_pedidos = row["total_pedidos"]
    faturamento = row["faturamento"]
    desconto = calcular_desconto(faturamento)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": desconto,
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": row["pendentes"],
        "pedidos_aprovados": row["aprovados"],
        "pedidos_cancelados": row["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2)
        if total_pedidos > 0
        else 0,
    }
