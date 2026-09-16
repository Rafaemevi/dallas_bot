
import os
import sqlite3
from datetime import datetime
from typing import Optional
import discord
from discord import app_commands, SelectOption
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, UserSelect, Select

TOKEN = os.getenv("DISCORD_TOKEN")

# ========================= CANAIS =========================
CANAL_SETAGEM_ID = 1549597861082300417
CANAL_PROMOCAO_ID = 1549563467139387422
CANAL_ADVERTENCIA_ID = 1549563495203217479
CANAL_EXONERACAO_ID = 1549563512584667256
CANAL_REBAIXAMENTO_ID = 1549563630452875407
CANAL_AUSENCIA_ID = 1549563878940213360
CANAL_HISTORICO_ID = 1549563664732786759
CANAL_LOGS_ID = 1549607907040034898
CANAL_APROVACOES_ID = 1549598924514398308

# ========================= CARGOS =========================
COMANDO_GOT_ID = 1548710304978968596
SUB_COMANDO_GOT_ID = 1548710307168395284
SUPERVISOR_GOT_ID = 1548710310318313542
COORDENADOR_GOT_ID = 1548710308946911356
ESPECIALISTA_GOT_ID = 1548710311576469564
EXECUTOR_GOT_ID = 1548710312922976347
OPERADOR_GOT_ID = 1548710314189660190
RECRUTADOR_GOT_ID = 1549606586371018762

HIERARQUIA = [
    COMANDO_GOT_ID, SUB_COMANDO_GOT_ID, SUPERVISOR_GOT_ID,
    COORDENADOR_GOT_ID, ESPECIALISTA_GOT_ID, RECRUTADOR_GOT_ID,
    EXECUTOR_GOT_ID, OPERADOR_GOT_ID
]

PERMISSOES = {
    # Setagem pode ser solicitada por qualquer pessoa.
    "setagem": None,
    "promocao": COORDENADOR_GOT_ID,
    "advertencia": COORDENADOR_GOT_ID,
    "exoneracao": COORDENADOR_GOT_ID,
    "rebaixamento": COORDENADOR_GOT_ID,
    "ausencia": COORDENADOR_GOT_ID,
    "historico": COORDENADOR_GOT_ID,
}

PREFIXOS = {
    COMANDO_GOT_ID: "[CMD]", SUB_COMANDO_GOT_ID: "[SUB]",
    SUPERVISOR_GOT_ID: "[SUP]", COORDENADOR_GOT_ID: "[COORD]",
    ESPECIALISTA_GOT_ID: "[ESP]", EXECUTOR_GOT_ID: "[EXE]",
    OPERADOR_GOT_ID: "[OP]", RECRUTADOR_GOT_ID: "[REC]",
}

# ========================= IMAGENS =========================
IMAGEM_PAINEL = "https://cdn.discordapp.com/attachments/1549563963862163497/1549574008905924678/content.png?ex=6aab30c1&is=6aa9df41&hm=c0a24f3fb007641c480929433c676e41771a0e524ed3aad4cb995f1ac3370210&"
IMAGEM_SETAGEM = "https://cdn.discordapp.com/attachments/1549563963862163497/1549571790525829221/content.png?ex=6aab2eb0&is=6aa9dd30&hm=48f321759c2ad0128e3ff268cb06a9b91f9768f01ca0940b77e952743599918f&"
IMAGEM_PROMOCAO = "https://cdn.discordapp.com/attachments/1549563963862163497/1549571893604913332/content.png?ex=6aab2ec9&is=6aa9dd49&hm=35c383b29b39944235a5807a9bc7fbb412ebca2b87fee31c1f019cc45d862dbe&"
IMAGEM_ADVERTENCIA = "https://cdn.discordapp.com/attachments/1549563963862163497/1549572163055386758/content.png?ex=6aab2f09&is=6aa9dd89&hm=4928e6231b8178859e99d7677094a64cd42a9812b4bfb706d89b291a05891d07&"
IMAGEM_EXONERACAO = "https://cdn.discordapp.com/attachments/1549563963862163497/1549572534385508415/content.png?ex=6aab2f61&is=6aa9dde1&hm=b7e8b1fbb3583290c4e8e0af4e739217124665fc45df9d26fc2558ea000f4633&"
IMAGEM_REBAIXAMENTO = "https://cdn.discordapp.com/attachments/1549563963862163497/1549572895884447785/content.png?ex=6aab2fb8&is=6aa9de38&hm=6fe76956fb716b05591a413c6cc96a65b27b22ae79cfcb9dc48d41038170d7cb&"
IMAGEM_AUSENCIA = "https://cdn.discordapp.com/attachments/1549563963862163497/1549573674410053725/content.png?ex=6aab3071&is=6aa9def1&hm=ce91ba48c1211e6b2a0b3c23cdfe5de6b14f7a7a0700256cf82d39070a92c156&"
IMAGEM_CONSULTA = "https://cdn.discordapp.com/attachments/1549563963862163497/1549573924910530560/content.png?ex=6aab30ad&is=6aa9df2d&hm=88491cfd20e7c4bc5f2cbd984d43e093b1f30612ff6af4ffada662631593fd4a&"
IMAGEM_HISTORICO = IMAGEM_CONSULTA

