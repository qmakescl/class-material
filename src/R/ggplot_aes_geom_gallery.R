# docs/data-science/ggplot-visualization.html 03절(aes), 04절(geom), 05절(축 눈금 글자)의 그림을 만든다.
# 아래 codes 의 문자열을 그대로 실행해 그림을 저장하고, 같은 문자열을 JSON으로 내보낸다.
# 쪽에 싣는 코드와 그림이 어긋나지 않게 하려는 것이다.
# 저장소 맨 위에서 실행한다: Rscript src/R/ggplot_aes_geom_gallery.R [코드를 내보낼 JSON 경로]
# 필요한 패키지: ggplot2(4.0 이상), ragg, jsonlite

library(ggplot2)

out_dir <- file.path("docs", "assets", "images", "ggplot")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

codes <- list(
  # ---- 03절: aes() 안과 밖 ----
  "aes-fixed" = 'ggplot(
  data = mtcars,
  mapping = aes(
    x = wt,
    y = mpg
  )
) +
  geom_point(colour = "steelblue", size = 2)',
  "aes-constant" = 'ggplot(
  data = mtcars,
  mapping = aes(
    x = wt,
    y = mpg,
    colour = "steelblue"
  )
) +
  geom_point(size = 2)',
  "aes-numeric" = 'ggplot(
  data = mtcars,
  mapping = aes(
    x = wt,
    y = mpg,
    colour = cyl
  )
) +
  geom_point(size = 2)',
  "aes-factor" = 'ggplot(
  data = mtcars,
  mapping = aes(
    x = wt,
    y = mpg,
    colour = factor(cyl)
  )
) +
  geom_point(size = 2)',
  "aes-size" = 'ggplot(
  data = mtcars,
  mapping = aes(
    x = wt,
    y = mpg,
    size = hp
  )
) +
  geom_point(alpha = 0.6)',
  "aes-shape" = 'ggplot(
  data = mtcars,
  mapping = aes(
    x = wt,
    y = mpg,
    colour = factor(cyl),
    shape = factor(am)
  )
) +
  geom_point(size = 2)',
  "aes-global" = 'ggplot(
  data = mtcars,
  mapping = aes(
    x = wt,
    y = mpg,
    colour = factor(cyl)
  )
) +
  geom_point(size = 2) +
  geom_smooth(method = "lm", se = FALSE)',
  "aes-layer" = 'ggplot(
  data = mtcars,
  mapping = aes(
    x = wt,
    y = mpg
  )
) +
  geom_point(aes(colour = factor(cyl)), size = 2) +
  geom_smooth(method = "lm", se = FALSE)',
  # ---- 04절: geom_*() ----
  "geom-histogram" = 'ggplot(
  data = mtcars,
  mapping = aes(x = mpg)
) +
  geom_histogram(binwidth = 2)',
  "geom-density" = 'ggplot(
  data = mtcars,
  mapping = aes(x = mpg)
) +
  geom_density()',
  "geom-bar" = 'ggplot(
  data = mtcars,
  mapping = aes(x = factor(cyl))
) +
  geom_bar()',
  "geom-col" = 'mpg_by_cyl <- aggregate(mpg ~ cyl, data = mtcars, FUN = mean)

ggplot(
  data = mpg_by_cyl,
  mapping = aes(
    x = factor(cyl),
    y = mpg
  )
) +
  geom_col()',
  "geom-boxplot" = 'ggplot(
  data = mtcars,
  mapping = aes(
    x = factor(cyl),
    y = mpg
  )
) +
  geom_boxplot()',
  "geom-box-jitter" = 'ggplot(
  data = mtcars,
  mapping = aes(
    x = factor(cyl),
    y = mpg
  )
) +
  geom_boxplot(outlier.shape = NA) +
  geom_jitter(width = 0.15, height = 0)',
  "geom-line" = 'ggplot(
  data = economics,
  mapping = aes(
    x = date,
    y = unemploy
  )
) +
  geom_line()',
  "geom-smooth" = 'ggplot(
  data = cars,
  mapping = aes(
    x = speed,
    y = dist
  )
) +
  geom_point() +
  geom_smooth(method = "lm")',
  "geom-text" = 'mtcars2 <- transform(mtcars, model = rownames(mtcars))

ggplot(
  data = mtcars2,
  mapping = aes(
    x = wt,
    y = mpg,
    label = model
  )
) +
  geom_point() +
  geom_text(size = 2.5, vjust = -0.7, hjust = "inward", check_overlap = TRUE)',
  # ---- 05절: 축 눈금 글자 ----
  "scale-default" = 'ggplot(
  data = economics,
  mapping = aes(
    x = date,
    y = unemploy
  )
) +
  geom_line()',
  "scale-comma" = 'ggplot(
  data = economics,
  mapping = aes(
    x = date,
    y = unemploy
  )
) +
  geom_line() +
  scale_y_continuous(labels = scales::label_comma()) +
  labs(y = "실업자 수 (천 명)")',
  "geom-hline" = 'ggplot(
  data = mtcars,
  mapping = aes(
    x = wt,
    y = mpg
  )
) +
  geom_point() +
  geom_hline(yintercept = mean(mtcars$mpg), linetype = "dashed")'
)

for (id in names(codes)) {
  env <- new.env()
  # 코드의 마지막 식이 그림이다
  p <- eval(parse(text = codes[[id]]), envir = env)
  suppressMessages(
    ggsave(file.path(out_dir, paste0(id, ".png")), p,
           device = ragg::agg_png, width = 4, height = 3, dpi = 150)
  )
}

args <- commandArgs(trailingOnly = TRUE)
if (length(args) >= 1) {
  jsonlite::write_json(codes, args[1], auto_unbox = TRUE, pretty = TRUE)
}
