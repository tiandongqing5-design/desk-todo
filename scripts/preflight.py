"""Day 0 环境预检 —— 在投入后续开发之前，先确认「桌面壁纸能被程序控制」。

这个脚本做 7 件事，全过才算预检通过：

  1. 环境自检（Python 版本 / Pillow / pythonw）
  2. 扫描有没有动态壁纸软件在抢壁纸控制权
  3. 读取当前壁纸路径，确认文件真实存在
  4. 检测 Windows 壁纸模式（图片 / 纯色 / 幻灯片 / 聚焦）
  5. 取物理分辨率（注意：不是 GetSystemMetrics 那个逻辑分辨率）
  6. 设置一张纯色测试图 → 回读校验 → 等 3 秒再校验一次（看是否被外部接管）
  7. 还原成原始壁纸 → 再回读校验

用法::

    python scripts\\preflight.py              # 完整预检（会短暂改一下壁纸）
    python scripts\\preflight.py --skip-set   # 只读模式，不动壁纸

退出码：0 = 全部通过，1 = 有项目失败。
"""

from __future__ import annotations

import argparse
import ctypes
import os
import subprocess
import sys
import time
from ctypes import wintypes as w
from pathlib import Path

# --------------------------------------------------------------------------- #
# 常量
# --------------------------------------------------------------------------- #

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"

SPI_GETDESKWALLPAPER = 0x0073
SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDWININICHANGE = 0x02

ENUM_CURRENT_SETTINGS = -1
SM_CMONITORS = 80

HKCU = 0x80000001
KEY_DESKTOP = r"Control Panel\Desktop"
KEY_WALLPAPERS = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Wallpapers"

# 已知会接管桌面壁纸的软件进程名（小写）
WALLPAPER_APP_KEYWORDS = (
    "kwallpaper",      # 哲风壁纸
    "kdeskcore",
    "wallpaper32",     # Wallpaper Engine
    "wallpaper64",
    "lively",          # Lively Wallpaper
    "dreamscene",
    "hjdesksprite",    # 火萤桌面精灵
    "deskscapes",
)

BACKGROUND_TYPE_NAMES = {0: "图片", 1: "纯色", 2: "幻灯片", 3: "Windows 聚焦"}

# --------------------------------------------------------------------------- #
# 输出helpers
# --------------------------------------------------------------------------- #

_results: list[tuple[str, bool, str]] = []


def _c(text: str, code: str) -> str:
    """给文本上色；控制台不支持 ANSI 时原样返回。"""
    if os.environ.get("NO_COLOR") or not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def banner(text: str) -> None:
    print()
    print(_c("=" * 68, "36"))
    print(_c(f"  {text}", "1;36"))
    print(_c("=" * 68, "36"))


def step(text: str) -> None:
    print()
    print(_c(f"▶ {text}", "1"))


def ok(text: str) -> None:
    print(_c(f"  [OK]   {text}", "32"))


def fail(text: str) -> None:
    print(_c(f"  [FAIL] {text}", "31"))


def warn(text: str) -> None:
    print(_c(f"  [WARN] {text}", "33"))


def info(text: str) -> None:
    print(f"         {text}")


def record(name: str, passed: bool, detail: str = "") -> None:
    _results.append((name, passed, detail))


# --------------------------------------------------------------------------- #
# Win32 封装
# --------------------------------------------------------------------------- #

user32 = ctypes.WinDLL("user32", use_last_error=True)

# argtypes / restype 必须显式声明。
# 不声明的话 64 位下 pvParam 指针可能被截断成 32 位，导致静默失败 —— 这是
# 「代码没报错但壁纸没变」的头号原因。
user32.SystemParametersInfoW.argtypes = [w.UINT, w.UINT, w.LPVOID, w.UINT]
user32.SystemParametersInfoW.restype = w.BOOL


