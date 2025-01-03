import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage

# 获取正确的资源路径
def resource_path(relative_path):
    """ 获取资源绝对路径 """
    try:
        # PyInstaller创建临时文件夹,将路径存储于_MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 创建主窗口和基本设置
root = tk.Tk()
root.title("交易计算器")
root.geometry("430x610")
root.resizable(False, False)

# 设置窗口图标
icon_path = resource_path(os.path.join("img", "1.png"))
icon = PhotoImage(file=icon_path)
root.iconphoto(False, icon)

# 加载图标
btc_icon = PhotoImage(file=resource_path(os.path.join("img", "delete.png")))
calculator_icon = PhotoImage(file=resource_path(os.path.join("img", "calculator.png")))
copy_icon = PhotoImage(file=resource_path(os.path.join("img", "copy.png")))

# 加载输入框标签图标
buy_icon = PhotoImage(file=resource_path(os.path.join("img", "buy.png")))
sell_icon = PhotoImage(file=resource_path(os.path.join("img", "sell.png")))
increase_icon = PhotoImage(file=resource_path(os.path.join("img", "increase.png")))
btc_label_icon = PhotoImage(file=resource_path(os.path.join("img", "btc.png")))

# 加载杠杆图标
leverage_icon = PhotoImage(file=resource_path(os.path.join("img", "leverage.png")))

# 定义固定的杠杆值
LEVERAGE_VALUES = [1, 3, 5, 10, 20, 50, 75, 100, 125]

def snap_to_nearest(value):
    """将滑动条值吸附到最近的刻度值"""
    value = float(value)
    return min(LEVERAGE_VALUES, key=lambda x: abs(x - value))

def on_leverage_scale_change(value):
    """当滑动条值改变时更新杠杆输入框"""
    try:
        leverage = snap_to_nearest(float(value))
        leverage_entry.delete(0, tk.END)
        leverage_entry.insert(0, str(int(leverage)))
        
        # 更新可持有金额提示 (与合约面值保持一致)
        amount = float(amount_entry.get() if amount_entry.get() else 0)
        position_value = amount * leverage
        leverage_hint.config(text=f"当前杠杆倍数最高可持有: {position_value:.8f} USDT")
        calculate_profit()
    except ValueError:
        pass

def on_leverage_entry_change(event=None):
    """当杠杆输入框值改变时更新滑动条"""
    try:
        value = float(leverage_entry.get())
        if 1 <= value <= 125:
            value = snap_to_nearest(value)
            leverage_scale.set(value)
            
            # 更新可持有金额提示
            amount = float(amount_entry.get() if amount_entry.get() else 0)
            position_value = amount * value
            leverage_hint.config(text=f"当前杠杆倍数最高可持有: {position_value:.8f} USDT")
            calculate_profit()
    except ValueError:
        pass

def calculate_profit():
    """计算盈亏"""
    try:
        if not validate_inputs():
            return
            
        leverage = float(leverage_entry.get())
        open_price = float(open_price_entry.get())
        close_price = float(close_price_entry.get())
        amount = float(amount_entry.get())
        direction = direction_var.get()

        # 计算基础数据
        position_value = amount * leverage
        initial_margin = amount
        maintenance_margin = initial_margin * 0.5

        # 计算价格涨跌幅
        price_movement = ((close_price - open_price) / open_price) * 100

        # 根据方向计算
        if direction == "做多":
            profit = position_value * (close_price - open_price) / open_price
            display_movement = price_movement
            price_change = price_movement
        else:  # 做空
            profit = position_value * (open_price - close_price) / open_price
            display_movement = -price_movement
            price_change = -price_movement

        # 爆仓价格计算
        if direction == "做多":
            liquidation_price = open_price * (1 - 1/leverage * 0.995)
        else:
            liquidation_price = open_price * (1 + 1/leverage * 0.995)
        
        roi = (profit / amount) * 100
        distance_to_liquidation = abs((open_price - liquidation_price) / open_price * 100)

        # 更新显示结果
        result_text = (
            f"盈亏金额: {profit:.8f} USDT\n"
            f"收益率: {roi:.2f}%\n"
            f"爆仓价格: {liquidation_price:.8f} USDT\n"
            f"合约面值: {position_value:.8f} USDT\n"
            f"初始保证金: {initial_margin:.8f} USDT\n"
            f"维持保证金: {maintenance_margin:.8f} USDT\n"
            f"开仓至平仓涨跌: {display_movement:+.2f}%\n"
            f"价格变动: {price_change:.2f}%\n"
            f"距离爆仓: {distance_to_liquidation:.2f}%"
        )
        result_label.config(text=result_text)

    except ValueError:
        result_label.config(text="请输入有效的数字")

