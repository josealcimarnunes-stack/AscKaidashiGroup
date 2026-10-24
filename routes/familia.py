import os
import json
import zipfile
import tempfile
from flask import Blueprint, render_template, request, current_app, jsonify, send_file
from werkzeug.utils import secure_filename

familia_bp = Blueprint("familia", __name__)

# Caminho para o ficheiro de persistência JSON
ARQUIVO_JSON = os.path.join(os.path.dirname(__file__), "..", "dados_familia.json")

# Estrutura Mestre de Personagens, Estilos e Prompts (Padrão de Fábrica)
PERSONAGENS_CONFIG_PADRAO = {
    "mamae": {
        "nome": "Mamãe",
        "idade": "36 anos",
        "icone": "👩",
        "estilos": {
            "casual": "Realistic portrait of a 36-year-old welcoming Brazilian mother, parda/mestiça ethnicity, warm brown eyes, wavy dark brown hair, natural elegant casual look, soft studio lighting, 8k resolution",
            "trabalho": "Realistic portrait of a 36-year-old professional Brazilian woman in smart business casual attire, blazer, confident posture, office environment background, 8k resolution",
            "fitness": "Realistic portrait of a 36-year-old fit Brazilian woman in gym workout clothes, glowing healthy parda skin, ponytailed hair, modern gym background, photorealistic 8k",
            "casa": "Cozy portrait of a 36-year-old Brazilian mother at home, comfortable loungewear, warm family home ambient lighting, natural smile, 8k",
        },
    },
    "papai": {
        "nome": "Papai",
        "idade": "38 anos",
        "icone": "👨",
        "estilos": {
            "casual": "Realistic portrait of a 38-year-old friendly Brazilian father, parda skin, short dark hair, natural smile, modern casual outfit, photorealistic 8k",
            "trabalho": "Realistic portrait of a 38-year-old Brazilian man in casual business outfit, button-up shirt, confident smile, modern office setting, 8k",
            "fitness": "Realistic portrait of a 38-year-old athletic Brazilian man in sportswear, active background, sunlight, detailed skin 8k",
        },
    },
    "filha": {
        "nome": "Filha Jovem",
        "idade": "21 anos",
        "icone": "👩‍🦱",
        "estilos": {
            "casual": "Realistic portrait of a 21-year-old attractive Brazilian young woman, parda skin, expressive brown eyes, long wavy dark hair, stylish casual outfit, confident friendly smile, 8k resolution",
            "estudo": "Realistic portrait of a 21-year-old Brazilian female university student with backpack and tablet, modern library background, 8k",
            "balada": "Stylish portrait of a 21-year-old Brazilian woman in night party outfit, subtle vibrant party lights, fashionable look, 8k",
            "fitness": "Portrait of a 21-year-old Brazilian young woman in trendy gym clothes, active outdoor park, sunny day, 8k",
        },
    },
    "filho": {
        "nome": "Filho Teen",
        "idade": "17 anos",
        "icone": "👦",
        "estilos": {
            "casual": "Realistic portrait of a 17-year-old Brazilian teenage boy, parda skin, modern relaxed haircut, expressive energetic face, wearing a trendy hoodie, photorealistic 8k",
            "esporte": "Portrait of a 17-year-old Brazilian teen in sports gear, holding a soccer ball or near a court, energetic posture, 8k",
            "streetwear": "Stylish 17-year-old Brazilian teenager in urban streetwear, sneakers, modern urban background, 8k",
        },
    },
    "vova_raiz": {
        "nome": "Vovó Raíz",
        "idade": "65 anos",
        "icone": "👵",
        "estilos": {
            "casa": "A warm and loving 65-year-old Brazilian grandmother, natural parda/mestiça skin, gentle smile, natural grey wavy hair, fine lines around the eyes, beige cardigan, warm lighting, 8k",
            "cozinha": "Warm portrait of a 65-year-old Brazilian grandmother in cozy kitchen background, smiling gently, baking/cooking outfit, photorealistic 8k",
            "jardim": "A 65-year-old Brazilian grandmother in a green garden, natural sunlight, comfortable clothes, plants background, 8k",
        },
    },
    "vovo_raiz": {
        "nome": "Vovô Raíz",
        "idade": "68 anos",
        "icone": "👴",
        "estilos": {
            "casa": "A friendly 68-year-old Brazilian grandfather, parda skin, gentle smile, short white/grey hair, classic polo shirt, relaxed home setting, 8k",
            "oficina": "A 68-year-old Brazilian grandfather in home workshop environment, holding tools, smiling, relaxed, 8k",
            "passeio": "A 68-year-old Brazilian grandfather on a park bench, sunny day, casual jacket, gentle look, 8k",
        },
    },
    "vova_fit": {
        "nome": "Vovó Fit",
        "idade": "62 anos",
        "icone": "🏃‍♀️",
        "estilos": {
            "caminhada": "An athletic energetic 62-year-old Brazilian woman, fit body, glowing parda skin, grey ponytail, modern walking gear, park trail background, 8k",
            "academia": "Fit 62-year-old Brazilian woman doing light weights in modern gym, confident smile, active lifestyle, 8k",
            "praia": "Energetic 62-year-old Brazilian woman on tropical beach boardwalk, sunny morning light, sportswear, 8k",
        },
    },
    "vovo_fit": {
        "nome": "Vovô Fit",
        "idade": "65 anos",
        "icone": "🏃‍♂️",
        "estilos": {
            "corrida": "A fit active 65-year-old Brazilian man, toned physique, short silver hair, wearing running shirt, sports smartwatch, outdoor park background, 8k",
            "academia": "Active 65-year-old Brazilian grandfather in modern fitness gym, workout gear, energetic stance, 8k",
            "esporte": "A 65-year-old athletic Brazilian man outdoors, sports outfit, smiling, vibrant sunlight, 8k",
        },
    },
    "coringa_kids": {
        "nome": "Coringas Kids",
        "idade": "7 anos",
        "icone": "🎈",
        "estilos": {
            "brincando": "Realistic portrait of a cute 7-year-old Brazilian playful child, happy smile, casual colorful clothes, bright playground background, 8k",
            "escola": "Cute 7-year-old Brazilian child with colorful backpack, cheerful student look, classroom background, 8k",
            "festas": "Happy 7-year-old Brazilian kid at birthday party atmosphere, festive background, wearing party clothes, 8k",
        },
    },
    "pet": {
        "nome": "Pet (Golden)",
        "idade": "3 anos",
        "icone": "🐶",
        "estilos": {
            "brincando": "Cute loyal Golden Retriever dog, friendly playful eyes, vibrant fur, sunny green lawn background, highly detailed 8k",
            "dormindo": "Adorable Golden Retriever sleeping comfortably on a soft carpet, warm home ambient light, 8k",
            "passeio": "Golden Retriever on a leash during park walk, happy open mouth, outdoor daylight, 8k",
        },
    },
}