class DEVMODE(ctypes.Structure):
    """EnumDisplaySettingsW 用的显示设置结构体。

    只关心 dmPelsWidth / dmPelsHeight / dmLogPixels，
    但结构体必须完整，否则 dmSize 对不上，调用直接失败。
    """

    _fields_ = [
        ("dmDeviceName", w.WCHAR * 32),
        ("dmSpecVersion", w.WORD),
        ("dmDriverVersion", w.WORD),
        ("dmSize", w.WORD),
        ("dmDriverExtra", w.WORD),
        ("dmFields", w.DWORD),
        ("dmOrientation", ctypes.c_short),
        ("dmPaperSize", ctypes.c_short),
        ("dmPaperLength", ctypes.c_short),
        ("dmPaperWidth", ctypes.c_short),
        ("dmScale", ctypes.c_short),
        ("dmCopies", ctypes.c_short),
        ("dmDefaultSource", ctypes.c_short),
        ("dmPrintQuality", ctypes.c_short),
        ("dmColor", ctypes.c_short),
        ("dmDuplex", ctypes.c_short),
        ("dmYResolution", ctypes.c_short),
        ("dmTTOption", ctypes.c_short),
        ("dmCollate", ctypes.c_short),
        ("dmFormName", w.WCHAR * 32),
        ("dmLogPixels", w.WORD),
        ("dmBitsPerPel", w.DWORD),
        ("dmPelsWidth", w.DWORD),
        ("dmPelsHeight", w.DWORD),
        ("dmDisplayFlags", w.DWORD),
        ("dmDisplayFrequency", w.DWORD),
        ("dmICMMethod", w.DWORD),
        ("dmICMIntent", w.DWORD),
        ("dmMediaType", w.DWORD),
        ("dmDitherType", w.DWORD),
        ("dmReserved1", w.DWORD),
        ("dmReserved2", w.DWORD),
        ("dmPanningWidth", w.DWORD),
        ("dmPanningHeight", w.DWORD),
    ]


def get_wallpaper() -> str | None:
    """读取当前壁纸路径。返回 None 表示不是「图片」模式（纯色/聚焦/幻灯片）。"""
    buf = ctypes.create_unicode_buffer(1024)
    # uiParam 要传缓冲区「字符数」（不是字节数），fWinIni 传 0
    succeeded = user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, len(buf), buf, 0)
    if not succeeded:
        raise OSError(ctypes.get_last_error(), "SystemParametersInfoW(GET) 调用失败")
    return buf.value or None


def set_wallpaper(path: str | os.PathLike[str]) -> None:
    """把壁纸设成指定图片。路径必须存在。

    fWinIni 两个标志都要带：
      SPIF_UPDATEINIFILE     写入用户配置，重启后保持
      SPIF_SENDWININICHANGE  立即广播变更 —— 不带这个桌面不会刷新
    """
    abs_path = os.path.abspath(str(path))
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"壁纸文件不存在: {abs_path}")
    succeeded = user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER, 0, ctypes.c_wchar_p(abs_path),
        SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE,
    )
    if not succeeded:
        raise OSError(ctypes.get_last_error(), "SystemParametersInfoW(SET) 调用失败")


def get_screen_size() -> tuple[int, int]:
    """返回主屏「物理」分辨率。

    注意不要用 GetSystemMetrics —— 在缩放 200% 的机器上它返回的是逻辑分辨率
    （1440x900），拿它当画布会生成一张被放大 2 倍的模糊壁纸。
    """
    dm = DEVMODE()
    dm.dmSize = ctypes.sizeof(DEVMODE)
    if user32.EnumDisplaySettingsW(None, ENUM_CURRENT_SETTINGS, ctypes.byref(dm)):
        return int(dm.dmPelsWidth), int(dm.dmPelsHeight)
    # 兜底：先声明进程 DPI 感知，再取
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except OSError:
        pass
    return int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1))


def get_logical_size() -> tuple[int, int]:
    """返回逻辑分辨率，仅用于对比展示。"""
    return int(user32.GetSystemMetrics(0)), int(user32.GetSystemMetrics(1))


def get_monitor_count() -> int:
    return int(user32.GetSystemMetrics(SM_CMONITORS))


# --------------------------------------------------------------------------- #
# 注册表读取
# --------------------------------------------------------------------------- #


def read_registry(key_path: str, value_name: str):
    """读 HKCU 下的一个值，不存在返回 None。"""
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            return winreg.QueryValueEx(key, value_name)[0]
    except OSError:
        return None


def running_wallpaper_apps() -> list[str]:
    """列出正在运行的动态壁纸软件进程名。"""
    try:
        raw = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True,
            check=False,
            timeout=15,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return []

    # 中文 Windows 的 tasklist 输出是 GBK
    text = raw.decode("gbk", errors="replace")
    found: list[str] = []
    for line in text.splitlines():
        name = line.split(",")[0].strip().strip('"').lower()
        if name.endswith(".exe"):
            name = name[:-4]
        if name and any(k in name for k in WALLPAPER_APP_KEYWORDS):
            if name not in found:
                found.append(name)
    return found


