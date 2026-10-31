# docs/statistics/mean-test-with-r.html 06절 "프롬프트로 결과 한 번에 만들기"의 예시 결과물을 만든다.
# 쪽에 실은 프롬프트가 요구하는 것과 같은 것을 R로 직접 만들어, 학생이 받을 결과의 예로 싣는다.
#   1) APA 양식 요약표(표 1: 기술통계, 표 2: 검정 결과)의 숫자 -> 콘솔에 출력(쪽의 HTML 표에 옮겨 적는다)
#   2) 기술통계 도표 -> docs/assets/images/ttest/apa-box.png
#   3) 가설검정 도표(독립표본 t 검정의 t 분포·기각역·관측 t) -> docs/assets/images/ttest/apa-ttest.png
# 자료는 데이터 준비 자료의 48명(교육군 24, 대조군 24)과 같다.
# 저장소 맨 위에서 실행한다: Rscript src/R/ttest_prompt_outputs.R
# 필요한 패키지: ggplot2, dplyr, ragg

suppressMessages({ library(ggplot2); library(dplyr) })

d <- tibble(
  id    = 1:48,
  group = factor(rep(c(1, 0), each = 24), levels = c(1, 0), labels = c("교육군", "대조군")),
  sodium_pre = c(
    2350, 3340, 4150, 4660, 3300, 3680, 2630, 2420, 3300, 2900, 2120, 3330,
    4130, 4010, 3050, 2550, 3810, 3210, 2950, 3690, 3360, 3350, 2220, 2160,
    3370, 2660, 3380, 3390, 2450, 3400, 3340, 2550, 3930, 2370, 2460, 3850,
    3520, 3000, 3760, 3120, 1930, 2900, 3260, 3460, 4570, 3260, 3940, 4240),
  sodium_post = c(
    2430, 3120, 3310, 3780, 2100, 3430, 2100, 2280, 3390, 3110, 3050, 2680,
    3420, 3260, 2850, 2510, 3410, 3120, 2600, 3750, 2820, 2940, 2240, 1930,
    3810, 2150, 3550, 4030, 2230, 3110, 3170, 3400, 3470, 3250, 3400, 4050,
    3530, 1710, 3720, 2990, 1840, 2770, 3900, 3090, 3880, 3130, 4350, 4680)
) %>% mutate(diff = sodium_pre - sodium_post)

out_dir <- file.path("docs", "assets", "images", "ttest")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

# ---- 표 1: 집단별 기술통계 ----
tab1 <- d %>%
  group_by(group) %>%
  summarise(n = n(),
            pre_m = mean(sodium_pre),  pre_sd = sd(sodium_pre),
            post_m = mean(sodium_post), post_sd = sd(sodium_post),
            diff_m = mean(diff),        diff_sd = sd(diff), .groups = "drop")
# 평균은 소수 첫째 자리, 표준편차는 둘째 자리(표준편차는 평균보다 한 자리 더 적는다)
cat("표 1\n")
# 1,000 이상에는 세 자리 쉼표를 넣는다. R의 검정 출력에는 쉼표가 없으므로 표를 만들 때 넣는다
f1 <- function(x) formatC(x, format = "f", digits = 1, big.mark = ",")
f2 <- function(x) formatC(x, format = "f", digits = 2, big.mark = ",")
for (i in seq_len(nrow(tab1))) with(tab1[i, ], cat(sprintf(
  "%s | n = %d | 사전 %s (%s) | 사후 %s (%s) | 변화 %s (%s)\n",
  group, n, f1(pre_m), f2(pre_sd), f1(post_m), f2(post_sd), f1(diff_m), f2(diff_sd))))

