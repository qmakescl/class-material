# 회귀분석 자료(docs/statistics/regression-analysis.html)의 그림이 읽는 데이터를 만든다.
# 실행: Rscript src/R/prepare_regression_data.R   (저장소 루트에서)
#
# 입력
#   datasets/galton/Galton.tsv           갈턴(1886)의 부모와 자녀 키. 단위 인치, 자녀 1명 = 1행
#   R 패키지 HSAUR3 의 BtheB             Beat the Blues 무작위배정 임상시험(Proudfoot 외, 2003)
#     HSAUR3 가 없으면 install.packages("HSAUR3") 로 설치한 뒤 실행한다.
# 출력
#   docs/assets/data/regression-galton-btheb.js
#     window.GALTON_ALL : 자녀 898명. [가족, 아버지, 어머니, 아들이면 1, 자녀 키, 자녀 수] (cm)
#     window.BTHEB      : 2개월 BDI가 있는 97명. [BtheB이면 1, 항우울제 복용이면 1, 치료 전 BDI, 2개월 BDI]
#
# 값은 바꾸지 않는다. 키는 인치 × 2.54 로 cm 로 바꾸고 소수 셋째 자리까지 남긴다(인치가 소수 한 자리라 이것으로 정확하다).
# 그림의 회귀계수는 쪽의 스크립트가 이 값으로 직접 계산한다(src/R/regression_check.R 로 대조).
suppressPackageStartupMessages(library(tidyverse))

out <- "docs/assets/data/regression-galton-btheb.js"

galton <- read_tsv("datasets/galton/Galton.tsv", show_col_types = FALSE,
                   col_types = cols(Family = col_character()))
stopifnot(nrow(galton) == 898)

g_rows <- galton %>%
  transmute(fam = Family,
            father = round(Father * 2.54, 3),
            mother = round(Mother * 2.54, 3),
            son = as.integer(Gender == "M"),
            height = round(Height * 2.54, 3),
            kids = Kids)

if (!requireNamespace("HSAUR3", quietly = TRUE)) stop("HSAUR3 패키지가 필요하다: install.packages(\"HSAUR3\")")
data("BtheB", package = "HSAUR3")
b_rows <- BtheB %>%
  filter(!is.na(bdi.2m)) %>%
  transmute(btheb = as.integer(treatment == "BtheB"),
            drug = as.integer(drug == "Yes"),
            pre = bdi.pre,
            post = bdi.2m)
stopifnot(nrow(b_rows) == 97)

row_js <- function(df) {
  df %>%
    mutate(across(everything(), ~ if (is.character(.x)) paste0('"', .x, '"') else format(.x, trim = TRUE, scientific = FALSE))) %>%
    pmap_chr(function(...) paste0("[", paste(c(...), collapse = ","), "]")) %>%
    paste(collapse = ",\n")
}

js <- paste0(
  "/* 생성 파일 — 직접 수정하지 않는다.\n",
  "   src/R/prepare_regression_data.R 가 datasets/galton/Galton.tsv 와 R 패키지 HSAUR3 의 BtheB 에서 만든다. */\n",
  "window.GALTON_ALL = {\"source\":\"Galton, F. (1886). 원자료 randomservices.org/random/data/Galton.tsv\",\"unit\":\"cm\",",
  "\"cols\":[\"family\",\"father\",\"mother\",\"son\",\"height\",\"kids\"],\"rows\":[\n", row_js(g_rows), "\n]};\n",
  "window.BTHEB = {\"source\":\"Proudfoot et al. (2003), R package HSAUR3 (BtheB). 2개월 BDI 결측 3명 제외\",",
  "\"cols\":[\"btheb\",\"drug\",\"pre\",\"post\"],\"rows\":[\n", row_js(b_rows), "\n]};\n"
)
writeLines(js, out, useBytes = TRUE)
cat("갈턴", nrow(g_rows), "명, BtheB", nrow(b_rows), "명 →", out, "\n")
