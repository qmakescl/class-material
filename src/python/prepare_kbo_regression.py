"""2025 KBO 타석 기록에서 '평균으로의 회귀' 자료 데이터를 만든다.

대상 타자는 **규정타석**(팀당 경기수 x 3.1)을 채운 선수로 정한다. 2025 KBO는 팀당
144경기이므로 144 x 3.1 = 446.4타석이고, 이를 넘는 447타석 이상이 기준이 된다.
"전·후반기 모두 충분히 출전"처럼 분석자가 임의로 정하는 기준을 쓰지 않기 위한
선택이다. 규정타석은 리그가 정한 외부 기준이라 재현 가능하고, 이 코호트는 전원이
전·후반기 양쪽에 충분한 타수를 갖는다(확인 값은 halves.minAB 참고).

출력: docs/assets/data/kbo-regression.js  (window.KBO_REGRESSION)

- halves : 전·후반기 비교. 상·하위 10명의 이동, 같은 방향으로 움직인 선수 수,
  상관계수 두 개, 개별 최대 이동 사례, 상관 설명 산점도용 43명 전원의 타율 쌍(points).
- steps  : 선발에 쓰는 타수 N별 (첫 N타수 타율, 이후 타율) 쌍과 상·하위 25% 집단의
  이동. 타자 집합은 N에 관계없이 고정한다.
- shrink : 분산 분해와 축소추정(전원 평균 / James-Stein / 경험적 베이즈) 예측오차.

주의: 회귀가 향하는 곳은 리그 전체 평균이 아니라 **선발 모집단의 평균**이다.
규정타석 코호트의 평균 타율(cohortAvg)과 리그 전체 타율(leagueAvg)을 함께 담는다.

실행: uv run python src/python/prepare_kbo_regression.py
"""

from __future__ import annotations

import json
import math
import sqlite3
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "datasets" / "kbo_dashboard.sqlite3"
OUT = ROOT / "docs" / "assets" / "data" / "kbo-regression.js"

PA_PER_GAME = 3.1          # 규정타석 계수 (KBO)
HALF_SPLIT = "2025-07-01"  # 전·후반기 경계
CUTS = [20, 45, 75, 100, 150, 200]
SHRINK_CUTS = [45, 100, 200]
PICK = 0.25
TOP_N = 10


def load(con: sqlite3.Connection):
    """타자별 타석수와, 타수만 시간순으로 늘어놓은 안타 여부(0/1) 배열."""
    games = con.execute(
        """select max(c) from (select count(distinct game_pk) c from
             (select home_team t, game_pk from plate_appearances
              union select away_team t, game_pk from plate_appearances) group by t)"""
    ).fetchone()[0]
    pa_count: dict[str, int] = {}
    seq: dict[str, list[int]] = {}
    half: dict[str, dict[str, list[int]]] = {}
    for name, date, is_ab, is_hit in con.execute(
        """select batter_name, game_date, is_ab, is_hit from plate_appearances
           where events is not null and events <> ''
           order by batter_name, game_date, game_pk, at_bat_number"""
    ):
        pa_count[name] = pa_count.get(name, 0) + 1
        if is_ab:
            seq.setdefault(name, []).append(int(is_hit))
            d = half.setdefault(name, {"H1": [], "H2": []})
            d["H1" if date < HALF_SPLIT else "H2"].append(int(is_hit))
    return games, pa_count, seq, half


def corr(xs, ys):
    n = len(xs)
    mx, my = st.mean(xs), st.mean(ys)
    sx, sy = st.stdev(xs), st.stdev(ys)
    return sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / (n - 1) / (sx * sy)


