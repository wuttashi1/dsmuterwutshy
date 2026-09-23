<div align="center">

# Wutshy Voice Control

Discord voice-channel control panel with administrator-only Mute All and Unmute All actions.

[Contributing](CONTRIBUTING.md) · [Branches](https://github.com/wuttashi1/dsmuterwutshy/branches)

</div>

---

## Features

- `/voicecontrol` slash command.
- **Mute All** and **Unmute All** buttons for the current voice channel.
- Administrator permission checks before controlling members.

## Quick start

Create and activate a Python virtual environment, then:

```bash
python -m pip install -r requirements.txt
python main.py
```

Before starting, create a local `.env` with `DISCORD_TOKEN`. Enable Server Members Intent in the Discord Developer Portal. Invite the bot with application command access and permission to mute members.

## Project layout

- `main.py` — startup and slash command registration.
- `voice_control_view.py` — panel buttons and action handlers.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch and contribution guidelines.
