import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
import os
import json
import sys
import subprocess
from config.settings import AppConfig
from service.watermark_service import WatermarkService
from core.watermark_algorithm import apply_watermark
from version import get_app_title

class WatermarkGUI:
    def __init__(self):
        # 创建主窗口
        self.window = tk.Tk()
        self.window.title(get_app_title())
        self.window.geometry("800x600")

        # 初始化配置和服务
        self.config = AppConfig()
        self.watermark_service = WatermarkService(self.config)

        # 初始化变量
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.watermark_path = tk.StringVar()
        self.opacity = tk.DoubleVar(value=self.config.get('opacity', 1.0))
        self.target_width_var = tk.IntVar(value=self.config.get('target_width', 800))
        self.width_option = tk.StringVar(value=self.config.get('width_option', "uniform"))

        # 为变量添加trace回调，当值改变时自动更新预览
        self.target_width_var.trace('w', self.on_setting_changed)
        self.width_option.trace('w', self.on_setting_changed)
        self.opacity.trace('w', self.on_setting_changed)
        self.watermark_path.trace('w', self.on_watermark_changed)
        self.input_folder.trace('w', self.on_input_folder_changed)

        # 创建主框架
        self.create_main_frame()
        
        # 创建状态栏
        self.create_status_bar()
        
        # 加载配置
        self.load_config()
        
        # 预览图片相关变量
        self.preview_image = None
        self.current_preview = None

        # 更新图片列表和预览
        if self.input_folder.get():
            self.update_image_list()

        # 更新预览
        if self.watermark_path.get() and self.input_folder.get():
            self.update_preview()

    def create_main_frame(self):
        """创建主框架"""
        # 创建左右分隔的主框架
        main_frame = ttk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧设置面板
        settings_frame = ttk.Frame(main_frame)
        main_frame.add(settings_frame, weight=1)
        
        # 右侧预览面板
        preview_frame = ttk.Frame(main_frame)
        main_frame.add(preview_frame, weight=2)
        
        # 创建设置面板的控件
        self.create_settings_panel(settings_frame)
        
        # 创建预览面板的控件
        self.create_preview_panel(preview_frame)

    def create_settings_panel(self, parent):
        """创建设置面板"""
        # 水印图片选择
        ttk.Label(parent, text="水印图片（800*800）:").pack(anchor=tk.W, padx=5, pady=2)
        watermark_frame = ttk.Frame(parent)
        watermark_frame.pack(fill=tk.X, padx=5, pady=2)
        watermark_entry = ttk.Entry(watermark_frame, textvariable=self.watermark_path)
        watermark_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        # 绑定水印路径变化事件
        watermark_entry.bind("<KeyRelease>", self.on_setting_changed)
        watermark_entry.bind("<FocusOut>", self.on_setting_changed)
        ttk.Button(watermark_frame, text="选择水印", command=self.select_watermark).pack(side=tk.RIGHT)
        
        # 目标宽度输入
        ttk.Label(parent, text="统一输出图片宽度（像素）:").pack(anchor=tk.W, padx=5, pady=2)
        target_width_entry = ttk.Entry(parent, textvariable=self.target_width_var)
        target_width_entry.pack(fill=tk.X, padx=5, pady=2)
        # 绑定目标宽度变化事件
        target_width_entry.bind("<KeyRelease>", self.on_setting_changed)
        target_width_entry.bind("<FocusOut>", self.on_setting_changed)

        # 选择宽度选项
        width_option_frame = ttk.Frame(parent)  # 新建一个框架
        width_option_frame.pack(anchor=tk.W, padx=5, pady=2)
        uniform_radio = ttk.Radiobutton(width_option_frame, text="统一宽度", variable=self.width_option, value="uniform")
        uniform_radio.pack(side=tk.LEFT)
        uniform_radio.bind("<Button-1>", self.on_setting_changed)

        original_radio = ttk.Radiobutton(width_option_frame, text="保持原始宽度", variable=self.width_option, value="original")
        original_radio.pack(side=tk.LEFT)
        original_radio.bind("<Button-1>", self.on_setting_changed)

        # 透明度
        ttk.Label(parent, text="不透明度:").pack(anchor=tk.W, padx=5, pady=2)
        scale = ttk.Scale(parent, from_=0.0, to=1.0, variable=self.opacity, orient=tk.HORIZONTAL)
        scale.pack(fill=tk.X, padx=5, pady=2)
        scale.bind("<Motion>", self.on_setting_changed)
        scale.bind("<ButtonRelease-1>", self.on_setting_changed)
        
        # 文件夹选择
        ttk.Label(parent, text="输入文件夹:").pack(anchor=tk.W, padx=5, pady=2)
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, padx=5, pady=2)
        input_folder_entry = ttk.Entry(input_frame, textvariable=self.input_folder)
        input_folder_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        # 绑定输入文件夹变化事件
        input_folder_entry.bind("<KeyRelease>", self.on_input_folder_entry_changed)
        input_folder_entry.bind("<FocusOut>", self.on_input_folder_entry_changed)
        ttk.Button(input_frame, text="浏览", command=self.select_input_folder).pack(side=tk.RIGHT)
        
        ttk.Label(parent, text="输出文件夹（默认在原目录）:").pack(anchor=tk.W, padx=5, pady=2)
        output_frame = ttk.Frame(parent)
        output_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Entry(output_frame, textvariable=self.output_folder).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(output_frame, text="浏览", command=self.select_output_folder).pack(side=tk.RIGHT)
        
        # 处理按钮和打开文件夹按钮的容器
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # 处理按钮
        ttk.Button(button_frame, text="开始处理", command=self.start_process).pack(side=tk.LEFT, padx=5)
        
        # 打开输出文件夹按钮
        ttk.Button(button_frame, text="打开输出文件夹", command=self.open_output_folder).pack(side=tk.RIGHT, padx=5)
        
        # 图片列表
        ttk.Label(parent, text="图片列表:").pack(anchor=tk.W, padx=5, pady=2)
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # 创建图片列表和滚动条
        self.image_listbox = tk.Listbox(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_listbox.yview)
        self.image_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定列表选择事件
        self.image_listbox.bind('<<ListboxSelect>>', self.on_select_image)

    def create_preview_panel(self, parent):
        """创建预览面板"""
        # 创建预览画布
        self.preview_canvas = tk.Canvas(parent, bg='white')
        self.preview_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # 绑定画布大小变化事件，当窗口调整大小时重新调整预览
        self.preview_canvas.bind('<Configure>', self.on_canvas_configure)

    def create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.window)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)

    # 事件处理方法
    def select_input_folder(self):
        """选择输入文件夹并更新图片列表"""
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder.set(folder)
            # 自动设置输出文件夹为输入文件夹下的watermarked子文件夹
            self.output_folder.set(os.path.join(folder, 'watermarked'))
            self.update_image_list()

            # 验证输入文件夹是否包含图片
            if not self.update_image_list():
                messagebox.showwarning("警告", "输入文件夹中没有支持的图片文件！")

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)

    def select_watermark(self):
        """选择水印图片"""
        file = filedialog.askopenfilename(filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if file:
            self.watermark_path.set(file)
            self.update_preview()

            # 验证水印图片格式
            if not file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                messagebox.showerror("错误", "请选择有效的水印图片格式！")

    def update_image_list(self):
        """更新图片列表"""
        self.image_listbox.delete(0, tk.END)
        if not self.input_folder.get():
            return False  # 返回 False，表示未更新
        
        # 获取输入文件夹路径
        input_folder_path = self.input_folder.get()
        
        # 调试信息：输出输入文件夹路径
        print(f"输入文件夹路径: {input_folder_path}")
        
        # 获取所有支持的图片文件
        image_files = [f for f in os.listdir(input_folder_path) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'))]
        
        
        # 逐个检查文件类型
        valid_images = []
        for image_file in image_files:
            file_path = os.path.join(input_folder_path, image_file)
            try:
                with Image.open(file_path) as img:
                    img.verify()  # 验证文件是否为有效的图片
                print(f"有效图片: {image_file}")
                valid_images.append(image_file)  # 仅添加有效图片
            except Exception as e:
                print(f"无效图片: {image_file} - 错误: {str(e)}")
        
        if not valid_images:
            return False  # 返回 False，表示没有有效图片
        
        for image_file in valid_images:
            self.image_listbox.insert(tk.END, image_file)
        
        if valid_images:
            self.image_listbox.selection_set(0)
            self.update_preview()
        
        return True  # 返回 True，表示成功更新

    def on_select_image(self, event):
        """当选择图片列表中的项目时更新预览"""
        self.update_preview()

    def update_preview(self):
        """更新预览图像"""
        if not self.input_folder.get():
            return

        selection = self.image_listbox.curselection()
        if not selection:
            return

        image_name = self.image_listbox.get(selection[0])
        image_path = os.path.join(self.input_folder.get(), image_name)

        try:
            # 更新配置以确保预览使用最新设置
            self.config.update(
                watermark_path=self.watermark_path.get(),
                opacity=self.opacity.get(),
                target_width=self.target_width_var.get(),
                width_option=self.width_option.get()
            )

            # 使用服务创建预览，确保与实际处理逻辑一致
            watermarked = self.watermark_service.create_preview(image_path)

            if not watermarked:
                # 如果服务返回None，则直接显示原图
                watermarked = Image.open(image_path)

            if watermarked:
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()

                if canvas_width > 1 and canvas_height > 1:
                    ratio = min(canvas_width / watermarked.width, canvas_height / watermarked.height)
                    new_size = (int(watermarked.width * ratio), int(watermarked.height * ratio))
                    watermarked = watermarked.resize(new_size, Image.Resampling.LANCZOS)

                    self.preview_image = ImageTk.PhotoImage(watermarked)
                    self.preview_canvas.delete("all")
                    self.preview_canvas.create_image(
                        canvas_width / 2,
                        canvas_height / 2,
                        image=self.preview_image,
                        anchor=tk.CENTER
                    )
        except Exception as e:
            messagebox.showerror("错误", f"预览失败: {str(e)}")

    def open_output_folder(self):
        """打开输出文件夹"""
        output_folder = self.output_folder.get() or os.path.join(self.input_folder.get(), 'images')
        if not os.path.exists(output_folder):
            messagebox.showerror("错误", "输出文件夹不存在！")
            return
        
        try:
            # 根据操作系统打开文件夹
            if sys.platform == 'win32':
                os.startfile(output_folder)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', output_folder])
            else:  # linux
                subprocess.run(['xdg-open', output_folder])
        except Exception as e:
            messagebox.showerror("错误", f"打开文件夹失败: {str(e)}")

    def start_process(self):
        """开始处理图片，显示进度"""
        if not self.validate_inputs():
            return
        
        try:
            self.status_var.set("处理中...")
            self.window.update()

            # 更新配置
            self.config.update(
                input_folder=self.input_folder.get(),
                output_folder=self.output_folder.get(),
                watermark_path=self.watermark_path.get(),
                opacity=self.opacity.get(),
                target_width=self.target_width_var.get(),
                width_option=self.width_option.get()
            )

            # 定义进度回调函数
            def progress_callback(current, total, filename):
                self.status_var.set(f"正在处理: {filename}")
                self.progress_var.set((current / total) * 100)
                self.window.update()

            # 调用服务进行处理
            self.watermark_service.process_images_with_progress(progress_callback)

            self.status_var.set("处理完成！")
            self.progress_var.set(100)
            if messagebox.askyesno("完成", "图片处理完成！是否打开输出文件夹？"):
                self.open_output_folder()
        except Exception as e:
            self.status_var.set("处理出错")
            messagebox.showerror("错误", f"处理失败: {str(e)}")

    def validate_inputs(self):
        """验证输入参数"""
        if not self.input_folder.get():
            messagebox.showerror("错误", "请选择输入文件夹！")
            return False
            
        if not self.watermark_path.get():
            messagebox.showerror("错误", "请选择水印图片！")
            return False
            
        try:
            opacity = float(self.opacity.get())
            if not 0 <= opacity <= 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("错误", "不透明度必须在0-1之间！")
            return False
        
        return True

    def get_app_path(self):
        """获取应用程序所在目录"""
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe文件
            return os.path.dirname(sys.executable)
        else:
            # 如果是脚本文件
            return os.path.dirname(os.path.abspath(__file__))

    def save_config(self):
        """保存配置到文件"""
        self.config.update(
            watermark_path=self.watermark_path.get(),
            opacity=self.opacity.get(),
            target_width=self.target_width_var.get(),
            width_option=self.width_option.get()
        )
        self.config.save()

    def load_config(self):
        """从文件加载配置"""
        self.config.load()
        self.watermark_path.set(self.config.get('watermark_path', ''))
        self.opacity.set(self.config.get('opacity', 1.0))
        self.target_width_var.set(self.config.get('target_width', 800))
        self.width_option.set(self.config.get('width_option', 'uniform'))

    def on_setting_changed(self, *args):
        """当设置改变时更新预览"""
        # 使用after方法延迟更新，避免频繁刷新
        if hasattr(self, '_update_timer'):
            self.window.after_cancel(self._update_timer)
        self._update_timer = self.window.after(100, self.update_preview)

    def on_watermark_changed(self, *args):
        """当水印路径改变时更新预览"""
        # 验证水印文件是否存在
        watermark_path = self.watermark_path.get()
        if watermark_path and os.path.exists(watermark_path):
            self.on_setting_changed()

    def on_input_folder_changed(self, *args):
        """当输入文件夹路径改变时更新图片列表"""
        # 使用after方法延迟更新，避免频繁刷新
        if hasattr(self, '_folder_update_timer'):
            self.window.after_cancel(self._folder_update_timer)
        self._folder_update_timer = self.window.after(500, self._delayed_folder_update)

    def on_input_folder_entry_changed(self, *args):
        """当用户在输入框中手动输入文件夹路径时"""
        # 验证路径是否存在
        folder_path = self.input_folder.get()
        if folder_path and os.path.exists(folder_path) and os.path.isdir(folder_path):
            self.on_input_folder_changed()

    def _delayed_folder_update(self):
        """延迟更新文件夹内容"""
        folder_path = self.input_folder.get()
        if folder_path and os.path.exists(folder_path) and os.path.isdir(folder_path):
            # 自动设置输出文件夹
            if not self.output_folder.get():
                self.output_folder.set(os.path.join(folder_path, 'watermarked'))
            self.update_image_list()

    def on_canvas_configure(self, event):
        """当画布大小改变时重新调整预览"""
        # 使用after方法延迟更新，避免频繁刷新
        if hasattr(self, '_canvas_update_timer'):
            self.window.after_cancel(self._canvas_update_timer)
        self._canvas_update_timer = self.window.after(200, self.update_preview)

    def run(self):
        """运行主循环"""
        self.window.mainloop()
        self.save_config()  # 退出时保存配置


if __name__ == "__main__":
    app = WatermarkGUI()
    app.run() 