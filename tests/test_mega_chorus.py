def test_merge_3songs_chorus_info():
    """
    This test specifically processes three songs from tests/songList,
    detects each song's chorus, prints the detailed info, merges them,
    and then prints the merged MP3's size and duration. No other logs.

    Run with: pytest -s tests/test_mega_chorus.py
    so that print output is visible.
    """
    import os
    from pydub import AudioSegment
    from src.audio_processing import load_audio, save_audio_segment
    from src.inference import detect_chorus

    # 1) Define the 3 songs
    songs = [
        "tests/songList/test_sample_01.mp3",
        "tests/songList/test_sample_02.mp3",
        "tests/songList/test_sample_03.mp3"
    ]

    # 2) Prepare output file for the merged result
    out_merged = "tests/songList/mega_chorus.mp3"
    if os.path.exists(out_merged):
        os.remove(out_merged)

    # 3) Merge process
    merged = AudioSegment.empty()

    for idx, song_file in enumerate(songs, start=1):
        # Load audio as array
        audio_data, sr = load_audio(song_file)

        # Detect chorus => get start/end/conf/fallback
        segment = detect_chorus(audio_data, sr, min_duration=15.0, max_duration=30.0, threshold=0.7)

        # Print each song's chorus info
        dur = segment.duration
        fallback_str = "(fallback)" if segment.is_fallback else ""
        conf_str = f"{segment.confidence:.2f}" if segment.confidence is not None else "N/A"
        print(f"Song #{idx}: {song_file}")
        print(f"  Chorus => start={segment.start:.2f}s, end={segment.end:.2f}s, "
              f"duration={dur:.2f}s, conf={conf_str} {fallback_str}")

        # Use pydub to slice from file
        full_audio = AudioSegment.from_file(song_file)
        start_ms = int(segment.start * 1000)
        end_ms = int(segment.end * 1000)
        chorus_part = full_audio[start_ms:end_ms]

        # Append to merged
        merged += chorus_part

    # 4) Export the merged file
    merged.export(out_merged, format="mp3")

    # 5) Print final merged info
    merged_duration_sec = len(merged) / 1000.0
    file_size = os.path.getsize(out_merged) if os.path.exists(out_merged) else 0
    print("\n--- Merged Result ---")
    print(f"Output file: {out_merged}")
    print(f"Final duration: {merged_duration_sec:.2f} seconds")
    print(f"File size: {file_size} bytes\n")