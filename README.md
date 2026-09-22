# desk-todo · 桌面待办

> 一个把「今日待办」直接画在**桌面背景**上的待办事项管理器。
> 同时也是一个从零开始的 Python 工程实战项目：从内存版命令行工具，一路演进到
> 桌面壁纸面板 + Flask Web 界面。

[![Python](https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white)](#运行环境)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Pillow](https://img.shields.io/badge/Pillow-12.x-2C2C54)](https://python-pillow.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](#license)

---

## 这是什么

普通人管待办要开 App、切窗口、点几下。这个项目的思路不一样：**待办就长在桌面上**。

程序会读取你当前的壁纸，把一个半透明的「今日待办」卡片合成到右下角，再设回成新壁纸。
勾选完成之后刷新一下，桌面上那一项就划掉了 —— 不用切换任何窗口。

同时它有一套完整的增删改查能力，三种入口共用同一份数据：

| 入口 | 用什么操作 | 适合场景 |
|---|---|---|
| 命令行 | `python -m desktodo.cli` | 快速加一条、改状态 |
| 桌面壁纸 | 直接看桌面 | 随时瞄一眼今天要做什么 |
| 浏览器 | `http://127.0.0.1:5000` | 舒服地编辑、拖动优先级 |

## 效果预览

```
┌──────────────────────────────────────────────┐
│                                              │
│                    （你的壁纸）               │
│                                              │
│                                              │
│                        ┌──────────────────┐  │
│                        │ 今日待办 1/3      │  │
│                        │ ✔ 写好 README     │  │
│                        │ □ 学 ctypes 设壁纸 │  │
│                        │ □ 提交代码        │  │
│                        └──────────────────┘  │
└──────────────────────────────────────────────┘
```

> 截图占位：首次跑通后把桌面截图放到 `docs/images/preview.png`。

---

## 运行环境

| 项 | 要求 | 本机实测 |
|---|---|---|
| 操作系统 | Windows 10/11 | Windows 11 build 10.0.26200 |
| Python | 3.11+ | **3.11.16**（项目内 `.venv`） |
| 关键依赖 | Pillow、Flask | Pillow 12.3.0 / Flask 3.x |
| 可选依赖 | pywin32（多显示器进阶） | 已装 312 |

> **为什么必须用 Windows？** 设置桌面壁纸依赖 Win32 API
> （`SystemParametersInfoW`），这是 Windows 独有的。
> 代码里对该 API 做了隔离，其他系统可以跑 CLI 和 Web 部分，但不会有桌面面板。

### 关于 Python 环境

本项目使用项目目录内的 `.venv` 虚拟环境，解释器基座是本机的 conda 环境 `daily`（Python 3.11.16）。

```
D:\WorkBuddy\desk-todo\.venv\Scripts\python.exe     -> Python 3.11.16
D:\WorkBuddy\desk-todo\.venv\Scripts\pythonw.exe    -> 无控制台启动（壁纸刷新用）
```

`.venv/` 已被 `.gitignore` 忽略，不会进仓库。

**为什么不用 conda 环境？** 原本计划从 `daily` 克隆一个 conda 环境 `desktodo`，
但 `conda create` / `conda --clone` 在本机被文件操作保护拦截（清理临时索引文件时触发批量删除确认），
无法完成。改用 `.venv` 后同样拿到了 Python 3.11.16，而且环境在项目内、便于随项目删除重建。

两条使用规范，踩过坑所以写下来：

1. **调 Python 时写全路径**，不要依赖 `activate`。脚本、计划任务、`.vbs` 里一律用
   `D:\WorkBuddy\desk-todo\.venv\Scripts\python.exe`。否则会出现「手动双击能跑、计划任务跑不了」。
2. **不要升级 venv 里的 pip**。用 conda 的 Python 建的 venv，其 pip 是 24.0（自带 wheel）。
   执行 `pip install --upgrade pip` 会先卸载旧 pip 再下载新 pip，中途失败就会留下一个坏掉的
   `~ip` 目录，之后 `python -m pip` 直接报 `No module named pip`。真要升级就重建 venv。

---

## 安装

```bash
git clone https://github.com/tiandongqing5-design/desk-todo.git
cd desk-todo
```

如果你在同一台机器上，`.venv` 已经建好了，直接跳到「准备数据」。
换机器的话按下面重建环境：

```bash
# 1) 建虚拟环境（用本机 Python 3.11，或任意 3.11+ 解释器）
python -m venv .venv

# 2) 装依赖
.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3)（可选）多显示器进阶功能需要 pywin32
.venv\Scripts\python.exe -m pip install pywin32
```

### 准备数据

首次运行前，把示例数据复制成真正的数据文件：

```bash
copy data\todos.example.json data\todos.json
```

`data/todos.json` 被 `.gitignore` 忽略，它是你的个人数据，不会被提交。

---

## 使用

> 下面用 `.venv\Scripts\python.exe` 全路径调用，**不需要先 `activate`**。
> 如果你已经激活了虚拟环境，把前面那段路径去掉即可。

### 命令行

```bash
.venv\Scripts\python.exe -m desktodo.cli
```

> 注意必须用 `python -m desktodo.cli`，**不要**直接 `python desktodo/cli.py`。
> 后者会丢包上下文，报 `attempted relative import with no known parent package`。

### 桌面壁纸面板

```bash
python scripts\refresh.py          # 刷新一次
python scripts\refresh.py --restore # 还原成原始壁纸
```

### Web 界面

```bash
python -m desktodo.web.app
```

然后浏览器打开 <http://127.0.0.1:5000>。

> 默认只监听本机。**这个界面没有任何登录认证**，不要改成 `0.0.0.0` 暴露到公网。

### 自动化（可选）

先确认哲风壁纸之类的动态壁纸软件已退出，然后注册计划任务：

```bash
scripts\install_task.bat           # 每 20 分钟自动刷新一次
scripts\uninstall_task.bat         # 卸载
```

---

## 项目结构

```
desk-todo/
├── desktodo/                  # 主包
│   ├── models.py              # Todo 数据结构
│   ├── storage.py             # ★ 唯一数据真源（读写 + 锁）
│   ├── cli.py                 # 命令行入口
│   ├── panel.py               # Pillow 渲染待办面板
│   ├── wallpaper.py           # ★ Win32 壁纸读写
│   ├── daemon.py              # 常驻定时刷新
│   └── web/                   # Flask 应用
│       ├── app.py
│       ├── templates/index.html
│       └── static/{style.css, app.js}
├── scripts/                   # 预检 / 刷新 / 计划任务
├── data/                      # 数据（todos.json 不入库）
├── output/                    # 生成的壁纸（不入库）
├── logs/                      # 日志（不入库）
└── docs/                      # 路线图与排查手册
```

**一条重要约定**：所有数据读写都只走 `desktodo/storage.py`。
CLI、桌面面板、Flask 三者都调用它，保证同一份数据不会分叉。

---

## 版本演进路线

| 版本 | 内容 | 状态 |
|---|---|---|
| V0.5 | 内存版 CLI：增 / 查 / 完成 / 删 | 计划中 |
| V1.0 | JSON 文件持久化 + 异常处理 | 计划中 |
| V1.5 | 模块化拆分 + 桌面壁纸面板 | 计划中 |
| V2.0 | Flask Web + 自动定时刷新 | 计划中 |
| V2.5 | SQLite / 打包 exe / 多显示器（可选） | 未启动 |

详细的逐日任务见 [`docs/roadmap.md`](docs/roadmap.md)。

---

## 已知限制

- **只支持 Windows**：桌面壁纸功能依赖 Win32 API。
- **单显示器**：目前只处理主屏。多屏需要 `IDesktopWallpaper` COM 接口（pywin32 已具备条件，待实现）。
- **动态壁纸会冲突**：如果装了 Wallpaper Engine、哲风壁纸这类动态壁纸软件，它们会覆盖程序设置的静态壁纸。
  使用前请先退出这类软件。
- **面板右下角留白**：合成时会额外避让约 120px 给任务栏，这是按 200% 缩放的屏幕算的，
  不同缩放比例下需要微调。

---

## 常见问题

**Q：代码没报错，但桌面壁纸没变？**
按顺序排查这四点：
1. 动态壁纸软件是否在跑（检查进程里有没有 `kwallpaper`、`wallpaper32` 之类）
2. `SystemParametersInfoW` 的 `fWinIni` 是否带了 `SPIF_SENDWININICHANGE`（0x02）
3. 是否在反复覆盖同一个文件名 —— Windows 会缓存壁纸，换成带时间戳的新文件名
4. 是否在计划任务里跑 —— 计划任务默认可能在非交互式会话（Session 0）执行，
   那里设置的壁纸不属于当前登录桌面。改成「只在用户登录时运行」

**Q：桌面上的面板越刷新越黑，叠了好几层？**
程序每次都基于「当前壁纸」叠加，而当前壁纸已经是上一次生成的图。
`state.json` 记录了原始底图，会检测到这种情况并自动退回底图重渲染。
如果它失灵了，删掉 `state.json` 再刷新一次。

**Q：JSON 里的中文变成了 `\u5f85\u529e` 这种？**
写文件时漏了 `ensure_ascii=False`。中文系统还要显式指定 `encoding="utf-8"`，
否则会按系统默认的 GBK 编码去读写，导致乱码。

**Q：`ModuleNotFoundError: No module named 'flask'`？**
依赖装到别的解释器上了。确认用的是项目自己的：
```bash
D:\WorkBuddy\desk-todo\.venv\Scripts\python.exe -m pip install Flask
```

**Q：`No module named pip`，venv 里的 pip 坏了？**
多半是执行过 `pip install --upgrade pip` 且中途失败，留下了一个 `~ip` 残缺目录。
删掉 `.venv` 重建一次，然后**不要再升级 venv 的 pip**（见上文「关于 Python 环境」）。

**Q：`conda: command not found`？**
本项目不需要 conda 运行。conda 只是当初用来提供 Python 3.11 解释器的。
如果确实要用，完整路径是 `D:\Anaconda3\condabin\conda.bat`，或执行一次 `conda init` 后重开终端。

---

## 开发说明

提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<type>(<scope>): <描述>
```

| type | 用途 |
|---|---|
| `feat` | 新功能 |
| `fix` | 修 bug |
| `docs` | 文档 |
| `refactor` | 重构（不改变外部行为） |
| `style` | 格式调整 |
| `chore` | 杂务（构建、依赖、脚本） |

`type` 和 `scope` 用英文，描述可以用中文。示例：

```
feat(wallpaper): 实现设置桌面壁纸
fix(storage): 处理数据文件缺失与损坏
```

---

## License

MIT
