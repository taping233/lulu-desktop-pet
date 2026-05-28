from __future__ import annotations

import random
import queue
import sys
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from typing import NamedTuple
try:
    import winreg
except ImportError:  # pragma: no cover - Windows-only feature.
    winreg = None

from PIL import Image, ImageChops, ImageMath, ImageTk


CELL_W = 192
CELL_H = 208
TRANSPARENT_COLOR = (0, 255, 0)
SPRITESHEET_NAME = "spritesheet.webp"
STARTUP_FRAME_NAME = "startup_frame.webp"
AUTOSTART_NAME = "lulu在摸鱼"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
AUTHOR_TEXT = "\u5236\u4f5c\u8005 github taping233"
CELL_EDGE_TRIM_X_PX = 6
CELL_EDGE_TRIM_Y_PX = 0
EDGE_MARGIN_PX = 24
EDGE_ACTION_COOLDOWN = 18.0

ACTION_COUNT = 30


class ScreenRect(NamedTuple):
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top

STATES = [("idle", 0, 6, 150)] + [
    (f"action-{i:02d}", i, 6, 125) for i in range(1, ACTION_COUNT + 1)
]
SMOOTH_FRAME_ORDER = (0, 1, 2, 3, 4, 5, 4, 3, 2, 1)
STATE_FRAME_ORDERS = {
    "action-30": (0, 1, 2, 3, 4, 5),
}
STATE_DELAYS = {"idle": 220, "action-03": 150, "action-04": 150}
DEFAULT_ACTION_DELAY = 185

ACTION_LABELS = [
    "\u6325\u624b\u81ea\u62cd",
    "\u5f00\u5fc3\u8df3\u8df3",
    "\u53f3\u8fb9\u6e9c\u8fbe",
    "\u5de6\u8fb9\u6e9c\u8fbe",
    "\u62b1\u9c7c\u5de5\u4f5c",
    "\u5976\u8336\u95ea\u5149",
    "\u7b49\u732b\u732b",
    "\u4f4e\u7535\u91cf\u8db4\u5012",
    "\u59d4\u5c48\u54ed\u54ed",
    "\u751f\u6c14\u5192\u70df",
    "\u63a2\u5934\u770b\u770b",
    "\u62b1\u732b\u5145\u7535",
    "\u88ab\u7a9d\u7761\u89c9",
    "\u4e70\u4e70\u4e70",
    "\u6bdb\u7ebf\u7403",
    "\u706b\u9505\u5f00\u996d",
    "\u8db4\u4e0b\u6ca1\u7535",
    "\u60ca\u5413\u5f39\u8d77",
    "\u5bb3\u7f9e\u6342\u8138",
    "\u5b8c\u6210\u6492\u82b1",
    "\u559d\u6c34\u63d0\u9192",
    "\u5403\u5c0f\u86cb\u7cd5",
    "\u4f38\u61d2\u8170",
    "\u96e8\u4f1e\u8e66\u8e66",
    "\u62b1\u6795\u6253\u76f9",
    "\u70ed\u8336\u65f6\u95f4",
    "\u7535\u8111\u5de5\u4f5c",
    "\u6652\u592a\u9633",
    "\u62cd\u624b\u9f13\u52b1",
    "\u8f6c\u5708\u5f00\u5fc3",
]

ACTIONS = [(label, [(f"action-{index:02d}", 2)]) for index, label in enumerate(ACTION_LABELS, start=1)]

