# 회귀분석 자료(docs/statistics/regression-analysis.html) 본문의 수치를 다시 계산해 대조한다.
# 실행: Rscript src/R/regression_check.R   (저장소 루트에서)
# 필요: tidyverse, HSAUR3, car, emmeans, lmtest (뒤의 넷이 없으면 그 부분만 건너뛴다)
suppressPackageStartupMessages(library(tidyverse))
hr <- function(s) cat("\n====", s, "====\n")
has <- function(p) requireNamespace(p, quietly = TRUE)

g <- read_tsv("datasets/galton/Galton.tsv", show_col_types = FALSE,
              col_types = cols(Family = col_character())) %>%
  mutate(father = Father * 2.54, mother = Mother * 2.54, height = Height * 2.54,
         sex = factor(if_else(Gender == "M", "아들", "딸"), levels = c("딸", "아들")),
         male = as.integer(Gender == "M"))
sons <- filter(g, Gender == "M")

# ---- 01 상관 --------------------------------------------------------------------
hr("01 상관")
cat("자녀", nrow(g), "가족", n_distinct(g$Family), "아들", nrow(sons), "\n")
cat(sprintf("r(아버지, 아들) = %.3f, r(어머니, 아들) = %.3f, r(아버지, 어머니) = %.3f\n",
            cor(sons$father, sons$height), cor(sons$mother, sons$height), cor(sons$father, sons$mother)))
fam <- distinct(g, Family, father, mother)
cat(sprintf("가족 단위 r(아버지, 어머니) = %.3f (%d가족)\n", cor(fam$father, fam$mother), nrow(fam)))
print(cor.test(sons$father, sons$height))
zf <- (sons$father - mean(sons$father)) / sd(sons$father)
zs <- (sons$height - mean(sons$height)) / sd(sons$height)
cat("사분면 (곱 > 0, < 0, = 0):", sum(zf * zs > 0), sum(zf * zs < 0), sum(zf * zs == 0), "\n")
cat(sprintf("공분산 = %.2f cm², 평균(sd): 아버지 %.1f (%.2f), 아들 %.1f (%.2f)\n",
            cov(sons$father, sons$height), mean(sons$father), sd(sons$father), mean(sons$height), sd(sons$height)))

# ---- 02 단순회귀 ----------------------------------------------------------------
hr("02 단순회귀")
f1 <- lm(height ~ father, sons)
print(summary(f1))
cat(sprintf("r × sy/sx = %.4f, R² = r² = %.4f\n",
            cor(sons$father, sons$height) * sd(sons$height) / sd(sons$father), cor(sons$father, sons$height)^2))
print(coef(lm(father ~ height, sons)))
print(confint(f1))

# ---- 03 잔차 분석 ---------------------------------------------------------------
hr("03 잔차 분석")
print(shapiro.test(resid(f1)))
if (has("lmtest")) print(lmtest::bptest(f1))
rs <- rstandard(f1)
cat("|표준화 잔차| > 2:", sum(abs(rs) > 2), " > 3:", sum(abs(rs) > 3), " 범위", round(range(rs), 2), "\n")
cat(sprintf("Cook 거리 최댓값 %.3f, 지렛값 최댓값 %.3f (평균 %.4f)\n",
            max(cooks.distance(f1)), max(hatvalues(f1)), mean(hatvalues(f1))))
cat("±1, ±2 시그마 안:", mean(abs(resid(f1)) <= sigma(f1)), mean(abs(resid(f1)) <= 2 * sigma(f1)), "\n")
fam_e <- sons %>% mutate(e = resid(f1)) %>% group_by(Family) %>% filter(n() >= 2) %>% ungroup()
cat("아들이 둘 이상인 가족:", n_distinct(fam_e$Family), "가족", nrow(fam_e), "명\n")
print(anova(lm(e ~ factor(Family), data = fam_e)))
# 가족 안 상관(ICC, 일원분산분석 추정)
a <- anova(lm(e ~ factor(Family), data = fam_e)); n0 <- {ni <- table(fam_e$Family); (sum(ni) - sum(ni^2) / sum(ni)) / (length(ni) - 1)}
icc <- (a$`Mean Sq`[1] - a$`Mean Sq`[2]) / (a$`Mean Sq`[1] + (n0 - 1) * a$`Mean Sq`[2])
cat(sprintf("가족 안 잔차 상관(ICC) = %.3f\n", icc))
# 가족마다 아들 키를 평균해 가족 하나를 관측 하나로 쓰면 (원자료는 가족 안에서 키 순으로 적혀 있어 첫 줄만 고르면 치우친다)
one <- sons %>% group_by(Family) %>% summarise(father = first(father), height = mean(height))
f1one <- lm(height ~ father, one)
cat(sprintf("가족 단위(%d가족): 기울기 %.3f (SE %.3f), 465명 전체: SE %.3f\n", nrow(one), coef(f1one)[2],
            summary(f1one)$coef[2, 2], summary(f1)$coef[2, 2]))

# ---- 04 다중회귀 ----------------------------------------------------------------
hr("04 다중회귀")
f2 <- lm(height ~ father + mother, sons)
print(summary(f2))
cat("어머니만:", coef(lm(height ~ mother, sons)), " R²", summary(lm(height ~ mother, sons))$r.squared, "\n")
if (has("car")) print(car::vif(f2))
print(predict(f2, newdata = tibble(father = 180, mother = c(160, 170))))

