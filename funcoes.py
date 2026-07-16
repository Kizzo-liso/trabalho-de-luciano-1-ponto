import json

import os
# Importa o módulo "os" (Operating System), que permite ao Python
# interagir com o sistema operacional.
# Neste projeto, ele é utilizado para verificar se os arquivos
# "oficinas.json" e "participantes.json" já existem antes de tentar
# abri-los. Isso evita erros caso seja a primeira execução do programa,
# permitindo que o sistema utilize os dados padrão quando os arquivos
# ainda não foram criados.

import tkinter as tk

ARQUIVO_OFICINAS = "oficinas.json"
ARQUIVO_PARTICIPANTES = "participantes.json"
# Constantes que armazenam o nome dos arquivos onde os dados do sistema
# serão salvos. Utilizar constantes evita repetir o nome dos arquivos em
# várias partes do código, tornando a manutenção mais simples. Caso seja
# necessário alterar o nome de um arquivo futuramente, basta modificar
# apenas esta constante.


# ====================================================
# MÓDULO: CARREGAMENTO E SALVAMENTO DE DADOS
# Funções:
#   - carregar_dados()
#   - salvar_oficinas_no_arquivo()
#   - salvar_participantes_no_arquivo()
# Objetivo:
#   Manter a persistência das informações do sistema.
# ====================================================
def carregar_dados(caminho, padrao):
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return padrao


