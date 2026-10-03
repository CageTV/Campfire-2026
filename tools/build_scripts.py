"""Compile Campfire's scripts with the official Papyrus compiler.

  python tools/build_scripts.py esl      compile the scripts esl_build.py rewrote (esl-work/scripts) -> esl-work/pex
  python tools/build_scripts.py          compile all of src/scripts -> build/scripts

Import order: the scripts being built first, then the rest of src/scripts, then SDK/framework sources, then vanilla.
One compiler run per script (the compiler's -all mode hung on this kind of source set); a per-file timeout names any hang.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = r"E:\Tabula Rasa\Stock Game"
MODS = r"E:\Tabula Rasa\mods"
FF = r"E:\WorkSpace\Frostfall-Modernized\imports"      # SkyUI SDK, CheskoPapyrusShared, compile-only stubs

mode = sys.argv[1] if len(sys.argv) > 1 else "all"
src_dir = os.path.join(HERE, "esl-work", "scripts") if mode == "esl" else os.path.join(HERE, "src", "scripts")
out = os.path.join(HERE, "esl-work", "pex") if mode == "esl" else os.path.join(HERE, "build", "scripts")
COMPILER = os.path.join(GAME, "Papyrus Compiler", "PapyrusCompiler.exe")
FLAGS = os.path.join(GAME, "Data", "Source", "Scripts", "TESV_Papyrus_Flags.flg")
IMPORTS = [
    src_dir,
    os.path.join(HERE, "src", "scripts"),
    os.path.join(os.path.dirname(FF), "upstream-chesko", "Scripts", "Source"),   # Frostfall's FrostUtil etc. (Campfire references them softly)
    os.path.join(FF, "skyui"),
    os.path.join(FF, "chesko-shared"),
    os.path.join(FF, "stubs"),
    os.path.join(MODS, "Skyrim Script Extender (SKSE64)", "Scripts", "Source"),
    os.path.join(MODS, "PapyrusUtil SE - Modders Scripting Utility Functions", "Scripts", "Source"),
    os.path.join(MODS, "powerofthree's Papyrus Extender", "Source", "scripts"),
    os.path.join(MODS, "FileAccess Interface for Skyrim SE Scripts - FISSES", "scripts", "source"),
    os.path.join(GAME, "Data", "Source", "Scripts"),
]
for p in [COMPILER, FLAGS, src_dir] + IMPORTS:
    if not os.path.exists(p):
        raise SystemExit(f"missing: {p}")
os.makedirs(out, exist_ok=True)
os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
log, rc = "", 0
names = sorted(n for n in os.listdir(src_dir) if n.lower().endswith(".psc"))
for name in names:
    cmd = [COMPILER, name, f"-f={FLAGS}", "-i=" + ";".join(IMPORTS), f"-o={out}"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=src_dir, timeout=120)
        log += (r.stdout or "") + (r.stderr or "")
        rc = rc or r.returncode
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/F", "/IM", "PapyrusCompiler.exe"], capture_output=True)
        log += f"{name}: compilation failed (compiler hang, killed after 120 s)\n"
        rc = 1
with open(os.path.join(HERE, "build", f"compile-{mode}.log"), "w", encoding="utf-8") as f:
    f.write(log)
pexs = [n for n in os.listdir(out) if n.lower().endswith(".pex")]
errors = [l for l in log.splitlines() if ".psc(" in l or "compilation failed" in l.lower()]
print(f"compiler exit {rc}: {len(pexs)} .pex from {len(names)} .psc; {len(errors)} error lines (log: build/compile-{mode}.log)")
for l in errors[:25]:
    print("  " + l)
sys.exit(0 if rc == 0 and not errors else 1)