# ---- 05 더미변수 ----------------------------------------------------------------
hr("05 더미변수")
print(summary(lm(height ~ sex, g)))
print(g %>% group_by(sex) %>% summarise(n = n(), M = mean(height), SD = sd(height)))
print(t.test(height ~ sex, g, var.equal = TRUE))
f3 <- lm(height ~ father + mother + sex, g); print(summary(f3))
f3i <- lm(height ~ (father + mother) * sex, g); print(anova(f3, f3i))
# 그림(아버지 키 하나와 성별)의 모형
w1 <- lm(height ~ father, g); w2 <- lm(height ~ father + sex, g); w3 <- lm(height ~ father * sex, g)
for (m in list(w1, w2, w3)) { print(round(coef(m), 4)); cat(" R²", round(summary(m)$r.squared, 4), " σ", round(sigma(m), 3), "\n") }
print(anova(w2, w3))

# ---- 06 로지스틱 ----------------------------------------------------------------
hr("06 로지스틱")
l1 <- glm(male ~ height, binomial, g); print(summary(l1))
print(exp(coef(l1))); print(exp(confint(l1)))
cat(sprintf("확률 0.5가 되는 키 = %.1f cm\n", -coef(l1)[1] / coef(l1)[2]))
for (h in c(160, 165, 170, 175, 180)) cat(h, "cm: p =", round(plogis(coef(l1)[1] + coef(l1)[2] * h), 3), "\n")
p1 <- fitted(l1); print(table(예측 = if_else(p1 > .5, "아들", "딸"), 실제 = g$sex)); cat("정확도", mean((p1 > .5) == g$male), "\n")
lpm <- lm(male ~ height, g); print(coef(lpm)); cat("선형확률모형 예측 범위", range(fitted(lpm)), " 0 미만", sum(fitted(lpm) < 0), " 1 초과", sum(fitted(lpm) > 1), "\n")
l2 <- glm(male ~ height + father + mother, binomial, g); print(summary(l2)); print(exp(coef(l2))); print(exp(confint(l2)))
p2 <- fitted(l2); cat("정확도2", mean((p2 > .5) == g$male), "\n")
print(anova(l1, l2, test = "Chisq"))

# ---- 07 공분산분석 --------------------------------------------------------------
hr("07 공분산분석 (BtheB)")
if (has("HSAUR3")) {
  data("BtheB", package = "HSAUR3")
  d <- BtheB %>% filter(!is.na(bdi.2m)) %>% mutate(treatment = factor(treatment, levels = c("TAU", "BtheB")))
  print(count(d, treatment)); print(d %>% group_by(treatment) %>% summarise(pre = mean(bdi.pre), post = mean(bdi.2m)))
  a0 <- lm(bdi.2m ~ treatment, d); print(summary(a0)$coef)
  a1 <- lm(bdi.2m ~ bdi.pre + treatment, d); print(summary(a1)); print(confint(a1))
  a2 <- lm(bdi.2m ~ bdi.pre + drug + treatment, d); print(summary(a2)); print(confint(a2))
  c1 <- lm(bdi.2m ~ bdi.pre, d); c2 <- lm(bdi.2m ~ bdi.pre + drug, d)
  print(anova(c1, a1)); print(anova(c2, a2))
  cat(sprintf("공변량만 R² %.4f → 집단 더한 R² %.4f (ΔR² %.4f)\n", summary(c2)$r.squared, summary(a2)$r.squared, summary(a2)$r.squared - summary(c2)$r.squared))
  cat(sprintf("ANCOVA 1: 공변량만 R² %.4f → %.4f\n", summary(c1)$r.squared, summary(a1)$r.squared))
  print(anova(a1, lm(bdi.2m ~ bdi.pre * treatment, d)))
  cat("치료 전 BDI 평균", mean(d$bdi.pre), "\n")
  if (has("emmeans") && has("car")) {
    suppressPackageStartupMessages(library(emmeans))
    print(car::Anova(a1, type = 2)); print(emmeans(a1, ~ treatment))
    print(car::Anova(a2, type = 2)); print(emmeans(a2, ~ treatment)); print(confint(pairs(emmeans(a2, ~ treatment))))
  }
}

# ---- 08 위계적 회귀 -------------------------------------------------------------
hr("08 위계적 회귀")
h1 <- lm(height ~ sex, g); h2 <- lm(height ~ sex + father + mother, g); h3 <- lm(height ~ sex + father + mother + Kids, g)
r2 <- map_dbl(list(h1, h2, h3), ~ summary(.x)$r.squared); cat("R²", round(r2, 4), " ΔR²", round(diff(r2), 4), "\n")
cat("수정 R²", round(map_dbl(list(h1, h2, h3), ~ summary(.x)$adj.r.squared), 4), "\n")
print(anova(h1, h2, h3)); print(summary(h3)$coef)
p1m <- lm(height ~ father + mother, g); cat("부모 먼저: R²", round(summary(p1m)$r.squared, 4), "→", round(r2[2], 4), " Δ", round(r2[2] - summary(p1m)$r.squared, 4), "\n")
print(anova(p1m, h2))
cat("성별과 부모 키의 상관:", round(cor(g$male, g$father), 3), round(cor(g$male, g$mother), 3), "\n")
