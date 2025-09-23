import json
from pathlib import Path

PROGRESS_FILE = ".shinigami-progress.json"


class Writer:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._progress_path = output_dir / PROGRESS_FILE
        self._written: set[str] = set()
        self._load()

    def _load(self):
        if self._progress_path.exists():
            data = json.loads(self._progress_path.read_text())
            self._written = set(data.get("written", []))

    def _save(self):
        self._progress_path.write_text(json.dumps({"written": sorted(self._written)}))

    def write_file(self, rel_path: str, content: str) -> Path:
        full = self.output_dir / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content)
        self._written.add(rel_path)
        self._save()
        return full

    def is_written(self, rel_path: str) -> bool:
        return rel_path in self._written

    def reset(self):
        self._written.clear()
        if self._progress_path.exists():
            self._progress_path.unlink()
