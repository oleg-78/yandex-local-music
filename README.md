[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.6+-blue.svg)](https://www.home-assistant.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Version](https://img.shields.io/github/v/release/YOUR_GITHUB/yandex-local-music)


# 🎵 Yandex Local Music (NAS)

Custom Home Assistant integration for **silent playback of local or NAS music**
on **Yandex Station** devices.

> Designed for users who want background music (birds, rain, ambient sounds, playlists)
> without Alice voice prompts like “Включаю”.

---

## ✨ Key Features

- 🎵 Play music from **local folders or NAS**
- 🔇 **Silent playback** (no voice response from Alice)
- 🔀 Random track selection
- 🧠 Track history (avoid immediate repeats)
- 📂 **Recursive folder scanning**
- 🔊 Support for **multiple Yandex Stations**
- 🎯 Target specific speaker per call
- 🎚 Optional volume preset before playback
- 🧩 Native **Config Flow UI**
- 🖼 Custom SVG icon
- 🏠 Fully local, no cloud dependency

---

## 🧠 Why this integration?

Standard Yandex Station commands like:
“Включи плейлист…”
always trigger voice feedback from Alice.

This integration:
- plays audio **directly** via Home Assistant
- uses `media-source://`
- starts playback **instantly and silently**

Perfect for:
- 🚿 bathroom automations
- 🌙 night ambient sounds
- 🌲 nature / birds background
- 🏠 smart home scenes

---

## 📦 Installation (HACS)

### 1️⃣ Add custom repository

1. Open **HACS → Integrations**
2. Click **⋮ → Custom repositories**
3. Add: https://github.com/oleg-78/yandex-local-music

4. Category: **Integration**

### 2️⃣ Install integration

- Find **Yandex Local Music (NAS)**
- Click **Download**
- Restart Home Assistant

---

## ⚙️ Configuration

After restart:

1. **Settings → Devices & Services**
2. **Add Integration**
3. Select **Yandex Local Music (NAS)**

### Required fields:

| Field | Description |
|-----|------------|
| **Yandex Station** | media_player entity |
| **Media folder** | `media-source://media_source/...` |
| **History length** | How many tracks to remember |

Example folder: media-source://media_source/media/nas/nas/Music/Birds

---

## ▶️ Available Services

### ▶️ Play random track

Plays a random track from configured folder.

```yaml
service: yandex_local_music.play_random
data:
  target_player: media_player.yandex_station_bathroom
  volume_level: 0.25

Fields:
	•	target_player (optional) — specific Yandex Station
	•	volume_level (optional) — 0.0 … 1.0

🔄 Rebuild index

Force re-scan of media folder.
service: yandex_local_music.rebuild_index
Useful after adding new files.

🤖 Example Automations

🚿 Bathroom: play birds when motion detected

alias: Bathroom Birds
trigger:
  - platform: state
    entity_id: binary_sensor.shower_presence
    to: "on"
condition:
  - condition: time
    after: "06:00:00"
    before: "23:00:00"
action:
  - service: yandex_local_music.play_random
    data:
      target_player: media_player.yandex_station_bathroom
      volume_level: 0.3

🌙 Night ambient sounds

alias: Night Ambient
trigger:
  - platform: time
    at: "23:30:00"
action:
  - service: yandex_local_music.play_random
    data:
      target_player: media_player.yandex_station_bedroom
      volume_level: 0.15

🖼 Icon

Custom SVG icon included in integration.
Optimized for Home Assistant UI and HACS.

🔧 Troubleshooting

❌ Integration not visible in HACS
	•	Check hacs.json exists in repo root
	•	Ensure custom_components/ structure is correct

❌ No tracks found
	•	Check Media Source path
	•	Run rebuild_index
	•	Ensure files are supported audio formats

❌ Alice still speaks
	•	Make sure you are using play_random
	•	Do not use media_player.play_media with command


⸻

📚 Supported formats
	•	MP3
	•	AAC
	•	M4A
	•	OGG / OPUS
	•	WAV

⸻

🧩 Compatibility
	•	Home Assistant 2024.6+
	•	Yandex Station via yandex_station integration
	•	Local Media Source / NAS

⸻

🧑‍💻 Author

Created with ❤️ for Home Assistant
Author: OLEG RESHETNIKOV

