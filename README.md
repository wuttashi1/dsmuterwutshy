<div align="center">

# Wutshy Voice Control

Discord-бот с панелью управления голосовым каналом: массовое отключение и включение микрофонов для администраторов.

[Правила разработки](CONTRIBUTING.md) · [Ветки](https://github.com/wuttashi1/dsmuterwutshy/branches)

</div>

---

## Возможности

- Slash-команда `/voicecontrol`.
- Кнопки **Mute All** и **Unmute All** для текущего голосового канала.
- Проверка прав администратора перед управлением участниками.

## Запуск

```bash
python -m venv .venv
# Активируйте .venv для вашей оболочки
python -m pip install -r requirements.txt
python main.py
```

Перед запуском создайте локальный `.env` с `DISCORD_TOKEN`. В Discord Developer Portal включите Server Members Intent; при добавлении бота предоставьте доступ к slash-командам и право отключать микрофоны участников.

## Навигация

- `main.py` — запуск и регистрация `/voicecontrol`.
- `voice_control_view.py` — кнопки и обработчики панели.

## Разработка

Соглашения по веткам и изменениям: [CONTRIBUTING.md](CONTRIBUTING.md).
