"""
Точка входа Discord-бота: slash-команда /voicecontrol и регистрация intents.
"""

from __future__ import annotations

import logging
import os
import traceback

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from voice_control_view import VoiceControlView

# Загружаем переменные из .env (DISCORD_TOKEN)
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Intents: members и voice_states обязательны для member.voice и списка участников канала
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True


class VoiceControlBot(commands.Bot):
    """Бот с префиксом (не используется для slash) и синхронизацией дерева команд."""

    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self) -> None:
        """Синхронизация глобальных slash-команд при старте."""
        await self.tree.sync()
        logger.info("Синхронизация slash-команд завершена.")


bot = VoiceControlBot()


@bot.tree.command(
    name="voicecontrol",
    description="Панель управления голосом в вашем текущем голосовом канале",
)
async def voicecontrol(interaction: discord.Interaction) -> None:
    """
    Показывает embed с кнопками Mute All / Unmute All для канала,
    в котором сейчас находится вызвавший пользователь.
    """
    # Только на сервере (не в ЛС)
    if interaction.guild is None:
        await interaction.response.send_message(
            "Команда доступна только на сервере.",
            ephemeral=True,
        )
        return

    member = interaction.user
    if not isinstance(member, discord.Member):
        await interaction.response.send_message(
            "Не удалось определить участника сервера.",
            ephemeral=True,
        )
        return

    # Только администраторы Discord (флаг Administrator)
    if not member.guild_permissions.administrator:
        await interaction.response.send_message(
            "Использовать `/voicecontrol` могут только пользователи с правом **Администратор**.",
            ephemeral=True,
        )
        return

    # Голосовое состояние: пользователь должен быть в голосовом канале
    voice = member.voice
    if voice is None or voice.channel is None:
        await interaction.response.send_message(
            "Вы **не в голосовом канале**. Зайдите в канал и выполните команду снова.",
            ephemeral=True,
        )
        return

    channel = voice.channel
    if not isinstance(channel, discord.VoiceChannel):
        await interaction.response.send_message(
            "Текущий канал не является обычным голосовым (например, сцена). "
            "Используйте обычный voice-канал.",
            ephemeral=True,
        )
        return

    embed = discord.Embed(
        title="Управление голосовым каналом",
        description=(
            f"**Канал:** {channel.mention}\n\n"
            "Ниже кнопки применяются ко **всем** участникам этого канала "
            "(кроме ботов).\n\n"
            "🔇 **Mute All** — серверный mute и deafen\n"
            "🔊 **Unmute All** — снять mute и deafen"
        ),
        color=discord.Color.dark_teal(),
    )
    embed.add_field(
        name="Права",
        value="Команда и кнопки доступны только **администраторам** сервера.",
        inline=False,
    )
    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)
    embed.set_footer(text="DS Voice Control")
    embed.timestamp = discord.utils.utcnow()

    view = VoiceControlView(channel)

    logger.info(
        "/voicecontrol: пользователь=%s (%s) | канал=%s (%s) | гильдия=%s",
        member,
        member.id,
        channel.name,
        channel.id,
        interaction.guild.id,
    )

    await interaction.response.send_message(embed=embed, view=view)


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
) -> None:
    """Логирование и ответ пользователю при ошибках slash-команд."""
    logger.error(
        "Ошибка slash-команды: %s",
        error,
        exc_info=(type(error), error, error.__traceback__),
    )
    if isinstance(error, app_commands.CommandInvokeError) and error.original:
        logger.error(
            "Первопричина: %s",
            error.original,
            exc_info=(type(error.original), error.original, error.original.__traceback__),
        )

    msg = "Произошла ошибка при выполнении команды. Попробуйте позже."
    if interaction.response.is_done():
        await interaction.followup.send(msg, ephemeral=True)
    else:
        await interaction.response.send_message(msg, ephemeral=True)


@bot.event
async def on_error(event_method: str, /, *args, **kwargs) -> None:
    """Логирование необработанных исключений в событиях."""
    logger.exception("Ошибка в событии %s", event_method)


@bot.event
async def on_ready() -> None:
    """Сообщение в консоль при готовности бота."""
    if bot.user:
        logger.info("Бот в сети: %s (id=%s)", bot.user, bot.user.id)
    else:
        logger.info("Бот в сети (user ещё не загружен)")


def main() -> None:
    token = os.getenv("DISCORD_TOKEN", "").strip()
    if not token:
        logger.error("В файле .env не задана переменная DISCORD_TOKEN.")
        raise SystemExit(1)

    try:
        bot.run(token, log_handler=None)
    except discord.LoginFailure:
        logger.error("Неверный токен. Проверьте DISCORD_TOKEN в .env.")
        raise SystemExit(1) from None
    except Exception:
        logger.error("Не удалось запустить бота:\n%s", traceback.format_exc())
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