def build_halves(cohort, half, league):
    rec = []
    for n in cohort:
        h1, h2 = half[n]["H1"], half[n]["H2"]
        rec.append({"name": n, "ab1": len(h1), "ab2": len(h2),
                    "a1": sum(h1) / len(h1), "a2": sum(h2) / len(h2)})
    for r in rec:
        r["d"] = r["a2"] - r["a1"]
    cohort_avg = sum(sum(half[n]["H1"]) + sum(half[n]["H2"]) for n in cohort) / \
                 sum(len(half[n]["H1"]) + len(half[n]["H2"]) for n in cohort)
    by1 = sorted(rec, key=lambda r: r["a1"])
    low, high = by1[:TOP_N], by1[-TOP_N:]

    def side(grp, direction):
        return {
            "n": len(grp),
            "before": round(st.mean([r["a1"] for r in grp]), 4),
            "after": round(st.mean([r["a2"] for r in grp]), 4),
            "sameDirection": sum(1 for r in grp if (r["d"] > 0) == (direction > 0)),
            "members": [{"name": r["name"], "ab1": r["ab1"], "a1": round(r["a1"], 4),
                         "ab2": r["ab2"], "a2": round(r["a2"], 4), "d": round(r["d"], 4)}
                        for r in sorted(grp, key=lambda r: r["a1"])],
        }

    return {
        "split": HALF_SPLIT,
        "cohortAvg": round(cohort_avg, 4),
        "leagueAvg": round(league, 4),
        "minAB": {"h1": min(r["ab1"] for r in rec), "h2": min(r["ab2"] for r in rec)},
        "maxAB": {"h1": max(r["ab1"] for r in rec), "h2": max(r["ab2"] for r in rec)},
        "high": side(high, -1),
        "low": side(low, +1),
        # 상관 설명용 산점도: 43명 전원의 (전반기 타율, 후반기 타율)
        "points": [[round(r["a1"], 4), round(r["a2"], 4)] for r in sorted(rec, key=lambda r: r["name"])],
        "rBetween": round(corr([r["a1"] for r in rec], [r["a2"] for r in rec]), 3),
        "rChange": round(corr([r["a1"] for r in rec], [r["d"] for r in rec]), 3),
        "biggestDrop": max(rec, key=lambda r: -r["d"])["name"],
        "biggestRise": max(rec, key=lambda r: r["d"])["name"],
    }


def build_steps(cohort, seq):
    steps = []
    for cut in CUTS:
        before = [sum(seq[n][:cut]) / cut for n in cohort]
        after = [sum(seq[n][cut:]) / len(seq[n][cut:]) for n in cohort]
        k = max(1, round(len(before) * PICK))
        order = sorted(range(len(before)), key=lambda i: before[i])
        low, high = order[:k], order[len(order) - k:]
        hb, ha = st.mean([before[i] for i in high]), st.mean([after[i] for i in high])
        lb, la = st.mean([before[i] for i in low]), st.mean([after[i] for i in low])
        steps.append({
            "cut": cut,
            "pairs": [[round(before[i], 4), round(after[i], 4)] for i in range(len(before))],
            "k": k,
            "high": {"before": round(hb, 4), "after": round(ha, 4)},
            "low": {"before": round(lb, 4), "after": round(la, 4)},
            "gapBefore": round(hb - lb, 4), "gapAfter": round(ha - la, 4),
        })
    return steps


def build_shrink(cohort, seq):
    """분산 분해와 축소추정 예측오차. 실력 분산 추정이 음수면 0으로 잡는다."""
    out = []
    for cut in SHRINK_CUTS:
        before = [sum(seq[n][:cut]) / cut for n in cohort]
        hits = [sum(seq[n][:cut]) for n in cohort]
        truth = [sum(seq[n][cut:]) / len(seq[n][cut:]) for n in cohort]
        k = len(before)
        m = st.mean(before)
        var_obs = st.variance(before)
        var_samp = st.mean([b * (1 - b) / cut for b in before])
        var_true = var_obs - var_samp
        rho = max(0.0, var_true) / var_obs

        y = [math.sqrt(cut) * math.asin(2 * b - 1) for b in before]
        yb = st.mean(y)
        ss = sum((v - yb) ** 2 for v in y)
        shrink = max(0.0, 1 - (k - 3) / ss)
        js = [(math.sin((yb + shrink * (v - yb)) / math.sqrt(cut)) + 1) / 2 for v in y]

        if var_true > 1e-7:
            total = m * (1 - m) / var_true - 1
            a, b_ = m * total, (1 - m) * total
            eb = [(hits[i] + a) / (cut + a + b_) for i in range(k)]
            prior = {"a": round(a, 1), "b": round(b_, 1), "size": round(a + b_)}
        else:
            eb = [m] * k
            prior = None

        sse = lambda p: sum((p[i] - truth[i]) ** 2 for i in range(k))
        raw, grand = sse(before), sse([m] * k)
        out.append({
            "cut": cut, "players": k,
            "sdObs": round(math.sqrt(var_obs), 4),
            "sdSamp": round(math.sqrt(var_samp), 4),
            "sdSkill": round(math.sqrt(max(var_true, 0.0)), 4),
            "skillVarNegative": var_true < 0,
            "rho": round(rho, 3), "jsShrink": round(shrink, 3), "ebPrior": prior,
            "sse": {"raw": round(raw, 4), "grand": round(grand, 4),
                    "js": round(sse(js), 4), "eb": round(sse(eb), 4)},
            "gain": {"grand": round(raw / grand, 2), "js": round(raw / sse(js), 2),
                     "eb": round(raw / sse(eb), 2)},
        })
    return out


