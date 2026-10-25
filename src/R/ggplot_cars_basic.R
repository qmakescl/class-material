# docs/data-science/ggplot-visualization.html 01절의 그림을 만든다.
# 가장 짧은 ggplot() 코드(모든 구성요소를 기본값으로 둔 cars 산점도)를 그려 PNG로 저장한다.
# 저장소 맨 위에서 실행한다: Rscript src/R/ggplot_cars_basic.R
# 필요한 패키지: ggplot2(4.0 이상), ragg

library(ggplot2)

out_dir <- file.path("docs", "assets", "images", "ggplot")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

# 본문의 코드와 똑같이 쓴다. 테마 기본값이 바뀌어 있지 않도록 theme_set()을 쓰지 않는다.
p <- ggplot(
  data = cars,
  mapping = aes(
    x = speed,
    y = dist
  )
) +
  geom_point()

ggsave(file.path(out_dir, "cars-basic.png"), p,
       device = ragg::agg_png, width = 7, height = 4.5, dpi = 150)