def validate_inputs():
    """验证所有输入框是否都已填写"""
    fields = {
        "开仓价格": open_price_entry.get(),
        "平仓价格": close_price_entry.get(),
        "涨跌幅": price_movement_entry.get(),
        "保证金金额": amount_entry.get()
    }
    
    empty_fields = [name for name, value in fields.items() if not value.strip()]
    if empty_fields:
        result_label.config(text=f"请填写: {', '.join(empty_fields)}")
        return False
    return True

def calculate_close_price(event=None):
    try:
        if not price_movement_entry.get():
            return
        open_price = float(open_price_entry.get())
        movement = float(price_movement_entry.get())
        
        close_price = open_price * (1 + movement/100)
        close_price_entry.delete(0, tk.END)
        close_price_entry.insert(0, f"{close_price:.8f}")
        calculate_profit()
    except ValueError:
        pass

def calculate_movement(event=None):
    try:
        if not close_price_entry.get():
            return
        open_price = float(open_price_entry.get())
        close_price = float(close_price_entry.get())
        
        movement = ((close_price - open_price) / open_price) * 100
        price_movement_entry.delete(0, tk.END)
        price_movement_entry.insert(0, f"{movement:+.2f}")
    except ValueError:
        pass

def clear_all():
    """清空所有输入框"""
    leverage_entry.delete(0, tk.END)
    leverage_entry.insert(0, "1")
    leverage_scale.set(1)
    open_price_entry.delete(0, tk.END)
    close_price_entry.delete(0, tk.END)
    price_movement_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    result_label.config(text="等待计算...")

# 添加保证金输入框的事件处理
def on_amount_change(event=None):
    """当保证金金额改变时更新可持有金额"""
    try:
        amount = float(amount_entry.get() if amount_entry.get() else 0)
        leverage = float(leverage_entry.get() if leverage_entry.get() else 1)
        position_value = amount * leverage
        leverage_hint.config(text=f"当前杠杆倍数最高可持有: {position_value:.8f} USDT")
    except ValueError:
        pass

def copy_all():
    """复制所有输入值和计算结果到剪贴板"""
    try:
        # 获取所有输入值
        input_text = (
            f"杠杆: {leverage_entry.get()}\n"
            f"开仓价格: {open_price_entry.get()}\n"
            f"平仓价格: {close_price_entry.get()}\n"
            f"涨跌幅(%): {price_movement_entry.get()}\n"
            f"保证金金额: {amount_entry.get()}\n"
            f"方向: {direction_var.get()}\n"
            f"\n计算结果:\n"
            f"{result_label.cget('text')}"
        )
        
        # 复制到剪贴板
        root.clipboard_clear()
        root.clipboard_append(input_text)
        root.update()  # 确保更新剪贴板
        
        # 显示提示（可选）
        result_label.config(text="已复制到剪贴板!\n\n" + result_label.cget('text'))
    except Exception as e:
        result_label.config(text="复制失败，请重试")

# 创建样式
style = ttk.Style()
style.theme_use('clam')

# 主题颜色
PRIMARY_COLOR = "#1a73e8"  # Google Blue
BG_COLOR = "#f8f9fa"
SECONDARY_BG = "#ffffff"
TEXT_COLOR = "#202124"
BORDER_COLOR = "#dadce0"