DB_FILE = "got_dallas.db"

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ========================= BANCO =========================
def conectar():
    return sqlite3.connect(DB_FILE)

def iniciar_banco():
    con = conectar()
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS historico(
        id INTEGER PRIMARY KEY AUTOINCREMENT,guild_id INTEGER NOT NULL,
        membro_id INTEGER NOT NULL,tipo TEXT NOT NULL,autor_id INTEGER NOT NULL,
        cargo_anterior TEXT DEFAULT '',cargo_novo TEXT DEFAULT '',
        motivo TEXT DEFAULT '',recrutador_id INTEGER,observacao TEXT DEFAULT '',
        protocolo TEXT NOT NULL,criado_em TEXT NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS pendentes_setagem(
        id INTEGER PRIMARY KEY AUTOINCREMENT,guild_id INTEGER NOT NULL,
        membro_id INTEGER NOT NULL,nome_rp TEXT NOT NULL,id_rp TEXT NOT NULL,
        recrutador TEXT NOT NULL,solicitante_id INTEGER NOT NULL,
        mensagem_id INTEGER,canal_id INTEGER,status TEXT DEFAULT 'PENDENTE',
        criado_em TEXT NOT NULL)""")
    con.commit()
    con.close()

def protocolo(tipo):
    return f"GOT-{tipo[:3].upper()}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

def salvar_historico(guild_id,membro_id,tipo,autor_id,cargo_anterior="",cargo_novo="",
                      motivo="",recrutador_id=None,observacao=""):
    p = protocolo(tipo)
    con = conectar(); cur = con.cursor()
    cur.execute("""INSERT INTO historico
        (guild_id,membro_id,tipo,autor_id,cargo_anterior,cargo_novo,motivo,
         recrutador_id,observacao,protocolo,criado_em)
        VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
        (guild_id,membro_id,tipo,autor_id,cargo_anterior,cargo_novo,motivo,
         recrutador_id,observacao,p,datetime.now().isoformat(timespec="seconds")))
    con.commit(); con.close()
    return p

def contar_acoes(guild_id,membro_id,tipo):
    con=conectar(); cur=con.cursor()
    cur.execute("SELECT COUNT(*) FROM historico WHERE guild_id=? AND membro_id=? AND tipo=?",
                (guild_id,membro_id,tipo))
    n=cur.fetchone()[0]; con.close(); return n

def buscar_historico(guild_id,membro_id,limite=20):
    con=conectar(); cur=con.cursor()
    cur.execute("""SELECT id,tipo,autor_id,cargo_anterior,cargo_novo,motivo,
                   recrutador_id,observacao,protocolo,criado_em
                   FROM historico WHERE guild_id=? AND membro_id=?
                   ORDER BY id DESC LIMIT ?""",(guild_id,membro_id,limite))
    rows=cur.fetchall(); con.close(); return rows

def criar_pendente(guild_id,membro_id,nome,id_rp,recrutador):
    con=conectar(); cur=con.cursor()
    cur.execute("""INSERT INTO pendentes_setagem
        (guild_id,membro_id,nome_rp,id_rp,recrutador,solicitante_id,criado_em)
        VALUES(?,?,?,?,?,?,?)""",
        (guild_id,membro_id,nome,id_rp,recrutador,membro_id,
         datetime.now().isoformat(timespec="seconds")))
    pid=cur.lastrowid; con.commit(); con.close(); return pid

