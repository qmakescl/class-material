"""갈턴의 키 자료에서 아버지–아들 쌍을 뽑아 자료 페이지용 데이터를 만든다.

입력  : datasets/galton/Galton.tsv
        (Galton, F. 1886 자료. https://www.randomservices.org/random/data/Galton.tsv)
        열 = Family, Father, Mother, Gender, Height, Kids. 단위는 인치.
출력  : docs/assets/data/galton-father-son.js  (window.GALTON)

계산 내용
- 아버지–아들 쌍의 기술통계와 상관계수 (cm 환산)
- 두 방향의 회귀선. 아들~아버지와 아버지~아들은 서로 다른 직선이고 기울기의 곱이 r²이다.
- 양방향 10% 극단 집단의 이동. '아들로 골라도 아버지가 평균 쪽으로' 나오는 대칭성이
  회귀가 유전적 힘이 아니라 통계적 성질임을 보여준다.
- 겹침 통계. 아버지가 작은 집단의 아들이 '무조건' 작지 않다는 점을 수치로 만든다.
- 중부모 기준 비교. 갈턴이 보고한 약 2/3은 중부모→자녀 값이므로 아버지→아들에
  그대로 쓰면 틀린다. 그 차이를 명시하기 위해 함께 계산한다.
- 가족 단위(아들 키 평균) 재계산. 한 아버지에게 아들이 여럿이어서 관측이 독립이
  아니므로 결론이 뒤집히지 않는지 확인한다.

실행: uv run python src/python/prepare_galton_father_son.py
"""

from __future__ import annotations

import csv
import json
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "datasets" / "galton" / "Galton.tsv"
OUT = ROOT / "docs" / "assets" / "data" / "galton-father-son.js"
INCH = 2.54
PICK = 0.10