def salvar_oficinas_no_arquivo():
    dados = dict(oficinas)
    dados["validate"] = "true"
    with open(ARQUIVO_OFICINAS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def salvar_participantes_no_arquivo():
    dados = dict(participantes)
    dados["validate"] = "true"
    with open(ARQUIVO_PARTICIPANTES, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


oficinas = carregar_dados(ARQUIVO_OFICINAS, {
    "oficinas": [
        {"id": 1, "nome": "Oficina de informática", "instrutor": "João",
         "carga_horaria": 40, "vagas": 20, "inscritos": []},
        {"id": 2, "nome": "Oficina de python", "instrutor": "Maria",
         "carga_horaria": 30, "vagas": 15, "inscritos": []},
    ]
})

participantes = carregar_dados(ARQUIVO_PARTICIPANTES, {
    "participantes": [
        {"id": 1, "nome": "Carlos", "email": "carlos@email.com", "curso": "Agronomia"},
        {"id": 2, "nome": "Ana", "email": "ana@email.com", "curso": "Informática"},
    ]
})

# ====================================================
# FUNÇÕES AUXILIARES (HELPERS)
# Funções de apoio utilizadas em diferentes partes
# do sistema para consultas e operações comuns.
# ====================================================
def obter_oficina(oficina_id):
    return next((o for o in oficinas["oficinas"] if o["id"] == oficina_id), None)


def obter_participante(participante_id):
    return next((p for p in participantes["participantes"] if p["id"] == participante_id), None)


def vagas_disponiveis(oficina):
    return oficina["vagas"] - len(oficina.get("inscritos", []))


def opcoes_oficinas():
    return [f'{o["id"]} - {o["nome"]}' for o in oficinas["oficinas"]] or ["(nenhuma oficina cadastrada)"]


def opcoes_participantes():
    return [f'{p["id"]} - {p["nome"]}' for p in participantes["participantes"]] or ["(nenhum participante cadastrado)"]


def extrair_id(texto_opcao):
    try:
        return int(texto_opcao.split(" - ")[0])
    except (ValueError, IndexError):
        return None

# ---------------------------------------------------------------------------
# NAVEGAÇÃO GENÉRICA
# Padroniza a troca entre as telas (janelas Toplevel) do sistema, escondendo
# a tela de origem e exibindo a tela de destino, evitando repetir esse
# código em cada função de navegação.
# ---------------------------------------------------------------------------
def ir_para(tela_origem, tela_destino, on_abrir=None):
    if on_abrir:
        on_abrir()
    tela_origem.withdraw()
    tela_destino.deiconify()


# ---------------------------------------------------------------------------
# OFICINAS: CRIAR
# Funções responsáveis por abrir a tela de cadastro de oficinas, validar os
# dados informados pelo usuário e salvar a nova oficina no sistema.
# ---------------------------------------------------------------------------

def abrir_tela_criar_oficina():
    label_mensagem_criar.config(text="")
    ir_para(tela_principal, tela_criar_oficina)


def voltar_para_principal():
    entry_nome.delete(0, tk.END)
    entry_instrutor.delete(0, tk.END)
    entry_carga.delete(0, tk.END)
    entry_vagas.delete(0, tk.END)
    label_mensagem_criar.config(text="")
    ir_para(tela_criar_oficina, tela_principal)


def salvar_oficina():
    nome = entry_nome.get().strip()
    instrutor = entry_instrutor.get().strip()
    carga = entry_carga.get().strip()
    vagas = entry_vagas.get().strip()

    if not nome or not instrutor or not carga or not vagas:
        label_mensagem_criar.config(text="Preencha todos os campos!", fg="red")
        return

    try:
        carga = int(carga)
        vagas = int(vagas)
    except ValueError:
        label_mensagem_criar.config(text="Carga horária e vagas devem ser números!", fg="red")
        return

    if carga <= 0 or vagas < 0:
        label_mensagem_criar.config(text="Valores inválidos!", fg="red")
        return

    novo_id = max((o["id"] for o in oficinas["oficinas"]), default=0) + 1
    oficinas["oficinas"].append({
        "id": novo_id,
        "nome": nome,
        "instrutor": instrutor,
        "carga_horaria": carga,
        "vagas": vagas,
        "inscritos": []
    })

    salvar_oficinas_no_arquivo()

    label_mensagem_criar.config(text=f"Oficina '{nome}' criada com sucesso!", fg="green")

    entry_nome.delete(0, tk.END)
    entry_instrutor.delete(0, tk.END)
    entry_carga.delete(0, tk.END)
    entry_vagas.delete(0, tk.END)

    tela_criar_oficina.after(1200, voltar_para_principal)


# ---------------------------------------------------------------------------
# OFICINAS: LISTAR   
# Monta dinamicamente a tabela de oficinas cadastradas, exibindo ID, nome,
# instrutor, carga horária e vagas disponíveis de cada uma.
# ---------------------------------------------------------------------------
def atualizar_lista_oficinas():
    for widget in frame_lista.winfo_children():
        widget.destroy()

    if not oficinas["oficinas"]:
        tk.Label(frame_lista, text="Nenhuma oficina cadastrada.", font=("Arial", 12), bg="lightblue") \
            .grid(row=0, column=0, columnspan=5, pady=5)
        return

    for linha, oficina in enumerate(oficinas["oficinas"]):
        disponiveis = vagas_disponiveis(oficina)
        tk.Label(frame_lista, text=oficina["id"], font=("Arial", 10), bg="lightblue", width=4, anchor="w") \
            .grid(row=linha, column=0, padx=2, pady=2, sticky="w")
        tk.Label(frame_lista, text=oficina["nome"], font=("Arial", 10), bg="lightblue", width=18, anchor="w",
                 wraplength=140, justify="left").grid(row=linha, column=1, padx=2, pady=2, sticky="w")
        tk.Label(frame_lista, text=oficina["instrutor"], font=("Arial", 10), bg="lightblue", width=10, anchor="w") \
            .grid(row=linha, column=2, padx=2, pady=2, sticky="w")
        tk.Label(frame_lista, text=f'{oficina["carga_horaria"]}h', font=("Arial", 10), bg="lightblue", width=6,
                 anchor="w").grid(row=linha, column=3, padx=2, pady=2, sticky="w")
        tk.Label(frame_lista, text=f'{disponiveis}/{oficina["vagas"]}', font=("Arial", 10), bg="lightblue", width=8,
                 anchor="w").grid(row=linha, column=4, padx=2, pady=2, sticky="w")


def abrir_tela_listar_oficinas():
    ir_para(tela_principal, tela_listar_oficinas, atualizar_lista_oficinas)


def voltar_de_listar():
    ir_para(tela_listar_oficinas, tela_principal)


# ---------------------------------------------------------------------------
# PARTICIPANTES: CADASTRAR
# Funções responsáveis por abrir a tela de cadastro de participantes,
# validar os dados informados e salvar o novo participante no sistema.
# ---------------------------------------------------------------------------
def abrir_tela_cadastrar_participante():
    label_mensagem_participante.config(text="")
    ir_para(tela_principal, tela_cadastrar_participante)


def voltar_de_cadastrar_participante():
    entry_nome_participante.delete(0, tk.END)
    entry_email_participante.delete(0, tk.END)
    entry_curso_participante.delete(0, tk.END)
    label_mensagem_participante.config(text="")
    ir_para(tela_cadastrar_participante, tela_principal)


def salvar_participante():
    nome = entry_nome_participante.get().strip()
    email = entry_email_participante.get().strip()
    curso = entry_curso_participante.get().strip()

    if not nome or not email or not curso:
        label_mensagem_participante.config(text="Preencha todos os campos!", fg="red")
        return

    if "@" not in email or "." not in email:
        label_mensagem_participante.config(text="Email inválido!", fg="red")
        return

    novo_id = max((p["id"] for p in participantes["participantes"]), default=0) + 1
    participantes["participantes"].append({
        "id": novo_id,
        "nome": nome,
        "email": email,
        "curso": curso
    })

    salvar_participantes_no_arquivo()

    label_mensagem_participante.config(text=f"Participante '{nome}' cadastrado com sucesso!", fg="green")

    entry_nome_participante.delete(0, tk.END)
    entry_email_participante.delete(0, tk.END)
    entry_curso_participante.delete(0, tk.END)

    tela_cadastrar_participante.after(1200, voltar_de_cadastrar_participante)


# ---------------------------------------------------------------------------
# INSCRIÇÃO EM OFICINA
# Funções responsáveis por preparar a tela de inscrição (atualizando os
# menus de oficinas e participantes) e por efetivar a inscrição, aplicando
# as regras de negócio: existência dos cadastros, duplicidade e vagas.
# ---------------------------------------------------------------------------
def abrir_tela_inscricao():
    label_mensagem_inscricao.config(text="")

    menu_oficinas["menu"].delete(0, "end")
    for opcao in opcoes_oficinas():
        menu_oficinas["menu"].add_command(label=opcao, command=lambda v=opcao: var_oficina_inscricao.set(v))
    var_oficina_inscricao.set(opcoes_oficinas()[0])

    menu_participantes["menu"].delete(0, "end")
    for opcao in opcoes_participantes():
        menu_participantes["menu"].add_command(label=opcao, command=lambda v=opcao: var_participante_inscricao.set(v))
    var_participante_inscricao.set(opcoes_participantes()[0])

    ir_para(tela_principal, tela_inscricao)


def voltar_de_inscricao():
    label_mensagem_inscricao.config(text="")
    ir_para(tela_inscricao, tela_principal)


def inscrever_participante():
    oficina_id = extrair_id(var_oficina_inscricao.get())
    participante_id = extrair_id(var_participante_inscricao.get())

    oficina = obter_oficina(oficina_id) if oficina_id is not None else None
    participante = obter_participante(participante_id) if participante_id is not None else None

    if not oficina or not participante:
        label_mensagem_inscricao.config(text="Selecione uma oficina e um participante válidos!", fg="red")
        return

    if participante_id in oficina.get("inscritos", []):
        label_mensagem_inscricao.config(text="Este participante já está inscrito nesta oficina!", fg="red")
        return

    if vagas_disponiveis(oficina) <= 0:
        label_mensagem_inscricao.config(text="Não há vagas disponíveis nesta oficina!", fg="red")
        return

    oficina.setdefault("inscritos", []).append(participante_id)
    salvar_oficinas_no_arquivo()

    label_mensagem_inscricao.config(
        text=f'{participante["nome"]} inscrito(a) em "{oficina["nome"]}" com sucesso!', fg="green"
    )


# ---------------------------------------------------------------------------
# PARTICIPANTES INSCRITOS POR OFICINA
# Funções responsáveis por exibir, para a oficina selecionada, a lista de
# participantes nela inscritos, atualizando a tela conforme a seleção muda.
# ---------------------------------------------------------------------------
def atualizar_lista_inscritos(*_):
    for widget in frame_lista_inscritos.winfo_children():
        widget.destroy()

    oficina_id = extrair_id(var_oficina_inscritos.get())
    oficina = obter_oficina(oficina_id) if oficina_id is not None else None

    if not oficina:
        tk.Label(frame_lista_inscritos, text="Selecione uma oficina.", font=("Arial", 11), bg="lightblue").pack()
        return

    inscritos_ids = oficina.get("inscritos", [])
    if not inscritos_ids:
        tk.Label(frame_lista_inscritos, text="Nenhum participante inscrito nesta oficina.",
                 font=("Arial", 11), bg="lightblue", wraplength=340).pack()
        return

    for participante_id in inscritos_ids:
        participante = obter_participante(participante_id)
        if participante:
            texto = f'{participante["nome"]} — {participante["email"]} ({participante["curso"]})'
            tk.Label(frame_lista_inscritos, text=texto, font=("Arial", 10), bg="lightblue",
                     anchor="w", justify="left", wraplength=340).pack(fill="x", padx=5, pady=2)


def abrir_tela_listar_inscritos():
    menu_oficinas_inscritos["menu"].delete(0, "end")
    for opcao in opcoes_oficinas():
        menu_oficinas_inscritos["menu"].add_command(
            label=opcao, command=lambda v=opcao: (var_oficina_inscritos.set(v), atualizar_lista_inscritos())
        )
    var_oficina_inscritos.set(opcoes_oficinas()[0])
    atualizar_lista_inscritos()
    ir_para(tela_principal, tela_listar_inscritos)


def voltar_de_listar_inscritos():
    ir_para(tela_listar_inscritos, tela_principal)


# ---------------------------------------------------------------------------
# TELA PRINCIPAL 
# ---------------------------------------------------------------------------
# Esta seção cria a janela principal do sistema e configura sua aparência.
# Nela são exibidos o título da aplicação e os botões de acesso às funções.
# Cada botão direciona o usuário para uma tela específica do sistema.
# Também são definidos o tamanho, a cor de fundo e o comportamento da janela.
# Esta é a primeira interface apresentada quando o programa é iniciado.
# ---------------------------------------------------------------------------
tela_principal = tk.Tk()
tela_principal.title("# Sistema de Gerenciamento de Oficinas")
tela_principal.geometry("420x400")
tela_principal.configure(bg="lightblue")
tela_principal.resizable(False, False)
tela_principal.protocol("WM_DELETE_WINDOW", lambda: tela_principal.destroy())

frame_topo = tk.Frame(tela_principal, bg="lightblue")
frame_topo.pack(pady=20)
tk.Label(frame_topo, text="Sistema de Gerenciamento de Oficinas", font=("Arial", 16), bg="lightblue",
         wraplength=380).pack() # wraplength define, em pixels, a largura máxima que o texto pode ocupar antes de quebrar para a linha seguinte.

frame_botoes = tk.Frame(tela_principal, bg="lightblue")
frame_botoes.pack(pady=10)

tk.Button(frame_botoes, text="Criar Oficina", font=("Arial", 12), width=22,
          command=abrir_tela_criar_oficina).pack(pady=6)
tk.Button(frame_botoes, text="Cadastrar Participante", font=("Arial", 12), width=22,
          command=abrir_tela_cadastrar_participante).pack(pady=6)
tk.Button(frame_botoes, text="Inscrever em Oficina", font=("Arial", 12), width=22,
          command=abrir_tela_inscricao).pack(pady=6)
tk.Button(frame_botoes, text="Listar Oficinas", font=("Arial", 12), width=22,
          command=abrir_tela_listar_oficinas).pack(pady=6)
tk.Button(frame_botoes, text="Participantes por Oficina", font=("Arial", 12), width=22,
          command=abrir_tela_listar_inscritos).pack(pady=6)


# ---------------------------------------------------------------------------
# TELA CRIAR OFICINA
# ---------------------------------------------------------------------------
# Cria a interface responsável pelo cadastro de novas oficinas.
# Nela são exibidos os campos para preenchimento dos dados e os botões de ação.
# Também define a aparência e o comportamento da janela.
# ---------------------------------------------------------------------------
tela_criar_oficina = tk.Toplevel(tela_principal)
tela_criar_oficina.title("# Criar Oficina")
tela_criar_oficina.geometry("400x320")
tela_criar_oficina.configure(bg="lightblue")
tela_criar_oficina.resizable(False, False)
tela_criar_oficina.protocol("WM_DELETE_WINDOW", voltar_para_principal) #.protocol(...): método que permite interceptar "protocolos de janela" do sistema operacional/gerenciador de janelas.
#Essa linha configura o que acontece quando o usuário tenta fechar a janela tela_criar_oficina clicando no "X" (o botão de fechar padrão do sistema operacional).
tela_criar_oficina.withdraw()#Esconde a janela, mas mantém tudo em memória (pode reexibir depois)

tk.Label(tela_criar_oficina, text="Criar Oficina", font=("Arial", 16), bg="lightblue").pack(pady=15)

frame_formulario = tk.Frame(tela_criar_oficina, bg="lightblue")
frame_formulario.pack(pady=5)

tk.Label(frame_formulario, text="Nome:", font=("Arial", 12), bg="lightblue").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_nome = tk.Entry(frame_formulario, font=("Arial", 12))
entry_nome.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame_formulario, text="Instrutor:", font=("Arial", 12), bg="lightblue").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_instrutor = tk.Entry(frame_formulario, font=("Arial", 12))
entry_instrutor.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame_formulario, text="Carga Horária:", font=("Arial", 12), bg="lightblue").grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_carga = tk.Entry(frame_formulario, font=("Arial", 12))
entry_carga.grid(row=2, column=1, padx=10, pady=5)