def main() -> None:
    with sqlite3.connect(DB) as con:
        games, pa_count, seq, half = load(con)
        league = sum(sum(v) for v in seq.values()) / sum(len(v) for v in seq.values())
    qual_exact = games * PA_PER_GAME
    qual = math.floor(qual_exact) + 1          # 446.4 초과 → 447타석 이상
    cohort = sorted(n for n, c in pa_count.items() if c >= qual and n in seq)

    data = {
        "source": "2025 KBO (slothman3878/kbo_playbyplay, CC BY 4.0)",
        "qualified": {"games": games, "perGame": PA_PER_GAME,
                      "exact": round(qual_exact, 1), "threshold": qual},
        "players": len(cohort),
        "minAB": min(len(seq[n]) for n in cohort),
        "maxAB": max(len(seq[n]) for n in cohort),
        "pick": PICK, "topN": TOP_N,
        "halves": build_halves(cohort, half, league),
        "steps": build_steps(cohort, seq),
        "shrink": build_shrink(cohort, seq),
    }
    data["league"] = data["halves"]["cohortAvg"]   # 위젯 기준선 = 코호트 평균

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "/* 생성 파일 — 직접 수정하지 않는다.\n"
        "   src/python/prepare_kbo_regression.py 가 datasets/kbo_dashboard.sqlite3 에서 만든다. */\n"
        "window.KBO_REGRESSION = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    q, h = data["qualified"], data["halves"]
    print(f"{OUT.relative_to(ROOT)} 생성")
    print(f"■ 규정타석 = {q['games']}경기 x {q['perGame']} = {q['exact']} → {q['threshold']}타석 이상")
    print(f"   대상 {data['players']}명 · 타수 {data['minAB']}~{data['maxAB']}")
    print(f"   전반기 타수 {h['minAB']['h1']}~{h['maxAB']['h1']} · 후반기 {h['minAB']['h2']}~{h['maxAB']['h2']}"
          f"  (전원 양쪽에 타수 있음)")
    print(f"   코호트 평균 타율 {h['cohortAvg']} · 리그 전체 {h['leagueAvg']}")
    print(f"\n■ 전·후반기 (상·하위 {data['topN']}명)")
    print(f"   상위 {h['high']['before']} → {h['high']['after']} ({h['high']['after']-h['high']['before']:+.4f})"
          f"  하락 {h['high']['sameDirection']}/{h['high']['n']}명")
    print(f"   하위 {h['low']['before']} → {h['low']['after']} ({h['low']['after']-h['low']['before']:+.4f})"
          f"  상승 {h['low']['sameDirection']}/{h['low']['n']}명")
    print(f"   corr(전반기,후반기)={h['rBetween']:+.3f}  corr(전반기,변화)={h['rChange']:+.3f}")
    print(f"   최대 상승 {h['biggestRise']} · 최대 하락 {h['biggestDrop']}")
    print(f"\n■ 위젯 (선발 상·하위 {PICK:.0%} = {data['steps'][0]['k']}명)")
    print(f"   {'N':>5} {'상위 전→후':>18} {'하위 전→후':>18} {'선발격차':>9} {'이후격차':>9}")
    for s in data["steps"]:
        print(f"   {s['cut']:>5}   {s['high']['before']:.3f} → {s['high']['after']:.3f}"
              f"      {s['low']['before']:.3f} → {s['low']['after']:.3f}"
              f"   {s['gapBefore']:>+9.3f} {s['gapAfter']:>+9.3f}")
    print(f"\n■ 축소추정")
    print(f"   {'N':>5} {'관측sd':>8} {'표집sd':>8} {'실력sd':>8} {'ρ':>6} {'JSρ̂':>6}"
          f" {'①관측':>9} {'②평균':>9} {'③JS':>9}  개선(②/③)")
    for x in data["shrink"]:
        neg = " *" if x["skillVarNegative"] else ""
        print(f"   {x['cut']:>5} {x['sdObs']:>8.4f} {x['sdSamp']:>8.4f} {x['sdSkill']:>8.4f}{neg}"
              f" {x['rho']:>6.3f} {x['jsShrink']:>6.3f}"
              f" {x['sse']['raw']:>9.4f} {x['sse']['grand']:>9.4f} {x['sse']['js']:>9.4f}"
              f"  {x['gain']['grand']:.2f}배 / {x['gain']['js']:.2f}배")
    print("   * 실력 분산 추정이 음수여서 0으로 잡은 경우")


if __name__ == "__main__":
    main()