def pegar_pendente(pid):
    con=conectar(); cur=con.cursor()
    cur.execute("""SELECT id,guild_id,membro_id,nome_rp,id_rp,recrutador,
                   solicitante_id,mensagem_id,canal_id,status,criado_em
                   FROM pendentes_setagem WHERE id=?""",(pid,))
    r=cur.fetchone(); con.close(); return r

def finalizar_pendente(pid,status):
    con=conectar(); cur=con.cursor()
    cur.execute("UPDATE pendentes_setagem SET status=? WHERE id=?",(status,pid))
    con.commit(); con.close()

def salvar_mensagem_pendente(pid,msg_id,canal_id):
    con=conectar(); cur=con.cursor()
    cur.execute("UPDATE pendentes_setagem SET mensagem_id=?,canal_id=? WHERE id=?",
                (msg_id,canal_id,pid))
    con.commit(); con.close()

def pendentes_guild(guild_id):
    con=conectar(); cur=con.cursor()
    cur.execute("SELECT id FROM pendentes_setagem WHERE guild_id=? AND status='PENDENTE'",
                (guild_id,))
    r=[x[0] for x in cur.fetchall()]; con.close(); return r

# ========================= CARGOS =========================
def posicoes():
    return {rid:i for i,rid in enumerate(HIERARQUIA) if rid}

def cargo_got_atual(membro):
    p=posicoes()
    cargos=[r for r in membro.roles if r.id in p]
    return sorted(cargos,key=lambda r:p[r.id])[0] if cargos else None

def todos_cargos_got(membro):
    ids=set(posicoes())
    return [r for r in membro.roles if r.id in ids]

def pode_aprovar_setagem(membro):
    atual = cargo_got_atual(membro)
    if atual is None:
        return False

    p = posicoes()
    nivel_recrutador = p.get(RECRUTADOR_GOT_ID)
    nivel_atual = p.get(atual.id)

    if nivel_recrutador is None or nivel_atual is None:
        return False

    return nivel_atual <= nivel_recrutador


def pode_usar(membro,acao):
    if acao == "setagem":
        return True

    p=posicoes()
    minimo=PERMISSOES.get(acao)
    atual=cargo_got_atual(membro)
    return bool(minimo in p and atual and p[atual.id] <= p[minimo])

def cargo_por_id(guild,rid):
    return guild.get_role(rid)

def nickname_para(membro,cargo,nome_rp=None,id_rp=None):
    if nome_rp and id_rp:
        nome=nome_rp.strip(); ident=id_rp.strip()
    else:
        nome=membro.display_name
        for pre in PREFIXOS.values():
            if nome.upper().startswith(pre.upper()+" "):
                nome=nome[len(pre):].strip(); break
        if "|" in nome: nome=nome.split("|",1)[0].strip()
        ident=str(membro.id)
    return f"{PREFIXOS.get(cargo.id,'')} {nome} | {ident}".strip()[:32]

async def aplicar_cargo(membro,cargo,nome_rp=None,id_rp=None):
    antigos=[r for r in todos_cargos_got(membro) if r.id!=cargo.id]
    if antigos: await membro.remove_roles(*antigos,reason="Atualização G.O.T")
    await membro.add_roles(cargo,reason="Atualização G.O.T")
    try:
        await membro.edit(nick=nickname_para(membro,cargo,nome_rp,id_rp),
                          reason="Nickname automático G.O.T")
    except discord.Forbidden:
        pass

# ========================= EMBEDS =========================
def embed_base(titulo,descricao="",cor=None):
    e=discord.Embed(title=titulo,description=descricao,
                    color=cor or discord.Color.dark_grey(),timestamp=datetime.now())
    e.set_footer(text="G.O.T DALLAS CITY • SISTEMA ADMINISTRATIVO")
    return e

def img(e,url):
    if url: e.set_image(url=url)
    return e

async def enviar(guild,canal_id,embed,view=None):
    canal=guild.get_channel(canal_id)
    if not canal: return None
    try: return await canal.send(embed=embed,view=view)
    except discord.Forbidden: return None

async def log(guild,embed):
    await enviar(guild,CANAL_LOGS_ID,embed)