tk.Label(frame_formulario, text="Vagas:", font=("Arial", 12), bg="lightblue").grid(row=3, column=0, padx=10, pady=5, sticky="e")
entry_vagas = tk.Entry(frame_formulario, font=("Arial", 12))
entry_vagas.grid(row=3, column=1, padx=10, pady=5)

label_mensagem_criar = tk.Label(tela_criar_oficina, text="", font=("Arial", 10), bg="lightblue", wraplength=360)
label_mensagem_criar.pack(pady=5)

frame_botoes_criar = tk.Frame(tela_criar_oficina, bg="lightblue")
frame_botoes_criar.pack(pady=10)
tk.Button(frame_botoes_criar, text="Criar", font=("Arial", 12), command=salvar_oficina).grid(row=0, column=0, padx=5)
tk.Button(frame_botoes_criar, text="Voltar", font=("Arial", 12), command=voltar_para_principal).grid(row=0, column=1, padx=5)


# ---------------------------------------------------------------------------
# TELA LISTAR OFICINAS
# ---------------------------------------------------------------------------
# Esta tela exibe todas as oficinas cadastradas no sistema.
# É criado um cabeçalho para organizar as informações em formato de tabela.
# Os dados das oficinas são inseridos dinamicamente em um Frame.
# Também é disponibilizado um botão para retornar à tela principal.
# O layout foi desenvolvido para facilitar a visualização das informações.
# ---------------------------------------------------------------------------
tela_listar_oficinas = tk.Toplevel(tela_principal)
tela_listar_oficinas.title("# Listar Oficinas")
tela_listar_oficinas.geometry("420x340")
tela_listar_oficinas.configure(bg="lightblue")
tela_listar_oficinas.resizable(False, False)
tela_listar_oficinas.protocol("WM_DELETE_WINDOW", voltar_de_listar)
tela_listar_oficinas.withdraw()

