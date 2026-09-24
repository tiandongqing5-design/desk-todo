# 学习路线图 · desk-todo

> 24 天，每天约 1 小时。周一至周六学习，**周日缓冲**（补进度 / 休息）。
> 原则：每天结束必须有一个**肉眼可见的成果** + 一次 `git commit`。
> 跑不通就 `git checkout .` 回滚到昨天的状态，明天重来 —— 不要留一个跑不起来的半成品过夜。

进度追踪：把 `[ ]` 改成 `[x]`，然后提交一次 `docs: 更新学习进度`。

---

## 阶段总览

| 阶段 | 天数 | 主题 | 产出 |
|---|---|---|---|
| 准备 | Day 0 | 环境预检 + 建仓 | 仓库上线，壁纸方案验证通过 |
| 第 1 周 | D1–D6 | 语法基础 + Git 起步 | V1.0：能持久化的命令行待办 |
| 第 2 周 | D7–D12 | 工程化 + Win32 壁纸 | V1.5：**待办出现在桌面上** |
| 第 3 周 | D13–D18 | 自动化 + Flask 起步 | 自动刷新 + 网页能看能改 |
| 第 4 周 | D19–D24 | V2.0 完工与交付 | 完整项目 + 文档 + v2.0 tag |

---

## Day 0 · 项目启动

- [x] **0.1** 建目录 `D:\WorkBuddy\desk-todo\`
  - ✅ 目录骨架已建（desktodo / web / data / output / logs / scripts / docs）
- [x] **0.2** 建 Python 环境并装依赖
  - ⚠️ 原计划从 `daily` 克隆 conda 环境 `desktodo`，但 `conda create` / `--clone`
    被本机文件操作保护拦截（清理临时索引文件时触发批量删除确认），无法完成。
    **改用项目内 `.venv`**，基座仍是 `daily` 的 Python 3.11.16。
  - ✅ 结果：`.venv` 内 Python 3.11.16 + Flask 3.1.3 + Pillow 12.3.0，`requirements.txt` 已生成
  - ⚠️ 注意：**不要**在 venv 里执行 `pip install --upgrade pip`，会把它弄坏（详见 README）
- [x] **0.3** 写 `.gitignore`、`README.md`、`docs/roadmap.md`
  - ✅ 已完成；`.gitignore` 覆盖 `output/`、`logs/`、`data/todos.json`、`.venv/`
- [x] **0.4** 安装 gh CLI 并登录
  - ✅ gh 2.101.0 已装入系统 PATH（`C:\Program Files\GitHub CLI\`）
  - ✅ 已完成浏览器授权，`gh auth status` 显示 `✓ Logged in to github.com account tiandongqing5-design`
  - ✅ `gh auth setup-git` 已执行，`credential.https://github.com.helper` 指向 gh
  - 💡 踩坑记录：`gh auth login` 必须在**沙箱外的用户终端**执行；且 gh 是 Go 程序**不读 Windows 系统代理**，
    只认 `HTTP_PROXY` 类环境变量 —— 实测走 Clash 代理时 `api.github.com` 返回 403，**直连才通**
- [x] **0.5** 跑 `preflight.py` 预检
  - ✅ **12/12 项全部通过**（2026-09-22）。壁纸方案确认可行
  - 实测记录：
    - `SystemParametersInfoW(SET)` 返回成功，回读一致
    - 等待 3 秒后仍一致 → 没有被外部程序延迟接管
    - 还原原始壁纸成功 → `【哲风壁纸】天空-孤独-小猫.jpg`
    - 物理分辨率 2880×1800，逻辑 1440×900，缩放 200%（画布必须按物理像素算）
    - 哲风壁纸进程已退出；当前为「图片」模式（WallpaperStyle=10 填充）
  - ⚠️ 结论：**后续开发与使用期间需保持哲风壁纸处于退出状态**
