# docs/statistics/mean-test-with-r.html 02절의 QQ 그림을 만든다.
# 자료는 그 쪽의 실험판과 데이터 준비 자료가 쓰는 48명의 사전 나트륨 섭취량(교육군 24명 + 대조군 24명)과 같다.
# 쪽의 코드와 똑같이 stat_qq() + stat_qq_line()으로 그리고, Shapiro-Wilk 검정 결과를 함께 출력한다.
# 저장소 맨 위에서 실행한다: Rscript src/R/ttest_qq_plot.R
# 필요한 패키지: ggplot2, ragg

library(ggplot2)

sodium_pre <- c(
  # 교육군 24명
  2350, 3340, 4150, 4660, 3300, 3680, 2630, 2420, 3300, 2900, 2120, 3330,
  4130, 4010, 3050, 2550, 3810, 3210, 2950, 3690, 3360, 3350, 2220, 2160,
  # 대조군 24명
  3370, 2660, 3380, 3390, 2450, 3400, 3340, 2550, 3930, 2370, 2460, 3850,
  3520, 3000, 3760, 3120, 1930, 2900, 3260, 3460, 4570, 3260, 3940, 4240
)
d <- data.frame(sodium_pre = sodium_pre)

out_dir <- file.path("docs", "assets", "images", "ttest")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

# 쪽의 코드와 같다. 테마 기본값이 바뀌어 있지 않도록 theme_set()을 쓰지 않는다.
p_qq <- ggplot(d, aes(sample = sodium_pre)) +
  stat_qq() +
  stat_qq_line()

ggsave(file.path(out_dir, "qq-sodium-pre.png"), p_qq,
       device = ragg::agg_png, width = 5, height = 5, dpi = 150)

print(shapiro.test(sodium_pre))
