"""Netflix Tudum 주간 통계 데이터 로더 모듈.

이 모듈은 datasets/tudum 디렉터리에 위치한 Netflix 주간 통계 엑셀 파일들을
일관된 인터페이스로 읽고 처리하기 위한 DataLoader 클래스들을 제공합니다.

구조:
- BaseDataLoader: 엑셀 파일 로딩, 캐싱, 스키마 검증 및 공통 필터링을 제공하는 기본 클래스
- CountryWeeklyDataLoader: 국가별 주간 순위(country_weekly) 전용 로더
- GlobalWeeklyDataLoader: 글로벌 주간 순위 및 시청 지표(global_weekly) 전용 로더
- TudumDataLoader: 위 두 로더를 하나로 묶어 제공하는 통합 인터페이스
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd


class BaseDataLoader(ABC):
    """Netflix Tudum 데이터셋을 읽기 위한 기본 추상 데이터로더 클래스."""

    def __init__(
        self,
        file_path: str | Path | None = None,
        data_dir: str | Path = "datasets/tudum",
        sheet_name: str = "Top 10",
        file_pattern: str = "*.xlsx",
    ) -> None:
        """기본 데이터로더 초기화.

        Args:
            file_path: 읽을 엑셀 파일의 직접 경로. 지정하지 않으면 data_dir에서 file_pattern으로 탐색.
            data_dir: 데이터셋이 저장된 디렉터리 경로.
            sheet_name: 엑셀 시트 이름 (기본값: 'Top 10').
            file_pattern: 자동 탐색에 사용할 파일명 패턴.
        """
        self.data_dir = Path(data_dir)
        self.sheet_name = sheet_name
        self.file_pattern = file_pattern
        self.file_path = Path(file_path) if file_path else self._resolve_file_path()
        self._data: pd.DataFrame | None = None

    def _resolve_file_path(self) -> Path:
        """data_dir 내에서 file_pattern과 일치하는 최신 파일을 탐색하여 반환."""
        if not self.data_dir.exists():
            raise FileNotFoundError(f"데이터 디렉터리를 찾을 수 없습니다: {self.data_dir}")

        matches = sorted(self.data_dir.glob(self.file_pattern))
        if not matches:
            raise FileNotFoundError(
                f"패턴 '{self.file_pattern}'과 일치하는 파일이 {self.data_dir} 에 없습니다."
            )
        # 파일명 기준 가장 최신 파일(사전식 정렬 마지막 항목) 선택
        return matches[-1]

    @property
    @abstractmethod
    def required_columns(self) -> list[str]:
        """데이터셋에 반드시 포함되어야 하는 필수 컬럼 목록."""
        pass

    @abstractmethod
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터셋별 특화 정제 작업을 수행하는 내부 메서드."""
        pass

    def validate_schema(self, df: pd.DataFrame) -> None:
        """필수 컬럼이 DataFrame에 포함되어 있는지 검증."""
        missing = [col for col in self.required_columns if col not in df.columns]
        if missing:
            raise ValueError(
                f"파일({self.file_path.name})에 필수 컬럼이 누락되었습니다: {missing}"
            )

    def load(self, force_reload: bool = False) -> pd.DataFrame:
        """엑셀 파일에서 데이터를 로드하고 정제하여 반환.

        Args:
            force_reload: True이면 캐시된 데이터를 무시하고 파일을 다시 읽음.

        Returns:
            정제된 데이터가 담긴 pd.DataFrame.
        """
        if self._data is not None and not force_reload:
            return self._data.copy()

        if not self.file_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {self.file_path}")

        raw_df = pd.read_excel(
            self.file_path,
            sheet_name=self.sheet_name,
            engine="openpyxl",
        )
        self.validate_schema(raw_df)
        cleaned_df = self._clean_data(raw_df)
        self._data = cleaned_df
        return self._data.copy()

    def get_data(self, refresh: bool = False) -> pd.DataFrame:
        """로드된 데이터를 반환 (아직 로드되지 않았으면 자동으로 load 수행)."""
        if self._data is None or refresh:
            return self.load(force_reload=refresh)
        return self._data.copy()

    def get_summary(self) -> dict[str, Any]:
        """데이터셋의 기본 요약 메타데이터 반환."""
        df = self.get_data()
        weeks = sorted(df["week"].dropna().unique())
        return {
            "file_name": self.file_path.name,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "start_week": str(weeks[0]) if weeks else None,
            "end_week": str(weeks[-1]) if weeks else None,
            "total_weeks": len(weeks),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
        }

    def get_weeks(self) -> list[str]:
        """존재하는 모든 주차 목록을 최신순으로 반환."""
        df = self.get_data()
        return sorted(df["week"].dropna().unique().tolist(), reverse=True)

    def get_latest_week(self) -> str:
        """가장 최신 주차 문자열 반환."""
        weeks = self.get_weeks()
        if not weeks:
            raise ValueError("데이터에 주차(week) 정보가 없습니다.")
        return weeks[0]

    def filter_by_week(self, week: str | date | datetime | pd.Timestamp) -> pd.DataFrame:
        """특정 주차의 데이터만 필터링하여 반환."""
        df = self.get_data()
        target_week = str(week)[:10]
        return df[df["week"] == target_week].copy()

    def get_latest_week_data(self) -> pd.DataFrame:
        """가장 최신 주차의 데이터 반환."""
        return self.filter_by_week(self.get_latest_week())


