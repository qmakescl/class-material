"""NASA GISTEMP 연간 지구 평균기온 편차를 회귀분석 실습용 xlsx로 정리한다.

원본: datasets/temperature/GLB.Ts+dSST.csv (NASA GISS Surface Temperature
Analysis, GLB.Ts+dSST, 1880년~현재). 월별 편차(℃, 1951-1980년 평균 대비)
표에서 연평균(J-D 열)만 뽑아 "연도-연평균기온편차" 두 열로 정리하고,
자료가 아직 다 채워지지 않은 최근 연도(J-D가 '***')는 제외한다.

출처: NASA GISS Surface Temperature Analysis (GISTEMP v4)
https://data.giss.nasa.gov/gistemp/  (공개 자료, 출처 표기 조건)
GISTEMP Team, 2026: GISS Surface Temperature Analysis (GISTEMP), version 4.
NASA Goddard Institute for Space Studies.
"""

import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import Reference, ScatterChart, Series
from openpyxl.chart.trendline import Trendline
from openpyxl.styles import Alignment, Font

ROOT = Path(__file__).resolve().parents[2]
SRC_CSV = ROOT / "datasets" / "temperature" / "GLB.Ts+dSST.csv"
OUT_XLSX = ROOT / "docs" / "downlodable" / "연간평균기온-실습데이터.xlsx"


def load_annual_anomaly(path: Path) -> list[tuple[int, float]]:
    """NASA GISTEMP CSV에서 (연도, 연평균 기온편차) 쌍만 뽑아 반환한다."""
    with path.open(encoding="utf-8") as f:
        rows = list(csv.reader(f))
    header = rows[1]  # 1행은 "Land-Ocean: Global Means" 제목, 2행이 실제 헤더
    jd_idx = header.index("J-D")
    out = []
    for row in rows[2:]:
        if not row or not row[0].strip().isdigit():
            continue
        value = row[jd_idx].strip()
        if value in ("", "***"):
            continue  # 아직 연간 집계가 끝나지 않은 해(자료 채록 중)는 제외
        out.append((int(row[0]), float(value)))
    return out


def build_workbook(rows: list[tuple[int, float]]) -> Workbook:
    wb = Workbook()
    ws = wb.active
    ws.title = "데이터"
    ws.append(["연도", "지구 연평균기온편차 (℃, 1951-1980 평균 대비)"])
    for cell in ws[1]:
        cell.font = Font(bold=True)
    for year, value in rows:
        ws.append([year, value])
    ws.column_dimensions["A"].width = 10
    ws.column_dimensions["B"].width = 34
    ws["A1"].alignment = Alignment(horizontal="center")

    chart = ScatterChart()
    chart.title = "지구 연평균기온편차 추이"
    chart.x_axis.title = "연도"
    chart.y_axis.title = "기온편차 (℃)"
    chart.height, chart.width = 10, 18
    n = len(rows)
    xvalues = Reference(ws, min_col=1, min_row=2, max_row=1 + n)
    yvalues = Reference(ws, min_col=2, min_row=1, max_row=1 + n)
    series = Series(yvalues, xvalues, title_from_data=True)
    series.marker.symbol = "circle"
    series.marker.size = 4
    series.graphicalProperties.line.noFill = True
    series.trendline = Trendline(trendlineType="linear", dispEq=True, dispRSqr=True)
    chart.series.append(series)
    ws.add_chart(chart, "D2")

    note = wb.create_sheet("설명")
    lines = [
        ["출처", "NASA GISS Surface Temperature Analysis (GISTEMP v4)"],
        ["원본 URL", "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"],
        ["인용", "GISTEMP Team, 2026: GISS Surface Temperature Analysis (GISTEMP), version 4. NASA Goddard Institute for Space Studies."],
        ["단위", "℃ (1951-1980년 30년 평균 기온 대비 편차, 절대 기온이 아님)"],
        ["기간", f"{rows[0][0]}–{rows[-1][0]}년 ({n}개 연도, 연간 집계가 끝나지 않은 최근 해는 제외)"],
        ["실습 제안", "연도(x)를 매출-광고비 실습의 x처럼 두고 회귀직선을 적합해 보십시오. 기울기가 '연평균 10년당 기온 상승폭'을 뜻합니다."],
    ]
    for r in lines:
        note.append(r)
    note.column_dimensions["A"].width = 12
    note.column_dimensions["B"].width = 90
    for row in note.iter_rows(min_row=1, max_row=len(lines)):
        row[0].font = Font(bold=True)
        row[0].alignment = Alignment(vertical="top")
        row[1].alignment = Alignment(wrap_text=True, vertical="top")

    return wb


def main() -> None:
    rows = load_annual_anomaly(SRC_CSV)
    wb = build_workbook(rows)
    OUT_XLSX.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT_XLSX)
    print(f"{len(rows)}개 연도 저장 완료 → {OUT_XLSX.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
