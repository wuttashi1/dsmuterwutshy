"""
Интерактивное меню (View) с кнопками Mute All / Unmute All.
Кнопки применяют серверный mute и deafen ко всем участникам указанного голосового канала.
"""

from __future__ import annotations

import logging

import discord
from discord import ui

logger = logging.getLogger(__name__)


class VoiceControlView(ui.View):
    """
    View с двумя кнопками для массового mute/deafen в голосовом канале.

    При создании сохраняется id канала из момента вызова /voicecontrol,
    чтобы действия всегда относились к тому же каналу.
    """

    def __init__(self, voice_channel: discord.VoiceChannel) -> None:
        # timeout=None — кнопки остаются активными, пока работает бот (пока сообщение существует)
        super().__init__(timeout=None)
        self.voice_channel_id: int = voice_channel.id
        self.guild_id: int = voice_channel.guild.id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Ограничение доступа: только пользователи с правом Administrator
        могут нажимать кнопки.
        """
        user = interaction.user
        if not isinstance(user, discord.Member):
            await interaction.response.send_message(
                "Это действие доступно только на сервере.",
                ephemeral=True,
            )
            return False
        if not user.guild_permissions.administrator:
            await interaction.response.send_message(
                "Только **администраторы** могут использовать эти кнопки.",
                ephemeral=True,
            )
            return False
        return True

    @ui.button(label="Mute All", style=discord.ButtonStyle.danger, emoji="🔇", row=0)
    async def mute_all(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        """Заглушить всех: mute=True, deafen=True."""
        await self._apply_voice_state(interaction, mute=True, deafen=True)

    @ui.button(label="Unmute All", style=discord.ButtonStyle.success, emoji="🔊", row=0)
    async def unmute_all(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        """Снять заглушение: mute=False, deafen=False."""
        await self._apply_voice_state(interaction, mute=False, deafen=False)

    async def _apply_voice_state(
        self,
        interaction: discord.Interaction,
        *,
        mute: bool,
        deafen: bool,
    ) -> None:
        """Обходит участников канала и вызывает member.edit(mute=..., deafen=...)."""
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "Не удалось определить сервер.",
                ephemeral=True,
            )
            return

        raw = guild.get_channel(self.voice_channel_id)
        if raw is None or not isinstance(raw, discord.VoiceChannel):
            await interaction.response.send_message(
                "Голосовой канал не найден или был удалён.",
                ephemeral=True,
            )
            return

        channel: discord.VoiceChannel = raw

        # Для нескольких участников отвечаем через defer, чтобы не превысить лимит времени interaction
        await interaction.response.defer(ephemeral=True)

        action_label = "mute_all" if mute else "unmute_all"
        human = "заглушены" if mute else "размьючены"
        failed: list[str] = []

        for member in channel.members:
            if member.bot:
                continue
            try:
                await member.edit(
                    mute=mute,
                    deafen=deafen,
                    reason=f"Voice control ({action_label}) — {interaction.user}",
                )
            except discord.Forbidden:
                failed.append(member.display_name)
                logger.warning(
                    "Нет прав изменить состояние голоса для %s в канале %s",
                    member,
                    channel.name,
                )
            except discord.HTTPException as exc:
                failed.append(member.display_name)
                logger.warning("HTTP-ошибка при edit для %s: %s", member, exc)

        logger.info(
            "VoiceControl [%s]: админ=%s (%s) | канал=%s (%s) | неудач=%s",
            action_label,
            interaction.user,
            interaction.user.id,
            channel.name,
            channel.id,
            len(failed),
        )

        if failed:
            preview = ", ".join(failed[:10])
            suffix = " …" if len(failed) > 10 else ""
            await interaction.followup.send(
                f"Канал **{channel.name}**: часть участников обработана.\n"
                f"Не удалось применить: **{preview}**{suffix}",
                ephemeral=True,
            )
        else:
            await interaction.followup.send(
                f"Канал **{channel.name}**: все участники **{human}** "
                "(микрофон и звук).",
                ephemeral=True,
            )