tk.Label(tela_listar_oficinas, text="Listar Oficinas", font=("Arial", 16), bg="lightblue").pack(pady=15)

frame_cabecalho = tk.Frame(tela_listar_oficinas, bg="lightblue")
frame_cabecalho.pack(fill="x", padx=10)

tk.Label(frame_cabecalho, text="ID", font=("Arial", 10, "bold"), bg="lightblue", width=4, anchor="w").grid(row=0, column=0, sticky="w")
tk.Label(frame_cabecalho, text="Nome", font=("Arial", 10, "bold"), bg="lightblue", width=18, anchor="w").grid(row=0, column=1, sticky="w")
tk.Label(frame_cabecalho, text="Instrutor", font=("Arial", 10, "bold"), bg="lightblue", width=10, anchor="w").grid(row=0, column=2, sticky="w")
tk.Label(frame_cabecalho, text="Carga Hor.", font=("Arial", 10, "bold"), bg="lightblue", width=6, anchor="w").grid(row=0, column=3, sticky="w")
tk.Label(frame_cabecalho, text="Vagas", font=("Arial", 10, "bold"), bg="lightblue", width=8, anchor="w").grid(row=0, column=4, sticky="w")

frame_lista = tk.Frame(tela_listar_oficinas, bg="lightblue")
frame_lista.pack(pady=5, padx=10, fill="x")