- [x] **0.6** 配置 git 全局身份
  - ✅ user.name / user.email / init.defaultBranch=main / core.quotepath=false / core.autocrlf=true
- [x] **0.7** `git init` + 首次 commit
  - ✅ 分支 `main`，8 个文件，提交 `chore: 初始化项目骨架并添加 .gitignore`
  - ✅ 远程仓库已建并推送：https://github.com/tiandongqing5-design/desk-todo （public，已匿名验证可访问）
  - ✅ 已打 `day0` 标签并推送到远程
  - 💡 踩坑记录：github.com 可达性是**时变**的。不要写死全局 `git config http.proxy`，
    否则代理一关就变成连接被拒，比网络抖动更难排查。做法：先直连，报错再临时挂一次代理

---

## 第 1 周 · 语法基础 + Git 起步（D1–D6）

目标产出：**V1.0 —— 数据能存下来的命令行待办工具**

### Day 1 · Git 工作流
- [x] 学习：工作区 / 暂存区 / 提交三个概念，`status` → `diff` → `add` → `commit` → `push` 五步循环
- [x] 写：`hello.py` —— 函数默认参数、f-string、类型提示、`sys.argv`、`__main__` 守卫
- [x] 成果：本地 5 次提交全部推送到 GitHub，网页 History 可见
- [x] 自测：`git log --oneline` 看到 5 次提交；改一行后 `git status` 显示 modified、
  `git diff` 看到红绿差异、`git restore` 能撤销
- [x] 提交：`feat(cli): 添加 hello.py 入门脚本` + `docs: 修正 Day 0 完成状态并勾选 Day 1`
  - 💡 **关键机制**：`git commit` **不会**立刻出现在网页上，只有 `git push` 之后 History 才会变
  - 💡 刻意分成两次提交：一次代码、一次文档 —— 示范「一个提交只做一件事」

### Day 2 · list 与 dict
- [ ] 学习：`list` 的增删改查、`dict` 的键值对、`while True` 循环、`input()`、f-string
- [ ] 写：`desktodo/cli.py` —— 内存版待办，支持 `add` / `list` / `quit`
- [ ] 数据结构：`{"id": 1, "title": "写 README", "done": False}`
- [ ] 成果：终端里能连续添加待办并列出，编号 1/2/3 正确
- [ ] 自测：连续添加 3 条 → 列表显示带编号 → 退出程序不报错
- [ ] 提交：`feat(cli): 实现内存版待办添加与列表`

### Day 3 · 函数抽取 + 完成/删除
- [ ] 学习：把重复代码抽成函数、`enumerate()`、参数与返回值
- [ ] 写：`cli.py` 增加 `done` / `remove` 命令
- [ ] 成果：能标记完成、能删除；完成项显示 `✔`，未完成显示 `□`
- [ ] 自测：标记完成后符号变化；删除一条后剩余编号不重复
- [ ] 提交：`feat(cli): 支持标记完成与删除待办`

### Day 4 · 文件读写 + JSON
- [ ] 学习：`open()` / `with` 语句、`json.dump` / `json.load`、`pathlib.Path`
- [ ] 写：`desktodo/storage.py` —— 读写 `data/todos.json`
- [ ] ⚠️ **中文系统重点**：必须写 `encoding="utf-8"` 和 `ensure_ascii=False`，否则中文变乱码或 `\u5f85\u529e`
- [ ] 成果：**关掉终端重开，数据还在**
- [ ] 自测：添加 → 关终端 → 重开 → `list` 仍显示；用记事本打开 JSON，中文正常显示
- [ ] 提交：`feat(storage): 用 JSON 文件持久化待办数据`

