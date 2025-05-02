import os
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
from tqdm import tqdm

# 字体配置支持中文
font_paths = [
    "C:/USERS/NAIL_/APPDATA/LOCAL/MICROSOFT/WINDOWS/FONTS/LXGWNEOXIHEI.TTF",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simsun.ttc",
]

chinese_font = None
for font_path in font_paths:
    if os.path.exists(font_path):
        try:
            chinese_font = FontProperties(fname=font_path)
            break
        except Exception:
            pass

if chinese_font is None:
    chinese_font = FontProperties()

rcParams['font.family'] = chinese_font.get_name()

def analyze_wav_with_fft(file_path, max_harmonics=10, duration=5):
    """
    分析WAV文件，使用FFT转换为三角函数组合，并重构信号。

    参数:
        file_path: WAV文件路径
        max_harmonics: 最大谐波数量
        duration: 分析的音频时长（秒）

    返回:
        原始信号、重构信号、三角函数参数、采样率、时间轴、FFT结果、频率轴
    """
    # 加载音频文件
    print("加载音频文件: {}".format(file_path))
    signal, sample_rate = sf.read(file_path, always_2d=True)
    signal = signal[:, 0] if signal.ndim > 1 else signal  # 转换为单声道
    print("音频加载完成（总体进度：约10%）")

    # 限制分析样本数
    samples_to_analyze = min(len(signal), int(duration * sample_rate))
    signal = signal[:samples_to_analyze]

    # 创建时间轴
    time = np.arange(samples_to_analyze) / sample_rate

    # 执行FFT
    print("执行快速傅里叶变换...")
    fft_result = np.fft.fft(signal)
    fft_magnitude = np.abs(fft_result[:samples_to_analyze // 2])
    fft_phase = np.angle(fft_result[:samples_to_analyze // 2])
    frequencies = np.fft.fftfreq(samples_to_analyze, 1/sample_rate)[:samples_to_analyze // 2]
    print("FFT完成（总体进度：约20%）")

    # 选择最大谐波
    top_indices = np.argpartition(fft_magnitude, -max_harmonics)[-max_harmonics:]
    amplitudes = fft_magnitude[top_indices] * 2.0 / samples_to_analyze
    freqs = frequencies[top_indices]
    phases = fft_phase[top_indices]
    print("谐波选择完成（总体进度：约25%）")

    # 保存三角函数参数
    trig_functions = [
        {"frequency": freqs[i], "amplitude": amplitudes[i], "phase": phases[i]}
        for i in range(len(top_indices))
    ]

    # 向量化重构
    print("重构信号...")
    time_2pi = 2 * np.pi * time
    reconstructed = np.zeros(samples_to_analyze, dtype=float)
    for func in tqdm(trig_functions, desc="处理谐波", unit="harmonic"):
        reconstructed += func["amplitude"] * np.cos(time_2pi * func["frequency"] + func["phase"])
    print("信号重构完成（总体进度：约95%）")

    return signal, reconstructed, trig_functions, sample_rate, time, fft_result, frequencies

def display_results(signal, reconstructed, trig_functions, sample_rate, time, fft_result, frequencies):
    """显示分析结果并保存输出。"""
    # 缓冲三角函数参数
    trig_lines = []
    trig_expression = ""
    for i, func in enumerate(trig_functions):
        if func["frequency"] < 0.1:  # 跳过直流分量
            continue
        term = "{:.4f} * cos(2π * {:.2f}Hz * t + {:.4f})".format(func["amplitude"], func["frequency"], func["phase"])
        trig_expression += term if i == 0 else " + {}".format(term)
        trig_lines.append("{:.4f}*c2p*{:.4f}*x+{:.4f}\n".format(100*func["amplitude"], func["frequency"], func["phase"]))

    # 单次写入文件
    with open('do.txt', 'w', encoding='utf-8') as f:
        f.writelines(trig_lines)

    print("\n音乐可表示为以下三角函数的和:")
    print(trig_expression)

    # 绘图
    plt.figure(figsize=(15, 10))

    # 绘制前2秒波形，降采样加速
    show_samples = min(int(2 * sample_rate), len(signal))
    downsample = 10  # 每10个样本绘制一个点
    plt.subplot(2, 1, 1)
    plt.plot(time[:show_samples:downsample], signal[:show_samples:downsample], label='原始信号')
    plt.plot(time[:show_samples:downsample], reconstructed[:show_samples:downsample], label='重构信号', alpha=0.7)
    plt.title('原始信号与重构信号比较（前2秒）')
    plt.xlabel('时间（秒）')
    plt.ylabel('振幅')
    plt.legend()
    plt.grid(True)

    # 绘制频谱
    plt.subplot(2, 1, 2)
    fft_magnitude = np.abs(fft_result)[:len(signal)//2]
    plt.plot(frequencies, fft_magnitude)
    plt.title('信号频谱')
    plt.xlabel('频率（Hz）')
    plt.ylabel('振幅')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("fft_analysis_result.png")
    plt.close()

    # 保存重构信号
    sf.write("output.wav", reconstructed, sample_rate)
    print("\n重构信号已保存为 'output.wav'")
    print("所有操作完成（总体进度：100%）")

def main():
    file_path = "dacapo.wav"
    max_harmonics = int(input("请输入谐波数量（推荐：10-100）："))
    duration = int(input("请输入分析时长（秒，推荐：5-10）："))
    signal, reconstructed, trig_functions, sample_rate, time, fft_result, frequencies = analyze_wav_with_fft(
        file_path, max_harmonics, duration
    )
    display_results(signal, reconstructed, trig_functions, sample_rate, time, fft_result, frequencies)

if __name__ == "__main__":
    main()