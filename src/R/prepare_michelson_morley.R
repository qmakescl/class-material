# Michelson(1879)의 빛의 속도 반복측정 100회를 자료 페이지용 JS 자산으로 만든다.
#
# 입력  : R 기본 패키지 datasets 의 morley
#         (Michelson, A. A. 1882. Experimental determination of the velocity of light
#          made at the U.S. Naval Academy, Annapolis. 측정은 1879년)
#         Expt = 실험 회차(1-5), Run = 회차 안의 순번(1-20),
#         Speed = 빛의 속도(km/s)에서 299,000을 뺀 값
# 출력  : docs/assets/data/michelson-morley.js  (window.MICHELSON)
#
# 실행  : Rscript src/R/prepare_michelson_morley.R   (저장소 루트에서)

out_path <- file.path("docs", "assets", "data", "michelson-morley.js")
if (!dir.exists(dirname(out_path))) stop("저장소 루트에서 실행하세요: ", dirname(out_path))

d <- datasets::morley
speed <- d$Speed + 299000          # km/s
m <- mean(speed)
s <- sd(speed)
true_c <- 299792.458                # 현재 정의값 (km/s)

within <- function(k) mean(abs(speed - m) <= k * s)

js_num <- function(x, digits = 1) sprintf(paste0("%.", digits, "f"), x)

payload <- paste0(
  "{",
  '"source":"Michelson, A. A. (1882). 1879년 측정. R datasets::morley",',
  '"unit":"km/s",',
  '"n":', nrow(d), ",",
  '"trueValue":', js_num(true_c, 3), ",",
  '"mean":', js_num(m, 1), ",",
  '"sd":', js_num(s, 1), ",",
  '"within1":', js_num(within(1), 3), ",",
  '"within2":', js_num(within(2), 3), ",",
  '"expt":[', paste(d$Expt, collapse = ","), "],",
  '"run":[', paste(d$Run, collapse = ","), "],",
  '"speed":[', paste(js_num(speed, 0), collapse = ","), "]",
  "}"
)

writeLines(
  c(
    "/* 생성 파일 — 직접 수정하지 않는다.",
    "   src/R/prepare_michelson_morley.R 이 R datasets::morley 에서 만든다. */",
    paste0("window.MICHELSON = ", payload, ";")
  ),
  out_path,
  useBytes = TRUE
)

cat(out_path, "생성\n")
cat(sprintf("  n = %d, 평균 %.1f km/s, 표준편차 %.1f km/s\n", nrow(d), m, s))
cat(sprintf("  평균 - 참값 = %.1f km/s\n", m - true_c))
cat(sprintf("  평균±1sd 안 %.0f%%, 평균±2sd 안 %.0f%%\n", 100 * within(1), 100 * within(2)))