SAYINGS = [
    "好像该吃饭啦。",
    "你吃了吗？",
    "今天也要好好吃饭。",
    "今天天气真好啊。",
    "记得喝口水。",
    "起来站一下吧。",
    "伸个懒腰再继续。",
    "别一直盯着屏幕哦。",
    "先休息一分钟吧。",
    "我有点想吃小蛋糕。",
    "奶茶可以少糖吗？",
    "今天也辛苦啦。",
    "要不要摸摸猪猪？",
    "我在这里陪你。",
    "慢慢来，不着急。",
    "先把水杯拿近一点。",
    "眼睛休息一下吧。",
    "要不要出去走两步？",
    "吃点热乎的吧。",
    "别忘了回消息哦。",
    "任务一点点做就好。",
    "我觉得你可以的。",
    "猪猪正在充电中。",
    "今天也要开心一点。",
    "要按时吃晚饭。",
    "别空腹喝咖啡。",
    "困了就眯一会儿。",
    "桌面好热闹呀。",
    "我闻到好吃的了。",
    "鱼鱼是我的。",
    "猫猫也想你了。",
    "先保存一下文件吧。",
    "小心别忘记保存。",
    "喝水喝水喝水。",
    "肩膀放松一下。",
    "脖子转一转。",
    "手腕也休息一下。",
    "今天已经很棒了。",
    "不要太勉强自己。",
    "要不要听首歌？",
    "我想躺一会儿。",
    "电量快满啦。",
    "电量不足，求抱抱。",
    "好想吃火锅。",
    "今天适合吃点甜的。",
    "先吃一口再工作。",
    "不要饿着自己。",
    "冰箱里还有什么？",
    "我可以帮你卖萌。",
    "你点我干嘛呀。",
    "再点一下也可以。",
    "猪猪收到指令。",
    "正在努力可爱。",
    "我刚刚发呆了。",
    "今天的云很好看。",
    "窗外亮亮的。",
    "记得透透气。",
    "要不要开窗一下？",
    "先把桌子收一下？",
    "有点想睡觉。",
    "午休时间到了吗？",
    "晚上别熬太晚。",
    "早点睡会变可爱。",
    "你今天笑了吗？",
    "给你一点好运。",
    "好事会发生的。",
    "不要忘记吃水果。",
    "要不要泡杯茶？",
    "咖啡也要配水。",
    "猪猪在巡逻。",
    "我看见你啦。",
    "你是不是又忙忘了？",
    "先深呼吸一下。",
    "呼气，吸气。",
    "今天也平安顺利。",
    "小目标先完成一个。",
    "做完这个就休息。",
    "你已经做很多啦。",
    "不要和自己生气。",
    "慢慢整理思路。",
    "把待办写下来吧。",
    "先做最小的一步。",
    "别怕，我陪着。",
    "猪猪给你打气。",
    "可以奖励自己一下。",
    "今天想吃什么？",
    "我投票吃热的。",
    "零食要分享吗？",
    "好像有点冷。",
    "披件外套吧。",
    "空调别开太低。",
    "下雨也没关系。",
    "晴天适合散步。",
    "我想晒太阳。",
    "抱抱猫猫也不错。",
    "毛线球滚走啦。",
    "购物袋有点重。",
    "完成啦，撒花！",
    "今天也谢谢你。",
    "明天也会很好。",
]

