import pyautogui
import time

print("3 秒后开始执行...")
time.sleep(3)

with open('do.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.1)
        pyautogui.write(line, interval=0.05)

        pyautogui.click(x=1386, y=718)
        time.sleep(0.1)
