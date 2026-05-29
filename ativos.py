from database import conectar_banco
from constantes import CATEGORIAS_ATIVO, STATUS_VULN
import vulnerabilidades

def mostrar_indice():
    conn, cursor = conectar_banco()
    cursor.execute("SELECT id, nome FROM ativos ORDER BY id;")
    ativos = cursor.fetchall()
    conn.close()
    if not ativos:
        print("\n[!] Nenhum ativo cadastrado.")
        return False
    print("\n--- LISTA DE ATIVOS ---")
    for ativo in ativos:
        print(f"{ativo['id']:<6} | {ativo['nome']:<20}")
    return True

def cadastrar_ativo():
    print("\n--- NOVO CADASTRO ---")
    nome = input("Nome/Hostname do Ativo: ").strip()
    if nome.lower() == "v": return
    responsavel = input("Responsável: ").strip()
    local = input("Setor/Localização: ").strip()

    while True:
        for c, n in CATEGORIAS_ATIVO.items(): print(f"{c} - {n}")
        t_input = input("Código da categoria: ").strip()
        if t_input.isdigit() and int(t_input) in CATEGORIAS_ATIVO:
            tipo_nome = CATEGORIAS_ATIVO[int(t_input)]
            break
        print("[!] Inválido.")

    conn, cursor = conectar_banco()
    cursor.execute("INSERT INTO ativos (nome, tipo, localizacao, responsavel) VALUES (?, ?, ?, ?)", (nome, tipo_nome, local, responsavel))
    ativo_id = cursor.lastrowid

    if input("Adicionar vulnerabilidade inicial? (S/N): ").lower() == "s":
        v = vulnerabilidades.coletar_dados_vulnerabilidade()
        if v:
            cursor.execute("""
                INSERT INTO vulnerabilidades (descricao, severidade, status, responsavel_correcao, ativo_id)
                VALUES (?, ?, ?, ?, ?)""", (v['descricao'], v['severidade'], v['status'], v['responsavel_correcao'], ativo_id))
    
    conn.commit()
    conn.close()
    print(f"[+] Ativo {ativo_id} cadastrado.")

def consultar_ativo():
    termo = input("\nNome para busca: ").strip()
    conn, cursor = conectar_banco()
    cursor.execute("SELECT * FROM ativos WHERE nome LIKE ?", (f"%{termo}%",))
    encontrados = cursor.fetchall()
    for a in encontrados:
        print(f"\nID: {a['id']} | {a['nome']} ({a['tipo']})")
        cursor.execute("SELECT * FROM vulnerabilidades WHERE ativo_id = ?", (a['id'],))
        for v in cursor.fetchall():
            print(f"  -> [{v['severidade']}] {v['descricao']} - {v['status']}")
    conn.close()

def gerenciar_ativo():
    if not mostrar_indice(): return
    id_at = input("\nID do ativo: ").strip()
    conn, cursor = conectar_banco()
    cursor.execute("SELECT * FROM ativos WHERE id = ?", (id_at,))
    if not cursor.fetchone(): 
        conn.close(); return
    
    print("1. Nova Vuln | 2. Mudar Status | 3. Editar Dados")
    op = input("Opção: ")
    if op == "1":
        v = vulnerabilidades.coletar_dados_vulnerabilidade()
        if v:
            cursor.execute("INSERT INTO vulnerabilidades (descricao, severidade, status, responsavel_correcao, ativo_id) VALUES (?,?,?,?,?)",
                           (v['descricao'], v['severidade'], v['status'], v['responsavel_correcao'], id_at))
    elif op == "2":
        cursor.execute("SELECT * FROM vulnerabilidades WHERE ativo_id = ?", (id_at,))
        vs = cursor.fetchall()
        for i, v in enumerate(vs): print(f"{i} - {v['descricao']}")
        idx = int(input("Item: "))
        st = int(input("Novo Status (1-4): "))
        cursor.execute("UPDATE vulnerabilidades SET status = ? WHERE id = ?", (STATUS_VULN[st], vs[idx]['id']))
    
    conn.commit()
    conn.close()

def remover_ativo():
    if not mostrar_indice(): return
    id_at = input("\nID para remover: ").strip()
    conn, cursor = conectar_banco()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("DELETE FROM ativos WHERE id = ?", (id_at,))
    conn.commit()
    conn.close()