import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

PREFIXES = ["[관전]", "[대기]", "[막판]"]


def clean_nickname(name: str) -> str:
    for prefix in PREFIXES:
        name = name.replace(prefix, "")
    return name.strip()


class NicknameView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def change_nick(self, interaction: discord.Interaction, prefix: str | None):
        member = interaction.user
        current_name = member.nick or member.name
        base_name = clean_nickname(current_name)

        if prefix is None:
            new_name = base_name
            msg = f"닉네임을 원래대로 복귀했습니다: `{new_name}`"
        else:
            new_name = f"{prefix} {base_name}"
            msg = f"닉네임을 변경했습니다: `{new_name}`"

        try:
            await member.edit(nick=new_name)
            await interaction.response.send_message(msg, ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(
                "봇에게 닉네임 변경 권한이 없거나, 봇 역할이 대상 멤버보다 아래에 있습니다.",
                ephemeral=True
            )

    @discord.ui.button(label="관전 적용", style=discord.ButtonStyle.primary, custom_id="nick_watch")
    async def watch(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_nick(interaction, "[관전]")

    @discord.ui.button(label="대기 적용", style=discord.ButtonStyle.primary, custom_id="nick_wait")
    async def wait(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_nick(interaction, "[대기]")

    @discord.ui.button(label="막판 적용", style=discord.ButtonStyle.primary, custom_id="nick_last")
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_nick(interaction, "[막판]")

    @discord.ui.button(label="원래대로", style=discord.ButtonStyle.secondary, custom_id="nick_reset")
    async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.change_nick(interaction, None)


@bot.event
async def on_ready():
    bot.add_view(NicknameView())
    await bot.tree.sync()
    print(f"{bot.user} 로그인 완료")


@bot.tree.command(name="닉네임패널", description="관전/대기/막판 닉네임 변경 패널을 생성합니다.")
async def nickname_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏷️ 관전 대기 막판",
        description=(
            "아래 버튼을 클릭하면 닉네임 앞에 상태가 표시됩니다.\n\n"
            "✅ 관전 적용 → `[관전] 닉네임`\n"
            "👍 대기 적용 → `[대기] 닉네임`\n"
            "👀 막판 적용 → `[막판] 닉네임`\n"
            "↩️ 원래대로 → 상태 표시 제거"
        ),
        color=0x7B61FF
    )

    await interaction.response.send_message(embed=embed, view=NicknameView())


if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN 환경변수가 없습니다.")

bot.run(TOKEN)