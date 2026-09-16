import os
import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput, UserSelect

TOKEN = os.getenv("DISCORD_TOKEN")
CANAL_SETAGEM_ID = 1549563326986588270
RECRUTADOR_GOT_ID = 1549567128049418250

CARGOS_SETAGEM = {
    "OPERADOR": 1549566691393142816,
    "EXECUTOR": 1549566650590953583,
    "ESPECIALISTA": 1549566611877400636,
    "RECRUTADOR": 1549567128049418250,
    "COORDENADOR": 1549566873417285703,
    "SUPERVISOR": 1549566529018789970,
    "SUB COMANDO": 1549566380259414117,
    "COMANDO": 1549566308922826902,
}

HIERARQUIA = list(CARGOS_SETAGEM.values())

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

def pode_usar_setagem(member):
    cargo = member.guild.get_role(RECRUTADOR_GOT_ID)
    return cargo is not None and cargo in member.roles

def embed_base(titulo, descricao, cor=discord.Color.blue()):
    return discord.Embed(title=titulo, description=descricao, color=cor)

class SetagemModal(Modal):
    def __init__(self, alvo, cargo):
        super().__init__(title="📋 Setagem — G.O.T Dallas")
        self.alvo, self.cargo = alvo, cargo
        self.motivo = TextInput(label="Motivo da setagem", placeholder="Digite o motivo...", style=discord.TextStyle.paragraph, required=True, max_length=1000)
        self.observacao = TextInput(label="Observação", placeholder="Opcional...", style=discord.TextStyle.paragraph, required=False, max_length=1000)
        self.add_item(self.motivo)
        self.add_item(self.observacao)

    async def on_submit(self, interaction):
        if not pode_usar_setagem(interaction.user):
            return await interaction.response.send_message("❌ Você não possui permissão para realizar setagens.", ephemeral=True)
        bot_member = interaction.guild.me
        if bot_member is None or self.cargo >= bot_member.top_role:
            return await interaction.response.send_message("❌ O cargo do bot precisa estar acima do cargo que será colocado.", ephemeral=True)

        antigos = [r for r in self.alvo.roles if r.id in HIERARQUIA and r < bot_member.top_role]
        try:
            await self.alvo.add_roles(self.cargo, reason=f"Setagem por {interaction.user}")
            if antigos:
                await self.alvo.remove_roles(*antigos, reason=f"Atualização por {interaction.user}")
        except discord.Forbidden:
            return await interaction.response.send_message("❌ Não tenho permissão para alterar os cargos. Verifique **Gerenciar Cargos** e a hierarquia.", ephemeral=True)
        except discord.HTTPException:
            return await interaction.response.send_message("❌ O Discord recusou a alteração.", ephemeral=True)

        embed = embed_base("🟢 SETAGEM REALIZADA",
            f"👤 **Membro:** {self.alvo.mention}\n"
            f"🎖️ **Cargo:** {self.cargo.mention}\n"
            f"👮 **Responsável:** {interaction.user.mention}\n\n"
            f"📝 **Motivo:**\n{self.motivo.value}\n\n"
            f"📌 **Observação:**\n{self.observacao.value or 'Nenhuma'}",
            discord.Color.green())
        canal = interaction.guild.get_channel(CANAL_SETAGEM_ID)
        if canal:
            await canal.send(embed=embed)
        await interaction.response.send_message("✅ **Setagem realizada com sucesso!**", ephemeral=True)

class CargoSetagemSelect(Select):
    def __init__(self, alvo):
        self.alvo = alvo
        super().__init__(
            placeholder="🎖️ Selecione o cargo...",
            min_values=1, max_values=1,
            options=[discord.SelectOption(label=n, value=str(i), description=f"Setar {n}") for n, i in CARGOS_SETAGEM.items()]
        )

    async def callback(self, interaction):
        if not pode_usar_setagem(interaction.user):
            return await interaction.response.send_message("❌ Você não possui permissão.", ephemeral=True)
        cargo = interaction.guild.get_role(int(self.values[0]))
        if cargo is None:
            return await interaction.response.send_message("❌ Cargo não encontrado.", ephemeral=True)
        await interaction.response.send_modal(SetagemModal(self.alvo, cargo))

class CargoSetagemView(View):
    def __init__(self, alvo):
        super().__init__(timeout=120)
        self.add_item(CargoSetagemSelect(alvo))

class MembroSetagemSelect(UserSelect):
    def __init__(self):
        super().__init__(placeholder="👤 Selecione o membro...", min_values=1, max_values=1)

    async def callback(self, interaction):
        if not pode_usar_setagem(interaction.user):
            return await interaction.response.send_message("❌ Você não possui permissão.", ephemeral=True)
        membro = self.values[0]
        await interaction.response.send_message(
            embed=embed_base("🎖️ ESCOLHA O CARGO", f"👤 **Membro:** {membro.mention}\n\nSelecione o cargo.", discord.Color.blue()),
            view=CargoSetagemView(membro), ephemeral=True)

class MembroSetagemView(View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(MembroSetagemSelect())

@bot.tree.command(name="setagem", description="Realiza a setagem de um membro.")
async def setagem(interaction):
    if not pode_usar_setagem(interaction.user):
        return await interaction.response.send_message("❌ Você não possui permissão para usar a setagem.", ephemeral=True)
    await interaction.response.send_message(
        embed=embed_base("🎖️ SETAGEM — G.O.T DALLAS CITY", "Selecione abaixo o membro que receberá a setagem.", discord.Color.blue()),
        view=MembroSetagemView(), ephemeral=True)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Bot online: {bot.user} | {len(synced)} comando(s) sincronizado(s)")
    except Exception as e:
        print(f"❌ Erro ao sincronizar: {e}")

if not TOKEN:
    raise RuntimeError("Configure a variável DISCORD_TOKEN antes de iniciar o bot.")

bot.run(TOKEN)
