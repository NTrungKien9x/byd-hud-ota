import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ARDUINO_CLI = r"C:\Program Files\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe"
SKETCH_V1 = r"C:\Users\NTK's\Documents\Arduino\HUD_BYD_Dolphin"
SKETCH_V2 = r"C:\Users\NTK's\Documents\Arduino\HUD_BYD_Dolphin_V2"
BOOT_APP0 = r"C:\Users\NTK's\AppData\Local\Arduino15\packages\esp32\hardware\esp32\3.2.0\tools\partitions\boot_app0.bin"
FQBN = "esp32:esp32:esp32s3:FlashSize=16M,PartitionScheme=app3M_fat9M_16MB,PSRAM=opi"
WEB_DIR = os.path.dirname(os.path.abspath(__file__))
FW_DIR = os.path.join(WEB_DIR, "firmware")

def sync_v1_to_v2():
    os.makedirs(SKETCH_V2, exist_ok=True)
    headers = [f for f in os.listdir(SKETCH_V1) if f.endswith(".h")]
    for h in headers:
        shutil.copy2(os.path.join(SKETCH_V1, h), os.path.join(SKETCH_V2, h))
    with open(os.path.join(SKETCH_V1, "HUD_BYD_Dolphin.ino"), "r", encoding="utf-8") as f:
        src = f.read()
    src_v2 = re.sub(r"(#define\s+LCD_DRIVER_DEFAULT\s+)0\b", r"\g<1>1", src, count=1)
    assert "#define LCD_DRIVER_DEFAULT     1" in src_v2 or re.search(r"#define\s+LCD_DRIVER_DEFAULT\s+1\b", src_v2)
    with open(os.path.join(SKETCH_V2, "HUD_BYD_Dolphin_V2.ino"), "w", encoding="utf-8") as f:
        f.write(src_v2)
    m = re.search(r'#define\s+BLE_HUD_FW_STR\s+"([^"]+)"', src)
    ver = m.group(1) if m else "2.60"
    print(f"[1/4] Synced V1 -> V2 ({len(headers)} headers, fw=v{ver})")
    return ver

def compile_variant(sketch_dir, out_bin_name, copy_boot_parts=False):
    ino_base = os.path.basename(sketch_dir)
    build_dir = os.path.join(tempfile.gettempdir(), f"byd_build_{ino_base}")
    os.makedirs(build_dir, exist_ok=True)
    env = os.environ.copy()
    env["GOMAXPROCS"] = "1"
    env["GOGC"] = "25"
    env["GOMEMLIMIT"] = "160MiB"
    with tempfile.TemporaryDirectory() as td:
        cmd = [
            ARDUINO_CLI, "compile",
            "--fqbn", FQBN,
            "--jobs", "1",
            "--build-path", build_dir,
            "--output-dir", td,
            sketch_dir,
        ]
        r = None
        for attempt in range(1, 4):
            print(f"      Compiling {ino_base} (attempt {attempt}/3)...")
            r = subprocess.run(cmd, capture_output=True, text=True, env=env)
            if r.returncode == 0:
                break
            err_txt = (r.stdout or "") + "\n" + (r.stderr or "")
            if ".ino:" in err_txt or "hud_" in err_txt:
                break
        if r.returncode != 0:
            print(r.stdout)
            print(r.stderr)
            sys.exit(r.returncode)
        app_bin = os.path.join(td, f"{ino_base}.ino.bin")
        shutil.copy2(app_bin, os.path.join(FW_DIR, out_bin_name))
        if copy_boot_parts:
            shutil.copy2(os.path.join(td, f"{ino_base}.ino.bootloader.bin"), os.path.join(FW_DIR, "bootloader.bin"))
            shutil.copy2(os.path.join(td, f"{ino_base}.ino.partitions.bin"), os.path.join(FW_DIR, "partitions.bin"))
            shutil.copy2(BOOT_APP0, os.path.join(FW_DIR, "boot_app0.bin"))
        sz = os.path.getsize(os.path.join(FW_DIR, out_bin_name))
        sha = hashlib.sha256(open(os.path.join(FW_DIR, out_bin_name), "rb").read()).hexdigest()[:12]
        print(f"      OK: firmware/{out_bin_name} ({sz:,} bytes, sha256={sha}...)")

def update_json_version(ver):
    for fn in ("version.json", "manifest_v1.json", "manifest_v2.json"):
        p = os.path.join(WEB_DIR, fn)
        if os.path.exists(p):
            obj = json.load(open(p, "r", encoding="utf-8"))
            obj["version"] = ver
            with open(p, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=2)
                f.write("\n")

if __name__ == "__main__":
    os.makedirs(FW_DIR, exist_ok=True)
    ver = sync_v1_to_v2()
    print("[2/4] Building V1 (SKU 10120005 / 2509)...")
    compile_variant(SKETCH_V1, "byd_hud_v1.bin", copy_boot_parts=True)
    print("[3/4] Building V2 (SKU 10120003 / 2636)...")
    compile_variant(SKETCH_V2, "byd_hud_v2.bin", copy_boot_parts=False)
    print("[4/4] Updating manifest & version.json...")
    update_json_version(ver)
    print(f"DONE! Ready to upload {WEB_DIR} to GitHub Pages (v{ver}).")
