# docs/statistics/anova-with-r.html 의 표·그림에 적힌 수치를 R 내장 데이터셋으로 다시 계산해 확인한다.
# 파일을 만들지 않고 콘솔에만 출력한다. 실행: Rscript src/R/anova_check.R
# 필요한 패키지: tidyverse, car, rstatix (emmeans_test 는 emmeans)
suppressPackageStartupMessages({
  library(tidyverse)
  library(car)
  library(rstatix)
})
options(width = 120)
hr <- function(title) cat("\n==== ", title, " ====\n", sep = "")

# ---- 01 일원배치: PlantGrowth ----------------------------------------------
hr("표 1. 집단별 기술통계")
pg <- PlantGrowth %>% mutate(group = factor(group, levels = c("ctrl", "trt1", "trt2")))
print(pg %>% group_by(group) %>% summarise(n = n(), mean = mean(weight), sd = sd(weight), var = var(weight)))
print(pg %>% summarise(n = n(), mean = mean(weight), sd = sd(weight), var = var(weight)))

hr("표 2. 등분산·정규성")
print(leveneTest(weight ~ group, data = pg))
print(bartlett.test(weight ~ group, data = pg))
fit <- aov(weight ~ group, data = pg)
print(shapiro.test(residuals(fit)))

hr("표 3. 일원배치 분산분석표, η², 임계값")
print(summary(fit))
print(eta_squared(fit))
cat("F.05(2, 27) =", qf(0.95, 2, 27), "\n")

hr("표 4. Tukey HSD")
print(TukeyHSD(fit))

hr("표 4, 표 4-1. Bonferroni, Holm, Scheffe, Dunnett, Games-Howell")
print(pairwise.t.test(pg$weight, pg$group, p.adjust.method = "bonferroni"))
print(pg %>% pairwise_t_test(weight ~ group, pool.sd = TRUE, p.adjust.method = "bonferroni"))
print(pg %>% pairwise_t_test(weight ~ group, pool.sd = TRUE, p.adjust.method = "holm"))
msw <- deviance(fit) / df.residual(fit)
cat("HSD =", qtukey(0.95, 3, 27) * sqrt(msw / 10), "\n")
cat("Bonferroni 반폭 =", qt(1 - 0.05 / 6, 27) * sqrt(msw * 0.2), "\n")
t_21 <- 0.865 / sqrt(msw * 0.2)
cat("Scheffe p (trt2 - trt1) =", pf(t_21^2 / 2, 2, 27, lower.tail = FALSE), "\n")
print(pg %>% games_howell_test(weight ~ group))
if (requireNamespace("multcomp", quietly = TRUE)) {
  print(summary(multcomp::glht(fit, linfct = multcomp::mcp(group = "Dunnett"))))
}

hr("Tukey-Kramer: ChickWeight 18일, 사료별 반복수가 다름")
ch18 <- ChickWeight %>% as_tibble() %>%
  group_by(Chick) %>% filter(n() == 12) %>% ungroup() %>%
  filter(Time == 18) %>% mutate(Diet = factor(Diet))
fit18 <- aov(weight ~ Diet, data = ch18)
print(TukeyHSD(fit18))
mse18 <- deviance(fit18) / df.residual(fit18)
se18 <- sqrt(mse18 / 2 * (1 / 10 + 1 / 16))
cat("MSE =", mse18, " 분모 =", se18, " q =", 72.6 / se18, " 임계값 =", qtukey(0.95, 4, 41), "\n")

# ---- 02 이원배치: ToothGrowth ------------------------------------------------
hr("표 5. 칸별 평균(표준편차)와 주변평균")
tg <- ToothGrowth %>% mutate(dose = factor(dose), supp = factor(supp, levels = c("OJ", "VC")))
print(tg %>% group_by(supp, dose) %>% summarise(n = n(), mean = mean(len), sd = sd(len), .groups = "drop"))
print(tg %>% group_by(supp) %>% summarise(mean = mean(len)))
print(tg %>% group_by(dose) %>% summarise(mean = mean(len)))
cat("전체 평균 =", mean(tg$len), "\n")

hr("표 6. 이원배치 분산분석표 (Levene, 부분 η²)")
print(leveneTest(len ~ supp * dose, data = tg))
fit2 <- aov(len ~ supp * dose, data = tg)
print(summary(fit2))
print(tg %>% anova_test(len ~ supp * dose, effect.size = "pes"))
cat("SST =", sum((tg$len - mean(tg$len))^2), "\n")

hr("그림: 가법 모형 예측값(행평균 + 열평균 − 전체평균)")
gm <- mean(tg$len)
print(tg %>% group_by(supp) %>% mutate(rm = mean(len)) %>% group_by(dose) %>% mutate(cm = mean(len)) %>%
  group_by(supp, dose) %>% summarise(add = first(rm) + first(cm) - gm, .groups = "drop"))

