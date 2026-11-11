# docs/data-science/ggplot-visualization.html 11절(사례: 나이팅게일의 로즈 도표)의 그림을 만든다.
# codes 의 문자열을 차례로 같은 환경에서 실행해 단계마다 그림을 저장하고, 같은 문자열을 JSON으로 내보낸다.
# 쪽에 싣는 코드와 그림이 어긋나지 않게 하려는 것이다.
# 저장소 맨 위에서 실행한다: Rscript src/R/ggplot_nightingale.R [코드를 내보낼 JSON 경로]
# 필요한 패키지: tidyverse(ggplot2 4.0 이상), HistData, showtext, ragg, jsonlite
# 자료: HistData::Nightingale. 크림 전쟁 중 동방 주둔 영국군의 월별 사망 원인(1854년 4월 ~ 1856년 3월, 24개월)

out_dir <- file.path("docs", "assets", "images", "ggplot")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

codes <- list(
  # 1단계: 자료 살펴보기. 그림을 만들지 않고 glimpse() 결과만 콘솔에 찍는다(쪽의 출력 상자에 옮겨 적는다)
  "rose-look" = 'library(tidyverse)
library(HistData)

glimpse(Nightingale)   # 행·열의 수, 열마다 자료형과 앞부분 값
?Nightingale           # 열의 뜻과 단위를 적은 도움말',
  "rose-prep" = 'library(tidyverse)
library(HistData)
library(showtext)

font_add_google("Noto Sans KR", "Noto Sans KR")
showtext_auto()

# 세 사망 원인의 사망률(연 환산, 1,000명당)을 한 열로 모은 긴 모양
rose <- Nightingale %>%
  select(Date, Disease.rate, Wounds.rate, Other.rate) %>%
  pivot_longer(
    cols = ends_with(".rate"),
    names_to = "cause",
    values_to = "rate"
  ) %>%
  mutate(
    cause = factor(
      cause,
      levels = c("Disease.rate", "Wounds.rate", "Other.rate"),
      labels = c("질병", "부상", "기타")
    )
  )',
  # 2단계 앞: 넓은 모양 그대로 그려 보기. 원인마다 레이어를 하나씩 쓰게 되고, 레이어끼리는 쌓이지 않고 겹친다
  "rose-0-wide" = 'ggplot(
  data = Nightingale,
  mapping = aes(x = Date)
) +
  geom_col(
    aes(
      y = Disease.rate,
      fill = "질병"
    )
  ) +
  geom_col(
    aes(
      y = Wounds.rate,
      fill = "부상"
    )
  ) +
  geom_col(
    aes(
      y = Other.rate,
      fill = "기타"
    )
  )',
  # 3단계: position 을 적지 않으면 기본값 "stack" 으로 쌓인다
  "rose-1-bar" = 'ggplot(
  data = rose,
  mapping = aes(
    x = Date,
    y = rate,
    fill = cause
  )
) +
  geom_col()',
  # 3단계 펼침 상자: position 별 막대 배치. 막대가 잘 보이도록 여섯 달(1854년 10월 ~ 1855년 3월)만 쓴다
  "pos-data" = 'rose_winter <- rose %>%
  filter(Date >= as.Date("1854-10-01"), Date <= as.Date("1855-03-01"))',
  "pos-stack" = 'ggplot(
  data = rose_winter,
  mapping = aes(
    x = Date,
    y = rate,
    fill = cause
  )
) +
  geom_col(position = "stack")',
  "pos-dodge" = 'ggplot(
  data = rose_winter,
  mapping = aes(
    x = Date,
    y = rate,
    fill = cause
  )
) +
  geom_col(position = "dodge")',
  "pos-fill" = 'ggplot(
  data = rose_winter,
  mapping = aes(
    x = Date,
    y = rate,
    fill = cause
  )
) +
  geom_col(position = "fill")',
  "pos-identity" = 'ggplot(
  data = rose_winter,
  mapping = aes(
    x = Date,
    y = rate,
    fill = cause
  )
) +
  geom_col(position = "identity", alpha = 0.6)',
  "rose-2-polar" = 'ggplot(
  data = rose,
  mapping = aes(
    x = Date,
    y = rate,
    fill = cause
  )
) +
  geom_col() +
  coord_polar()',
  "rose-3-area" = '# 작은 쐐기가 큰 쐐기에 가리지 않도록 달마다 큰 값부터 그린다