# 配置所有样式
style.configure("Main.TFrame", background=BG_COLOR)
style.configure(
    "TEntry",
    fieldbackground=SECONDARY_BG,
    borderwidth=1,
    relief="solid",
    padding=5,
    font=('Microsoft YaHei UI', 9),
    foreground=TEXT_COLOR
)
style.configure(
    "TLabel",
    background=BG_COLOR,
    foreground=TEXT_COLOR,
    font=('Microsoft YaHei UI', 9, 'bold')
)
style.configure(
    "Calculate.TButton",
    padding=(10, 5),
    font=('Microsoft YaHei UI', 9, 'bold'),
    background="#34a853",
    foreground="white"
)
style.configure(
    "Clear.TButton",
    padding=(10, 5),
    font=('Microsoft YaHei UI', 9),
    background="#ea4335",
    foreground="white"
)
style.configure(
    "Copy.TButton",
    padding=(10, 5),
    font=('Microsoft YaHei UI', 9),
    background=PRIMARY_COLOR,
    foreground="white"
)
style.configure(
    "TRadiobutton",
    background=BG_COLOR,
    font=('Microsoft YaHei UI', 9)
)
style.configure(
    "Result.TFrame",
    background=SECONDARY_BG,
    relief="solid",
    borderwidth=1
)
style.configure(
    "Result.TLabel",
    background=SECONDARY_BG,
    font=('Microsoft YaHei UI', 9),
    wraplength=280,
    foreground=TEXT_COLOR
)
style.configure(
    "Horizontal.TScale",
    background=BG_COLOR,
    troughcolor=SECONDARY_BG,
    borderwidth=0,
    sliderthickness=15,
    sliderlength=10
)

# 为滑动条指针添加颜色
style.map(
    "Horizontal.TScale",
    background=[("active", "#1a73e8"), ("!active", "#4caf50")],
    troughcolor=[("active", "#e0f7fa"), ("!active", "#c8e6c9")]
)

# 修改主窗口设置
root.configure(bg=BG_COLOR)

# 创建主框架
main_frame = ttk.Frame(root, padding="10", style="Main.TFrame")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# 创建杠杆控制部分
leverage_frame = ttk.Frame(main_frame, style="Main.TFrame")
leverage_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=3)

leverage_input_frame = ttk.Frame(leverage_frame, style="Main.TFrame")
leverage_input_frame.pack(side="top", fill="x")

# 使用杠杆图标
ttk.Label(leverage_input_frame, text="杠杆:", image=leverage_icon, compound="left").pack(side="left", padx=3)
leverage_entry = ttk.Entry(leverage_input_frame, width=10)
leverage_entry.pack(side="left", padx=3)

scale_frame = ttk.Frame(leverage_frame, style="Main.TFrame")
scale_frame.pack(side="top", fill="x", pady=2)

# 创建滑动条
leverage_scale = ttk.Scale(
    scale_frame,
    from_=LEVERAGE_VALUES[0],
    to=LEVERAGE_VALUES[-1],
    orient="horizontal",
    command=on_leverage_scale_change
)
leverage_scale.pack(fill="x", padx=3, pady=(0, 40))  # 增加底部间距给标签

# 定义要显示的刻度值
SCALE_MARKS = [1, 10, 20, 50, 75, 100, 125]

# 创建刻度标签
for value in SCALE_MARKS:
    label = ttk.Label(
        scale_frame, 
        text=f"{value}x", 
        font=('Microsoft YaHei UI', 8),
        foreground="#5f6368",
        background=BG_COLOR
    )
    
    # 计算相对位置，特殊处理边界值
    if value == 1:
        position = 0
    elif value == 125:
        position = 1
    else:
        position = (value - 1) / (125 - 1)
    
    # 放置标签，使用不同的锚点
    if value == 1:
        anchor = "nw"
    elif value == 125:
        anchor = "ne"
    else:
        anchor = "n"
        
    label.place(
        relx=position,
        rely=0.7,  # 调整标签垂直位置
        anchor=anchor
    )

# 创建杠杆提示标签
leverage_hint = ttk.Label(
    leverage_frame, 
    text="当前杠杆倍数最高可持有: 0.00000000 USDT",
    font=('Microsoft YaHei UI', 8),
    foreground="#5f6368"  # Google Gray
)
leverage_hint.pack(side="top", padx=3)