### Day 5 · 异常处理
- [ ] 学习：`try` / `except` / `else` / `finally`、精确捕获异常类型、`raise ... from`
- [ ] 写：`storage.py` 处理 `FileNotFoundError`（自动建新文件）、`json.JSONDecodeError`（备份损坏文件）
- [ ] ❌ 反模式：`except: pass` —— 异常处理不是让程序别崩，是让它**崩得有信息量**
- [ ] 成果：手动把 JSON 改坏 → 程序给出友好提示并自动备份，而不是一堆崩溃堆栈
- [ ] 自测：删掉 json 能自动重建；手写一个 `{坏掉的` 进去，程序提示「已备份到 xxx」
- [ ] 提交：`fix(storage): 处理数据文件缺失与损坏`

### Day 6 · 文档 + 打 tag
- [ ] 学习：README 该写什么（这是什么 / 怎么装 / 怎么用）、语义化版本、`git tag`
- [ ] 写：完善 `README.md`，补上安装与使用说明
- [ ] 成果：仓库首页清晰可读，别人照 README 能跑起来
- [ ] 自测：`git tag -a v1.0 -m "..."` + `git push --tags`，网页能看到 tag
- [ ] 提交：`docs: 补充 V1.0 安装与使用说明`

---

## 第 2 周 · 工程化 + Win32 壁纸（D7–D12）

目标产出：**V1.5 —— 待办卡片出现在桌面右下角**

### Day 7 · 模块化
- [ ] 学习：模块与包、`__init__.py`、`python -m` 与直接运行的区别
- [ ] 写：拆成 `models.py` / `storage.py` / `cli.py`，引入 `dataclass`
- [ ] ⚠️ **坑**：不要 `python desktodo/cli.py`，会报 `attempted relative import with no known parent package`。统一用 `python -m desktodo.cli`
- [ ] 成果：CLI 行为完全不变，但代码分成三层
- [ ] 自测：`python -m desktodo.cli` 正常工作；每个目录都有 `__init__.py`
- [ ] 提交：`refactor: 按 models/storage/cli 拆分模块`

### Day 8 · 读取壁纸（ctypes 入门）
- [ ] 学习：`ctypes` 调用 Win32 API、`argtypes` / `restype`、宽字符 API
- [ ] 写：`desktodo/wallpaper.py` 的 `get_wallpaper()`
- [ ] 常量：`SPI_GETDESKWALLPAPER = 0x0073`
- [ ] ⚠️ **坑**：`argtypes` 必须显式声明，否则 64 位下指针被截断，静默失败
- [ ] ⚠️ **坑**：路径含中文和全角括号，只能用宽字符 API（`...W`），不要走 subprocess
- [ ] 成果：终端打印出当前壁纸的真实路径
- [ ] 自测：输出的路径和你桌面实际用的壁纸一致，且文件存在
- [ ] 提交：`feat(wallpaper): 通过 Win32 API 读取当前壁纸`

### Day 9 · 设置壁纸
- [ ] 学习：C API 用**返回值**表示失败（不抛异常），所以必须检查返回值
- [ ] 写：`wallpaper.py` 的 `set_wallpaper()`
- [ ] 常量：`SPI_SETDESKWALLPAPER = 0x0014`，`fWinIni = 0x01 | 0x02`
  - `SPIF_SENDWININICHANGE`（0x02）**不能漏**，漏了桌面不会刷新
- [ ] ⚠️ **坑**：文件名要带时间戳。Windows 会缓存壁纸，反复覆盖同名文件可能显示旧图
- [ ] 成果：用一张纯色测试图 → **桌面 1 秒内变色**
- [ ] 自测：设置成功且桌面真的变了；故意传一个不存在的路径，应抛 `FileNotFoundError`
- [ ] 提交：`feat(wallpaper): 实现设置桌面壁纸`

### Day 10 · Pillow 渲染 + DPI 坑
- [ ] 学习：`Image` / `ImageDraw` / `ImageFont`、坐标系统、`textbbox` 度量
- [ ] 写：`desktodo/panel.py` —— 先渲染一行「你好，壁纸」文字
- [ ] ⚠️ **大坑**：**逻辑像素 ≠ 物理像素**。`GetSystemMetrics` 给的是逻辑尺寸，
  缩放 200% 时它只有物理尺寸的一半，拿它当画布会让壁纸被放大 2 倍、文字发虚
  - 解决：用 `EnumDisplaySettingsW` 取物理像素
