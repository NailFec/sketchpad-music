import pytesseract
from PIL import ImageGrab, ImageDraw
import os
import sys

# --- 配置 ---
# 设置 Tesseract 可执行文件的路径
# 这个路径取决于你的操作系统和 Tesseract 的安装位置。
# 请根据你的实际安装路径修改下面这一行！
# 示例：
# Windows: r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# macOS (使用 Homebrew): r'/usr/local/bin/tesseract' 或 r'/opt/homebrew/bin/tesseract' (对于 ARM 芯片)
# Linux: r'/usr/bin/tesseract' 或 r'/usr/local/bin/tesseract'

tesseract_path = None # 请在这里设置你的 Tesseract 路径！

# 尝试根据操作系统提供一些常见路径，但强烈建议手动确认并设置
if sys.platform == "win32":
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if not os.path.exists(tesseract_path):
         # Check 32-bit program files
         tesseract_path = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
elif sys.platform == "darwin": # macOS
    tesseract_path = r'/usr/local/bin/tesseract'
    if not os.path.exists(tesseract_path):
         tesseract_path = r'/opt/homebrew/bin/tesseract' # Newer Homebrew path for ARM Macs
elif sys.platform.startswith("linux"):
    tesseract_path = r'/usr/bin/tesseract'
    if not os.path.exists(tesseract_path):
         tesseract_path = r'/usr/local/bin/tesseract'

# 检查并设置 Tesseract 命令
if tesseract_path and os.path.exists(tesseract_path):
     pytesseract.pytesseract.tesseract_cmd = tesseract_path
     print(f"Using Tesseract executable at: {tesseract_path}")
else:
    print("\n错误：Tesseract 可执行文件路径未正确设置或文件不存在。")
    print(f"请确认您已安装 Tesseract OCR，并修改脚本中的 'tesseract_path' 变量，使其指向正确的 Tesseract 可执行文件位置。")
    print("Tesseract 下载地址：https://tesseract-ocr.github.io/tessdoc/Installation.html")
    # 如果路径错误，后续操作会失败，但我们不在此处直接退出，让用户看到错误信息。


# --- 主逻辑 ---

def find_text_on_screen(target_text="cos"):
    """
    截取屏幕，使用 OCR 查找指定文本，并返回包含该文本的区域的坐标。
    """
    if not tesseract_path or not os.path.exists(tesseract_path):
        print("由于 Tesseract 路径错误，无法执行文字识别。请先修正配置。")
        return None

    try:
        # 1. 截取整个屏幕
        print("正在截取屏幕...")
        screenshot = ImageGrab.grab()
        # 可以选择保存截图进行调试
        # screenshot.save("screenshot.png")

        # 2. 使用 OCR 获取文本和位置信息
        print("正在进行文字识别 (OCR)...这可能需要一些时间。")
        # 使用 image_to_data 可以获取每个识别出的文本块的详细信息，包括位置
        # lang='eng' 可以指定语言，如果屏幕上的文字不是英文，你可能需要安装并指定其他语言包
        data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

        # 3. 处理数据，查找目标文本
        target_locations = []
        n_boxes = len(data['level']) # 识别出的文本块数量

        print(f"分析了 {n_boxes} 个文本块...")

        for i in range(n_boxes):
            # data['text'][i] 是识别出的文本
            # data['conf'][i] 是识别的置信度，可以用来过滤低置信度的结果（可选）
            # data['left'][i], data['top'][i], data['width'][i], data['height'][i] 是文本块的坐标和尺寸

            text = data['text'][i]

            # 检查文本是否非空且包含目标字符串（不区分大小写）
            if text and target_text.lower() in text.lower():
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]

                # 存储识别到的文本和它的坐标（x, y, 宽度, 高度）
                target_locations.append({
                    'text': text,
                    'box': (x, y, w, h)
                })

        return target_locations

    except pytesseract.TesseractNotFoundError:
        print("\n错误：Tesseract OCR 引擎未找到。")
        print("请确认您已正确安装 Tesseract OCR，并且 'tesseract_path' 变量指向了正确的路径。")
        print("Tesseract 下载地址：https://tesseract-ocr.github.io/tessdoc/Installation.html")
        return None # 表示操作失败

    except Exception as e:
        print(f"\n发生未知错误: {e}")
        return None # 表示操作失败


# --- 运行函数并打印结果 ---

if __name__ == "__main__":
    target_string = "cos" # 你要查找的文本

    found_locations = find_text_on_screen(target_string)

    if found_locations is not None: # 检查函数是否成功执行
        if found_locations:
            print(f"\n在屏幕上找到了 '{target_string}' 的以下位置 (x, y, 宽度, 高度):")
            for location in found_locations:
                print(f"  识别文本: '{location['text']}' - 位置: {location['box']}")

            # --- 可选：在截图上绘制找到的框并保存 ---
            # 确保安装了 Pillow
            print("\n正在将找到的区域绘制到截图中...")
            try:
                screenshot_with_boxes = ImageGrab.grab()
                draw = ImageDraw.Draw(screenshot_with_boxes)
                for location in found_locations:
                    x, y, w, h = location['box']
                    # 绘制矩形 (起始x, 起始y, 结束x, 结束y)
                    draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
                screenshot_with_boxes.save(f"screenshot_with_{target_string}_boxes.png")
                print(f"已保存截图文件 'screenshot_with_{target_string}_boxes.png'，其中标记了找到的区域。")
            except Exception as e:
                 print(f"无法在截图中绘制框并保存: {e}")


        else:
            print(f"\n在屏幕上没有找到 '{target_string}'。")