# 创建其他输入框
entries = [
    ("开仓价格:", open_price_entry := ttk.Entry(main_frame), buy_icon),
    ("平仓价格:", close_price_entry := ttk.Entry(main_frame), sell_icon),
    ("涨跌幅(%):", price_movement_entry := ttk.Entry(main_frame), increase_icon),
    ("保证金金额:", amount_entry := ttk.Entry(main_frame), btc_label_icon)
]

# 布局输入框和标签
for i, (label_text, entry, icon) in enumerate(entries, 1):
    ttk.Label(main_frame, text=label_text, image=icon, compound="left").grid(
        row=i, 
        column=0, 
        padx=8, 
        pady=8, 
        sticky="w"
    )
    entry.grid(
        row=i, 
        column=1, 
        padx=8, 
        pady=8, 
        sticky="ew"
    )
    entry.configure(width=20)

# 方向选择框架
direction_frame = ttk.Frame(main_frame, style="Main.TFrame")
direction_frame.grid(column=0, row=5, columnspan=2, pady=5)
direction_var = tk.StringVar(value="做多")

# 创建做多和做空按钮
long_button = ttk.Radiobutton(
    direction_frame, 
    text="做多", 
    variable=direction_var, 
    value="做多",
    style="Long.TRadiobutton"
)
long_button.pack(side="left", padx=20)

short_button = ttk.Radiobutton(
    direction_frame, 
    text="做空", 
    variable=direction_var, 
    value="做空",
    style="Short.TRadiobutton"
)
short_button.pack(side="left", padx=20)

# 配置做多和做空按钮的样式
style.configure(
    "Long.TRadiobutton",
    background="#a5d6a7",  # 更深的绿色背景
    foreground="#1b5e20",  # 深绿色字体
    font=('Microsoft YaHei UI', 9)
)

style.configure(
    "Short.TRadiobutton",
    background="#ef9a9a",  # 更深的红色背景
    foreground="#b71c1c",  # 深红色字体
    font=('Microsoft YaHei UI', 9)
)

# 按钮框架
button_frame = ttk.Frame(main_frame, style="Main.TFrame")
button_frame.grid(column=0, row=6, columnspan=2, pady=10)

calculate_button = ttk.Button(
    button_frame, 
    text=" 计算", 
    image=calculator_icon, 
    compound="left", 
    command=calculate_profit, 
    style="Calculate.TButton"
)
calculate_button.pack(side="left", padx=3)

clear_button = ttk.Button(
    button_frame, 
    text=" 清空", 
    image=btc_icon, 
    compound="left", 
    command=clear_all, 
    style="Clear.TButton"
)
clear_button.pack(side="left", padx=3)

copy_button = ttk.Button(
    button_frame, 
    text=" 复制", 
    image=copy_icon,  # 使用新的复制图标
    compound="left", 
    command=copy_all, 
    style="Copy.TButton"
)
copy_button.pack(side="left", padx=3)

# 结果显示框架
result_frame = ttk.Frame(main_frame, relief="groove", padding="10", style="Result.TFrame")
result_frame.grid(
    column=0, 
    row=7, 
    columnspan=2, 
    pady=10, 
    padx=8, 
    sticky=(tk.W, tk.E)
)

# 添加阴影效果
def add_shadow(widget):
    widget.configure(relief="solid", borderwidth=1)

add_shadow(result_frame)

result_label = ttk.Label(
    result_frame,
    text="等待计算...",
    justify="left",
    font=('Microsoft YaHei UI', 9),
    wraplength=280
)
result_label.pack(fill="both", expand=True)

# 绑定事件
leverage_entry.bind('<KeyRelease>', on_leverage_entry_change)
close_price_entry.bind('<KeyRelease>', calculate_movement)
price_movement_entry.bind('<KeyRelease>', calculate_close_price)

# 设置初始值
leverage_entry.insert(0, "1")
leverage_scale.set(1)

# 在创建完输入框后添加绑定
amount_entry.bind('<KeyRelease>', on_amount_change)

# 运行主循环
root.mainloop()