class CountryWeeklyDataLoader(BaseDataLoader):
    """Netflix Tudum 국가별 주간 순위(Country Weekly Top 10) 전용 로더."""

    def __init__(
        self,
        file_path: str | Path | None = None,
        data_dir: str | Path = "datasets/tudum",
        sheet_name: str = "Top 10",
        file_pattern: str = "*country_weekly.xlsx",
    ) -> None:
        super().__init__(
            file_path=file_path,
            data_dir=data_dir,
            sheet_name=sheet_name,
            file_pattern=file_pattern,
        )

    @property
    def required_columns(self) -> list[str]:
        return [
            "country_name",
            "country_iso2",
            "week",
            "category",
            "weekly_rank",
            "show_title",
            "season_title",
            "cumulative_weeks_in_top_10",
        ]

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """국가별 데이터 정제 및 타입 변환."""
        cleaned = df.copy()

        # 주차 형식 통일 (YYYY-MM-DD 문자열)
        cleaned["week"] = pd.to_datetime(cleaned["week"]).dt.strftime("%Y-%m-%d")

        # 정수형 컬럼 변환
        cleaned["weekly_rank"] = pd.to_numeric(cleaned["weekly_rank"], errors="coerce").astype("Int64")
        cleaned["cumulative_weeks_in_top_10"] = pd.to_numeric(
            cleaned["cumulative_weeks_in_top_10"], errors="coerce"
        ).astype("Int64")

        # 문자열 컬럼 공백 제거 및 결측치 처리
        string_cols = ["country_name", "country_iso2", "category", "show_title", "season_title"]
        for col in string_cols:
            if col in cleaned.columns:
                cleaned[col] = cleaned[col].fillna("N/A").astype(str).str.strip()

        return cleaned

    def get_countries(self) -> list[str]:
        """포함된 모든 국가 이름 목록을 알파벳순으로 반환."""
        df = self.get_data()
        return sorted(df["country_name"].dropna().unique().tolist())

    def get_country_codes(self) -> list[str]:
        """포함된 모든 국가의 ISO2 코드 목록을 알파벳순으로 반환."""
        df = self.get_data()
        return sorted(df["country_iso2"].dropna().unique().tolist())

    def filter_by_country(self, country: str) -> pd.DataFrame:
        """국가명 또는 ISO2 코드로 데이터 필터링.

        Args:
            country: 국가명(예: 'South Korea') 또는 ISO2 코드(예: 'KR'). 대소문자 무관.
        """
        df = self.get_data()
        target = country.strip().lower()
        mask = (df["country_name"].str.lower() == target) | (df["country_iso2"].str.lower() == target)
        return df[mask].copy()

    def filter_by_title(self, title: str, exact: bool = False) -> pd.DataFrame:
        """작품명으로 필터링.

        Args:
            title: 찾고자 하는 작품명.
            exact: True이면 정확히 일치, False이면 부분 일치(대소문자 무관).
        """
        df = self.get_data()
        if exact:
            return df[df["show_title"] == title].copy()
        return df[df["show_title"].str.contains(title, case=False, na=False)].copy()

    def get_top_ranked(self, rank: int = 1, country: str | None = None) -> pd.DataFrame:
        """지정된 순위(기본값: 1위)에 오른 기록만 필터링."""
        df = self.get_data()
        mask = df["weekly_rank"] == rank
        if country:
            target = country.strip().lower()
            country_mask = (df["country_name"].str.lower() == target) | (
                df["country_iso2"].str.lower() == target
            )
            mask &= country_mask
        return df[mask].copy()

    def get_title_history(self, title: str, country: str | None = None) -> pd.DataFrame:
        """특정 작품의 주차별 순위 변동 히스토리를 반환."""
        df = self.filter_by_title(title, exact=False)
        if country:
            target = country.strip().lower()
            mask = (df["country_name"].str.lower() == target) | (df["country_iso2"].str.lower() == target)
            df = df[mask]
        return df.sort_values(by=["week", "country_name", "weekly_rank"]).copy()


