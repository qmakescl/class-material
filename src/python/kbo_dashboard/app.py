"""KBO 2025시즌 타석 데이터 탐색용 로컬 대시보드 (Flask + sqlite3).

`datasets/kbo_dashboard.sqlite3`를 읽어, 팀 · 타자 · 주자 상황(on_1b/2b/3b) ·
타석 결과(events) · 해당 타석 득점(runs_scored)을 선택해 필터링한 결과를 보여준다.
`/viewer`에서는 원본 투구 단위 데이터를 컬럼 변형 없이 그대로 볼 수 있다.
원본 데이터는 재배포하지 않으며, 이 서버는 로컬(127.0.0.1)에서만 실행한다.

사전 준비:
    uv run python src/python/kbo_dashboard/ingest.py

실행:
    uv run python src/python/kbo_dashboard/app.py
    (기본 http://127.0.0.1:5050)
"""

import argparse
import sqlite3
from pathlib import Path

from flask import Flask, g, jsonify, render_template, request

DB_PATH = Path(__file__).resolve().parents[3] / "datasets" / "kbo_dashboard.sqlite3"

TEAM_LABELS = {
    "HH": "한화 이글스",
    "HT": "KIA 타이거즈",
    "KT": "KT 위즈",
    "LG": "LG 트윈스",
    "LT": "롯데 자이언츠",
    "NC": "NC 다이노스",
    "OB": "두산 베어스",
    "SK": "SSG 랜더스",
    "SS": "삼성 라이온즈",
    "WO": "키움 히어로즈",
}

EVENT_LABELS = {
    "single": "1루타",
    "double": "2루타",
    "triple": "3루타",
    "home_run": "홈런",
    "walk": "볼넷",
    "hit_by_pitch": "몸에 맞는 공",
    "strikeout": "삼진",
    "field_out": "야수 아웃",
    "double_play": "병살",
    "triple_play": "삼중살",
    "sac_bunt": "희생번트",
    "sac_fly": "희생플라이",
    "field_error": "실책 출루",
    "fielders_choice": "야수선택",
    "catcher_interference": "포수 방해",
}

app = Flask(__name__)


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        if not DB_PATH.exists():
            raise FileNotFoundError(
                f"{DB_PATH} 가 없습니다. 먼저 "
                "`uv run python src/python/kbo_dashboard/ingest.py`를 실행하세요."
            )
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def dataset_meta() -> dict:
    rows = get_db().execute("SELECT key, value FROM dataset_meta").fetchall()
    return {row["key"]: row["value"] for row in rows}


def runner_clause(param_name: str, column: str, conditions: list, params: list) -> None:
    """on_1b/2b/3b 필터: any(전체) / yes(주자 있음) / no(주자 없음)."""
    value = request.args.get(param_name, "any")
    if value == "yes":
        conditions.append(f"{column} IS NOT NULL")
    elif value == "no":
        conditions.append(f"{column} IS NULL")


def build_filters() -> tuple[str, list]:
    conditions: list[str] = []
    params: list = []

    runner_clause("on_1b", "on_1b", conditions, params)
    runner_clause("on_2b", "on_2b", conditions, params)
    runner_clause("on_3b", "on_3b", conditions, params)

    # 득점권: 2루 또는 3루에 주자가 있는 상황 (1루만 있는 경우는 포함하지 않음)
    risp = request.args.get("risp", "any")
    if risp == "yes":
        conditions.append("(on_2b IS NOT NULL OR on_3b IS NOT NULL)")
    elif risp == "no":
        conditions.append("(on_2b IS NULL AND on_3b IS NULL)")

    events = [e for e in request.args.getlist("event") if e in EVENT_LABELS]
    if events:
        placeholders = ",".join("?" for _ in events)
        conditions.append(f"events IN ({placeholders})")
        params.extend(events)

    runs = request.args.getlist("runs")
    if runs:
        run_conditions = []
        for r in runs:
            if r == "3+":
                run_conditions.append("runs_scored >= 3")
            else:
                run_conditions.append("runs_scored = ?")
                params.append(int(r))
        conditions.append("(" + " OR ".join(run_conditions) + ")")

    team = request.args.get("team", "").strip()
    if team:
        conditions.append("batting_team = ?")
        params.append(team)

    batter = request.args.get("batter", "").strip()
    if batter:
        conditions.append("batter_name = ?")
        params.append(batter)

    where = " AND ".join(conditions) if conditions else "1=1"
    return where, params


