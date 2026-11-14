"""skeleton/ 아래의 실습 폴더 뼈대를 zip으로 묶어 docs/downlodable/ 에 둔다.

실행: uv run python src/python/build_skeleton_zip.py [폴더이름 ...]
      폴더 이름을 주지 않으면 skeleton/ 아래의 모든 폴더를 묶는다.
예:   skeleton/categorical-tests/ → docs/downlodable/categorical-tests.zip

- zip 안의 맨 위 폴더는 뼈대의 이름(예: categorical-tests/)이다. 풀면 바로 그 폴더가 생긴다.
- .gitignore, .gitkeep 같은 숨김 파일도 넣는다(빈 폴더를 유지하고 커밋 규칙을 함께 나눠 주려고).
- .DS_Store 는 넣지 않는다. 파일 순서와 시각을 고정해 다시 만들어도 내용이 같으면 같은 zip이 된다.
- 한글 파일 이름은 zip의 UTF-8 표시를 켜서 저장한다(Python zipfile 이 자동으로 한다).
"""

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKELETON = ROOT / "skeleton"
OUT_DIR = ROOT / "docs" / "downlodable"
FIXED_TIME = (2026, 1, 1, 0, 0, 0)
SKIP = {".DS_Store"}


def build(name: str) -> Path:
    """skeleton/<name>/ 을 docs/downlodable/<name>.zip 으로 묶는다."""
    src = SKELETON / name
    if not src.is_dir():
        raise SystemExit(f"뼈대 폴더가 없다: {src}")
    out = OUT_DIR / f"{name}.zip"
    paths = sorted(p for p in src.rglob("*") if p.name not in SKIP)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            arc = f"{name}/{p.relative_to(src).as_posix()}"
            if p.is_dir():
                info = zipfile.ZipInfo(arc + "/", FIXED_TIME)
                info.external_attr = 0o40755 << 16
                zf.writestr(info, "")
            else:
                info = zipfile.ZipInfo(arc, FIXED_TIME)
                info.external_attr = 0o100644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                zf.writestr(info, p.read_bytes())
    return out


def main() -> None:
    names = sys.argv[1:] or sorted(p.name for p in SKELETON.iterdir() if p.is_dir())
    for name in names:
        out = build(name)
        with zipfile.ZipFile(out) as zf:
            files = [i for i in zf.infolist() if not i.is_dir()]
        print(f"{out.relative_to(ROOT)}: 파일 {len(files)}개, {out.stat().st_size:,} 바이트")


if __name__ == "__main__":
    main()