class GlobalWeeklyDataLoader(BaseDataLoader):
    """Netflix Tudum 글로벌 주간 순위 및 뷰(Global Weekly Top 10) 전용 로더."""

    def __init__(
        self,
        file_path: str | Path | None = None,
        data_dir: str | Path = "datasets/tudum",
        sheet_name: str = "Top 10",
        file_pattern: str = "*global_weekly.xlsx",
    ) -> None:
        super().__init__(
            file_path=file_path,
            data_dir=data_dir,
            sheet_name=sheet_name,
            file_pattern=file_pattern,
        )

    @property
    def required_columns(self) -> list[str]:
        return [
            "week",
            "category",
            "weekly_rank",
            "show_title",
            "season_title",
            "weekly_hours_viewed",
            "runtime",
            "weekly_views",
            "cumulative_weeks_in_top_10",
        ]

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """글로벌 주간 데이터 정제 및 타입 변환."""
        cleaned = df.copy()

        # 주차 형식 통일 (YYYY-MM-DD 문자열)
        cleaned["week"] = pd.to_datetime(cleaned["week"]).dt.strftime("%Y-%m-%d")

        # 정수형 컬럼 변환
        cleaned["weekly_rank"] = pd.to_numeric(cleaned["weekly_rank"], errors="coerce").astype("Int64")
        cleaned["weekly_hours_viewed"] = pd.to_numeric(
            cleaned["weekly_hours_viewed"], errors="coerce"
        ).astype("Int64")
        cleaned["cumulative_weeks_in_top_10"] = pd.to_numeric(
            cleaned["cumulative_weeks_in_top_10"], errors="coerce"
        ).astype("Int64")

        # 부동소수점 컬럼 변환
        cleaned["runtime"] = pd.to_numeric(cleaned["runtime"], errors="coerce").astype(float)
        cleaned["weekly_views"] = pd.to_numeric(cleaned["weekly_views"], errors="coerce").astype(float)

        # 문자열 컬럼 공백 제거 및 결측치 처리
        string_cols = ["category", "show_title", "season_title"]
        for col in string_cols:
            if col in cleaned.columns:
                cleaned[col] = cleaned[col].fillna("N/A").astype(str).str.strip()

        return cleaned

    def get_categories(self) -> list[str]:
        """포함된 모든 카테고리 목록 반환."""
        df = self.get_data()
        return sorted(df["category"].dropna().unique().tolist())

    def filter_by_category(self, category: str) -> pd.DataFrame:
        """카테고리명(예: 'Films (English)', 'TV')으로 필터링."""
        df = self.get_data()
        mask = df["category"].str.contains(category, case=False, na=False)
        return df[mask].copy()

    def filter_by_title(self, title: str, exact: bool = False) -> pd.DataFrame:
        """작품명으로 필터링.

        Args:
            title: 찾고자 하는 작품명.
            exact: True이면 정확히 일치, False이면 부분 일치(대소문자 무관).
        """
        df = self.get_data()
        if exact:
            return df[df["show_title"] == title].copy()
        return df[df["show_title"].str.contains(title, case=False, na=False)].copy()

    def get_top_viewed(
        self,
        top_n: int = 10,
        by: str = "weekly_views",
        category: str | None = None,
    ) -> pd.DataFrame:
        """시청 지표(조회수 또는 시청 시간) 기준 상위 작품 반환.

        Args:
            top_n: 반환할 행 수.
            by: 정렬 기준 컬럼 ('weekly_views' 또는 'weekly_hours_viewed').
            category: 특정 카테고리로 제한할 경우 지정.
        """
        if by not in ["weekly_views", "weekly_hours_viewed"]:
            raise ValueError("by 인자는 'weekly_views' 또는 'weekly_hours_viewed' 여야 합니다.")

        df = self.get_data()
        if category:
            df = df[df["category"].str.contains(category, case=False, na=False)]

        return df.sort_values(by=by, ascending=False).head(top_n).copy()

    def get_title_history(self, title: str) -> pd.DataFrame:
        """특정 작품의 글로벌 주차별 지표 변동 히스토리를 반환."""
        df = self.filter_by_title(title, exact=False)
        return df.sort_values(by=["week", "category", "weekly_rank"]).copy()