# ========================= SETAGEM: FORMULÁRIO ÚNICO =========================
class SetagemModal(Modal,title="Registro GOT Dallas"):
    nome=TextInput(label="Nome",placeholder="Ex: Almeida Santos",required=True,max_length=80)
    id_rp=TextInput(label="ID",placeholder="Ex: 11277",required=True,max_length=30)
    recrutador=TextInput(label="Recrutador",placeholder="Nome de quem te recrutou",
                         required=True,max_length=80)

    async def on_submit(self,interaction):
        if not isinstance(interaction.user,discord.Member):
            await interaction.response.send_message("❌ Não foi possível identificar seu usuário no servidor.",ephemeral=True); return

        pid=criar_pendente(interaction.guild.id,interaction.user.id,
                           self.nome.value.strip(),self.id_rp.value.strip(),
                           self.recrutador.value.strip())

        e=img(embed_base("🦉 SETAGEM PENDENTE",
                         "Nova solicitação aguardando aprovação.",
                         discord.Color.from_rgb(110,95,70)),IMAGEM_SETAGEM)
        e.add_field(name="👤 NOME RP",value=f"`{self.nome.value.strip()}`",inline=True)
        e.add_field(name="🆔 ID RP",value=f"`{self.id_rp.value.strip()}`",inline=True)
        e.add_field(name="👮 DISCORD",value=interaction.user.mention,inline=True)
        e.add_field(name="🤝 RECRUTADOR",value=self.recrutador.value.strip(),inline=True)
        e.add_field(name="🎖️ CARGO",value="Operador GOT",inline=True)
        e.add_field(name="🏷️ NICKNAME",
                    value=f"`[OP] {self.nome.value.strip()} | {self.id_rp.value.strip()}`",
                    inline=False)

        m=await enviar(interaction.guild,CANAL_APROVACOES_ID,e,AprovacaoSetagemView(pid))
        if not m:
            finalizar_pendente(pid,"ERRO_ENVIO")
            await interaction.response.send_message(
                "❌ Não consegui enviar para o canal de aprovações.",ephemeral=True); return

        salvar_mensagem_pendente(pid,m.id,m.channel.id)
        await interaction.response.send_message(
            "✅ Formulário enviado para aprovação.",ephemeral=True)

# ========================= APROVAÇÃO =========================
class AprovacaoSetagemView(View):
    def __init__(self,pid):
        super().__init__(timeout=None)
        self.add_item(AprovarButton(pid))
        self.add_item(RecusarButton(pid))

class AprovarButton(Button):
    def __init__(self,pid):
        super().__init__(label="APROVAR",emoji="✅",style=discord.ButtonStyle.success,
                         custom_id=f"got:setagem:aprovar:{pid}")
        self.pid=pid

    async def callback(self,interaction):
        if not isinstance(interaction.user,discord.Member): return

        # Qualquer pessoa pode pedir SETAGEM, mas somente RECRUTADOR ou acima pode aprovar.
        if not pode_usar(interaction.user,"setagem"):
            await interaction.response.send_message(
                "❌ Apenas **Recrutador ou superior** pode aprovar uma setagem.",
                ephemeral=True
            )
            return

        if not interaction.channel.permissions_for(interaction.user).view_channel:
            await interaction.response.send_message("❌ Você não tem acesso a este canal.",ephemeral=True); return

        p=pegar_pendente(self.pid)
        if not p or p[9]!="PENDENTE":
            await interaction.response.send_message("⚠️ Esta solicitação já foi processada.",ephemeral=True); return

        _,guild_id,membro_id,nome,id_rp,recrutador,_,_,_,_,_=p
        membro=interaction.guild.get_member(membro_id)
        cargo=cargo_por_id(interaction.guild,OPERADOR_GOT_ID)
        if not membro:
            await interaction.response.send_message("❌ O membro não está mais no servidor.",ephemeral=True); return
        if not cargo:
            await interaction.response.send_message("❌ Cargo Operador GOT não encontrado.",ephemeral=True); return
        if cargo >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ Coloque o cargo do bot acima de Operador GOT.",ephemeral=True); return

        # IMPORTANTE: pega o cargo anterior ANTES de aplicar o novo.
        anterior=cargo_got_atual(membro)
        try:
            await aplicar_cargo(membro,cargo,nome,id_rp)
        except discord.Forbidden:
            await interaction.response.send_message("❌ O bot não conseguiu aplicar o cargo.",ephemeral=True); return

        prot=salvar_historico(
            guild_id,membro.id,"SETAGEM",interaction.user.id,
            anterior.name if anterior else "Sem cargo G.O.T",cargo.name,
            observacao=f"Nome RP: {nome} | ID RP: {id_rp} | Recrutador: {recrutador}")
        finalizar_pendente(self.pid,"APROVADA")

        e=img(embed_base("✅ SETAGEM APROVADA",
                         "Setagem aprovada e aplicada.",
                         discord.Color.green()),IMAGEM_SETAGEM)
        e.add_field(name="👤 NOME RP",value=f"`{nome}`",inline=True)
        e.add_field(name="🆔 ID RP",value=f"`{id_rp}`",inline=True)
        e.add_field(name="🎖️ CARGO",value=cargo.mention,inline=True)
        e.add_field(name="🤝 RECRUTADOR",value=recrutador,inline=True)
        e.add_field(name="✅ APROVADO POR",value=interaction.user.mention,inline=True)
        e.add_field(name="📋 PROTOCOLO",value=f"`{prot}`",inline=True)
        e.add_field(name="🏷️ NICKNAME",value=f"`{nickname_para(membro,cargo,nome,id_rp)}`",inline=False)
        e.set_thumbnail(url=membro.display_avatar.url)
        await enviar(interaction.guild,CANAL_SETAGEM_ID,e)
        await log(interaction.guild,e)

        for x in self.view.children: x.disabled=True
        await interaction.response.edit_message(embed=e,view=self.view)

