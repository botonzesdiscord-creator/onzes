import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
import os  # Para pegar o token do Render

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="\\", intents=intents)

GUILD_ID = 1257268932729901096

# --- Formações ---
formacoes = {
    "4-4-2": [
        "        [GK]         ",
        "[LB] [CB1] [CB2] [RB]",
        "[LM] [CM1] [CM2] [RM]",
        "    [ST1]    [ST2]   "
    ],
    "4-4-2(2)": [
        "        [GK]            ",
        "[LB] [CB1] [CB2] [RB]   ",
        "       [MDC1]            ",
        "             [CM2]      ",
        "[LM2]             [RM2]   ",
        "     [ST1]  [ST2]       "
    ],
    "4-3-3": [
        "        [GK]           ",
        "[LB] [CB1] [CB2] [RB]  ",
        "  [CM1] [CM3] [CM2]    ",
        " [LW]     [ST]     [RW]"
    ],
    "4-3-3(offensive)": [
        "        [GK]           ",
        "[LB] [CB1] [CB2] [RB]  ",
        "  [CM1] [MOC] [CM2]    ",
        " [LW]     [ST]     [RW]"
    ],
    "4-3-3(defensive)": [
        "        [GK]           ",
        "[LB] [CB1] [CB2] [RB]  ",
        "  [CM1] [MDC] [CM2]    ",
        " [LW]     [ST]     [RW]"
    ],
    "4-2-3-1": [
        "        [GK]           ",
        "[LB] [CB1] [CB2] [RB]  ",
        "     [MDC1] [MDC2]        ",
        "[LM2]   [MOC]     [RM2]  ",
        "        [ST]     "
    ],
    "3-5-2": [
        "            [GK]               ",
        "     [CB1] [CB2] [CB3]         ",
        "[LM] [CM1] [CM2] [CM3] [RM]    ",
        "      [ST1]    [ST2]           "
    ]
}

# --- Coordenadas no campo (800x1200) ---
posicoes_xy = {
    "GK": (400, 1100),
    "LB": (150, 900),
    "CB1": (300, 900),
    "CB2": (500, 900),
    "CB3": (400, 900),
    "RB": (650, 900),
    "LM": (150, 600),
    "LM2": (150, 450),
    "MDC": (400, 750),
    "MDC1": (300, 750),
    "MDC2": (500, 750),
    "CM1": (300, 600),
    "CM2": (500, 600),
    "CM3": (400, 600),
    "RM": (650, 600),
    "RM2": (650, 450),
    "MOC": (400, 450),
    "LW": (150, 300),
    "ST": (400, 250),
    "ST1": (300, 250),
    "ST2": (500, 250),
    "RW": (650, 300)
}

equipes_temp = {}

# --- Função para gerar imagem da formação ---
def gerar_formacao_img(jogadores):
    img = Image.new("RGB", (800, 1200), (34, 139, 34))  # fundo verde
    draw = ImageDraw.Draw(img)

    # Linhas do campo
    draw.rectangle([50, 50, 750, 1150], outline="white", width=5)
    draw.line([50, 600, 750, 600], fill="white", width=5)  # linha horizontal do meio-campo
    cx, cy = 400, 600
    r = 100
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline="white", width=5)

    # Grande área inferior
    draw.rectangle([250, 950, 550, 1150], outline="white", width=5)
    # Grande área superior
    draw.rectangle([250, 50, 550, 250], outline="white", width=5)
    # Pequena área inferior
    rect_largura = 200
    rect_altura = 120
    draw.rectangle([cx - rect_largura//2, 1150 - rect_altura, cx + rect_largura//2, 1150], outline="white", width=5)
    # Pequena área superior
    draw.rectangle([cx - rect_largura//2, 50, cx + rect_largura//2, 50 + rect_altura], outline="white", width=5)

    # Balizas
    baliza_largura = 200
    baliza_altura = 40
    cx = 400
    campo_topo = 50
    campo_base = 1150

    # Baliza superior
    x1 = cx - baliza_largura // 3
    x2 = cx + baliza_largura // 3
    draw.line([x1, campo_topo, x1, campo_topo - baliza_altura], fill="black", width=5)
    draw.line([x2, campo_topo, x2, campo_topo - baliza_altura], fill="black", width=5)
    draw.line([x1, campo_topo - baliza_altura, x2, campo_topo - baliza_altura], fill="black", width=5)
    # Baliza inferior
    draw.line([x1, campo_base, x1, campo_base + baliza_altura], fill="black", width=5)
    draw.line([x2, campo_base, x2, campo_base + baliza_altura], fill="black", width=5)
    draw.line([x1, campo_base + baliza_altura, x2, campo_base + baliza_altura], fill="black", width=5)

    # Fonte
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()

    # Desenhar jogadores
    for pos, nome in jogadores.items():
        if pos in posicoes_xy:
            x, y = posicoes_xy[pos]
            draw.ellipse([x-50, y-50, x+50, y+50], fill=(178, 34, 34), outline="white", width=3)
            bbox = draw.textbbox((0, 0), nome[:6], font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            draw.text((x - w/2, y - h/2), nome[:6], fill="white", font=font)

    output_bytes = io.BytesIO()
    img.save(output_bytes, format="PNG")
    output_bytes.seek(0)
    return output_bytes

# --- Agrupar posições ---
def agrupar_posicoes(formacao):
    defesa, meio, ataque = [], [], []
    for linha in formacoes[formacao]:
        for token in linha.split():
            if "[" in token and "]" in token:
                pos = token.strip("[]")
                if pos == "GK" or pos.startswith("CB") or pos in ["LB", "RB"]:
                    defesa.append(pos)
                elif (
                    pos.startswith("CM")
                    or pos.startswith("MD")
                    or pos in ["LM", "LM2", "RM", "RM2", "MOC"]
                ):
                    meio.append(pos)
                elif pos.startswith("ST") or pos in ["LW", "RW"]:
                    ataque.append(pos)
    return defesa, meio, ataque

# --- Suas classes MensagemFinalModal, SetorModal, SetorButton, CancelButton, EnviarFormacaoButton, SetorView ---
# Cole todas exatamente como você tinha antes aqui

# --- Slash command ---
@bot.tree.command(name="11", description="Escolher formação da equipa")
@discord.app_commands.describe(esquema="Escolhe a formação")
@discord.app_commands.choices(
    esquema=[discord.app_commands.Choice(name=f, value=f) for f in formacoes.keys()]
)
async def slash_11(interaction: discord.Interaction, esquema: discord.app_commands.Choice[str]):
    esquema = esquema.value
    posicoes = [p.strip("[]") for linha in formacoes[esquema] for p in linha.split() if "[" in p and "]" in p]
    equipes_temp[interaction.user.id] = {
        "formacao": esquema,
        "jogadores": {},
        "posicoes": posicoes,
        "view_message": None,
        "view_obj": None
    }
    view = SetorView(interaction.user.id, esquema)
    await interaction.response.send_message("⚽ Escolhe um setor para adicionar os jogadores:", view=view, ephemeral=True)
    equipes_temp[interaction.user.id]["view_message"] = await interaction.original_response()
    equipes_temp[interaction.user.id]["view_obj"] = view

# --- Setup hook ---
@bot.event
async def setup_hook():
    guild = discord.Object(id=GUILD_ID)
    bot.tree.add_command(slash_11, guild=guild)
    await bot.tree.sync(guild=guild)
    print("✅ Comandos slash sincronizados na guilda!")

# --- on_ready ---
@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

# --- Rodar bot ---
TOKEN = os.environ['DISCORD_TOKEN']
bot.run(TOKEN)
