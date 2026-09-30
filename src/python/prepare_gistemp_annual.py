"""NASA GISTEMP 연평균 기온편차를 자료 페이지용 JS 데이터로 만든다.

입력  : datasets/temperature/GLB.Ts+dSST.csv (build_temperature_dataset.py 와 같은 원본)
출력  : docs/assets/data/gistemp-annual.js  (window.GISTEMP_ANNUAL)

연간 집계가 끝나지 않은 최근 해('***')는 제외한다. 파싱 규칙은
build_temperature_dataset.load_annual_anomaly 를 그대로 쓴다.

실행: uv run python src/python/prepare_gistemp_annual.py
"""

from __future__ import annotations

import json
from pathlib import Path

from build_temperature_dataset import SRC_CSV, load_annual_anomaly

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets" / "data" / "gistemp-annual.js"


def main() -> None:
    rows = load_annual_anomaly(SRC_CSV)
    data = {
        "source": "NASA GISS Surface Temperature Analysis (GISTEMP v4), GLB.Ts+dSST J-D",
        "unit": "℃, 1951–1980년 평균 대비 편차",
        "years": [y for y, _ in rows],
        "values": [v for _, v in rows],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "/* 생성 파일 — 직접 수정하지 않는다.\n"
        "   src/python/prepare_gistemp_annual.py 가 datasets/temperature/GLB.Ts+dSST.csv 에서 만든다. */\n"
        f"window.GISTEMP_ANNUAL = {json.dumps(data, ensure_ascii=False, separators=(',', ':'))};\n",
        encoding="utf-8",
    )
    print(f"{len(rows)} years ({rows[0][0]}–{rows[-1][0]}) -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