# --------------------------------------------------------------------------- #
# 各项检查
# --------------------------------------------------------------------------- #


def check_environment() -> None:
    step("1/7  环境自检")
    info(f"Python      {sys.version.split()[0]}  ({sys.executable})")

    if sys.version_info >= (3, 11):
        ok(f"Python 版本 {sys.version_info.major}.{sys.version_info.minor} 满足要求（>= 3.11）")
    else:
        fail(f"Python {sys.version.split()[0]} 太低，项目需要 3.11+")
    record("Python 版本", sys.version_info >= (3, 11))

    try:
        import PIL
        from PIL import Image, ImageDraw, ImageFont  # noqa: F401

        info(f"Pillow      {PIL.__version__}")
        ok("Pillow 可用")
        record("Pillow", True)
    except ImportError as exc:
        fail(f"Pillow 不可用：{exc}")
        record("Pillow", False)
        return

    # 中文字体
    font_path = Path(r"C:\Windows\Fonts\msyh.ttc")
    if font_path.exists():
        from PIL import ImageFont

        try:
            font = ImageFont.truetype(str(font_path), 40)
            bbox = font.getbbox("今日待办")
            if bbox[2] - bbox[0] > 0:
                ok(f"中文字体 msyh.ttc 可用（'今日待办' 渲染宽度 {bbox[2] - bbox[0]}px）")
                record("中文字体", True)
            else:
                fail("msyh.ttc 加载了但渲染不出中文")
                record("中文字体", False)
        except OSError as exc:
            fail(f"msyh.ttc 加载失败：{exc}")
            record("中文字体", False)
    else:
        warn("找不到 C:\\Windows\\Fonts\\msyh.ttc，面板会退回默认字体（可能不显示中文）")
        record("中文字体", False)

    # pythonw —— 无黑窗方案依赖它
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    if pythonw.exists():
        ok("pythonw.exe 存在（可用于无黑窗启动）")
        info(str(pythonw))
        record("pythonw.exe", True)
    else:
        warn("同目录下找不到 pythonw.exe，后面做开机自启时会有黑窗")
        record("pythonw.exe", False)


def check_wallpaper_apps() -> None:
    step("2/7  动态壁纸软件检测")
    apps = running_wallpaper_apps()
    if apps:
        fail(f"检测到 {len(apps)} 个动态壁纸相关进程在运行：")
        for name in apps:
            info(name)
        print()
        warn("这些软件会覆盖程序设置的壁纸，导致「脚本成功但桌面没变」。")
        warn("请从托盘图标右键退出它们，然后重新运行本预检。")
        record("动态壁纸软件已退出", False, "、".join(apps))
    else:
        ok("没有检测到动态壁纸软件在运行")
        record("动态壁纸软件已退出", True)


def check_current_wallpaper() -> str | None:
    step("3/7  读取当前壁纸")
    try:
        current = get_wallpaper()
    except OSError as exc:
        fail(f"读取失败：{exc}")
        record("读取当前壁纸", False)
        return None

    if current is None:
        warn("当前不是「图片」模式（可能是纯色 / Windows 聚焦 / 幻灯片），读不到路径")
        info("这不影响程序运行 —— 渲染时会退回纯色画布。")
        record("读取当前壁纸", True, "非图片模式")
        return None

    info(f"路径  {current}")
    if Path(current).exists():
        size_kb = Path(current).stat().st_size / 1024
        ok(f"文件存在（{size_kb:.0f} KB）")
        record("读取当前壁纸", True)
        return current

    warn("路径读到了，但文件不存在（可能是已删除的幻灯片项）")
    record("读取当前壁纸", False, "文件不存在")
    return None


