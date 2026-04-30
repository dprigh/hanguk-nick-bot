import re
import discord
from discord.ext import commands
from discord import app_commands

TOKEN = "여기에_봇_토큰"

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

STATUS_TAGS = ["[관전]", "[대기]", "[막판]"]

STATUS_PATTERN = re.compile(r"\s*(\[관전\]|\[대기\]|\[막판\])\s*")

# 서버 레벨 표시 형식에 맞게 필요하면 여기만 수정
LEVEL_PATTERN = re.compile(
    r"^(\[?\s*(?:Lv\.?|LV\.?|레벨|Level)?\s*\d+\s*\]?|Lv\.?\s*\d+)\s*",
    re.IGNORECASE
)


def remove_status_tags(name: str) -> str:
    name = STATUS_PATTERN.sub(" ", name)
    return " ".join(name.split())


def apply_status_tag(name: str, status_tag: str | None) -> str:
    clean_name = remove_status_tags(name)

    if status_tag is None:
        return clean_name

    level_match = LEVEL_PATTERN.match(clean_name)

    if level_match:
        level_text = level_match.group(0).strip()
        rest_name = clean_name[level_match.end():].strip()
        return f"{level_text} {status_tag} {rest_name}".strip()

    return f"{status_tag} {clean_name}".strip()


class NicknameView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def set_status(self, interaction: discord.Interaction, status_tag: str | None):
        member = interaction.user
        current_name = member.nick or member.name
        new_name = apply_status_tag(current_name, status_tag)

        if current_name == new_name:
            await interaction.response.send_message(
                "이미 적용된 상태입니다.",
                ephemeral=True
            )
            return

        try:
            await member.edit(nick=new_name, reason="상태 닉네임 버튼 변경")

            if status_tag is None:
                msg = f"닉네임을 원래대로 복구했습니다.\n`{new_name}`"
            else:
                msg = f"상태를 적용했습니다.\n`{new_name}`"

            await interaction.response.send_message(msg, ephemeral=True)

        except discord.Forbidden:
            await interaction.response.send_message(
                "닉네임 변경 권한이 없습니다.\n봇 역할이 대상 멤버 역할보다 위에 있는지 확인해 주세요.",
                ephemeral=True
            )

        except discord.HTTPException:
            await interaction.response.send_message(
                "닉네임 변경 중 오류가 발생했습니다.\n닉네임 길이 또는 권한을 확인해 주세요.",
                ephemeral=True
            )

    @discord.ui.button(label="관전 적용", style=discord.ButtonStyle.primary, custom_id="status_watch")
    async def watch(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_status(interaction, "[관전]")

    @discord.ui.button(label="대기 적용", style=discord.ButtonStyle.primary, custom_id="status_wait")
    async def wait(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_status(interaction, "[대기]")

    @discord.ui.button(label="막판 적용", style=discord.ButtonStyle.primary, custom_id="status_last")
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_status(interaction, "[막판]")

    @discord.ui.button(label="원래대로", style=discord.ButtonStyle.secondary, custom_id="status_reset")
    async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.set_status(interaction, None)


@bot.event
async def on_ready():
    bot.add_view(NicknameView())

    try:
        synced = await bot.tree.sync()
        print(f"슬래시 명령어 동기화 완료: {len(synced)}개")
    except Exception as e:
        print(f"명령어 동기화 실패: {e}")

    print(f"{bot.user} 로그인 완료")


@bot.tree.command(name="상태버튼", description="관전, 대기, 막판 닉네임 변경 버튼을 생성합니다.")
@app_commands.checks.has_permissions(manage_nicknames=True)
async def status_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏷️ 관전 · 대기 · 막판 상태 변경",
        description=(
            "아래 버튼을 누르면 닉네임에 상태가 적용됩니다.\n\n"
            "예시\n"
            "`Lv.12 구사장` → `Lv.12 [관전] 구사장`\n"
            "`Lv.13 [관전] 구사장` → `Lv.13 [대기] 구사장`\n"
            "`Lv.13 [대기] 구사장` → `Lv.13 구사장`\n\n"
            "레벨 숫자는 유지되고 상태만 변경됩니다."
        ),
        color=0x7B61FF
    )

    await interaction.response.send_message(embed=embed, view=NicknameView())


bot.run(TOKEN)