- [ ] ⚠️ **坑**：`textsize()` 在 Pillow 10+ 已被移除，改用 `font.getbbox()`
- [ ] ⚠️ **坑**：字体要写全路径 `C:\Windows\Fonts\msyh.ttc`，别用 `load_default()`（不支持中文）
- [ ] 成果：桌面出现清晰的「你好，壁纸」
- [ ] 自测：确认拿到的是**物理**分辨率（和「设置 → 系统 → 显示」里不同，是它乘以缩放比）；中文无方块
- [ ] 提交：`feat(panel): 用 Pillow 与微软雅黑渲染文字`

### Day 11 · 合成到壁纸角落
- [ ] 学习：RGBA 通道、`alpha_composite` / `paste` 的 mask 参数、半透明蒙层
- [ ] 写：`panel.py` 完整流程 —— 读原图 → Fill 缩放裁剪 → 画半透明圆角卡片 → 合成 → 输出 PNG
- [ ] ⚠️ **坑**：`base.paste(overlay, (0, 0), overlay)` 第三个 mask 参数是透明的关键，漏了会变成黑块
- [ ] ⚠️ **坑**：右下角定位要**额外留约 120px** 避让任务栏
- [ ] 成果：**桌面右下角出现半透明待办卡片**
- [ ] 自测：半透明效果正确、不遮挡任务栏、文字清晰
- [ ] 提交：`feat(panel): 将待办面板合成到壁纸右下角`

### Day 12 · 接真实数据 + 还原
- [ ] 学习：模块间职责划分 —— `panel.py` 渲染、`storage.py` 管数据、`wallpaper.py` 管系统调用
- [ ] 写：把真实待办数据接进面板；加 `--restore` 还原原始壁纸
- [ ] ⚠️ **坑**：**面板会层层叠加**。每次都基于「当前壁纸」合成，而当前壁纸已经是上次带面板的图，
  结果越叠越黑。用 `state.json` 记住原始底图
- [ ] 成果：CLI 里完成 1 条待办 → 刷新 → 桌面同步更新
- [ ] 自测：连续刷新 3 次，面板不叠加变黑；`--restore` 能还原原始壁纸
- [ ] 提交：`feat: V1.5 桌面壁纸面板完成` + 打 `v1.5` tag

---

## 第 3 周 · 自动化 + Flask 起步（D13–D18）

### Day 13 · 一键运行 + 日志
- [ ] 学习：`logging` 模块、为什么 `pythonw` 下 `print()` 会丢
- [ ] 写：`scripts/refresh.py`、`scripts/refresh_wallpaper.vbs`（第 2 个参数 `0` = 隐藏窗口）
- [ ] ⚠️ **坑**：`pythonw.exe` 没有控制台，`print()` 无处可去 → 必须写日志到 `logs/app.log`
- [ ] 成果：双击 vbs **无任何黑窗闪出**，桌面正常刷新
- [ ] 自测：双击后无黑窗；`logs/app.log` 有新记录
- [ ] 提交：`chore(scripts): 添加无窗口的刷新脚本`

### Day 14 · 常驻定时刷新（方案 A）
- [ ] 学习：`while True` + `time.sleep`、进程与信号、为什么要避免忙等待
- [ ] 写：`desktodo/daemon.py` —— 每 60 秒刷新一次
- [ ] 成果：改完 JSON 后不做任何操作，1 分钟内桌面自动更新
- [ ] 自测：后台跑起来，改数据，等一分钟看桌面
- [ ] 提交：`feat(daemon): 添加常驻后台定时刷新`