frame_botoes_listar = tk.Frame(tela_listar_oficinas, bg="lightblue")
frame_botoes_listar.pack(pady=15)
tk.Button(frame_botoes_listar, text="Voltar", font=("Arial", 12), command=voltar_de_listar).grid(row=0, column=0, padx=5)


# ---------------------------------------------------------------------------
# TELA CADASTRAR PARTICIPANTE
# ---------------------------------------------------------------------------
# Esta seção cria a interface para cadastrar novos participantes.
# O formulário contém os campos de nome, e-mail e curso.
# Também existe uma área para exibir mensagens de erro ou sucesso.
# Os botões permitem salvar o cadastro ou retornar ao menu principal.
# Todos os componentes gráficos são organizados utilizando Frames.
# ---------------------------------------------------------------------------
tela_cadastrar_participante = tk.Toplevel(tela_principal)
tela_cadastrar_participante.title("# Cadastrar Participante")
tela_cadastrar_participante.geometry("400x300")
tela_cadastrar_participante.configure(bg="lightblue")
tela_cadastrar_participante.resizable(False, False)
tela_cadastrar_participante.protocol("WM_DELETE_WINDOW", voltar_de_cadastrar_participante)
tela_cadastrar_participante.withdraw()

tk.Label(tela_cadastrar_participante, text="Cadastrar Participante", font=("Arial", 16), bg="lightblue").pack(pady=20)