class TudumDataLoader:
    """Netflix Tudum 데이터셋 전체를 관리하는 통합 데이터로더."""

    def __init__(self, data_dir: str | Path = "datasets/tudum") -> None:
        """통합 로더 초기화.

        Args:
            data_dir: tudum 데이터셋 엑셀 파일들이 있는 디렉터리 경로.
        """
        self.data_dir = Path(data_dir)
        self.country = CountryWeeklyDataLoader(data_dir=self.data_dir)
        self.global_data = GlobalWeeklyDataLoader(data_dir=self.data_dir)

    def load_all(self, force_reload: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
        """국가별 및 글로벌 데이터셋을 모두 로드하여 튜플로 반환."""
        country_df = self.country.load(force_reload=force_reload)
        global_df = self.global_data.load(force_reload=force_reload)
        return country_df, global_df

    def get_summary(self) -> dict[str, Any]:
        """두 데이터셋의 요약 정보를 딕셔너리로 반환."""
        return {
            "country_weekly": self.country.get_summary(),
            "global_weekly": self.global_data.get_summary(),
        }


def load_country_weekly(
    file_path: str | Path | None = None,
    data_dir: str | Path = "datasets/tudum",
) -> pd.DataFrame:
    """국가별 주간 순위 데이터를 손쉽게 로드하는 헬퍼 함수."""
    loader = CountryWeeklyDataLoader(file_path=file_path, data_dir=data_dir)
    return loader.load()


def load_global_weekly(
    file_path: str | Path | None = None,
    data_dir: str | Path = "datasets/tudum",
) -> pd.DataFrame:
    """글로벌 주간 순위 데이터를 손쉽게 로드하는 헬퍼 함수."""
    loader = GlobalWeeklyDataLoader(file_path=file_path, data_dir=data_dir)
    return loader.load()


if __name__ == "__main__":
    import time

    print("=== Netflix Tudum DataLoader 검증 및 시연 ===")
    tudum = TudumDataLoader()

    # 1. Global Weekly 데이터 로드
    print("\n[1] Global Weekly 데이터 로드 중...")
    t0 = time.perf_counter()
    df_global = tudum.global_data.load()
    t_global = time.perf_counter() - t0
    print(f"-> 로드 완료: {len(df_global):,} 행 ({t_global:.2f}초 소요)")

    global_summary = tudum.global_data.get_summary()
    print("-> 글로벌 데이터 요약:")
    for k, v in global_summary.items():
        print(f"   - {k}: {v}")

    latest_global_week = tudum.global_data.get_latest_week()
    print(f"\n-> 최신 주차({latest_global_week}) 카테고리별 1위 작품:")
    latest_global = tudum.global_data.get_latest_week_data()
    top1_global = latest_global[latest_global["weekly_rank"] == 1]
    print(top1_global[["category", "show_title", "weekly_views", "weekly_hours_viewed"]].to_string(index=False))

    print("\n-> 역대 글로벌 주간 최고 조회수 Top 5:")
    top_viewed = tudum.global_data.get_top_viewed(top_n=5, by="weekly_views")
    print(top_viewed[["week", "category", "show_title", "weekly_views"]].to_string(index=False))

    # 2. Country Weekly 데이터 로드 (대용량)
    print("\n[2] Country Weekly 데이터 로드 중 (약 50만 행)...")
    t0 = time.perf_counter()
    df_country = tudum.country.load()
    t_country = time.perf_counter() - t0
    print(f"-> 로드 완료: {len(df_country):,} 행 ({t_country:.2f}초 소요)")

    country_summary = tudum.country.get_summary()
    print("-> 국가별 데이터 요약:")
    for k, v in country_summary.items():
        print(f"   - {k}: {v}")

    # 한국(South Korea / KR) 데이터 필터링 예시
    print("\n-> 최신 주차 한국(KR) 1위 작품:")
    latest_country = tudum.country.get_latest_week_data()
    kr_latest = latest_country[
        (latest_country["country_iso2"] == "KR") & (latest_country["weekly_rank"] == 1)
    ]
    print(kr_latest[["category", "show_title", "cumulative_weeks_in_top_10"]].to_string(index=False))

    print("\n모든 로더 정상 동작 확인 완료!")