SAYINGS += [
    "我刚刚发呆了。",
    "正在努力可爱。",
    "你点我干嘛呢。",
    "再点一下也可以。",
    "猪猪收到指令。",
    "我闻到好吃的了。",
    "小蛋糕在哪里？",
    "火锅是不是在召唤？",
    "鱼鱼是我的。",
    "抱枕也想午睡。",
    "热茶时间到。",
    "先吃一口再工作。",
    "不要饿着自己。",
    "冰箱里还有什么？",
    "我可以帮你卖萌。",
    "先整理一下窗口吧。",
    "鼠标点得太快啦。",
    "键盘今天辛苦了。",
    "屏幕也需要眨眼。",
    "现在适合保存进度。",
    "别把灵感吓跑。",
    "把难题切小一点。",
    "先从最顺手的做起。",
    "给你一小块好运。",
    "我负责在旁边可爱。",
    "安静陪你三秒钟。",
    "三秒到了，我又来了。",
    "不要太勉强自己。",
    "我猜你需要一口水。",
    "这里有一只认真猪。",
    "我站岗，你工作。",
    "这个窗口风景不错。",
    "贴边的时候我会探头。",
    "角落里也有安全感。",
    "屏幕边边凉凉的。",
    "我差点贴成壁纸。",
    "我不是图标，我是猪。",
    "要不要听个冷笑话？",
    "冷笑话来了：冰箱为什么安静？因为它有冷静期。",
    "为什么键盘不说话？因为它只会按部就班。",
    "电脑也会累吗？会，它有休眠。",
    "猪为什么不怕热？因为它会哼哼散热。",
    "为什么杯子很会聊天？因为它有话口。",
    "为什么文件夹很专一？因为它只会收纳你给的东西。",
    "为什么闹钟很自信？因为它总会响起来。",
    "为什么鼠标会迷路？因为它没有导航，只有光标。",
    "为什么云朵不迟到？因为它走的是云端。",
    "为什么月亮不加班？因为它有阴晴圆缺。",
    "为什么猪猪适合当桌宠？因为它会默默陪桌。",
    "为什么代码想睡觉？因为它跑累了。",
    "为什么茶杯会发呆？因为它在泡自己。",
    "为什么书本不怕黑？因为它有知识点亮。",
    "为什么雨伞很低调？因为它只在撑场面时出现。",
    "为什么小蛋糕不说谎？因为它一看就很甜。",
    "为什么毛线球会迷路？因为它线索太多。",
    "为什么电池不吵架？因为它怕没电。",
    "为什么太阳很守时？因为它每天上线。",
    "小知识：所有猪都是双眼皮。",
    "小知识：猪的嗅觉很灵敏。",
    "小知识：猪很聪明，学习能力很强。",
    "小知识：猪会用声音表达情绪。",
    "小知识：猪喜欢干净的休息区。",
    "小知识：猪的鼻子很适合探索。",
    "小知识：家猪和野猪是近亲。",
    "小知识：猪会认路，也会记住熟悉的人。",
    "小知识：猪的叫声不止一种。",
    "小知识：小猪睡觉时常常挤在一起取暖。",
    "小知识：多喝水有助于保持专注。",
    "小知识：眨眼能帮助眼睛保持湿润。",
    "小知识：短暂休息常常能提高效率。",
    "小知识：番茄钟常见设置是二十五分钟专注。",
    "小知识：写下待办能减少脑内负担。",
    "小知识：拉伸肩颈能缓解久坐紧张。",
    "小知识：保存文件是很便宜的保险。",
    "小知识：屏幕太亮会更容易疲劳。",
    "小知识：热饮不一定提神，但很安慰。",
    "小知识：散步会帮大脑整理想法。",
    "小知识：睡眠会影响记忆整理。",
    "小知识：深呼吸能让节奏慢下来。",
    "小知识：阳光会影响人的生物钟。",
    "小知识：桌面越清爽，找东西越快。",
    "小知识：一句话任务比大目标更容易开始。",
    "小知识：水杯放近一点，喝水概率会变高。",
    "小知识：眼睛也喜欢远处的风景。",
    "小知识：站起来走几步能改善久坐僵硬。",
    "小知识：键盘快捷键能省下很多小动作。",
    "小知识：备份不是麻烦，是未来的感谢。",
    "今天的你适合慢慢发光。",
    "别把所有事情都塞进今天。",
    "可以先完成一个小小版本。",
    "有些问题睡一觉会变小。",
    "别让完美挡住开始。",
    "认真和休息可以轮流来。",
    "我喜欢你认真工作的样子。",
    "你的桌宠申请陪伴中。",
    "我在边上看着你，不吵。",
    "做不动的时候先喝水。",
    "想不出来就换个角度。",
    "可以把困难拆成三块。",
    "先处理最烦的那一小口。",
    "不要忘记夸自己一下。",
    "你不是机器，休息合理。",
    "今天不用每件事都满分。",
    "留一点力气给晚饭。",
    "灵感可能在水杯旁边。",
    "这一步已经算前进。",
    "慢一点也没关系。",
    "我给你的进度条鼓掌。",
    "这只猪认为你很棒。",
    "文件保存了吗？我只是问问。",
    "不要让标签页开会太久。",
    "关闭一个不用的窗口也算整理。",
    "耳机音量别太大。",
    "坐姿可以换一下。",
    "手离开鼠标休息十秒。",
    "眉头先松开一点。",
    "热水在等你。",
    "早点吃饭会更有力气。",
    "别让胃替你抗议。",
    "今天的天气适合温柔一点。",
    "把自己照顾好是正事。",
    "我把好运放在屏幕角落。",
    "需要我在边边探头吗？",
    "靠近边缘，猪猪启动侦察。",
    "角落安全员已上线。",
    "屏幕边界已确认。",
    "我从边边冒出来啦。",
    "这边没有危险，只有可爱。",
    "左边检查完毕。",
    "右边检查完毕。",
    "上边风有点大。",
    "下边适合趴一会儿。",
    "如果卡住了，先保存再试。",
    "如果焦虑了，先呼吸再想。",
    "如果饿了，先吃饭再拼。",
    "如果困了，闭眼五分钟。",
    "如果烦了，站起来走走。",
    "如果顺利，记得庆祝一下。",
    "如果不顺，也可以慢慢来。",
    "我会在这里等你回来。",
    "去倒水吧，我守着屏幕。",
    "去吃饭吧，我不偷看。",
    "去休息吧，桌面交给我。",
    "今天也不要忘记快乐。",
    "愿你的复制粘贴都成功。",
    "愿你的保存没有冲突。",
    "愿你的文件名一眼看懂。",
    "愿你的思路像热茶一样顺。",
    "愿你的问题自己变简单。",
    "愿你的鼠标手今天轻松。",
    "愿你的待办少一点。",
    "愿你的晚饭好吃一点。",
    "愿你的睡眠长一点。",
    "愿你今天被温柔对待。",
    "猪猪今天也在营业。",
    "我是一只严肃的可爱猪。",
    "可爱不是任务，是天赋。",
    "我没有偷懒，我在待机。",
    "待机也是一种陪伴。",
    "我刚刚巡逻到屏幕边缘。",
    "边缘很好，但别把我拖丢。",
    "我会贴边，但不会跑路。",
    "你工作，我卖萌，分工明确。",
    "请给本猪一点掌声。",
    "掌声收到，尾巴摇一下。",
    "今天也要按时下班哦。",
    "别让今天变成无限循环。",
    "循环可以，熬夜不行。",
    "我猜你需要一个暂停键。",
    "暂停一下，不会耽误太多。",
    "小猪提醒：喝水。",
    "小猪提醒：保存。",
    "小猪提醒：眨眼。",
    "小猪提醒：伸懒腰。",
    "小猪提醒：吃饭。",
    "小猪提醒：早点睡。",
]