def carregar_configuracao():
    """Carrega as configurações do ficheiro JSON no disco. Se não existir, cria um novo."""
    if os.path.exists(ARQUIVO_JSON):
        try:
            with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERRO] Falha ao carregar {ARQUIVO_JSON}: {e}")

    salvar_configuracao(PERSONAGENS_CONFIG_PADRAO)
    return PERSONAGENS_CONFIG_PADRAO


def salvar_configuracao(dados):
    """Grava as alterações fisicamente no ficheiro JSON."""
    try:
        with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        print("[SUCESSO] Dados salvos no ficheiro dados_familia.json com sucesso!")
    except Exception as e:
        print(f"[ERRO] Falha ao salvar no disco: {e}")


@familia_bp.route("/")
def menu_familia():
    """Tela 1: Visão Geral e Seleção dos Personagens"""
    personagens_config = carregar_configuracao()
    return render_template("familia_menu.html", personagens=personagens_config)


@familia_bp.route("/perfil/<personagem>", methods=["GET", "POST"])
def perfil_dedicado(personagem):
    """Tela 2: Painel Exclusivo do Personagem Selecionado"""
    personagens_config = carregar_configuracao()

    if personagem not in personagens_config:
        return render_template("familia_menu.html", personagens=personagens_config)

    dados_personagem = personagens_config[personagem]
    estilos_disponiveis = list(dados_personagem["estilos"].keys())

    estilo_ativo = request.args.get("estilo", estilos_disponiveis[0])
    if estilo_ativo not in estilos_disponiveis:
        estilo_ativo = estilos_disponiveis[0]

    # Salvamento do Prompt via POST
    if request.method == "POST":
        dados = request.get_json() or {}
        novo_prompt = dados.get("prompt", "")
        estilo_informado = dados.get("estilo", estilo_ativo)

        if estilo_informado in dados_personagem["estilos"]:
            dados_personagem["estilos"][estilo_informado] = novo_prompt
            salvar_configuracao(personagens_config)
            return jsonify({"status": "sucesso", "estilo": estilo_informado})

        return jsonify({"status": "erro", "mensagem": "Estilo inválido"}), 400

    prompt_atual = dados_personagem["estilos"][estilo_ativo]

    # Busca as fotos na pasta física do sistema
    pasta_fotos = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "personagens",
        personagem,
        estilo_ativo,
    )
    fotos = []
    if os.path.exists(pasta_fotos):
        fotos = [
            f
            for f in os.listdir(pasta_fotos)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
        ]

    return render_template(
        "familia_perfil.html",
        chave_personagem=personagem,
        p=dados_personagem,
        estilo_ativo=estilo_ativo,
        prompt=prompt_atual,
        fotos=fotos,
    )


