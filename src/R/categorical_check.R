# docs/statistics/categorical-test-with-r.html 본문에 적힌 수치를 다시 계산해 확인한다.
# 파일을 만들지 않고 콘솔에만 출력한다. 실행: Rscript src/R/categorical_check.R   (저장소 루트에서)
# 입력: docs/downlodable/서울-사망교통사고-2025.csv (src/R/categorical_sample_data.R 가 만든 배포용 샘플)
#       datasets/categorical/knhanes24_body_sample.csv (같은 스크립트가 만든 국민건강영양조사 추출본, 없으면 건너뜀)
# 필요한 패키지: tidyverse (effectsize 없이 효과크기를 식으로 계산한다)
suppressPackageStartupMessages(library(tidyverse))
options(width = 120)
hr <- function(title) cat("\n==== ", title, " ====\n", sep = "")

# ---- 데이터 준비: 페이지의 cat_prepare.R 과 같은 정리 -----------------------
acc <- read_csv("docs/downlodable/서울-사망교통사고-2025.csv", show_col_types = FALSE) %>%
  separate_wider_delim(사고유형, delim = " - ", names = c("사고유형", "사고세부")) %>%
  transmute(
    월 = factor(as.integer(str_extract(발생년월, "\\d+(?=월)")), levels = 1:12),
    주야 = factor(주야, levels = c("주간", "야간")),
    사고유형 = factor(사고유형, levels = c("차대사람", "차대차", "차량단독")),
    보행자사고 = factor(if_else(사고유형 == "차대사람", "차대사람", "그 외"), levels = c("차대사람", "그 외")),
    가해차종 = `가해운전자 차종`,
    차종묶음 = factor(case_when(
      가해차종 == "승용" ~ "승용",
      가해차종 %in% c("승합", "화물", "건설기계", "특수") ~ "승합·화물",
      가해차종 %in% c("이륜", "원동기", "자전거", "개인형이동수단(PM)") ~ "이륜·자전거"),
      levels = c("승용", "승합·화물", "이륜·자전거")),
    건설기계 = factor(if_else(가해차종 == "건설기계", "건설기계", "그 외 차종"), levels = c("건설기계", "그 외 차종"))
  )
hr("자료")
cat("행 수", nrow(acc), " 결측", sum(is.na(acc)), "\n")
print(count(acc, 사고유형)); print(table(acc$가해차종, acc$차종묶음))

# ---- 03 적합도와 단일 비율 ---------------------------------------------------
hr("03 월별 적합도")
obs <- table(acc$월); print(obs)
g1 <- chisq.test(obs); print(g1); cat("Cohen's w =", sqrt(g1$statistic / sum(obs)), "\n")
days <- as.numeric(table(month(seq(as.Date("2025-01-01"), as.Date("2025-12-31"), by = "day"))))
print(days); g2 <- chisq.test(obs, p = days / sum(days)); print(g2)
cat("df 11 임계값 =", qchisq(0.95, 11), "\n")
hr("03 야간 비율")
n_night <- sum(acc$주야 == "야간"); print(binom.test(n_night, nrow(acc), p = 0.5)); print(prop.test(n_night, nrow(acc), p = 0.5))
cat("Cohen's h =", 2 * asin(sqrt(n_night / nrow(acc))) - 2 * asin(sqrt(0.5)), "\n")

# ---- 04 독립성 ----------------------------------------------------------------
hr("04 주야 × 보행자사고")
t22 <- table(acc$주야, acc$보행자사고); print(t22); print(prop.table(t22, 1))
print(chisq.test(t22)); x0 <- chisq.test(t22, correct = FALSE); print(x0)
rp <- prop.table(t22, 1)
cat("위험비(주간/야간) =", rp[1, 1] / rp[2, 1], " 오즈비 ad/bc =", t22[1, 1] * t22[2, 2] / (t22[1, 2] * t22[2, 1]),
    " phi =", (t22[1, 1] * t22[2, 2] - t22[1, 2] * t22[2, 1]) / sqrt(prod(rowSums(t22)) * prod(colSums(t22))), "\n")
hr("04 주야 × 사고유형")
trc <- table(acc$주야, acc$사고유형); x1 <- chisq.test(trc); print(trc); print(round(x1$expected, 2)); print(x1)
cat("고전적 V =", sqrt(x1$statistic / sum(trc)), "\n")

# ---- 05 가정 점검과 Fisher ----------------------------------------------------
hr("05 가해차종(9종) × 사고유형")
t9 <- table(acc$가해차종, acc$사고유형); e9 <- suppressWarnings(chisq.test(t9))$expected
cat("칸", length(e9), " 5 미만", sum(e9 < 5), sprintf("(%.0f%%)", 100 * mean(e9 < 5)), " 1 미만", sum(e9 < 1), "\n")
print(suppressWarnings(chisq.test(t9)))
set.seed(2025); print(chisq.test(t9, simulate.p.value = TRUE, B = 10000))
hr("05 건설기계 × 보행자사고")
tb <- table(acc$건설기계, acc$보행자사고); print(tb); print(round(suppressWarnings(chisq.test(tb))$expected, 2))
print(suppressWarnings(chisq.test(tb))); print(fisher.test(tb))

# ---- 06 표준화 잔차 -----------------------------------------------------------
hr("06 차종묶음 × 사고유형")
t3 <- table(acc$차종묶음, acc$사고유형); r3 <- chisq.test(t3); print(t3); print(round(r3$expected, 2)); print(r3)
print(round(r3$stdres, 2)); cat("Bonferroni 기준(9칸) =", qnorm(1 - 0.05 / (2 * 9)), "\n")
cat("고전적 V =", sqrt(r3$statistic / (sum(t3) * (min(dim(t3)) - 1))), "\n")

# ---- 08 로지스틱 회귀 ---------------------------------------------------------
hr("08 로지스틱 회귀")
fit <- glm(보행자사고 == "차대사람" ~ 주야, family = binomial, data = acc)
print(exp(coef(fit))); print(suppressMessages(exp(confint(fit)))); print(anova(fit, test = "Chisq"))

# ---- 07 McNemar: 국민건강영양조사 2024 ----------------------------------------
kn_path <- "datasets/categorical/knhanes24_body_sample.csv"
if (file.exists(kn_path)) {
  hr("07 국민건강영양조사 체형 인식 × BMI")
  kn0 <- read_csv(kn_path, show_col_types = FALSE)
  cat("19세 이상", nrow(kn0), " BO1 분포:\n"); print(table(kn0$BO1, useNA = "ifany")); cat("BMI 결측", sum(is.na(kn0$HE_BMI)), "\n")
  kn <- kn0 %>% filter(BO1 %in% 1:5, !is.na(HE_BMI)) %>%
    mutate(인식비만 = factor(if_else(BO1 >= 4, "비만", "비만 아님"), levels = c("비만", "비만 아님")),
           측정비만 = factor(if_else(HE_BMI >= 25, "비만", "비만 아님"), levels = c("비만", "비만 아님")))
  tm <- table(인식 = kn$인식비만, 측정 = kn$측정비만); print(tm); N <- sum(tm)
  cat("N", N, " 인식 비만", rowSums(tm)[1] / N, " 측정 비만", colSums(tm)[1] / N, "\n")
  print(mcnemar.test(tm)); print(mcnemar.test(tm, correct = FALSE))
  b <- tm["비만", "비만 아님"]; cc <- tm["비만 아님", "비만"]; print(binom.test(b, b + cc))
  cat("g =", abs(b / (b + cc) - 0.5), " 대응 오즈비 =", b / cc, "\n"); print(chisq.test(tm))
}
