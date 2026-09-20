"""KBO 2025시즌 타석 데이터를 내려받아 로컬 sqlite3 DB로 변환하는 스크립트.

원본: Hugging Face `slothman3878/kbo_playbyplay` (CC BY 4.0, 투구 단위).
이 스크립트는 투구 단위 원본을 타석(plate appearance) 단위로 축약하고,
`is_ab`(타수 여부), `is_hit`(안타 여부)를 부여해 `datasets/kbo_dashboard.sqlite3`에
저장한다. 생성된 DB는 원본 재배포가 아니라 수업용 로컬 도구의 입력 데이터이며,
리포지토리에는 커밋하지 않는다 (.gitignore 처리).

실행:
    uv run python src/python/kbo_dashboard/ingest.py
"""

import sqlite3
import urllib.request
from pathlib import Path

import pandas as pd

DATASET_URL = (
    "https://huggingface.co/datasets/slothman3878/kbo_playbyplay/"
    "resolve/main/v0/kbo_pbp_2025.parquet"
)
DATASET_SOURCE = "slothman3878/kbo_playbyplay (Hugging Face, CC BY 4.0)"
DATASET_PAGE = "https://huggingface.co/datasets/slothman3878/kbo_playbyplay"

DATA_DIR = Path(__file__).resolve().parents[3] / "datasets"
PARQUET_CACHE = DATA_DIR / "kbo_pbp_2025.parquet"
DB_PATH = DATA_DIR / "kbo_dashboard.sqlite3"

# 공식 타수(AB) 판정에서 제외되는 이벤트: 볼넷, 사구, 희생플라이, 희생번트, 타격방해
NON_AB_EVENTS = {"walk", "hit_by_pitch", "sac_fly", "sac_bunt", "catcher_interference"}
HIT_EVENTS = {"single", "double", "triple", "home_run"}

PA_LEVEL_COLUMNS = [
    "game_pk",
    "at_bat_number",
    "game_date",
    "home_team",
    "away_team",
    "inning",
    "inning_topbot",
    "batter_name",
    "pitcher_name",
    "outs_when_up",
    "on_1b",
    "on_2b",
    "on_3b",
    "home_score",
    "away_score",
    "events",
    "runs_scored",
]


def download_parquet(force: bool = False) -> Path:
    """원본 parquet 파일을 datasets/ 아래에 캐시하고 경로를 반환."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if PARQUET_CACHE.exists() and not force:
        return PARQUET_CACHE
    print(f"다운로드 중: {DATASET_URL}")
    urllib.request.urlretrieve(DATASET_URL, PARQUET_CACHE)
    return PARQUET_CACHE


def build_plate_appearance_table(pitch_df: pd.DataFrame) -> pd.DataFrame:
    """투구 단위 DataFrame을 타석 단위로 축약하고 is_ab/is_hit를 부여."""
    pa_df = (
        pitch_df.sort_values(["game_pk", "at_bat_number", "pitch_number"])
        .groupby(["game_pk", "at_bat_number"], as_index=False)
        .last()[PA_LEVEL_COLUMNS]
    )
    pa_df["is_ab"] = (
        pa_df["events"].notna() & ~pa_df["events"].isin(NON_AB_EVENTS)
    ).astype(int)
    pa_df["is_hit"] = pa_df["events"].isin(HIT_EVENTS).astype(int)
    # top = away 공격, bot = home 공격
    pa_df["batting_team"] = pa_df["away_team"].where(
        pa_df["inning_topbot"] == "top", pa_df["home_team"]
    )
    return pa_df


def write_sqlite(pa_df: pd.DataFrame, db_path: Path) -> None:
    """타석 단위 DataFrame을 sqlite3 DB(plate_appearances 테이블)로 저장."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    try:
        pa_df.to_sql("plate_appearances", con, index=False)
        con.execute(
            "CREATE INDEX idx_pa_runners ON plate_appearances(on_1b, on_2b, on_3b)"
        )
        con.execute("CREATE INDEX idx_pa_events ON plate_appearances(events)")
        con.execute("CREATE INDEX idx_pa_team ON plate_appearances(batting_team)")
        con.execute("CREATE INDEX idx_pa_batter ON plate_appearances(batter_name)")
        con.execute(
            """
            CREATE TABLE dataset_meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        con.executemany(
            "INSERT INTO dataset_meta (key, value) VALUES (?, ?)",
            [
                ("source", DATASET_SOURCE),
                ("source_url", DATASET_PAGE),
                ("season", "2025"),
                ("row_count", str(len(pa_df))),
            ],
        )
        con.commit()
    finally:
        con.close()


def main() -> None:
    parquet_path = download_parquet()
    print(f"parquet 로드 중: {parquet_path}")
    pitch_df = pd.read_parquet(parquet_path)
    pa_df = build_plate_appearance_table(pitch_df)
    write_sqlite(pa_df, DB_PATH)

    league_avg = pa_df.loc[pa_df["is_ab"] == 1, "is_hit"].mean()
    risp = pa_df["on_2b"].notna() | pa_df["on_3b"].notna()
    risp_avg = pa_df.loc[risp & (pa_df["is_ab"] == 1), "is_hit"].mean()
    print(f"타석 수: {len(pa_df):,}")
    print(f"리그 전체 타율: {league_avg:.3f}")
    print(f"리그 득점권(2·3루) 타율: {risp_avg:.3f}")
    print(f"DB 저장 완료: {DB_PATH}")


if __name__ == "__main__":
    main()