### Day 15 · 计划任务（方案 B）+ 对比
- [ ] 学习：把调度权交给操作系统 vs 自己维护常驻进程，各自优缺点
- [ ] 写：`scripts/install_task.bat` / `uninstall_task.bat`
- [ ] ⚠️ **最隐蔽的坑**：计划任务默认可能在**非交互式会话（Session 0）**运行，
  那里设置的壁纸**不属于当前登录桌面** —— 任务显示「成功」，壁纸纹丝不动。
  解决：`taskschd.msc` 里勾选「只在用户登录时运行」
- [ ] 成果：任务计划程序里出现 `TodoWallpaper`，`schtasks /run` 能立即生效
- [ ] 自测：任务「上次运行结果」是 `0x0` **且**桌面真的变了（只看前者会被骗）
- [ ] 提交：`chore(scripts): 添加计划任务注册脚本`

### Day 16 · Flask 最小服务
- [ ] 学习：HTTP 请求响应模型、Flask 路由、模板渲染
- [ ] 写：`desktodo/web/app.py` + `templates/index.html`
- [ ] 成果：浏览器打开 `http://127.0.0.1:5000` 能看到页面
- [ ] 自测：页面正常显示；终端能看到访问日志（200）
- [ ] 提交：`feat(web): 搭建 Flask 最小 Web 服务`

### Day 17 · GET 接口 + 前端渲染
- [ ] 学习：RESTful 概念、JSON 响应、`fetch()`、DOM 操作
- [ ] 写：`GET /api/todos` + `static/app.js` 渲染列表
- [ ] ⚠️ **坑**：**数据文件要用绝对路径**。用相对路径 `data/todos.json` 时，
  Flask 的当前工作目录可能不同，导致「终端有 5 条、网页显示 0 条」
  - 解决：`Path(__file__).resolve().parent.parent / "data" / "todos.json"`
- [ ] 成果：**网页显示的列表和终端完全一致**
- [ ] 自测：终端加一条 → 刷新网页能看到它（验证共用同一份数据）
- [ ] 提交：`feat(web): 实现待办列表 API 与前端渲染`

### Day 18 · 新增与删除
- [ ] 学习：`POST` / `DELETE`、请求体解析、HTTP 状态码（201 / 204 / 400）
- [ ] 写：`POST /api/todos`、`DELETE /api/todos/<id>` + 表单与删除按钮
- [ ] 成果：能在网页上新增和删除待办
- [ ] 自测：网页新增后打开 JSON 确认真的写进去了；空标题应被拒（400）
- [ ] 提交：`feat(web): 支持新建与删除待办`

---

## 第 4 周 · V2.0 完工与交付（D19–D24）

### Day 19 · 勾选完成 + 统计
- [ ] 学习：`PATCH` 与 `PUT` 的区别（局部更新 vs 全量替换）
- [ ] 写：`PATCH /api/todos/<id>` + 顶部统计条
- [ ] 成果：网页勾选完成，顶部「已完成 2 / 5」实时变化
- [ ] 自测：勾选后 JSON 里 `done` 变成 `true`；改不存在的 id 返回 404
- [ ] 提交：`feat(web): 支持勾选完成与统计展示`

### Day 20 · 界面美化
- [ ] 学习：CSS 变量、flex 布局、毛玻璃效果（`backdrop-filter`）
- [ ] 写：`static/style.css` —— 深色玻璃拟态，与桌面壁纸面板视觉统一
- [ ] 成果：界面质感接近成品
- [ ] 自测：把窗口拉窄不破版；中文不出现字体回退
- [ ] 提交：`style(web): 优化界面为深色玻璃拟态风格`

### Day 21 · 网页触发壁纸刷新
- [ ] 学习：后端调用已有模块、让 Web 和桌面联动
- [ ] 写：`POST /api/wallpaper/refresh` + 前端按钮
- [ ] ⚠️ **坑**：Flask 开 `debug=True` 时会启动两个进程（自动重载），
  壁纸渲染可能被执行两次。渲染逻辑要隔离到独立脚本，或用 `use_reloader=False`