EDGE_SAYINGS = {
    "left": ["左边检查完毕。", "我从左边探头啦。", "贴住左边，启动侦察。"],
    "right": ["右边检查完毕。", "我从右边探头啦。", "贴住右边，保持可爱。"],
    "top": ["上边风有点大。", "我摸到屏幕天花板啦。", "顶部巡逻完成。"],
    "bottom": ["下边适合趴一会儿。", "底边安全员上线。", "我在底边休息一下。"],
}


def app_dir() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"))
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def startup_command() -> str:
    if getattr(sys, "frozen", False):
        return f'"{Path(sys.executable).resolve()}"'
    return f'"{Path(sys.executable).resolve()}" "{Path(__file__).resolve()}"'


def is_autostart_enabled() -> bool:
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            value, _ = winreg.QueryValueEx(key, AUTOSTART_NAME)
    except OSError:
        return False
    return value == startup_command()


def set_autostart(enabled: bool) -> None:
    if winreg is None:
        return
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
        if enabled:
            winreg.SetValueEx(key, AUTOSTART_NAME, 0, winreg.REG_SZ, startup_command())
        else:
            try:
                winreg.DeleteValue(key, AUTOSTART_NAME)
            except FileNotFoundError:
                pass


class PiggyPet:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("lulu在摸鱼")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#00ff00")
        try:
            self.root.wm_attributes("-transparentcolor", "#00ff00")
        except tk.TclError:
            pass

        self.scale = 0.72
        self.frames_ready = False
        self.loading_frames = False
        self.load_generation = 0
        self.load_queue: queue.Queue[tuple[int, float, object]] = queue.Queue()
        self.frames = self.load_startup_frames()
        self.state = "idle"
        self.frame_index = 0
        self.repeat_left = 0
        self.sequence: list[tuple[str, int]] = []
        self.persistent_action_state: str | None = None
        self.auto_at = time.monotonic() + 30
        self.edge_last_at = 0.0
        self.last_action_index: int | None = None
        self.drag_origin: tuple[int, int] | None = None
        self.drag_start: tuple[int, int] | None = None
        self.drag_last_x: int | None = None
        self.drag_moved = False
        self.speech_window: tk.Toplevel | None = None
        self.speech_after_id: str | None = None

        self.label = tk.Label(self.root, bg="#00ff00", bd=0, highlightthickness=0, cursor="hand2")
        self.label.pack()

        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="\u968f\u673a\u52a8\u4f5c", command=self.random_action)
        self.menu.add_command(label="\u5f85\u673a", command=lambda: self.play("idle"))
        self.action_menu = tk.Menu(self.menu, tearoff=0)
        for label, sequence in ACTIONS:
            self.action_menu.add_command(label=label, command=lambda seq=sequence: self.play_sequence(seq))
        self.menu.add_cascade(label="\u9009\u62e9\u52a8\u4f5c", menu=self.action_menu)
        self.persistent_action_menu = tk.Menu(self.menu, tearoff=0)
        for label, sequence in ACTIONS:
            state = sequence[0][0]
            self.persistent_action_menu.add_command(label=label, command=lambda s=state: self.hold_action(s))
        self.menu.add_cascade(label="\u5e38\u6001\u7ef4\u6301\u52a8\u4f5c", menu=self.persistent_action_menu)
        self.menu.add_command(label="\u53d6\u6d88\u5e38\u6001\u7ef4\u6301", command=self.clear_hold)
        self.menu.add_separator()
        self.menu.add_command(label="\u653e\u5927", command=lambda: self.resize(self.scale + 0.08))
        self.menu.add_command(label="\u7f29\u5c0f", command=lambda: self.resize(max(0.4, self.scale - 0.08)))
        self.menu.add_separator()
        self.menu.add_command(label="\u4f5c\u8005\u8bf4\u660e", command=self.show_author)
        self.menu.add_separator()
        self.autostart_var = tk.BooleanVar(value=is_autostart_enabled())
        self.menu.add_checkbutton(label="\u5f00\u673a\u81ea\u542f\u52a8", variable=self.autostart_var, command=self.toggle_autostart)
        self.menu.add_separator()
        self.menu.add_command(label="\u9000\u51fa", command=self.root.destroy)

        self.label.bind("<Button-1>", self.on_click)
        self.label.bind("<ButtonRelease-1>", self.on_release)
        self.label.bind("<Button-3>", self.show_menu)
        self.label.bind("<B1-Motion>", self.on_drag)

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{sw - 190}+{sh - 260}")
        self.play("idle")
        self.root.after(10, self.start_background_frame_load)

    def load_startup_frames(self) -> dict[str, tuple[list[ImageTk.PhotoImage], int]]:
        image = self.load_pil_frame(0, 0, self.scale)
        photo = ImageTk.PhotoImage(image)
        return {"idle": ([photo], self.delay_for_state("idle", STATES[0][3]))}

    def load_pil_frames(self, scale: float) -> dict[str, tuple[list[Image.Image], int]]:
        sheet_path = app_dir() / SPRITESHEET_NAME
        if not sheet_path.exists():
            binary_name = Path(sys.executable if getattr(sys, "frozen", False) else __file__).name
            raise FileNotFoundError(f"Missing {SPRITESHEET_NAME} next to {binary_name}")
        sheet = Image.open(sheet_path).convert("RGBA")
        frames: dict[str, tuple[list[Image.Image], int]] = {}
        for name, row, count, delay in STATES:
            images = []
            for col in range(count):
                crop = sheet.crop((col * CELL_W, row * CELL_H, (col + 1) * CELL_W, (row + 1) * CELL_H))
                crop = self.trim_cell_edges(crop)
                crop = self.scale_image(crop, scale)
                crop = self.prepare_for_color_key(crop)
                images.append(crop)
            frame_order = STATE_FRAME_ORDERS.get(name, SMOOTH_FRAME_ORDER)
            if len(images) > max(frame_order):
                images = [images[index] for index in frame_order]
            frames[name] = (images, self.delay_for_state(name, delay))
        return frames

    def load_frames(self) -> dict[str, tuple[list[ImageTk.PhotoImage], int]]:
        return self.photo_frames_from_pil(self.load_pil_frames(self.scale))

    def load_pil_frame(self, row: int, col: int, scale: float) -> Image.Image:
        if row == 0 and col == 0:
            startup_path = app_dir() / STARTUP_FRAME_NAME
            if startup_path.exists():
                with Image.open(startup_path) as startup:
                    crop = startup.convert("RGBA")
                crop = self.scale_image(crop, scale)
                return self.prepare_for_color_key(crop)

        sheet_path = app_dir() / SPRITESHEET_NAME
        if not sheet_path.exists():
            binary_name = Path(sys.executable if getattr(sys, "frozen", False) else __file__).name
            raise FileNotFoundError(f"Missing {SPRITESHEET_NAME} next to {binary_name}")
        with Image.open(sheet_path) as sheet:
            sheet = sheet.convert("RGBA")
            crop = sheet.crop((col * CELL_W, row * CELL_H, (col + 1) * CELL_W, (row + 1) * CELL_H))
        crop = self.trim_cell_edges(crop)
        crop = self.scale_image(crop, scale)
        return self.prepare_for_color_key(crop)

    @staticmethod
    def photo_frames_from_pil(frames: dict[str, tuple[list[Image.Image], int]]) -> dict[str, tuple[list[ImageTk.PhotoImage], int]]:
        return {name: ([ImageTk.PhotoImage(image) for image in images], delay) for name, (images, delay) in frames.items()}

    @staticmethod
    def delay_for_state(name: str, fallback: int) -> int:
        if name in STATE_DELAYS:
            return STATE_DELAYS[name]
        if name.startswith("action-"):
            return DEFAULT_ACTION_DELAY
        return fallback

    def scale_image(self, image: Image.Image, scale: float) -> Image.Image:
        width = max(1, int(image.width * scale))
        height = max(1, int(image.height * scale))
        return self.resize_rgba_premultiplied(image, (width, height))

    @staticmethod
    def trim_cell_edges(image: Image.Image) -> Image.Image:
        image = image.convert("RGBA")
        inset_x = min(CELL_EDGE_TRIM_X_PX, image.width // 2)
        inset_y = min(CELL_EDGE_TRIM_Y_PX, image.height // 2)
        if inset_x <= 0 and inset_y <= 0:
            return image
        alpha = image.getchannel("A")
        for offset in range(inset_x):
            for y in range(image.height):
                alpha.putpixel((offset, y), 0)
                alpha.putpixel((image.width - 1 - offset, y), 0)
        for offset in range(inset_y):
            for x in range(image.width):
                alpha.putpixel((x, offset), 0)
                alpha.putpixel((x, image.height - 1 - offset), 0)
        image.putalpha(alpha)
        return image

    @staticmethod
    def resize_rgba_premultiplied(image: Image.Image, size: tuple[int, int]) -> Image.Image:
        image = image.convert("RGBA")
        r, g, b, a = image.split()
        premultiplied = Image.merge(
            "RGBA",
            (
                ImageChops.multiply(r, a),
                ImageChops.multiply(g, a),
                ImageChops.multiply(b, a),
                a,
            ),
        ).resize(size, Image.Resampling.LANCZOS)

        r, g, b, a = premultiplied.split()
        unpremultiplied_channels = []
        for channel in (r, g, b):
            unpremultiplied_channels.append(
                ImageMath.eval("convert((c * 255) / (a + (a == 0)), 'L')", c=channel, a=a)
            )
        return Image.merge("RGBA", (*unpremultiplied_channels, a))

    @staticmethod
    def bleed_transparent_pixels(image: Image.Image) -> Image.Image:
        image = image.convert("RGBA")
        pixels = image.load()
        width, height = image.size
        for y in range(height):
            for x in range(width):
                if pixels[x, y][3] < 8:
                    pixels[x, y] = (255, 208, 196, 0)

        for _ in range(6):
            updates: list[tuple[int, int, tuple[int, int, int, int]]] = []
            for y in range(height):
                for x in range(width):
                    if pixels[x, y][3] != 0:
                        continue
                    neighbors = []
                    for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                        if 0 <= nx < width and 0 <= ny < height and pixels[nx, ny][3] > 0:
                            neighbors.append(pixels[nx, ny])
                    if neighbors:
                        r = sum(px[0] for px in neighbors) // len(neighbors)
                        g = sum(px[1] for px in neighbors) // len(neighbors)
                        b = sum(px[2] for px in neighbors) // len(neighbors)
                        updates.append((x, y, (r, g, b, 0)))
            if not updates:
                break
            for x, y, color in updates:
                pixels[x, y] = color
        return image

    @staticmethod
    def prepare_for_color_key(image: Image.Image) -> Image.Image:
        image = image.convert("RGBA")
        alpha_mask = image.getchannel("A").point(lambda a: 255 if a >= 40 else 0)
        keyed = Image.new("RGB", image.size, TRANSPARENT_COLOR)
        keyed.paste(image.convert("RGB"), mask=alpha_mask)
        keyed.putalpha(Image.new("L", image.size, 255))
        return keyed

    def resize(self, scale: float) -> None:
        self.scale = scale
        self.frames_ready = False
        self.load_generation += 1
        self.loading_frames = False
        self.frames = self.load_startup_frames()
        self.start_background_frame_load()
        if self.persistent_action_state:
            self.hold_action(self.persistent_action_state)
        else:
            self.play(self.state)

    def start_background_frame_load(self) -> None:
        if self.loading_frames:
            return
        self.loading_frames = True
        self.load_generation += 1
        generation = self.load_generation
        scale = self.scale

        def worker() -> None:
            try:
                result = self.load_pil_frames(scale)
                self.load_queue.put((generation, scale, result))
            except Exception as exc:
                self.load_queue.put((generation, scale, exc))

        threading.Thread(target=worker, daemon=True).start()
        self.root.after(50, self.poll_frame_load)

    def poll_frame_load(self) -> None:
        try:
            generation, scale, result = self.load_queue.get_nowait()
        except queue.Empty:
            self.root.after(50, self.poll_frame_load)
            return

        self.loading_frames = False
        if generation != self.load_generation or scale != self.scale:
            if self.loading_frames:
                self.root.after(50, self.poll_frame_load)
            return
        if isinstance(result, Exception):
            raise result
        self.frames = self.photo_frames_from_pil(result)
        self.frames_ready = True

    def play(self, state: str, repeats: int | None = None, clear_hold: bool = True) -> None:
        if clear_hold:
            self.persistent_action_state = None
        self.state = state
        self.frame_index = 0
        self.repeat_left = 999999 if state == "idle" else (repeats if repeats is not None else 2)
        if state == "idle":
            self.sequence = []
            self.auto_at = time.monotonic() + 30

    def play_sequence(self, sequence: list[tuple[str, int]], clear_hold: bool = True) -> None:
        if clear_hold:
            self.persistent_action_state = None
        self.sequence = list(sequence)
        state, repeats = self.sequence.pop(0)
        self.play_state_in_sequence(state, repeats, clear_hold=False)

    def play_state_in_sequence(self, state: str, repeats: int, clear_hold: bool = False) -> None:
        if clear_hold:
            self.persistent_action_state = None
        self.state = state
        self.frame_index = 0
        self.repeat_left = repeats

    def hold_action(self, state: str) -> None:
        self.persistent_action_state = state
        self.sequence = []
        self.play_state_in_sequence(state, 999999)

    def clear_hold(self) -> None:
        self.persistent_action_state = None
        self.play("idle")

    def random_action(self) -> None:
        if not self.frames_ready:
            return
        choices = list(range(len(ACTIONS)))
        if self.last_action_index in choices and len(choices) > 1:
            choices.remove(self.last_action_index)
        index = random.choice(choices)
        self.last_action_index = index
        _, sequence = ACTIONS[index]
        self.play_sequence(sequence)

    def choose_saying(self) -> str:
        if random.random() < 0.35:
            return self.time_saying()
        return random.choice(SAYINGS)

    @staticmethod
    def time_saying() -> str:
        now = time.localtime()
        clock = f"{now.tm_hour:02d}:{now.tm_min:02d}"
        hour = now.tm_hour
        if 5 <= hour < 9:
            options = [
                f"现在是{clock}，早上好，先喝口水吧。",
                f"{clock}啦，新的一天慢慢启动。",
                f"早上{clock}，早餐不要省略哦。",
            ]
        elif 9 <= hour < 12:
            options = [
                f"现在是{clock}，上午适合处理重要任务。",
                f"{clock}，专注一会儿，再伸个懒腰。",
                f"上午{clock}，保存一下当前进度吧。",
            ]
        elif 12 <= hour < 14:
            options = [
                f"现在是{clock}，该考虑午饭啦。",
                f"{clock}，午休和吃饭都很重要。",
                f"中午{clock}，别让胃替你加班。",
            ]
        elif 14 <= hour < 18:
            options = [
                f"现在是{clock}，下午也要记得喝水。",
                f"{clock}，有点困的话站起来走走。",
                f"下午{clock}，先做一个小目标。",
            ]
        elif 18 <= hour < 22:
            options = [
                f"现在是{clock}，晚饭吃了吗？",
                f"{clock}，今天也辛苦啦，慢慢收尾。",
                f"晚上{clock}，别忘了给自己一点休息。",
            ]
        else:
            options = [
                f"现在是{clock}，已经很晚啦，早点睡。",
                f"{clock}，夜猫子模式不建议长期运行。",
                f"深夜{clock}，保存文件，然后休息吧。",
            ]
        return random.choice(options)

    def tk_screen_rect(self) -> ScreenRect:
        return ScreenRect(0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight())

    def monitor_work_areas(self) -> list[ScreenRect]:
        if sys.platform != "win32":
            return [self.tk_screen_rect()]

        try:
            import ctypes
            from ctypes import wintypes

            class RECT(ctypes.Structure):
                _fields_ = [
                    ("left", wintypes.LONG),
                    ("top", wintypes.LONG),
                    ("right", wintypes.LONG),
                    ("bottom", wintypes.LONG),
                ]

            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("rcMonitor", RECT),
                    ("rcWork", RECT),
                    ("dwFlags", wintypes.DWORD),
                ]

            monitors: list[ScreenRect] = []

            def callback(hmonitor, _hdc, _rect, _data) -> int:
                info = MONITORINFO()
                info.cbSize = ctypes.sizeof(MONITORINFO)
                if ctypes.windll.user32.GetMonitorInfoW(hmonitor, ctypes.byref(info)):
                    work = info.rcWork
                    monitors.append(ScreenRect(work.left, work.top, work.right, work.bottom))
                return 1

            monitor_enum_proc = ctypes.WINFUNCTYPE(
                wintypes.BOOL,
                wintypes.HMONITOR,
                wintypes.HDC,
                ctypes.POINTER(RECT),
                wintypes.LPARAM,
            )
            ctypes.windll.user32.EnumDisplayMonitors(0, 0, monitor_enum_proc(callback), 0)
            if monitors:
                return monitors
        except Exception:
            pass

        return [self.tk_screen_rect()]

    def screen_rect_for_bounds(self, x: int, y: int, width: int, height: int) -> ScreenRect:
        monitors = self.monitor_work_areas()

        def overlap_area(rect: ScreenRect) -> int:
            overlap_w = max(0, min(x + width, rect.right) - max(x, rect.left))
            overlap_h = max(0, min(y + height, rect.bottom) - max(y, rect.top))
            return overlap_w * overlap_h

        best = max(monitors, key=overlap_area)
        if overlap_area(best) > 0:
            return best

        center_x = x + width // 2
        center_y = y + height // 2

        def distance_to_rect(rect: ScreenRect) -> int:
            dx = max(rect.left - center_x, 0, center_x - rect.right)
            dy = max(rect.top - center_y, 0, center_y - rect.bottom)
            return dx * dx + dy * dy

        return min(monitors, key=distance_to_rect)

    def current_screen_rect(self) -> ScreenRect:
        self.root.update_idletasks()
        return self.screen_rect_for_bounds(
            self.root.winfo_x(),
            self.root.winfo_y(),
            self.root.winfo_width(),
            self.root.winfo_height(),
        )

    def current_edges(self) -> list[str]:
        self.root.update_idletasks()
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen = self.screen_rect_for_bounds(x, y, width, height)
        edges = []
        if x <= screen.left + EDGE_MARGIN_PX:
            edges.append("left")
        if x + width >= screen.right - EDGE_MARGIN_PX:
            edges.append("right")
        if y <= screen.top + EDGE_MARGIN_PX:
            edges.append("top")
        if y + height >= screen.bottom - EDGE_MARGIN_PX:
            edges.append("bottom")
        return edges

    def snap_to_edges(self, edges: list[str]) -> None:
        if not edges:
            return
        self.root.update_idletasks()
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen = self.screen_rect_for_bounds(x, y, width, height)
        if "left" in edges:
            x = screen.left
        elif "right" in edges:
            x = screen.right - width
        if "top" in edges:
            y = screen.top
        elif "bottom" in edges:
            y = screen.bottom - height
        self.root.geometry(f"+{x}+{y}")
        self.position_speech()

    def trigger_edge_animation(self, force: bool = False) -> bool:
        if not self.frames_ready:
            return False
        edges = self.current_edges()
        if not edges:
            return False
        now = time.monotonic()
        if not force and now - self.edge_last_at < EDGE_ACTION_COOLDOWN:
            return False
        self.edge_last_at = now
        self.snap_to_edges(edges)
        edge = edges[0]
        if edge == "left":
            sequence = [("action-04", 1), ("action-11", 2)]
        elif edge == "right":
            sequence = [("action-03", 1), ("action-11", 2)]
        elif edge == "top":
            sequence = [("action-18", 2), ("action-11", 1)]
        else:
            sequence = [("action-17", 1), ("action-11", 1)]
        self.play_sequence(sequence, clear_hold=False)
        self.show_speech(random.choice(EDGE_SAYINGS[edge]))
        return True

    def on_click(self, event: tk.Event) -> None:
        self.drag_origin = (event.x_root - self.root.winfo_x(), event.y_root - self.root.winfo_y())
        self.drag_start = (event.x_root, event.y_root)
        self.drag_last_x = event.x_root
        self.drag_moved = False

    def on_release(self, event: tk.Event) -> None:
        if self.drag_moved:
            if not self.trigger_edge_animation(force=True):
                if self.persistent_action_state:
                    self.hold_action(self.persistent_action_state)
                else:
                    self.play("idle")
        else:
            self.show_speech(self.choose_saying())
            if not self.persistent_action_state:
                self.random_action()
        self.drag_origin = None
        self.drag_start = None
        self.drag_last_x = None
        self.drag_moved = False

    def on_drag(self, event: tk.Event) -> None:
        if not self.drag_origin:
            return
        if self.drag_start and (abs(event.x_root - self.drag_start[0]) > 3 or abs(event.y_root - self.drag_start[1]) > 3):
            self.drag_moved = True
        ox, oy = self.drag_origin
        self.root.geometry(f"+{event.x_root - ox}+{event.y_root - oy}")
        self.position_speech()
        if not self.frames_ready:
            return
        if self.drag_last_x is None:
            self.drag_last_x = event.x_root
            return
        dx = event.x_root - self.drag_last_x
        self.drag_last_x = event.x_root
        if abs(dx) < 2:
            return
        walk_state = "action-03" if dx > 0 else "action-04"
        if self.state != walk_state:
            self.play_state_in_sequence(walk_state, 999999)

    def show_menu(self, event: tk.Event) -> None:
        self.autostart_var.set(is_autostart_enabled())
        self.menu.tk_popup(event.x_root, event.y_root)

    def toggle_autostart(self) -> None:
        set_autostart(self.autostart_var.get())

    def show_author(self) -> None:
        messagebox.showinfo("\u4f5c\u8005\u8bf4\u660e", AUTHOR_TEXT, parent=self.root)

    def show_speech(self, text: str) -> None:
        if self.speech_after_id:
            self.root.after_cancel(self.speech_after_id)
            self.speech_after_id = None
        if self.speech_window is None or not self.speech_window.winfo_exists():
            self.speech_window = tk.Toplevel(self.root)
            self.speech_window.overrideredirect(True)
            self.speech_window.attributes("-topmost", True)
            self.speech_label = tk.Label(
                self.speech_window,
                bg="#fff8e8",
                fg="#8f4c2d",
                bd=2,
                relief="solid",
                padx=10,
                pady=6,
                font=("Microsoft YaHei UI", 10),
                wraplength=180,
                justify="center",
            )
            self.speech_label.pack()
        self.speech_label.configure(text=text)
        self.position_speech()
        self.speech_window.deiconify()
        self.speech_after_id = self.root.after(4000, self.hide_speech)

    def position_speech(self) -> None:
        if self.speech_window is None or not self.speech_window.winfo_exists():
            return
        self.speech_window.update_idletasks()
        screen = self.current_screen_rect()
        speech_width = self.speech_window.winfo_width()
        speech_height = self.speech_window.winfo_height()
        x = self.root.winfo_x() + max(0, (self.root.winfo_width() - speech_width) // 2)
        x = min(max(screen.left, x), max(screen.left, screen.right - speech_width))
        y = max(screen.top, self.root.winfo_y() - speech_height - 8)
        self.speech_window.geometry(f"+{x}+{y}")

    def hide_speech(self) -> None:
        self.speech_after_id = None
        if self.speech_window is not None and self.speech_window.winfo_exists():
            self.speech_window.withdraw()

    def tick(self) -> None:
        images, delay = self.frames.get(self.state, self.frames["idle"])
        self.label.configure(image=images[self.frame_index])
        self.label.image = images[self.frame_index]

        self.frame_index += 1
        if self.frame_index >= len(images):
            self.frame_index = 0
            if self.state != "idle":
                self.repeat_left -= 1
                if self.repeat_left <= 0:
                    if self.sequence:
                        state, repeats = self.sequence.pop(0)
                        self.play_state_in_sequence(state, repeats)
                    elif self.persistent_action_state:
                        self.play_state_in_sequence(self.persistent_action_state, 999999)
                    else:
                        self.play("idle")
            elif time.monotonic() >= self.auto_at:
                if not self.trigger_edge_animation():
                    self.random_action()

        self.root.after(delay, self.tick)

    def run(self) -> None:
        self.tick()
        self.root.mainloop()


def main() -> None:
    PiggyPet().run()


if __name__ == "__main__":
    main()