frame_formulario_participante = tk.Frame(tela_cadastrar_participante, bg="lightblue")
frame_formulario_participante.pack(pady=10)

tk.Label(frame_formulario_participante, text="Nome:", font=("Arial", 12), bg="lightblue").grid(row=0, column=0, padx=10, pady=5, sticky="e")
entry_nome_participante = tk.Entry(frame_formulario_participante, font=("Arial", 12))
entry_nome_participante.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame_formulario_participante, text="Email:", font=("Arial", 12), bg="lightblue").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_email_participante = tk.Entry(frame_formulario_participante, font=("Arial", 12))
entry_email_participante.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame_formulario_participante, text="Curso:", font=("Arial", 12), bg="lightblue").grid(row=2, column=0, padx=10, pady=5, sticky="e")
entry_curso_participante = tk.Entry(frame_formulario_participante, font=("Arial", 12))
entry_curso_participante.grid(row=2, column=1, padx=10, pady=5)

label_mensagem_participante = tk.Label(tela_cadastrar_participante, text="", font=("Arial", 10), bg="lightblue", wraplength=360)
label_mensagem_participante.pack(pady=5)

frame_botoes_participante = tk.Frame(tela_cadastrar_participante, bg="lightblue")
frame_botoes_participante.pack(pady=10)
tk.Button(frame_botoes_participante, text="Cadastrar", font=("Arial", 12), command=salvar_participante).grid(row=0, column=0, padx=5)
tk.Button(frame_botoes_participante, text="Voltar", font=("Arial", 12), command=voltar_de_cadastrar_participante).grid(row=0, column=1, padx=5)


# ---------------------------------------------------------------------------
# TELA INSCRIÇÃO EM OFICINA
# ---------------------------------------------------------------------------
# Esta tela permite realizar a inscrição de participantes em oficinas.
# São utilizados menus suspensos para selecionar oficina e participante.
# Após a seleção, o usuário pode confirmar a inscrição pelo botão Inscrever.
# Também existe uma área destinada às mensagens de validação do processo.
# O botão Voltar retorna o usuário para a tela principal.
# ---------------------------------------------------------------------------
tela_inscricao = tk.Toplevel(tela_principal)
tela_inscricao.title("# Inscrição em Oficina")
tela_inscricao.geometry("420x320")
tela_inscricao.configure(bg="lightblue")
tela_inscricao.resizable(False, False)
tela_inscricao.protocol("WM_DELETE_WINDOW", voltar_de_inscricao)
tela_inscricao.withdraw()

tk.Label(tela_inscricao, text="Inscrição em Oficina", font=("Arial", 16), bg="lightblue").pack(pady=20)

