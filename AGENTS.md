# Codex project notes

- This project only maintains the main Windows desktop pet executable.
- Do not rebuild, update, package, stage, or push installer artifacts such as `dist/lulu在摸鱼_Setup.exe`, `LuluSetup.spec`, or `installer/payload/*` unless the user explicitly asks for installer work.
- Do not rebuild, update, stage, or push 32-bit artifacts such as `dist/lulu在摸鱼_x86.exe` unless the user explicitly asks for a 32-bit build.
- For normal Windows packaging, build only `dist/lulu在摸鱼.exe` from `PiggyDesktopPet.spec`.