class RecusarButton(Button):
    def __init__(self,pid):
        super().__init__(label="RECUSAR",emoji="❌",style=discord.ButtonStyle.danger,
                         custom_id=f"got:setagem:recusar:{pid}")
        self.pid=pid
    async def callback(self,interaction):
        if not isinstance(interaction.user,discord.Member): return

        # A recusa também fica restrita a Recrutador ou superior.
        if not pode_usar(interaction.user,"setagem"):
            await interaction.response.send_message(
                "❌ Apenas **Recrutador ou superior** pode recusar uma setagem.",
                ephemeral=True
            )
            return

        p=pegar_pendente(self.pid)
        if not p or p[9]!="PENDENTE":
            await interaction.response.send_message("⚠️ Esta solicitação já foi processada.",ephemeral=True); return
        await interaction.response.send_modal(RecusarModal(self.pid))

class RecusarModal(Modal,title="Recusar Setagem"):
    motivo=TextInput(label="Motivo",placeholder="Informe o motivo da recusa...",
                     style=discord.TextStyle.paragraph,required=True,max_length=1000)
    def __init__(self,pid): super().__init__(); self.pid=pid
    async def on_submit(self,interaction):
        p=pegar_pendente(self.pid)
        if not p or p[9]!="PENDENTE":
            await interaction.response.send_message("⚠️ Esta solicitação já foi processada.",ephemeral=True); return
        finalizar_pendente(self.pid,"RECUSADA")
        _,_,_,nome,id_rp,recrutador,*_=p
        e=img(embed_base("❌ SETAGEM RECUSADA","A solicitação foi recusada.",discord.Color.red()),IMAGEM_SETAGEM)
        e.add_field(name="👤 NOME RP",value=f"`{nome}`",inline=True)
        e.add_field(name="🆔 ID RP",value=f"`{id_rp}`",inline=True)
        e.add_field(name="🤝 RECRUTADOR",value=recrutador,inline=True)
        e.add_field(name="❌ RECUSADO POR",value=interaction.user.mention,inline=True)
        e.add_field(name="📋 MOTIVO",value=self.motivo.value,inline=False)
        await interaction.response.edit_message(embed=e,view=None)

# ========================= PAINEL DE SETAGEM =========================
class PainelAcaoView(View):
    """Painel de setagem. Qualquer pessoa pode abrir o formulário."""
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(IniciarSetagemButton())


class IniciarSetagemButton(Button):
    def __init__(self):
        super().__init__(
            label="INICIAR SET",
            emoji="🦉",
            style=discord.ButtonStyle.success,
            custom_id="got:comando:setagem"
        )

    async def callback(self, interaction):
        # TODOS podem solicitar setagem.
        await interaction.response.send_modal(SetagemModal())


class PainelFixoView(View):
    """Painel permanente: qualquer pessoa no canal pode iniciar a setagem."""
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(IniciarSetagemPublicoButton())


