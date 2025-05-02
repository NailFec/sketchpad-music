import numpy as np
import scipy.io.wavfile as wav
import concurrent.futures
from tqdm import tqdm
import os

# 分块大小（样本数）
BLOCK_SIZE = 2**15
# 保留的最大频率分量数（可调节精度与效率）
MAX_COMPONENTS = 100

def process_block(block_index, block_data, rate):
    N = len(block_data)
    t = np.arange(N) / rate
    fft_result = np.fft.rfft(block_data)
    freqs = np.fft.rfftfreq(N, d=1/rate)

    magnitudes = np.abs(fft_result)
    phases = np.angle(fft_result)

    # 选出前 MAX_COMPONENTS 个频率分量
    indices = np.argsort(magnitudes)[-MAX_COMPONENTS:]
    result_expr = f"Block {block_index}:\n"
    reconstructed = np.zeros_like(block_data, dtype=np.float64)

    for i in indices:
        A = magnitudes[i] / N
        f = freqs[i]
        phi = phases[i]
        result_expr += f"y += {A:.5f} * cos(2π * {f:.2f} * t + {phi:.2f})\n"
        reconstructed += A * np.cos(2 * np.pi * f * t + phi)

    return (block_index, result_expr, reconstructed)

def main():
    rate, data = wav.read("dacapo.wav")

    if data.ndim > 1:
        data = data[:, 0]  # 仅处理单声道

    total_blocks = len(data) // BLOCK_SIZE
    results = [None] * total_blocks
    output_data = []

    with open("do.txt", "w", encoding='utf-8') as f, \
         concurrent.futures.ThreadPoolExecutor() as executor, \
         tqdm(total=total_blocks, desc="Processing blocks") as pbar:

        futures = []

        for i in range(total_blocks):
            block = data[i * BLOCK_SIZE : (i + 1) * BLOCK_SIZE]
            futures.append(executor.submit(process_block, i, block, rate))

        for future in concurrent.futures.as_completed(futures):
            block_index, expr, block_reconstructed = future.result()
            results[block_index] = (expr, block_reconstructed)
            pbar.update(1)

        # 输出公式
        for expr, _ in results:
            f.write(expr + "\n")

        # 合并重建后的音频数据
        for _, block_data in results:
            output_data.extend(block_data)

    output_data = np.array(output_data, dtype=np.int16)
    wav.write("output.ch.wav", rate, output_data)

if __name__ == "__main__":
    main()