- [ ] 成果：**网页点一下按钮 → 桌面壁纸立刻更新**
- [ ] 自测：点按钮后 2 秒内桌面变化（这是整个项目的亮点时刻）
- [ ] 提交：`feat(web): 支持从网页触发壁纸刷新`

### Day 22 · 边界与并发加固
- [ ] 学习：竞态条件、为什么需要锁、原子写（`os.replace`）
- [ ] 写：`storage.py` 加 `threading.RLock`；`os.replace` 原子写；输入校验
- [ ] ⚠️ **坑**：Flask 开发服务器是多线程的，Web 写入和定时刷新读取可能同时发生
- [ ] 成果：空标题被拒；快速连点 20 次新增，JSON 不会损坏
- [ ] 自测：空标题返回 400；连续快速操作后 JSON 仍是合法 JSON
- [ ] 提交：`fix(storage): 加固原子写入与并发锁`

### Day 23 · 文档与截图
- [ ] 学习：好 README 的结构、架构图怎么画（哪怕是 ASCII 的）
- [ ] 写：完善 `README.md`，补 `docs/wallpaper-notes.md` 排查手册，放桌面截图
- [ ] 成果：完整文档：架构图、截图、安装步骤、常见问题
- [ ] 自测：找一个同学（或自己换台机器）照 README 从零跑一遍，能跑通
- [ ] 提交：`docs: 完善 README 与架构说明`

### Day 24 · 复盘与发布
- [ ] 学习：回顾 24 天用了哪些知识点，哪些还没吃透
- [ ] 写：`docs/retrospective.md` 复盘 + 更新本文件勾选状态
- [ ] 成果：`git log --oneline` 有清晰的 24 天演进史；`git tag` 有 v1.0 / v1.5 / v2.0
- [ ] 自测：完整演示一遍 —— 命令行加一条 → 网页勾选 → 桌面同步更新
- [ ] 提交：`chore(release): 发布 V2.0` + 打 `v2.0` tag

---

## 卡住了怎么办

| 症状 | 大概率原因 | 去看 |
|---|---|---|
| `UnicodeDecodeError: 'gbk' codec` | 读写文件没写 `encoding="utf-8"` | README 常见问题 |
| JSON 里中文变 `\u5f85\u529e` | 漏了 `ensure_ascii=False` | README 常见问题 |
| 代码没报错但壁纸没变 | ① 动态壁纸软件在抢 ② 漏了 `SPIF_SENDWININICHANGE` ③ 文件名没换 ④ 计划任务在 Session 0 | `docs/wallpaper-notes.md` |
| 壁纸文字发虚 | 用了逻辑分辨率当画布 | `docs/wallpaper-notes.md` |
| 面板越刷新越黑 | 基于带面板的图又叠了一层 | 删 `state.json` 重试 |
| 网页看不到数据 | 数据文件用了相对路径 | `desktodo/storage.py` |
| `attempted relative import ...` | 直接跑了包内文件 | 用 `python -m desktodo.cli` |
| 计划任务「成功」但壁纸没变 | 非交互式会话（Session 0） | 改成「只在用户登录时运行」 |

---

## V2.5 可选扩展（不在这 24 天内）

想继续深挖的话，按难度递增：

- [ ] **SQLite 迁移** —— 触发条件：条目 > 1000 / 需要多条件查询 / 需要事务 / 多进程并发写
- [ ] **PyInstaller 打包成 exe** —— 让没装 Python 的电脑也能用
- [ ] **多显示器分别设置** —— 用 `IDesktopWallpaper` COM 接口（pywin32 已装，可直接试）
- [ ] **PyQt6 悬浮窗** —— 可点击勾选，实时性比壁纸好
- [ ] **待办分类与标签**、**重复任务**、**到期提醒**
