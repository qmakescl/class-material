"""2025 KBO 기록에서 함정 2(표집)·함정 3(층화) 자료 페이지용 데이터를 만든다.

출력: docs/assets/data/kbo-traps23.js  (window.KBO_TRAPS23)

담는 내용
- sizeBias : 크기 편향을 볼 수 있는 실측 수량 5종. 각 수량마다 단위 기준 평균과
  크기 편향 평균(Σn²/Σn), 모집단 분산, 막대용 분포를 담는다. 편향량이 정확히
  σ²/μ라는 항등식을 여러 실측 사례에서 확인할 수 있게 한다.
  ※ 항등식에는 모집단 분산(ddof=0)을 쓴다. 표본분산(ddof=1)을 쓰면 작은 표본에서
     값이 맞지 않는다.
- gameExample : 손으로 검산할 수 있는 실제 한 경기의 투수별 투구수.
- simpson : 층화 변수별 심슨 역전 쌍 개수와 대표 쌍. 선수 간 '타수 배분'의 산포
  (비중 표준편차)를 함께 담아, 배분이 고른 층화에서는 역전이 안 나온다는 것을 보인다.
- willRogers : '주전' 기준 타수를 바꿀 때 두 집단 평균이 같은 방향으로 움직이는 현상.
  선수 구성은 그대로이고 분류 기준만 바뀐다(병기 이동과 같은 구조).

실행: uv run python src/python/prepare_kbo_traps23.py
"""

from __future__ import annotations

import json
import sqlite3
import statistics as st
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "datasets" / "kbo_dashboard.sqlite3"
OUT = ROOT / "docs" / "assets" / "data" / "kbo-traps23.js"

FASTBALLS = ("4-Seam Fastball", "Sinker", "Cutter")
MIN_SPLIT_AB = 40
MIN_TOTAL_AB = 250


def size_bias(counts: list[int], key: str, label: str, unit_a: str, unit_b: str, bins: list[int]) -> dict:
    """P(선택) ∝ 값 인 표집에서 관측 평균이 μ + σ²/μ 가 되는 것을 실측으로 담는다."""
    n = len(counts)
    total = sum(counts)
    mu = total / n
    var = sum((c - mu) ** 2 for c in counts) / n          # 모집단 분산
    biased = sum(c * c for c in counts) / total
    hist = []
    for i, lo in enumerate(bins):
        hi = bins[i + 1] if i + 1 < len(bins) else None
        cnt = sum(1 for c in counts if c >= lo and (hi is None or c < hi))
        hist.append({"lo": lo, "hi": hi, "n": cnt})
    return {
        "key": key, "label": label, "unitA": unit_a, "unitB": unit_b,
        "n": n, "mean": round(mu, 3), "biased": round(biased, 3),
        "ratio": round(biased / mu, 3), "var": round(var, 3),
        "biasTerm": round(var / mu, 3), "hist": hist,
    }


def build_size_bias(con: sqlite3.Connection) -> list[dict]:
    q = lambda sql: [r[0] for r in con.execute(sql)]
    pa_where = "where events is not null and events <> ''"
    return [
        size_bias(q("select count(*) from pitches group by game_pk, at_bat_number"),
                  "pitchesPerPA", "타석당 투구수", "타석", "투구", [1, 2, 3, 4, 5, 6, 7, 8, 10]),
        size_bias(q(f"select count(*) from plate_appearances {pa_where} group by game_pk, inning, inning_topbot"),
                  "paPerInning", "이닝(반이닝)당 타석수", "이닝", "타석", [1, 3, 4, 5, 6, 7, 8, 10]),
        size_bias(q("select count(*) from pitches group by game_pk, pitcher_name"),
                  "pitchesPerAppearance", "한 경기 투수 1명의 투구수", "등판", "투구", [1, 10, 20, 30, 50, 70, 90, 110]),
        size_bias(q(f"select count(*) from plate_appearances {pa_where} group by batter_name"),
                  "paPerBatter", "타자별 시즌 타석수", "타자", "타석", [1, 20, 50, 100, 200, 300, 400, 500]),
        size_bias(q("select count(*) from pitches group by pitcher_name"),
                  "pitchesPerPitcher", "투수별 시즌 투구수", "투수", "투구", [1, 50, 150, 400, 800, 1200, 1800, 2400]),
    ]