frame_form_inscricao = tk.Frame(tela_inscricao, bg="lightblue")
frame_form_inscricao.pack(pady=10)

tk.Label(frame_form_inscricao, text="Oficina:", font=("Arial", 12), bg="lightblue").grid(row=0, column=0, padx=10, pady=8, sticky="e")
var_oficina_inscricao = tk.StringVar(value="(nenhuma oficina cadastrada)")
menu_oficinas = tk.OptionMenu(frame_form_inscricao, var_oficina_inscricao, "(nenhuma oficina cadastrada)")
menu_oficinas.config(font=("Arial", 11), width=22)
menu_oficinas.grid(row=0, column=1, padx=10, pady=8)

tk.Label(frame_form_inscricao, text="Participante:", font=("Arial", 12), bg="lightblue").grid(row=1, column=0, padx=10, pady=8, sticky="e")
var_participante_inscricao = tk.StringVar(value="(nenhum participante cadastrado)")
menu_participantes = tk.OptionMenu(frame_form_inscricao, var_participante_inscricao, "(nenhum participante cadastrado)")
menu_participantes.config(font=("Arial", 11), width=22)
menu_participantes.grid(row=1, column=1, padx=10, pady=8)

label_mensagem_inscricao = tk.Label(tela_inscricao, text="", font=("Arial", 10), bg="lightblue", wraplength=380)
label_mensagem_inscricao.pack(pady=5)

frame_botoes_inscricao = tk.Frame(tela_inscricao, bg="lightblue")
frame_botoes_inscricao.pack(pady=10)
tk.Button(frame_botoes_inscricao, text="Inscrever", font=("Arial", 12), command=inscrever_participante).grid(row=0, column=0, padx=5)
tk.Button(frame_botoes_inscricao, text="Voltar", font=("Arial", 12), command=voltar_de_inscricao).grid(row=0, column=1, padx=5)


# ---------------------------------------------------------------------------
# TELA PARTICIPANTES INSCRITOS POR OFICINA
# ---------------------------------------------------------------------------
# Esta interface permite consultar os participantes inscritos em cada oficina.
# O usuário seleciona uma oficina e o sistema exibe sua lista de inscritos.
# As informações são apresentadas dinamicamente em uma área específica.
# Também é disponibilizado um botão para retornar ao menu principal.
# A tela facilita a consulta e organização dos participantes cadastrados.
# ---------------------------------------------------------------------------
tela_listar_inscritos = tk.Toplevel(tela_principal)
tela_listar_inscritos.title("# Participantes por Oficina")
tela_listar_inscritos.geometry("420x360")
tela_listar_inscritos.configure(bg="lightblue")
tela_listar_inscritos.resizable(False, False)
tela_listar_inscritos.protocol("WM_DELETE_WINDOW", voltar_de_listar_inscritos)
tela_listar_inscritos.withdraw()

tk.Label(tela_listar_inscritos, text="Participantes Inscritos por Oficina", font=("Arial", 15), bg="lightblue",
         wraplength=380).pack(pady=15)

frame_selecao_inscritos = tk.Frame(tela_listar_inscritos, bg="lightblue")
frame_selecao_inscritos.pack(pady=5)

tk.Label(frame_selecao_inscritos, text="Oficina:", font=("Arial", 12), bg="lightblue").grid(row=0, column=0, padx=10, sticky="e")
var_oficina_inscritos = tk.StringVar(value="(nenhuma oficina cadastrada)")
menu_oficinas_inscritos = tk.OptionMenu(frame_selecao_inscritos, var_oficina_inscritos, "(nenhuma oficina cadastrada)")
menu_oficinas_inscritos.config(font=("Arial", 11), width=22)
menu_oficinas_inscritos.grid(row=0, column=1, padx=10)

frame_lista_inscritos = tk.Frame(tela_listar_inscritos, bg="lightblue")
frame_lista_inscritos.pack(pady=15, padx=15, fill="both", expand=True)

frame_botoes_inscritos = tk.Frame(tela_listar_inscritos, bg="lightblue")
frame_botoes_inscritos.pack(pady=10)
tk.Button(frame_botoes_inscritos, text="Voltar", font=("Arial", 12), command=voltar_de_listar_inscritos).grid(row=0, column=0, padx=5)



tela_principal.mainloop()