hr("표 7. 용량별 supp 단순 주효과")
model <- lm(len ~ supp * dose, data = tg)
print(tg %>% group_by(dose) %>% anova_test(len ~ supp, error = model) %>% adjust_pvalue(method = "bonferroni"))

hr("펼침 상자: 제곱합 유형 (mtcars)")
mt <- mtcars %>% mutate(am = factor(am, labels = c("auto", "manual")), cyl = factor(cyl))
print(anova(lm(mpg ~ am * cyl, data = mt)))
print(anova(lm(mpg ~ cyl * am, data = mt)))
print(Anova(lm(mpg ~ am * cyl, data = mt), type = 2))
print(Anova(lm(mpg ~ am * cyl, data = mt, contrasts = list(am = contr.sum, cyl = contr.sum)), type = 3))

# ---- 03 반복측정: ChickWeight 6·12·18일 ------------------------------------
hr("반복측정: 자료 준비")
chick <- ChickWeight %>%
  as_tibble() %>%
  group_by(Chick) %>% filter(n() == 12) %>% ungroup() %>%
  filter(Time %in% c(6, 12, 18)) %>%
  mutate(Chick = factor(as.character(Chick)), Time = factor(Time), Diet = factor(Diet))
cat("병아리 수 =", n_distinct(chick$Chick), " 행 =", nrow(chick), "\n")
print(chick %>% count(Diet) %>% mutate(n = n / 3))

hr("표 8. 분산·공분산 행렬과 차이 점수 분산")
wide <- chick %>% select(Chick, Time, weight) %>% pivot_wider(names_from = Time, values_from = weight)
print(cov(wide[, c("6", "12", "18")]))
cat("Var(12-6) =", var(wide$`12` - wide$`6`), " Var(18-6) =", var(wide$`18` - wide$`6`),
    " Var(18-12) =", var(wide$`18` - wide$`12`), "\n")

hr("표 9. 반복측정 분산분석 (Mauchly, GG/HF)")
res_rm <- anova_test(data = chick, dv = weight, wid = Chick, within = Time)
print(res_rm)
print(get_anova_table(res_rm, correction = "GG"))
# SS 분해: 독립집단으로 본 경우와 비교
fit_ind <- aov(weight ~ Time, data = chick)
fit_rm <- aov(weight ~ Time + Error(Chick / Time), data = chick)
print(summary(fit_ind))
print(summary(fit_rm))
cat("SST =", sum((chick$weight - mean(chick$weight))^2), "\n")

hr("그림: 시점별 평균과 95% CI")
print(chick %>% group_by(Time) %>% summarise(n = n(), mean = mean(weight), sd = sd(weight),
  lo = mean - qt(0.975, n - 1) * sd / sqrt(n), hi = mean + qt(0.975, n - 1) * sd / sqrt(n)))

hr("표 10. Bonferroni 대응표본 t 사후비교와 Hedges g")
print(chick %>% pairwise_t_test(weight ~ Time, paired = TRUE, p.adjust.method = "bonferroni"))
print(chick %>% cohens_d(weight ~ Time, paired = TRUE, hedges.correction = TRUE))

# ---- 04 혼합 설계: Diet × Time ---------------------------------------------
hr("표 11. 가정 점검")
print(chick %>% group_by(Time) %>% levene_test(weight ~ Diet))
print(box_m(wide %>% select(`6`, `12`, `18`), chick %>% distinct(Chick, Diet) %>% pull(Diet)))

hr("표 12. 혼합 설계 분산분석표")
res_mix <- anova_test(data = chick, dv = weight, wid = Chick, between = Diet, within = Time)
print(res_mix)
print(get_anova_table(res_mix, correction = "GG"))
print(summary(aov(weight ~ Diet * Time + Error(Chick / Time), data = chick)))

hr("표 13. 시점별 Diet 단순 주효과와 칸 평균")
print(chick %>% group_by(Time, Diet) %>% summarise(mean = mean(weight), se = sd(weight) / sqrt(n()), .groups = "drop") %>%
  pivot_wider(names_from = Diet, values_from = c(mean, se)))
print(chick %>% group_by(Time) %>% anova_test(dv = weight, wid = Chick, between = Diet))

hr("주의 상자: 시점을 4·8·12·16일로 바꾸면")
chick4 <- ChickWeight %>% as_tibble() %>%
  group_by(Chick) %>% filter(n() == 12) %>% ungroup() %>%
  filter(Time %in% c(4, 8, 12, 16)) %>%
  mutate(Chick = factor(as.character(Chick)), Time = factor(Time), Diet = factor(Diet))
res4 <- anova_test(data = chick4, dv = weight, wid = Chick, between = Diet, within = Time)
print(res4)
print(get_anova_table(res4, correction = "GG"))
