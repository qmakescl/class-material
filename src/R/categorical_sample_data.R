# 범주형 자료의 가설검정(docs/statistics/categorical-test-with-r.html) 실습용 샘플 자료를 만든다.
# 실행: Rscript src/R/categorical_sample_data.R   (저장소 루트에서)
#
# 1) 서울 사망 교통사고 (TAAS 내려받기, 2025년 발생 211건)
#    입력  datasets/categorical/taas_2024_seoul_deaths.xlsx  (파일 이름은 2024지만 발생년월은 2025년 1~12월)
#    출력  docs/downlodable/서울-사망교통사고-2025.csv      (배포용, UTF-8 + BOM: Excel에서도 한글이 보인다)
#          skeleton/categorical-tests/dataset/raw/ 에도 같은 파일을 복사한다 (실습 폴더 뼈대)
#    - 사고 1건 = 1행은 그대로 두고, 실습에 쓰는 열만 남긴다. 값은 바꾸지 않는다
#      (사고유형 "대분류 - 중분류"를 나누는 일, 발생년월에서 월을 꺼내는 일은 학생이 프롬프트로 한다).
#    - 사고내용(모두 "사망사고"), 사상자 수, 상해정도 열은 이 자료에서 쓰지 않아 뺀다.
#
# 2) 국민건강영양조사 2024 기본 DB (있을 때만)
#    입력  datasets/categorical/hn24_all.sas7bdat
#    출력  datasets/categorical/knhanes24_body_sample.csv   (재배포 불가: .gitignore, docs/ 에 두지 않는다)
#    - 성인(19세 이상)의 McNemar 실습 변수만 남긴다. 용량이 큰 원자료에서 필요한 열만 읽는다.
#    - 같은 폴더의 hn24_24rc.sas7bdat 는 24시간 회상 식품섭취 자료라 BO1, HE_BMI 가 없어 쓰지 않는다.
suppressPackageStartupMessages({
  library(tidyverse)
  library(readxl)
  library(haven)
})

# ---- 1) 서울 사망 교통사고 ----------------------------------------------------
taas_in  <- "datasets/categorical/taas_2024_seoul_deaths.xlsx"
taas_out <- "docs/downlodable/서울-사망교통사고-2025.csv"

taas <- read_excel(taas_in)
stopifnot(all(str_starts(taas$발생년월, "2025년")))   # 발생 연도 확인

taas_sample <- taas %>%
  select(구분번호, 발생년월, 주야, 시군구, 사고유형, 법규위반, 노면상태, 기상상태, 도로형태,
         `가해운전자 차종`, `가해운전자 성별`, `가해운전자 연령대`,
         `피해운전자 차종`, `피해운전자 성별`, `피해운전자 연령대`)
write_excel_csv(taas_sample, taas_out)
cat("사망 교통사고:", nrow(taas_sample), "행,", ncol(taas_sample), "열 →", taas_out, "\n")
# 실습 폴더 뼈대(skeleton/categorical-tests)에도 같은 파일을 둔다. zip은 src/python/build_skeleton_zip.py 로 다시 만든다.
skel_out <- "skeleton/categorical-tests/dataset/raw/서울-사망교통사고-2025.csv"
if (dir.exists(dirname(skel_out))) invisible(file.copy(taas_out, skel_out, overwrite = TRUE))

# ---- 2) 국민건강영양조사 2024 기본 DB -------------------------------------------
kn_in  <- "datasets/categorical/hn24_all.sas7bdat"
kn_out <- "datasets/categorical/knhanes24_body_sample.csv"

if (file.exists(kn_in)) {
  kn <- read_sas(kn_in, col_select = c(ID, sex, age, BO1, HE_BMI, wt_itvex, kstrata, psu)) %>%
    zap_labels() %>%
    filter(age >= 19)
  write_csv(kn, kn_out)
  cat("국민건강영양조사:", nrow(kn), "행 →", kn_out, "\n")
} else {
  cat("국민건강영양조사 기본 DB가 없어 건너뜀:", kn_in, "\n")
}
