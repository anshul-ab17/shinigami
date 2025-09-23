from shinigami.writer import Writer


def test_write_file(tmp_path):
    w = Writer(tmp_path)
    path = w.write_file("src/main.py", "print('hello')")
    assert path.exists()
    assert path.read_text() == "print('hello')"


def test_is_written_tracks(tmp_path):
    w = Writer(tmp_path)
    assert not w.is_written("src/main.py")
    w.write_file("src/main.py", "code")
    assert w.is_written("src/main.py")


def test_resume_skips_written(tmp_path):
    w1 = Writer(tmp_path)
    w1.write_file("src/main.py", "original")
    # New writer instance loads progress
    w2 = Writer(tmp_path)
    assert w2.is_written("src/main.py")


def test_reset_clears_progress(tmp_path):
    w = Writer(tmp_path)
    w.write_file("src/main.py", "code")
    w.reset()
    assert not w.is_written("src/main.py")