def build_game_example(con: sqlite3.Connection) -> dict:
    """투수 5명이 나오고 투구수 편차가 큰 실제 경기 하나 — 손으로 검산할 수 있게."""
    rows = con.execute(
        """select game_pk, pitcher_name, count(*) n from pitches group by 1, 2"""
    ).fetchall()
    per: dict[str, list[tuple[str, int]]] = {}
    for gp, name, n in rows:
        per.setdefault(gp, []).append((name, n))
    best = None
    for gp, lst in per.items():
        if len(lst) != 5:
            continue
        counts = [n for _, n in lst]
        mu = sum(counts) / 5
        score = max(counts) / mu
        if best is None or score > best[0]:
            best = (score, gp, sorted(lst, key=lambda t: -t[1]))
    _, gp, lst = best
    date, home, away = con.execute(
        "select game_date, home_team, away_team from pitches where game_pk=? limit 1", (gp,)
    ).fetchone()
    counts = [n for _, n in lst]
    total = sum(counts)
    mu = total / len(counts)
    var = sum((c - mu) ** 2 for c in counts) / len(counts)
    return {
        "date": date, "home": home, "away": away,
        "pitchers": [{"name": nm, "n": n} for nm, n in lst],
        "total": total, "mean": round(mu, 2), "var": round(var, 2),
        "biased": round(sum(c * c for c in counts) / total, 2),
        "ratio": round((sum(c * c for c in counts) / total) / mu, 2),
    }


def load_splits(con: sqlite3.Connection):
    hand = {
        name: ("우완" if mx < 0 else "좌완")
        for name, mx in con.execute(
            "select pitcher_name, avg(release_pos_x) from pitches where release_pos_x is not null group by 1"
        )
    }
    last_pitch = {
        (gp, ab): ("직구계열" if pn in FASTBALLS else "변화구")
        for gp, ab, pn in con.execute(
            """select p.game_pk, p.at_bat_number, p.pitch_name from pitches p
               join (select game_pk, at_bat_number, max(pitch_number) mp from pitches group by 1,2) m
                 on p.game_pk=m.game_pk and p.at_bat_number=m.at_bat_number and p.pitch_number=m.mp"""
        )
    }
    rows = con.execute(
        """select game_pk, at_bat_number, game_date, batter_name, pitcher_name,
                  inning_topbot, on_2b, on_3b, is_hit
           from plate_appearances
           where events is not null and events <> '' and is_ab = 1"""
    ).fetchall()
    recs = []
    for gp, ab, date, bat, pit, tb, b2, b3, hit in rows:
        recs.append({
            "b": bat, "hit": int(hit),
            "투수손": hand.get(pit),
            "시기": "전반기" if date < "2025-07-01" else "후반기",
            "홈원정": "홈" if tb == "bot" else "원정",
            "득점권": "득점권" if (b2 or b3) else "비득점권",
            "구종": last_pitch.get((gp, ab)),
        })
    return recs


def simpson_for(recs: list[dict], col: str, levels: tuple[str, str], label: str, note_level: str) -> dict:
    agg: dict[str, dict[str, list[int]]] = {}
    for r in recs:
        lv = r[col]
        if lv is None:
            continue
        d = agg.setdefault(r["b"], {l: [0, 0] for l in levels})
        d[lv][0] += 1
        d[lv][1] += r["hit"]
    players = {}
    for name, d in agg.items():
        ab = sum(d[l][0] for l in levels)
        if ab < MIN_TOTAL_AB or any(d[l][0] < MIN_SPLIT_AB for l in levels):
            continue
        players[name] = d
    shares = [agg[n][note_level][0] / sum(agg[n][l][0] for l in levels) for n in players]
    pairs = []
    for a, b in combinations(players, 2):
        for x, y in ((a, b), (b, a)):
            dx, dy = players[x], players[y]
            if all(dx[l][1] / dx[l][0] > dy[l][1] / dy[l][0] for l in levels):
                tx = sum(dx[l][1] for l in levels) / sum(dx[l][0] for l in levels)
                ty = sum(dy[l][1] for l in levels) / sum(dy[l][0] for l in levels)
                if tx < ty:
                    pairs.append((ty - tx, x, y))
                break
    pairs.sort(reverse=True)

    def side(name):
        d = players[name]
        ab = sum(d[l][0] for l in levels)
        h = sum(d[l][1] for l in levels)
        return {
            "name": name,
            "levels": [{"level": l, "ab": d[l][0], "h": d[l][1],
                        "avg": round(d[l][1] / d[l][0], 4),
                        "share": round(d[l][0] / ab, 3)} for l in levels],
            "ab": ab, "h": h, "avg": round(h / ab, 4),
        }

    top = None
    if pairs:
        _, x, y = pairs[0]
        top = {"better": side(x), "worse": side(y), "gap": round(pairs[0][0], 4)}
    return {
        "col": col, "label": label, "levels": list(levels), "noteLevel": note_level,
        "players": len(players), "reversals": len(pairs),
        "shareMean": round(st.mean(shares), 3), "shareSd": round(st.stdev(shares), 3),
        "shareMin": round(min(shares), 3), "shareMax": round(max(shares), 3),
        "top": top,
    }


