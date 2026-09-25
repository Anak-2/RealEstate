from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
EXAMPLE_PATH = Path(__file__).resolve().parents[2] / ".env.example"


def _read_lines() -> list[str]:
    if ENV_PATH.exists():
        return ENV_PATH.read_text(encoding="utf-8").splitlines()
    if EXAMPLE_PATH.exists():
        return EXAMPLE_PATH.read_text(encoding="utf-8").splitlines()
    return []


def get_env_value(key: str) -> str:
    for line in _read_lines():
        if line.strip().startswith(f"{key}="):
            return line.split("=", 1)[1].strip()
    return ""


def set_env_value(key: str, value: str) -> None:
    lines = _read_lines()
    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}")
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