# ---- 표 2: 검정 결과 ----
r1 <- t.test(d$sodium_pre, mu = 3000)
vt <- var.test(sodium_post ~ group, data = d)
r2 <- t.test(sodium_post ~ group, data = d, var.equal = vt$p.value >= 0.05)
edu <- d %>% filter(group == "교육군")
r3 <- t.test(edu$sodium_pre, edu$sodium_post, paired = TRUE)
sp <- sqrt(sum((tab1$n - 1) * tab1$post_sd^2) / (sum(tab1$n) - 2))
d2 <- (tab1$post_m[1] - tab1$post_m[2]) / sp
g2 <- d2 * (1 - 3 / (4 * (sum(tab1$n) - 2) - 1))
row <- function(name, r, es, es_name)
  sprintf("%s | t = %.2f | df = %s | p = %.3f | CI [%s, %s] | %s = %.2f",
          name, r$statistic, format(round(unname(r$parameter), 2)), r$p.value,
          f1(r$conf.int[1]), f1(r$conf.int[2]), es_name, es)
cat("\n표 2\n")
cat(row("단일표본(사전 vs 3000)", r1, (mean(d$sodium_pre) - 3000) / sd(d$sodium_pre), "d"), "\n")
cat(sprintf("등분산 검정 | F = %.3f | df = (%d, %d) | p = %.3f\n", vt$statistic, 23, 23, vt$p.value))
cat(row("독립표본(사후, 교육군 vs 대조군)", r2, g2, "g"), "\n")
cat(row("대응표본(교육군 사전 vs 사후)", r3, mean(edu$diff) / sd(edu$diff), "dz"), "\n")

# ---- 도표 1: 집단별 사후 섭취량, 상자 + 점 ----
p_box <- ggplot(d, aes(x = group, y = sodium_post)) +
  geom_boxplot(outlier.shape = NA, width = 0.5) +
  geom_jitter(width = 0.12, height = 0, alpha = 0.6) +
  stat_summary(fun = mean, geom = "point", shape = 23, size = 3, fill = "white") +
  labs(x = NULL, y = "사후 나트륨 섭취량 (mg/일)") +
  theme_classic(base_size = 12)
ggsave(file.path(out_dir, "apa-box.png"), p_box, device = ragg::agg_png,
       width = 5, height = 4, dpi = 150)

# ---- 도표 2: 가설검정 도표 (독립표본 Student t 검정) ----
t_obs <- unname(r2$statistic); df2 <- unname(r2$parameter)
crit <- qt(0.975, df2)
grid <- data.frame(t = seq(-4.5, 4.5, length.out = 601))
grid$dens <- dt(grid$t, df2)
p_t <- ggplot(grid, aes(t, dens)) +
  geom_area(data = subset(grid, t <= -crit), fill = "#ffb020", alpha = 0.5) +
  geom_area(data = subset(grid, t >=  crit), fill = "#ffb020", alpha = 0.5) +
  geom_area(data = subset(grid, t <= -abs(t_obs)), fill = "#2f6fed", alpha = 0.5) +
  geom_area(data = subset(grid, t >=  abs(t_obs)), fill = "#2f6fed", alpha = 0.5) +
  geom_line() +
  geom_vline(xintercept = c(-crit, crit), linetype = "dashed") +
  geom_vline(xintercept = t_obs, linewidth = 1) +
  annotate("text", x = t_obs, y = max(grid$dens) * 0.95, hjust = 1.1,
           label = sprintf("관측한 t = %.2f", t_obs)) +
  annotate("text", x = crit, y = max(grid$dens) * 0.6, hjust = -0.1,
           label = sprintf("임계값 ±%.2f", crit)) +
  labs(x = sprintf("t (df = %d)", df2), y = "밀도",
       title = sprintf("영가설 아래의 t 분포와 관측한 t: p = %.3f", r2$p.value),
       subtitle = "주황: 유의수준 0.05의 양측 기각역, 파랑: p-value") +
  theme_classic(base_size = 12)
ggsave(file.path(out_dir, "apa-ttest.png"), p_t, device = ragg::agg_png,
       width = 6, height = 4, dpi = 150)
cat("\n도표 저장 완료\n")