@familia_bp.route("/criar_pasta/<personagem>", methods=["POST"])
def criar_pasta(personagem):
    """Cria dinamicamente uma nova pasta/estilo para o personagem"""
    personagens_config = carregar_configuracao()
    if personagem not in personagens_config:
        return jsonify({"status": "erro", "mensagem": "Personagem não encontrado"}), 404

    dados = request.get_json() or {}
    nome_estilo_raw = dados.get("nome_estilo", "").strip()
    if not nome_estilo_raw:
        return jsonify({"status": "erro", "mensagem": "Nome da pasta inválido"}), 400

    nome_estilo = secure_filename(nome_estilo_raw.lower().replace(" ", "_"))

    if nome_estilo in personagens_config[personagem]["estilos"]:
        return jsonify({"status": "erro", "mensagem": "Esta pasta já existe!"}), 400

    personagens_config[personagem]["estilos"][
        nome_estilo
    ] = f"Realistic portrait of {personagens_config[personagem]['nome']}, custom style {nome_estilo}, 8k"
    salvar_configuracao(personagens_config)

    pasta_fisica = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "personagens",
        personagem,
        nome_estilo,
    )
    os.makedirs(pasta_fisica, exist_ok=True)

    return jsonify({"status": "sucesso", "estilo": nome_estilo})


@familia_bp.route("/enviar/<personagem>/<estilo>", methods=["POST"])
def enviar(personagem, estilo):
    """Recebe arquivos e salva na pasta correta"""
    arquivos = request.files.getlist("arquivos") or request.files.getlist("arquivo")

    if not arquivos or not arquivos[0].filename:
        return jsonify({"status": "erro", "mensagem": "Nenhum arquivo enviado"}), 400

    pasta_destino = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "personagens",
        personagem,
        estilo,
    )
    os.makedirs(pasta_destino, exist_ok=True)

    for arquivo in arquivos:
        if arquivo.filename:
            nome_seguro = secure_filename(arquivo.filename)
            caminho_completo = os.path.join(pasta_destino, nome_seguro)
            arquivo.save(caminho_completo)

    return jsonify({"status": "sucesso", "mensagem": "Upload realizado com sucesso!"})


@familia_bp.route("/baixar_zip/<personagem>/<estilo>")
def baixar_zip(personagem, estilo):
    """Compacta todas as fotos da pasta em um arquivo ZIP"""
    pasta_fotos = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "personagens",
        personagem,
        estilo,
    )

    if not os.path.exists(pasta_fotos):
        return "Pasta não encontrada", 404

    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    temp_zip.close()

    with zipfile.ZipFile(temp_zip.name, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(pasta_fotos):
            for file in files:
                caminho_completo = os.path.join(root, file)
                zipf.write(caminho_completo, arcname=file)

    return send_file(
        temp_zip.name,
        as_attachment=True,
        download_name=f"{personagem}_{estilo}_midias.zip",
        mimetype="application/zip",
    )
