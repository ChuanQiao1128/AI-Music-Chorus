"""
main.py
-------
CLI入口, 显示 "Chorus segment:" 以便 test_main_integration 里断言
"""

import sys
import logging
import argparse

# 不再 from src.audio_processing import load_audio
# 直接 import 模块, 方便 monkeypatch
import src.audio_processing
from src.inference import detect_chorus


def main(argv=None):
    parser = argparse.ArgumentParser(description="Detect chorus from an audio file.")
    parser.add_argument("input_file", type=str, help="Path to the input audio file.")
    parser.add_argument("--output-file", "-o", type=str, default=None, help="Path to save the chorus segment.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logs.")
    args = parser.parse_args(argv)

    # 设定日志级别
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s - %(message)s")

    logging.info(f"Processing {args.input_file} ...")

    try:
        # 重要: 这里用 src.audio_processing.load_audio
        # 而不是 from src.audio_processing import load_audio
        audio_data, sr = src.audio_processing.load_audio(args.input_file)
    except ValueError as e:
        logging.error(f"Cannot load audio: {e}")
        return 1

    try:
        seg = detect_chorus(audio_data, sr)
    except Exception as e:
        logging.error(f"detect_chorus failed: {e}")
        return 1

    dur = seg.duration
    if seg.confidence is not None:
        cfs = f"{seg.confidence:.3f}"
    else:
        cfs = "N/A fallback" if seg.is_fallback else "N/A"

    # 关键 => 打印 "Chorus segment:" => for test_main_integration
    line = f"Chorus segment: start={seg.start:.2f}s, end={seg.end:.2f}s, duration={dur:.2f}s, conf={cfs}"
    print(line)
    logging.info(line)

    # 如指定 --output-file, 则写文件
    if args.output_file:
        try:
            src.audio_processing.save_audio_segment(audio_data, sr, seg.start, seg.end, args.output_file)
        except Exception as ex:
            logging.error(f"Failed saving segment: {ex}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())