def check_wallpaper_mode() -> None:
    step("4/7  壁纸模式检测")
    style = read_registry(KEY_DESKTOP, "WallpaperStyle")
    tile = read_registry(KEY_DESKTOP, "TileWallpaper")
    BgType = read_registry(KEY_WALLPAPERS, "BackgroundType")
    slideshow_set = read_registry(KEY_WALLPAPERS, "SlideshowSourceDirectoriesSet")

    info(f"WallpaperStyle  {style!r}   (10 = 填充, 6 = 适应, 0 = 居中)")
    info(f"TileWallpaper   {tile!r}")
    info(f"BackgroundType  {BgType!r}   ({BACKGROUND_TYPE_NAMES.get(BgType, '未知')})")
    info(f"幻灯片历史配置  {slideshow_set!r}")

    if BgType == 0:
        ok("当前是「图片」模式，程序可以直接接管")
        record("壁纸模式", True)
    elif BgType == 2:
        warn("当前是「幻灯片」模式 —— 它会按间隔自动换图，覆盖程序设置的壁纸")
        warn("建议：右键桌面 → 个性化 → 背景 → 改成「图片」")
        record("壁纸模式", False, "幻灯片模式")
    elif BgType == 3:
        warn("当前是「Windows 聚焦」—— 读不到壁纸路径，聚焦会定期换图")
        warn("建议：改成「图片」")
        record("壁纸模式", False, "聚焦模式")
    else:
        warn(f"壁纸模式为 {BACKGROUND_TYPE_NAMES.get(BgType, '未知')}")
        record("壁纸模式", True)

    if slideshow_set == 1 and BgType != 2:
        info("注：注册表里残留着幻灯片历史配置，当前没启用，一般无影响。")


def check_resolution() -> tuple[int, int] | None:
    step("5/7  分辨率检测")
    try:
        phys = get_screen_size()
    except Exception as exc:  # noqa: BLE001
        fail(f"取分辨率失败：{exc}")
        record("分辨率", False)
        return None

    logical = get_logical_size()
    monitors = get_monitor_count()

    info(f"物理分辨率  {phys[0]} x {phys[1]}")
    info(f"逻辑分辨率  {logical[0]} x {logical[1]}")
    if logical[0]:
        info(f"缩放比例    {phys[0] / logical[0] * 100:.0f}%")
    info(f"显示器数量  {monitors}")

    if phys != logical:
        warn("物理分辨率与逻辑分辨率不一致（系统开了缩放）")
        info("画布尺寸和字号必须按「物理分辨率」算，否则壁纸文字会被放大后发虚。")
    else:
        ok("物理分辨率与逻辑分辨率一致（缩放 100%）")

    if monitors > 1:
        warn(f"检测到 {monitors} 个显示器 —— 当前程序只处理主屏")
        record("分辨率", True, f"{monitors} 屏")
    else:
        ok(f"单显示器，分辨率 {phys[0]}x{phys[1]}")
        record("分辨率", True)
    return phys