@app.route("/")
def index():
    meta = dataset_meta()
    db = get_db()
    codes = [
        row["batting_team"]
        for row in db.execute(
            "SELECT DISTINCT batting_team FROM plate_appearances ORDER BY batting_team"
        ).fetchall()
    ]
    teams = [(code, TEAM_LABELS.get(code, code)) for code in codes]
    return render_template(
        "index.html", meta=meta, event_labels=EVENT_LABELS, teams=teams
    )


def pitch_columns(db: sqlite3.Connection) -> list:
    """`pitches` 테이블의 컬럼 이름을 원본 순서 그대로 반환."""
    return [row["name"] for row in db.execute("PRAGMA table_info(pitches)").fetchall()]


@app.route("/viewer")
def viewer():
    """원본 투구 단위 데이터를 변형 없이 그대로 볼 수 있는 뷰어 페이지."""
    meta = dataset_meta()
    db = get_db()
    return render_template("viewer.html", meta=meta, columns=pitch_columns(db))


@app.route("/api/raw")
def api_raw():
    """`pitches` 테이블(원본 투구 단위)을 페이지 단위로 조회."""
    db = get_db()
    page = max(1, request.args.get("page", 1, type=int) or 1)
    page_size = min(200, max(10, request.args.get("page_size", 50, type=int) or 50))

    conditions: list[str] = []
    params: list = []

    game_date = request.args.get("game_date", "").strip()
    if game_date:
        conditions.append("game_date = ?")
        params.append(game_date)

    batter = request.args.get("batter", "").strip()
    if batter:
        conditions.append("batter_name = ?")
        params.append(batter)

    game_pk = request.args.get("game_pk", "").strip()
    if game_pk:
        conditions.append("game_pk = ?")
        params.append(game_pk)

    where = " AND ".join(conditions) if conditions else "1=1"

    total = db.execute(
        f"SELECT COUNT(*) AS n FROM pitches WHERE {where}", params
    ).fetchone()["n"]

    offset = (page - 1) * page_size
    rows = db.execute(
        f"""
        SELECT * FROM pitches
        WHERE {where}
        ORDER BY game_pk, at_bat_number, pitch_number
        LIMIT ? OFFSET ?
        """,
        [*params, page_size, offset],
    ).fetchall()

    columns = list(rows[0].keys()) if rows else pitch_columns(db)
    total_pages = max(1, (total + page_size - 1) // page_size)

    return jsonify(
        {
            "columns": columns,
            "rows": [list(row) for row in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    )


@app.route("/api/batters")
def api_batters():
    """팀을 고르면 해당 팀 소속 타자 목록만, 없으면 전체 타자 목록을 반환."""
    db = get_db()
    team = request.args.get("team", "").strip()
    if team:
        rows = db.execute(
            """
            SELECT DISTINCT batter_name FROM plate_appearances
            WHERE batting_team = ? AND batter_name IS NOT NULL
            ORDER BY batter_name
            """,
            (team,),
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT DISTINCT batter_name FROM plate_appearances
            WHERE batter_name IS NOT NULL
            ORDER BY batter_name
            """
        ).fetchall()
    return jsonify([row["batter_name"] for row in rows])


def build_monthly_avg(monthly_rows: list, league_monthly_avg: dict) -> list:
    """필터된 월별 집계와 리그 월별 평균을 합쳐 프론트엔드용 목록으로 변환.

    리그 쪽은 모든 월에 데이터가 있으므로, 필터된 쪽에 데이터가 없는 달도
    리그 평균과 나란히 비교할 수 있도록 리그 월 목록을 기준으로 순회한다.
    """
    filtered_by_month = {
        row["month"]: (row["ab"] or 0, row["hit"] or 0)
        for row in monthly_rows
        if row["month"] is not None
    }
    result = []
    for month in sorted(league_monthly_avg):
        ab, hit = filtered_by_month.get(month, (0, 0))
        result.append(
            {
                "month": month,
                "at_bats": ab,
                "hits": hit,
                "avg": round(hit / ab, 3) if ab else None,
                "league_avg": league_monthly_avg[month],
            }
        )
    return result


@app.route("/api/query")
def api_query():
    where, params = build_filters()
    db = get_db()

    count = db.execute(
        f"SELECT COUNT(*) AS n FROM plate_appearances WHERE {where}", params
    ).fetchone()["n"]

    ab_hit = db.execute(
        f"""
        SELECT SUM(is_ab) AS ab, SUM(is_hit) AS hit
        FROM plate_appearances
        WHERE {where}
        """,
        params,
    ).fetchone()
    ab, hit = ab_hit["ab"] or 0, ab_hit["hit"] or 0
    batting_avg = round(hit / ab, 3) if ab else None

    events_rows = db.execute(
        f"""
        SELECT events, COUNT(*) AS n
        FROM plate_appearances
        WHERE {where}
        GROUP BY events
        ORDER BY n DESC
        """,
        params,
    ).fetchall()

    runs_rows = db.execute(
        f"""
        SELECT runs_scored, COUNT(*) AS n
        FROM plate_appearances
        WHERE {where}
        GROUP BY runs_scored
        ORDER BY runs_scored
        """,
        params,
    ).fetchall()

    monthly_rows = db.execute(
        f"""
        SELECT strftime('%m', game_date) AS month, SUM(is_ab) AS ab, SUM(is_hit) AS hit
        FROM plate_appearances
        WHERE {where}
        GROUP BY month
        ORDER BY month
        """,
        params,
    ).fetchall()

    league_row = db.execute(
        "SELECT SUM(is_ab) AS ab, SUM(is_hit) AS hit FROM plate_appearances"
    ).fetchone()
    league_avg = (
        round(league_row["hit"] / league_row["ab"], 3) if league_row["ab"] else None
    )

    league_monthly_rows = db.execute(
        """
        SELECT strftime('%m', game_date) AS month, SUM(is_ab) AS ab, SUM(is_hit) AS hit
        FROM plate_appearances
        GROUP BY month
        ORDER BY month
        """
    ).fetchall()
    league_monthly_avg = {
        row["month"]: round(row["hit"] / row["ab"], 3) if row["ab"] else None
        for row in league_monthly_rows
        if row["month"] is not None
    }

    sample_rows = db.execute(
        f"""
        SELECT game_date, batting_team, batter_name, pitcher_name, inning, inning_topbot,
               on_1b, on_2b, on_3b, events, runs_scored
        FROM plate_appearances
        WHERE {where}
        ORDER BY game_date DESC, game_pk, at_bat_number
        LIMIT 20
        """,
        params,
    ).fetchall()

    return jsonify(
        {
            "count": count,
            "at_bats": ab,
            "hits": hit,
            "batting_avg": batting_avg,
            "league_season_avg": league_avg,
            "monthly_avg": build_monthly_avg(monthly_rows, league_monthly_avg),
            "events_breakdown": [
                {
                    "event": row["events"],
                    "label": EVENT_LABELS.get(row["events"], row["events"] or "(기록 없음)"),
                    "count": row["n"],
                }
                for row in events_rows
            ],
            "runs_breakdown": [
                {"runs_scored": row["runs_scored"], "count": row["n"]} for row in runs_rows
            ],
            "sample_rows": [
                {
                    "game_date": row["game_date"],
                    "batting_team": TEAM_LABELS.get(row["batting_team"], row["batting_team"]),
                    "batter_name": row["batter_name"],
                    "pitcher_name": row["pitcher_name"],
                    "inning": row["inning"],
                    "inning_topbot": row["inning_topbot"],
                    "on_1b": bool(row["on_1b"]),
                    "on_2b": bool(row["on_2b"]),
                    "on_3b": bool(row["on_3b"]),
                    "events": EVENT_LABELS.get(row["events"], row["events"]),
                    "runs_scored": row["runs_scored"],
                }
                for row in sample_rows
            ],
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="KBO 2025 타석 탐색 대시보드")
    parser.add_argument("--host", default="127.0.0.1", help="바인딩할 주소")
    parser.add_argument("--port", default=5050, type=int, help="포트")
    parser.add_argument("--debug", action="store_true", help="Flask 디버그 모드")
    args = parser.parse_args()

    print(f"KBO 대시보드: http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