rose <- rose %>%
  arrange(Date, desc(rate))

ggplot(
  data = rose,
  mapping = aes(
    x = Date,
    y = rate,
    fill = cause
  )
) +
  geom_col(position = "identity", alpha = 0.8) +
  scale_y_sqrt() +
  coord_polar()',
  "rose-4-facet" = 'rose <- rose %>%
  mutate(
    period = if_else(
      Date < as.Date("1855-04-01"),
      "1854년 4월 ~ 1855년 3월",
      "1855년 4월 ~ 1856년 3월"
    ),
    month = factor(
      month(Date),
      levels = c(4:12, 1:3),
      labels = paste0(c(4:12, 1:3), "월")
    )
  )

ggplot(
  data = rose,
  mapping = aes(
    x = month,
    y = rate,
    fill = cause
  )
) +
  geom_col(position = "identity", alpha = 0.8, width = 1) +
  scale_y_sqrt() +
  coord_polar(start = 3 * pi / 2) +
  facet_wrap(vars(period))',
  "rose-5-swap" = 'rose <- rose %>%
  mutate(
    period = factor(
      period,
      levels = c("1855년 4월 ~ 1856년 3월", "1854년 4월 ~ 1855년 3월")
    )
  )

ggplot(
  data = rose,
  mapping = aes(
    x = month,
    y = rate,
    fill = cause
  )
) +
  geom_col(position = "identity", alpha = 0.8, width = 1) +
  scale_y_sqrt() +
  coord_polar(start = 3 * pi / 2) +
  facet_wrap(vars(period))',
  "rose-6-final" = 'ggplot(
  data = rose,
  mapping = aes(
    x = month,
    y = rate,
    fill = cause
  )
) +
  geom_col(
    position = "identity",
    alpha = 0.85,
    width = 1,
    colour = "grey30",
    linewidth = 0.2
  ) +
  scale_y_sqrt() +
  scale_fill_manual(
    values = c("질병" = "#7BA3CC", "부상" = "#E08A86", "기타" = "#4D4D4D")
  ) +
  coord_polar(start = 3 * pi / 2) +
  facet_wrap(vars(period)) +
  labs(
    title = "동방 주둔 영국군의 사망 원인",
    subtitle = "크림 전쟁, 쐐기의 넓이 = 그달의 사망률(연 환산, 1,000명당)",
    fill = "사망 원인",
    caption = "자료: Nightingale(1858), R 패키지 HistData"
  ) +
  theme_minimal(base_family = "Noto Sans KR") +
  theme(
    axis.title = element_blank(),
    axis.text.y = element_blank(),
    panel.grid.major.y = element_blank(),
    strip.text = element_text(face = "bold", size = 11),
    legend.position = "bottom",
    plot.title = element_text(face = "bold", size = 15)
  )'
)

env <- new.env()
for (id in names(codes)) {
  res <- withVisible(eval(parse(text = codes[[id]], encoding = "UTF-8"), envir = env))
  if (id %in% c("rose-look", "pos-data")) next
  if (id == "rose-prep") {
    showtext::showtext_opts(dpi = 150)   # 저장 dpi와 글자 크기 계산 dpi를 맞춘다
    next
  }
  w <- if (id %in% c("rose-4-facet", "rose-5-swap", "rose-6-final")) 8 else if (startsWith(id, "pos-")) 4.5 else 5
  h <- if (id %in% c("rose-0-wide", "rose-1-bar")) 3.4 else if (startsWith(id, "pos-")) 3 else if (id %in% c("rose-4-facet", "rose-5-swap", "rose-6-final")) 5 else 5
  suppressWarnings(
    ggsave(file.path(out_dir, paste0(id, ".png")), res$value,
           device = ragg::agg_png, width = w, height = h, dpi = 150, bg = "white")
  )
}

args <- commandArgs(trailingOnly = TRUE)
if (length(args) >= 1) {
  jsonlite::write_json(codes, args[1], auto_unbox = TRUE, pretty = TRUE)
}