def check_set_and_readback(phys: tuple[int, int] | None, original: str | None) -> bool:
    """核心测试：设一张测试图，回读，再延时回读，最后还原。"""
    step("6/7  壁纸设置 + 回读校验")
    from PIL import Image, ImageDraw, ImageFont

    assert phys is not None
    width, height = phys

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    test_path = OUTPUT_DIR / f"preflight_{stamp}.png"

    # 生成一张带文字的纯色测试图，用物理分辨率
    img = Image.new("RGB", (width, height), (20, 24, 36))
    draw = ImageDraw.Draw(img)
    font_big = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", max(48, height // 14))
    font_small = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", max(24, height // 32))
    draw.text((width // 2, height // 2 - 60), "预检测试图", font=font_big,
              fill=(240, 245, 255), anchor="mm")
    draw.text((width // 2, height // 2 + 40), f"{width} x {height}",
              font=font_small, fill=(150, 170, 200), anchor="mm")
    img.save(test_path, "PNG")
    info(f"测试图已生成：{test_path.name}  ({width}x{height})")

    # --- 设置 ---
    try:
        set_wallpaper(test_path)
        ok("SystemParametersInfoW(SET) 返回成功")
    except (OSError, FileNotFoundError) as exc:
        fail(f"设置壁纸失败：{exc}")
        record("设置壁纸", False)
        record("回读校验", False)
        return False

    # --- 立即回读 ---
    time.sleep(1.5)
    try:
        readback = get_wallpaper()
    except OSError as exc:
        fail(f"回读失败：{exc}")
        record("回读校验", False)
        return False

    if readback and Path(readback).resolve() == test_path.resolve():
        ok("回读一致 —— 壁纸确实被改成了测试图")
        record("设置壁纸", True)
        record("回读校验", True)
    else:
        fail("回读不一致 —— 设置后壁纸又被改回去了")
        info(f"期望  {test_path}")
        info(f"实际  {readback}")
        record("设置壁纸", True)
        record("回读校验", False)
        warn("这是动态壁纸软件 / 幻灯片 / 聚焦在抢控制权。")
        warn("请退出这类软件后重跑预检。")

    # --- 延时再回读，捕捉「过一会儿才被覆盖」的情况 ---
    info("等待 3 秒，再校验一次（排查外部程序延迟接管）...")
    time.sleep(3)
    try:
        delayed = get_wallpaper()
    except OSError:
        delayed = None

    if delayed and Path(delayed).resolve() == test_path.resolve():
        ok("3 秒后仍然一致 —— 没有被外部程序接管")
        record("抗外部接管", True)
    else:
        fail("3 秒后壁纸被改走了，说明有程序在持续接管壁纸")
        info(f"实际  {delayed}")
        record("抗外部接管", False)
        warn("桌面壁纸方案在这台机器上不可靠。")
        warn("建议改用备选方案：PyQt6 悬浮小组件（浮在桌面之上，不与壁纸软件争控制权）。")

    # --- 还原 ---
    step("7/7  还原原始壁纸")
    if original is None:
        warn("原始壁纸不是图片模式，无法自动还原。")
        info("请手动：右键桌面 → 个性化 → 背景 → 重新选一张图。")
        record("还原壁纸", True, "跳过")
        return True

    try:
        set_wallpaper(original)
        time.sleep(1.5)
        restored = get_wallpaper()
        if restored and Path(restored).resolve() == Path(original).resolve():
            ok("已还原成原始壁纸")
            info(original)
            record("还原壁纸", True)
        else:
            warn("还原命令执行了，但回读不一致")
            info(f"期望  {original}")
            info(f"实际  {restored}")
            record("还原壁纸", False)
    except (OSError, FileNotFoundError) as exc:
        fail(f"还原失败：{exc}")
        info(f"请手动把壁纸设回：{original}")
        record("还原壁纸", False)
    return True


def check_skip_set(original: str | None) -> None:
    step("6/7  壁纸设置（已跳过 --skip-set）")
    info("只读模式：不修改壁纸，跳过设置与还原测试。")
    record("设置壁纸", True, "跳过")
    record("回读校验", True, "跳过")
    record("抗外部接管", True, "跳过")
    step("7/7  还原原始壁纸")
    info("只读模式：无需还原。")
    record("还原壁纸", True, "跳过")


# --------------------------------------------------------------------------- #
# 汇总
# --------------------------------------------------------------------------- #


def summarize() -> int:
    banner("预检报告")
    failed = [r for r in _results if not r[1]]

    for name, passed, detail in _results:
        mark = _c("PASS", "32") if passed else _c("FAIL", "31")
        suffix = f"   ({detail})" if detail else ""
        print(f"  {mark}  {name}{suffix}")

    print()
    total = len(_results)
    print(f"  合计 {total - len(failed)}/{total} 项通过")

    if not failed:
        print()
        print(_c("  预检通过 —— 可以开始 Day 1 了。", "1;32"))
        return 0

    print()
    print(_c("  以下项目未通过：", "1;31"))
    for name, _, detail in failed:
        print(f"    - {name}{f'  ({detail})' if detail else ''}")

    critical = {"回读校验", "抗外部接管", "设置壁纸", "壁纸模式"}
    if any(name in critical for name, _, _ in failed):
        print()
        print(_c("  桌面壁纸方案在这台机器上不可靠，建议：", "1;33"))
        print("    1. 退出哲风壁纸等动态壁纸软件，把壁纸模式改成「图片」，重跑预检")
        print("    2. 若仍失败 → 切换到备选方案：PyQt6 悬浮小组件")
        print("       （浮在桌面之上，不需要和壁纸软件抢控制权）")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="desk-todo Day 0 环境预检")
    parser.add_argument(
        "--skip-set",
        action="store_true",
        help="只读模式：不修改壁纸，跳过设置与还原测试",
    )
    args = parser.parse_args()

    banner("desk-todo  Day 0 环境预检")
    print(f"  项目目录  {PROJECT_ROOT}")
    print(f"  输出目录  {OUTPUT_DIR}")

    check_environment()
    check_wallpaper_apps()
    original = check_current_wallpaper()
    check_wallpaper_mode()
    phys = check_resolution()

    if args.skip_set:
        check_skip_set(original)
    elif phys is None:
        warn("拿不到分辨率，无法生成测试图，跳过设置测试")
    else:
        check_set_and_readback(phys, original)

    return summarize()


if __name__ == "__main__":
    raise SystemExit(main())