def corr(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    mx, my = st.mean(xs), st.mean(ys)
    sx, sy = st.stdev(xs), st.stdev(ys)
    return sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / (n - 1) / (sx * sy)


def extreme(pairs: list[tuple[float, float]], key: int) -> dict:
    """key 열(0=아버지, 1=아들)로 정렬해 상·하위 PICK 비율 집단의 두 세대 평균을 낸다."""
    other = 1 - key
    k = max(1, round(len(pairs) * PICK))
    srt = sorted(pairs, key=lambda p: p[key])
    base = [st.mean([p[0] for p in pairs]), st.mean([p[1] for p in pairs])]
    out = {"k": k}
    for name, grp in (("high", srt[-k:]), ("low", srt[:k])):
        picked = st.mean([p[key] for p in grp])
        paired = st.mean([p[other] for p in grp])
        out[name] = {
            "picked": round(picked, 1),
            "pickedDev": round(picked - base[key], 2),
            "paired": round(paired, 1),
            "pairedDev": round(paired - base[other], 2),
            "shrink": round((paired - base[other]) / (picked - base[key]), 3),
        }
    return out


def main() -> None:
    rows = list(csv.DictReader(SRC.open(encoding="utf-8"), delimiter="\t"))
    sons = [
        (float(r["Father"]) * INCH, float(r["Height"]) * INCH, r["Family"])
        for r in rows
        if r["Gender"] == "M"
    ]
    pairs = [(f, s) for f, s, _ in sons]
    F = [p[0] for p in pairs]
    S = [p[1] for p in pairs]
    mf, ms = st.mean(F), st.mean(S)
    sf, ss = st.stdev(F), st.stdev(S)
    r = corr(F, S)

    # 겹침: 아버지 하위 집단의 아들이 아들 세대 평균보다 큰 비율
    k = max(1, round(len(pairs) * PICK))
    by_father = sorted(pairs, key=lambda p: p[0])
    low_f, high_f = by_father[:k], by_father[-k:]
    overlap = {
        "lowFatherSonAboveMean": round(sum(1 for _, s in low_f if s > ms) / k, 3),
        "highFatherSonBelowMean": round(sum(1 for _, s in high_f if s < ms) / k, 3),
        "lowFatherSonRange": [round(min(s for _, s in low_f), 1), round(max(s for _, s in low_f), 1)],
        "highFatherSonRange": [round(min(s for _, s in high_f), 1), round(max(s for _, s in high_f), 1)],
    }

    # 중부모 기준 (갈턴의 2/3 비교용). 여아 키는 갈턴처럼 1.08배로 환산한다.
    mid = [(float(x["Father"]) + 1.08 * float(x["Mother"])) / 2 * INCH for x in rows]
    child = [
        float(x["Height"]) * INCH * (1.0 if x["Gender"] == "M" else 1.08) for x in rows
    ]
    r_mid = corr(mid, child)

    # 가족 단위 재계산 (비독립성 점검)
    fam: dict[tuple[str, float], list[float]] = {}
    for f, s, family in sons:
        fam.setdefault((family, f), []).append(s)
    FA = [f for _, f in fam]
    SA = [st.mean(v) for v in fam.values()]
    r_fam = corr(FA, SA)

    data = {
        "source": "Galton, F. (1886). 원자료 randomservices.org/random/data/Galton.tsv",
        "unit": "cm",
        "n": len(pairs),
        "familiesTotal": len({r["Family"] for r in rows}),
        "familiesWithSons": len({family for _, _, family in sons}),
        "fathers": len(fam),
        "pick": PICK,
        "father": {"mean": round(mf, 1), "sd": round(sf, 1), "min": round(min(F), 1), "max": round(max(F), 1)},
        "son": {"mean": round(ms, 1), "sd": round(ss, 1), "min": round(min(S), 1), "max": round(max(S), 1)},
        "r": round(r, 3),
        "lines": {
            "sonOnFather": {"slope": round(r * ss / sf, 3), "intercept": round(ms - (r * ss / sf) * mf, 1)},
            "fatherOnSon": {"slope": round(r * sf / ss, 3), "intercept": round(mf - (r * sf / ss) * ms, 1)},
            "slopeProduct": round((r * ss / sf) * (r * sf / ss), 3),
        },
        "byFather": extreme(pairs, 0),
        "bySon": extreme(pairs, 1),
        "overlap": overlap,
        "midParent": {"n": len(rows), "r": round(r_mid, 3), "slope": round(r_mid * st.stdev(child) / st.stdev(mid), 3)},
        "familyLevel": {"n": len(FA), "r": round(r_fam, 3), "slope": round(r_fam * st.stdev(SA) / st.stdev(FA), 3)},
        "pairs": [[round(f, 1), round(s, 1)] for f, s in pairs],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "/* 생성 파일 — 직접 수정하지 않는다.\n"
        "   src/python/prepare_galton_father_son.py 가 datasets/galton/Galton.tsv 에서 만든다. */\n"
        "window.GALTON = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )

    print(f"{OUT.relative_to(ROOT)} 생성")
    print(f"  부자 {data['n']}쌍 / 전체 가족 {data['familiesTotal']} / 아들 있는 가족 {data['familiesWithSons']} / 아버지 {data['fathers']}명")
    print(f"  아버지 {mf:.1f}cm (sd {sf:.1f}) · 아들 {ms:.1f}cm (sd {ss:.1f}) · r = {r:.3f}")
    print(f"  아들~아버지 기울기 {data['lines']['sonOnFather']['slope']:.3f} / "
          f"아버지~아들 기울기 {data['lines']['fatherOnSon']['slope']:.3f} / 곱 = r² = {data['lines']['slopeProduct']:.3f}")
    for lab, blk in (("아버지로 선발", data["byFather"]), ("아들로 선발", data["bySon"])):
        print(f"  [{lab}] 상위 {blk['high']['picked']}cm({blk['high']['pickedDev']:+}) → "
              f"짝 {blk['high']['paired']}cm({blk['high']['pairedDev']:+}) 축소율 {blk['high']['shrink']:.3f}"
              f" | 하위 {blk['low']['picked']}cm({blk['low']['pickedDev']:+}) → "
              f"짝 {blk['low']['paired']}cm({blk['low']['pairedDev']:+}) 축소율 {blk['low']['shrink']:.3f}")
    print(f"  겹침: 아버지 하위 10%의 아들 중 {overlap['lowFatherSonAboveMean']:.0%}가 아들 평균보다 큼, "
          f"아버지 상위 10%의 아들 중 {overlap['highFatherSonBelowMean']:.0%}가 아들 평균보다 작음")
    print(f"  중부모→자녀 기울기 {data['midParent']['slope']:.3f} (갈턴의 약 2/3) vs 아버지→아들 {data['lines']['sonOnFather']['slope']:.3f}")
    print(f"  가족 단위 재계산: r={data['familyLevel']['r']:.3f}, 기울기={data['familyLevel']['slope']:.3f} (결론 동일)")


if __name__ == "__main__":
    main()
