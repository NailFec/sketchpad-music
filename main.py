import os

import librosa
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties
from scipy.fftpack import fft

font_paths = ["C:/USERS/NAIL_/APPDATA/LOCAL/MICROSOFT/WINDOWS/FONTS/LXGWNEOXIHEI.TTF", "C:/Windows/Fonts/msyh.ttc",
              "C:/Windows/Fonts/simsun.ttc", ]

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
    分析WAV文件，使用FFT将其转换为三角函数的组合，并重构信号

    参数:
        file_path: WAV文件路径
        max_harmonics: 用于重构的最大谐波数量

    返回:
        原始信号，重构信号，三角函数参数列表
    """
    # 加载WAV文件
    print(f"正在加载音频文件: {file_path}")
    signal, sample_rate = librosa.load(file_path, sr=None, mono=True)

    samples_to_analyze = min(len(signal), duration * sample_rate)
    signal = signal[:samples_to_analyze]

    # 创建时间轴
    time = np.arange(samples_to_analyze) / sample_rate

    # 执行FFT
    print("执行快速傅里叶变换...")
    fft_result = fft(signal)
    fft_magnitude = np.abs(fft_result[:samples_to_analyze // 2])
    fft_phase = np.angle(fft_result[:samples_to_analyze // 2])

    # 获取频率轴
    frequencies = np.linspace(0, sample_rate / 2, len(fft_magnitude))

    # 找到最强的频率分量
    sorted_indices = np.argsort(fft_magnitude)[::-1]
    top_indices = sorted_indices[:max_harmonics]

    # 提取参数
    amplitudes = fft_magnitude[top_indices] * 2.0 / samples_to_analyze
    freqs = frequencies[top_indices]
    phases = fft_phase[top_indices]

    # 保存三角函数参数
    trig_functions = []
    for i in range(len(top_indices)):
        trig_functions.append({"frequency": freqs[i], "amplitude": amplitudes[i], "phase": phases[i]})

    # 重构信号
    print("重构信号...")
    reconstructed = np.zeros_like(time, dtype=float)
    for i in range(len(top_indices)):
        # 使用余弦函数重构
        reconstructed += amplitudes[i] * np.cos(2 * np.pi * freqs[i] * time + phases[i])

    return signal, reconstructed, trig_functions, sample_rate, time


def display_results(signal, reconstructed, trig_functions, sample_rate, time):
    """显示分析结果"""
    # Clear trig_params.txt file
    open('do.txt', 'w', encoding='utf-8').close()

    # 打印三角函数表达式
    print("\n音乐可以表示为以下三角函数的和:")
    trig_expression = ""
    for i, func in enumerate(trig_functions):
        if func["frequency"] < 0.1:  # 跳过DC分量（接近0Hz的频率）
            continue
        term = f"{func['amplitude']:.4f} * cos(2π * {func['frequency']:.2f}Hz * t + {func['phase']:.4f})"
        if i == 0:
            trig_expression = term
        else:
            trig_expression += f" + {term}"

    print(trig_expression)

    # 打印每个三角函数的参数
    print("\n参与相加的三角函数参数:")
    with open('do.txt', 'a', encoding='utf-8') as f:
        for i, func in enumerate(trig_functions):
            if func["frequency"] < 0.1:  # 跳过DC分量
                continue
            # f.write(f"==No.{i + 1}\n")
            # f.write(f"{func['frequency']:.2f}\n")
            # f.write(f"{func['amplitude']:.4f}\n")
            # f.write(f"{func['phase']:.4f}\n")
            f.write(f"{100*func['amplitude']:.4f}*c2p*{func['frequency']:.4f}*x+{func['phase']:.4f}\n")

    # 绘制原始信号和重构信号
    plt.figure(figsize=(15, 10))

    # 绘制前2秒的波形比较
    plt.subplot(2, 1, 1)
    show_samples = min(int(2 * sample_rate), len(signal))
    plt.plot(time[:show_samples], signal[:show_samples], label='原始信号')
    plt.plot(time[:show_samples], reconstructed[:show_samples], label='重构信号', alpha=0.7)
    plt.title('原始信号与重构信号比较 (前2秒)')
    plt.xlabel('时间 (秒)')
    plt.ylabel('振幅')
    plt.legend()
    plt.grid(True)

    # 绘制频谱
    plt.subplot(2, 1, 2)
    full_fft = np.abs(fft(signal))
    n = len(full_fft)
    freq_axis = np.fft.fftfreq(n, d=1 / sample_rate)
    plt.plot(freq_axis[:n // 2], full_fft[:n // 2])
    plt.title('信号频谱')
    plt.xlabel('频率 (Hz)')
    plt.ylabel('振幅')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("fft_analysis_result.png")
    plt.show()

    # 保存重构信号
    sf.write("output.wav", reconstructed, sample_rate)
    print("\n重构信号已保存为 'output.wav'")


def main():
    # 用户输入文件路径
    file_path = "ys2.wav"
    max_harmonics = int(input("请输入要使用的谐波数量 (推荐: 10-100): "))
    duration = int(input("请输入要分析的前几秒 (推荐：5-10): "))

    # 分析WAV文件
    signal, reconstructed, trig_functions, sample_rate, time = analyze_wav_with_fft(file_path, max_harmonics, duration)

    # 显示结果
    display_results(signal, reconstructed, trig_functions, sample_rate, time)


if __name__ == "__main__":
    main()