class IniciarSetagemPublicoButton(Button):
    def __init__(self):
        super().__init__(
            label="INICIAR SET",
            emoji="🦉",
            style=discord.ButtonStyle.success,
            custom_id="got:fixo:iniciar_setagem"
        )

    async def callback(self, interaction):
        # O painel é público e qualquer membro pode abrir o formulário.
        await interaction.response.send_modal(SetagemModal())


def criar_embed_painel_setagem():
    e = img(
        embed_base(
            "G.O.T DALLAS CITY • SETAGEM",
            "Preencha o formulário para solicitar sua setagem.",
            discord.Color.from_rgb(100, 85, 65)
        ),
        IMAGEM_SETAGEM
    )
    e.add_field(
        name="COMO FUNCIONA",
        value="Clique em **SETAGEM** e preencha Nome RP, ID da cidade e Recrutador.",
        inline=False
    )
    return e


async def enviar_painel_setagem(guild):
    canal = guild.get_channel(CANAL_SETAGEM_ID)
    if canal is None:
        try:
            canal = await guild.fetch_channel(CANAL_SETAGEM_ID)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException):
            return False

    if getattr(canal, "guild", None) and canal.guild.id != guild.id:
        return False

    try:
        mensagem = await canal.send(
            embed=criar_embed_painel_setagem(),
            view=PainelFixoView()
        )
        # Fixa a mensagem no canal para ficar sempre fácil de encontrar.
        try:
            await mensagem.pin(reason="Painel fixo de SETAGEM - G.O.T DALLAS CITY")
        except (discord.Forbidden, discord.HTTPException):
            # Se o bot não tiver permissão de fixar, o painel continua público e permanente.
            pass
        return True
    except (discord.Forbidden, discord.HTTPException):
        return False


@bot.tree.command(name="setagem", description="Abre o painel de setagem.")
async def setagem(interaction):
    # TODOS podem pedir SET.
    await interaction.response.send_message(
        embed=img(
            embed_base(
                "G.O.T DALLAS CITY • SETAGEM",
                "Clique em **INICIAR SET** para abrir o formulário."
            ),
            IMAGEM_SETAGEM
        ),
        view=PainelAcaoView(),
        ephemeral=True
    )


@bot.tree.command(
    name="instalar_setagem",
    description="Instala o painel fixo de setagem."
)
async def instalar_setagem(interaction):
    # Apenas Recrutador ou superior pode instalar o painel.
    if not pode_aprovar_setagem(interaction.user):
        await interaction.response.send_message(
            "❌ Apenas Recrutador ou superior pode instalar o painel.",
            ephemeral=True
        )
        return

    await interaction.response.defer(ephemeral=True)

    ok = await enviar_painel_setagem(interaction.guild)

    if ok:
        await interaction.followup.send(
            "✅ Painel de **SETAGEM** instalado com sucesso.",
            ephemeral=True
        )
    else:
        await interaction.followup.send(
            "❌ Não consegui enviar o painel para o canal configurado.",
            ephemeral=True
        )


@bot.tree.command(
    name="painel_setagem",
    description="Instala o painel de setagem no canal configurado."
)
async def painel_setagem(interaction):
    await instalar_setagem.callback(interaction)


@bot.event
async def on_ready():
    iniciar_banco()

    # Restaura o painel fixo de SETAGEM após reinícios.
    try:
        bot.add_view(PainelFixoView())
    except Exception as e:
        print("[GOT] erro ao restaurar painel de setagem:", e)

    # Restaura os botões de aprovações pendentes.
    for guild in bot.guilds:
        for pid in pendentes_guild(guild.id):
            try:
                bot.add_view(AprovacaoSetagemView(pid))
            except Exception as e:
                print("[GOT] erro ao restaurar aprovação:", e)

    try:
        synced = await bot.tree.sync()
        print(f"[GOT] {len(synced)} comandos sincronizados.")
    except Exception as e:
        print("[GOT] erro sync:", e)

    print(f"[GOT] Online como {bot.user}.")


@bot.tree.error
async def erro_comando(interaction,error):
    print("[GOT ERROR]",repr(error))
    try:
        if interaction.response.is_done():
            await interaction.followup.send("❌ Ocorreu um erro.",ephemeral=True)
        else:
            await interaction.response.send_message("❌ Ocorreu um erro.",ephemeral=True)
    except Exception: pass

if __name__=="__main__":
    iniciar_banco()
    if not TOKEN:
        raise RuntimeError("A variável DISCORD_TOKEN não foi configurada.")
    bot.run(TOKEN)