def build_will_rogers(con: sqlite3.Connection) -> dict:
    avgs = {}
    for name, h, ab in con.execute(
        """select batter_name, sum(is_hit), count(*) from plate_appearances
           where events is not null and events <> '' and is_ab = 1 group by 1"""
    ):
        if ab >= 100:
            avgs[name] = (h / ab, ab)
    def split(t):
        a = [v for v, ab in avgs.values() if ab >= t]
        b = [v for v, ab in avgs.values() if ab < t]
        return a, b
    steps = []
    for t in (450, 400, 350, 300, 250):
        a, b = split(t)
        steps.append({"threshold": t, "starters": len(a), "backups": len(b),
                      "starterAvg": round(st.mean(a), 4), "backupAvg": round(st.mean(b), 4)})
    return {
        "total": len(avgs),
        "poolAvg": round(st.mean([v for v, _ in avgs.values()]), 4),
        "steps": steps,
    }


def main() -> None:
    with sqlite3.connect(DB) as con:
        recs = load_splits(con)
        data = {
            "source": "2025 KBO (slothman3878/kbo_playbyplay, CC BY 4.0)",
            "sizeBias": build_size_bias(con),
            "gameExample": build_game_example(con),
            "simpson": [
                simpson_for(recs, "시기", ("전반기", "후반기"), "전반기 / 후반기", "후반기"),
                simpson_for(recs, "투수손", ("우완", "좌완"), "우완 / 좌완 투수 상대", "좌완"),
                simpson_for(recs, "구종", ("직구계열", "변화구"), "직구계열 / 변화구 상대", "변화구"),
                simpson_for(recs, "득점권", ("비득점권", "득점권"), "비득점권 / 득점권", "득점권"),
                simpson_for(recs, "홈원정", ("원정", "홈"), "원정 / 홈", "홈"),
            ],
            "willRogers": build_will_rogers(con),
            "minSplitAB": MIN_SPLIT_AB,
            "minTotalAB": MIN_TOTAL_AB,
        }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "/* 생성 파일 — 직접 수정하지 않는다.\n"
        "   src/python/prepare_kbo_traps23.py 가 datasets/kbo_dashboard.sqlite3 에서 만든다. */\n"
        "window.KBO_TRAPS23 = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"{OUT.relative_to(ROOT)} 생성\n")
    print("■ 크기 편향 (μ + σ²/μ 항등식 검산)")
    for s in data["sizeBias"]:
        ident = s["mean"] + s["biasTerm"]
        ok = "일치" if abs(ident - s["biased"]) < 0.02 else f"불일치({ident:.3f})"
        print(f"   {s['label']:24s} n={s['n']:>6,}  {s['unitA']} {s['mean']:8.2f} → {s['unitB']} {s['biased']:8.2f}"
              f"  배율 {s['ratio']:.2f}  μ+σ²/μ={ident:8.2f} {ok}")
    g = data["gameExample"]
    print(f"\n■ 손 검산용 경기: {g['date']} {g['away']}@{g['home']}")
    print("   " + " · ".join(f"{p['name']} {p['n']}구" for p in g["pitchers"]))
    print(f"   투수 기준 {g['mean']}구 / 투구 기준 {g['biased']}구 (배율 {g['ratio']}) "
          f"| μ+σ²/μ = {g['mean']} + {g['var']}/{g['mean']} = {g['mean']+g['var']/g['mean']:.2f}")
    print("\n■ 층화 변수별 심슨 역전")
    print(f"   {'층화':18s} {'대상':>5} {'역전쌍':>6} {'비중 sd':>8} {'비중 범위':>16}  대표 쌍")
    for s in data["simpson"]:
        rep = f"{s['top']['better']['name']} vs {s['top']['worse']['name']} (역전폭 {s['top']['gap']:.4f})" if s["top"] else "—"
        print(f"   {s['label']:18s} {s['players']:>5} {s['reversals']:>6} {s['shareSd']:>8.3f}"
              f" {s['shareMin']:.3f}~{s['shareMax']:.3f}  {rep}")
    w = data["willRogers"]
    print(f"\n■ 윌 로저스 (선수 {w['total']}명 고정, 전체 평균 {w['poolAvg']})")
    for s in w["steps"]:
        print(f"   기준 {s['threshold']}타수: 주전 {s['starters']:>3}명 {s['starterAvg']:.4f} | "
              f"백업 {s['backups']:>3}명 {s['backupAvg']:.4f}")


if __name__ == "__main__":
    main()
