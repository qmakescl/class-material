/* R 실습 자료 세 쪽이 함께 쓰는 스크립트
   (data-science/VScode-R-languageserver.html, statistics/prepare-for-ttest.html, statistics/mean-test-with-r.html)
   - 함수 도움말 사전(FN)과 풍선 도움말, 코드 상자의 주석 색·복사 버튼, 레일 목차의 현재 위치 표시,
     주소의 #이름이 가리키는 펼침 상자 열기.
   - 쪽의 본문 뒤, 그 쪽 고유의 스크립트 앞에 불러온다. FN, esc, wrapFns 는 뒤따르는 스크립트(실험판)가 그대로 쓴다. */

/* ── 함수 도움말 사전: [인수, 1 필수 / 0 선택 / 2 사실상 필수, 설명] ── */
const FN={
'install.packages':{pkg:'utils',sig:'install.packages(pkgs, repos, type)',why:'CRAN에서 패키지를 내려받아 설치한다. 컴퓨터마다 한 번만 하면 된다.',
  args:[['pkgs',1,'설치할 패키지 이름. 문자형 벡터'],['repos',0,'패키지를 내려받을 저장소 주소. 기본값은 R에 설정된 저장소'],['type',0,'내려받을 형식. "binary"는 미리 만들어 둔 설치 파일만 받는다. Windows와 macOS의 기본값은 바이너리를 우선하되 소스가 더 새 버전이면 묻는다']],ret:'없음. 설치 과정이 화면에 출력된다.'},
'library':{pkg:'base',sig:'library(package)',why:'설치된 패키지를 불러와 그 안의 함수를 쓸 수 있게 한다. R을 새로 켤 때마다 실행한다.',
  args:[['package',2,'불러올 패키지 이름. 따옴표 없이 적어도 된다. 생략하면 설치된 패키지 목록을 보여 준다']],ret:'없음(불러온 패키지 목록을 보이지 않게 돌려준다).'},
'c':{pkg:'base',sig:'c(...)',why:'여러 값을 묶어 하나의 벡터로 만든다.',
  args:[['...',2,'묶을 값들. 쉼표로 구분한다. <code>이름 = 값</code>으로 쓰면 이름 붙은 벡터가 된다']],ret:'벡터. 자료형이 섞이면 문자형 쪽으로 통일된다.'},
'rep':{pkg:'base',sig:'rep(x, times, each)',why:'값을 반복해 벡터를 만든다.',
  args:[['x',1,'반복할 값 또는 벡터'],['each',0,'원소 하나하나를 연달아 반복할 횟수'],['times',0,'벡터 전체를 반복할 횟수. 기본값 1']],ret:'x와 같은 자료형의 벡터.'},
'list':{pkg:'base',sig:'list(...)',why:'종류가 다른 객체들을 하나로 묶는다. 여기서는 Excel 시트 이름과 데이터프레임을 짝짓는 데 쓴다.',
  args:[['...',0,'<code>이름 = 객체</code> 꼴로 묶을 것들']],ret:'리스트.'},
'dir.create':{pkg:'base',sig:'dir.create(path, showWarnings = TRUE, recursive = FALSE)',why:'폴더를 만든다.',
  args:[['path',1,'만들 폴더의 경로. 문자열'],['showWarnings',0,'폴더가 이미 있을 때 경고를 낼지. 기본값 TRUE'],['recursive',0,'중간 폴더까지 한꺼번에 만들지. 기본값 FALSE']],ret:'성공 여부를 나타내는 논리값 하나(화면에는 보이지 않는다).'},
'write_xlsx':{pkg:'writexl',sig:'write_xlsx(x, path)',why:'데이터프레임을 Excel(.xlsx) 파일로 저장한다.',
  args:[['x',1,'데이터프레임 하나, 또는 이름 붙은 리스트. 리스트의 이름이 시트 이름이 된다'],['path',2,'저장할 파일 경로. 생략하면 임시 파일에 저장한다']],ret:'저장된 파일의 경로(화면에는 보이지 않는다).'},
'excel_sheets':{pkg:'readxl',sig:'excel_sheets(path)',why:'Excel 파일 안의 시트 이름을 확인한다.',
  args:[['path',1,'Excel 파일 경로']],ret:'시트 이름이 담긴 문자형 벡터.'},
'read_excel':{pkg:'readxl',sig:'read_excel(path, sheet = NULL, range = NULL, skip = 0)',why:'Excel 파일의 시트 하나를 읽는다.',
  args:[['path',1,'Excel 파일 경로'],['sheet',0,'읽을 시트의 이름 또는 번호. 기본값은 첫 번째 시트'],['range',0,'읽을 셀 범위. 예: "A1:D49"'],['skip',0,'위에서 건너뛸 행 수. 기본값 0']],ret:'tibble(데이터프레임의 한 종류). 기본 데이터프레임이 필요하면 <code>as.data.frame()</code>으로 바꾼다.'},
'View':{pkg:'utils',sig:'View(x)',why:'데이터를 표 형태의 창으로 띄워 본다.',args:[['x',1,'볼 데이터프레임']],ret:'없음. 표가 새 탭에 열린다.'},
'getwd':{pkg:'base',sig:'getwd()',why:'지금 R이 기준으로 삼는 작업 폴더를 확인한다.',args:[],ret:'폴더 경로 문자열 하나.'},
'factor':{pkg:'base',sig:'factor(x, levels, labels = levels)',why:'범주를 나타내는 변수(집단, 성별 등)를 factor로 만들고 수준의 순서를 정한다.',
  args:[['x',2,'범주로 만들 벡터'],['levels',0,'수준과 그 순서. 생략하면 값을 정렬한 순서'],['labels',0,'수준에 붙일 표시 이름. 기본값은 levels와 같다']],ret:'factor. <code>t.test()</code>는 첫 번째 수준에서 두 번째 수준을 뺀다.'},
'levels':{pkg:'base',sig:'levels(x)',why:'factor의 수준과 그 순서를 확인한다.',args:[['x',1,'factor']],ret:'수준 이름이 담긴 문자형 벡터.'},
'is.na':{pkg:'base',sig:'is.na(x)',why:'값마다 결측(NA)인지 확인한다.',args:[['x',1,'확인할 벡터 또는 데이터프레임']],ret:'x와 같은 모양의 논리값(TRUE는 결측).'},
'nrow':{pkg:'base',sig:'nrow(x)',why:'행의 수를 센다.',args:[['x',1,'데이터프레임 또는 행렬']],ret:'정수 하나.'},
'data':{pkg:'utils',sig:'data(...)',why:'R이나 패키지에 들어 있는 예제 데이터를 불러온다. cars처럼 R에 기본으로 들어 있는 데이터는 이 줄 없이 이름만 적어도 쓸 수 있다.',args:[['...',0,'불러올 데이터의 이름. 생략하면 쓸 수 있는 예제 데이터의 목록을 보여 준다']],ret:'불러온 데이터의 이름(화면에는 보이지 않는다).'},
'str':{pkg:'utils',sig:'str(object)',why:'객체의 구조를 짧게 보여 준다. 데이터프레임이면 행과 열의 수, 열마다의 자료형과 앞쪽 값이 나온다.',args:[['object',1,'구조를 볼 객체']],ret:'없음. 구조가 화면에 출력된다.'},
'plot':{pkg:'graphics',sig:'plot(x, y)',why:'기본 그림을 그린다. 숫자 열이 둘인 데이터프레임을 넣으면 산점도가 된다.',args:[['x',1,'가로축에 놓을 값. 데이터프레임을 넣을 수도 있다'],['y',0,'세로축에 놓을 값']],ret:'없음. 그림이 그려진다.'},
'hist':{pkg:'graphics',sig:'hist(x, breaks = "Sturges")',why:'히스토그램을 그린다. 값이 어떤 모양으로 퍼져 있는지 본다.',args:[['x',1,'숫자 벡터'],['breaks',0,'구간을 나누는 방법이나 구간의 수']],ret:'구간과 개수가 담긴 객체(화면에는 보이지 않는다). 그림이 그려진다.'},
'dim':{pkg:'base',sig:'dim(x)',why:'표의 행 수와 열 수를 한 번에 확인한다.',args:[['x',1,'데이터프레임 또는 행렬']],ret:'길이 2인 정수 벡터. 앞이 행 수, 뒤가 열 수다.'},
'names':{pkg:'base',sig:'names(x)',why:'열 이름을 확인한다.',args:[['x',1,'데이터프레임. 이름 붙은 벡터나 리스트도 된다']],ret:'이름이 담긴 문자형 벡터.'},
'head':{pkg:'utils',sig:'head(x, n = 6)',why:'표의 앞쪽 몇 행을 본다.',args:[['x',1,'데이터프레임 또는 벡터'],['n',0,'볼 행의 수. 기본값 6']],ret:'앞쪽 n행으로 된 데이터프레임.'},
'tail':{pkg:'utils',sig:'tail(x, n = 6)',why:'표의 뒤쪽 몇 행을 본다. 파일 끝에 합계 줄이나 빈 줄이 딸려 왔는지 볼 때 쓴다.',args:[['x',1,'데이터프레임 또는 벡터'],['n',0,'볼 행의 수. 기본값 6']],ret:'뒤쪽 n행으로 된 데이터프레임.'},
'summary':{pkg:'base',sig:'summary(object)',why:'열마다 요약 통계를 한꺼번에 보여 준다. 숫자 열은 최솟값, 1사분위수, 중앙값, 평균, 3사분위수, 최댓값이 나온다.',args:[['object',1,'데이터프레임. 벡터 하나나 모형 결과를 넣을 수도 있다']],ret:'요약 표. 결측이 있는 열에는 결측의 개수(NA\'s)가 함께 나온다.'},
'n_distinct':{pkg:'dplyr',sig:'n_distinct(..., na.rm = FALSE)',why:'서로 다른 값이 몇 개인지 센다. 행 수와 같으면 겹치는 값이 없는 것이다.',args:[['...',2,'셀 대상인 벡터(열)'],['na.rm',0,'결측을 빼고 셀지. 기본값 FALSE']],ret:'정수 하나.'},
'median':{pkg:'stats',sig:'median(x, na.rm = FALSE)',why:'중앙값을 구한다. 값을 크기순으로 줄 세웠을 때 가운데 값이다.',args:[['x',1,'숫자 벡터'],['na.rm',0,'결측을 빼고 계산할지. 기본값 FALSE']],ret:'숫자 하나.'},
'quantile':{pkg:'stats',sig:'quantile(x, probs, na.rm = FALSE)',why:'분위수를 구한다. probs = 0.25이면 1사분위수, 0.75이면 3사분위수다.',args:[['x',1,'숫자 벡터'],['probs',0,'구할 위치. 0과 1 사이의 값. 생략하면 0, 0.25, 0.5, 0.75, 1의 다섯 값을 모두 구한다'],['na.rm',0,'결측을 빼고 계산할지. 기본값 FALSE']],ret:'이름 붙은 숫자 벡터. 예: 25%'},
'min':{pkg:'base',sig:'min(..., na.rm = FALSE)',why:'가장 작은 값을 구한다.',args:[['...',1,'숫자 벡터'],['na.rm',0,'결측을 빼고 계산할지. 기본값 FALSE']],ret:'숫자 하나.'},
'max':{pkg:'base',sig:'max(..., na.rm = FALSE)',why:'가장 큰 값을 구한다.',args:[['...',1,'숫자 벡터'],['na.rm',0,'결측을 빼고 계산할지. 기본값 FALSE']],ret:'숫자 하나.'},
'mean':{pkg:'base',sig:'mean(x, na.rm = FALSE)',why:'산술평균을 구한다.',
  args:[['x',1,'숫자 벡터'],['na.rm',0,'결측을 빼고 계산할지. 기본값 FALSE. 결측이 하나라도 있으면 결과가 NA가 된다']],ret:'숫자 하나.'},
'sd':{pkg:'stats',sig:'sd(x, na.rm = FALSE)',why:'표본 표준편차를 구한다. 분모는 n − 1이다.',
  args:[['x',1,'숫자 벡터'],['na.rm',0,'결측을 빼고 계산할지. 기본값 FALSE']],ret:'숫자 하나.'},
'var':{pkg:'stats',sig:'var(x, na.rm = FALSE)',why:'표본 분산을 구한다. 분모는 n − 1이다.',
  args:[['x',1,'숫자 벡터'],['na.rm',0,'결측을 빼고 계산할지. 기본값 FALSE']],ret:'숫자 하나(벡터 하나를 넣었을 때).'},
'boxplot':{pkg:'graphics',sig:'boxplot(x, horizontal = FALSE)',why:'상자그림을 그린다. 사분위수로 값이 퍼진 모양을 본다.',args:[['x',1,'숫자 벡터'],['horizontal',0,'TRUE이면 상자를 가로로 눕혀 그린다. 기본값 FALSE']],ret:'그림에 쓴 통계값이 담긴 리스트(화면에는 보이지 않는다). 그림이 그려진다.'},
'length':{pkg:'base',sig:'length(x)',why:'벡터에 값이 몇 개 들어 있는지 센다.',args:[['x',1,'벡터. 데이터프레임을 넣으면 열의 수가 나온다']],ret:'정수 하나.'},
'class':{pkg:'base',sig:'class(x)',why:'객체가 어떤 종류인지 확인한다.',args:[['x',1,'종류를 볼 객체']],ret:'종류의 이름이 담긴 문자형 벡터. 예: "numeric", "data.frame"'},
'round':{pkg:'base',sig:'round(x, digits = 0)',why:'반올림한다.',args:[['x',1,'숫자 또는 숫자 벡터'],['digits',0,'남길 소수 자릿수. 기본값 0']],ret:'x와 길이가 같은 숫자 벡터.'},
'sqrt':{pkg:'base',sig:'sqrt(x)',why:'제곱근을 구한다.',args:[['x',1,'0 이상의 숫자 또는 숫자 벡터']],ret:'x와 길이가 같은 숫자 벡터.'},
'cor':{pkg:'stats',sig:'cor(x, y, method = "pearson")',why:'두 변수의 상관계수를 구한다.',
  args:[['x',1,'숫자 벡터'],['y',2,'x와 길이가 같은 숫자 벡터. x가 표이면 생략할 수 있다'],['method',0,'"pearson"(기본값), "spearman", "kendall"']],ret:'−1과 1 사이의 숫자 하나(두 벡터를 넣었을 때).'},
'unname':{pkg:'base',sig:'unname(obj)',why:'값에 붙어 있는 이름표를 뗀다. 여기서는 t 값에 붙은 "t"라는 이름을 지운다.',args:[['obj',1,'이름이 붙은 객체']],ret:'이름이 없어진 같은 값.'},
'shapiro.test':{pkg:'stats',sig:'shapiro.test(x)',why:'Shapiro–Wilk 정규성 검정. 영가설은 "자료가 정규분포에서 나왔다"이다.',
  args:[['x',1,'숫자 벡터. 결측을 뺀 값이 3개 이상 5000개 이하여야 한다']],ret:'검정 결과 리스트(htest). <code>$statistic</code>에 W, <code>$p.value</code>에 p-value가 있다.'},
'tibble':{pkg:'tibble',sig:'tibble(...)',why:'길이가 같은 벡터들을 열로 삼아 표(tibble)를 만든다. tidyverse에서 쓰는 데이터프레임이다.',
  args:[['...',2,'<code>열이름 = 벡터</code> 꼴. 모든 벡터의 길이가 같아야 한다']],ret:'tibble. 행은 사례, 열은 변수다. 출력하면 앞 10행과 열의 자료형을 보여 준다.'},
'write_csv':{pkg:'readr',sig:'write_csv(x, file)',why:'데이터프레임을 CSV 파일로 저장한다. 인코딩은 UTF-8이고 행 번호는 쓰지 않는다.',
  args:[['x',1,'저장할 데이터프레임'],['file',1,'저장할 파일 경로']],ret:'넣은 데이터프레임 x(화면에는 보이지 않는다). 파일이 만들어진다.'},
'read_csv':{pkg:'readr',sig:'read_csv(file, col_types = NULL, locale = default_locale())',why:'CSV 파일을 읽어 tibble로 만든다. 열의 자료형을 추측해 알려 준다.',
  args:[['file',1,'읽을 파일 경로'],['col_types',0,'열의 자료형을 직접 정할 때. 기본값은 자동 추측'],['locale',0,'인코딩 등 지역 설정. 기본값은 UTF-8. <code>locale()</code>로 만든다']],ret:'tibble.'},
'locale':{pkg:'readr',sig:'locale(encoding = "UTF-8")',why:'파일을 읽을 때의 지역 설정(인코딩, 소수점 기호 등)을 만든다. <code>read_csv()</code>의 locale 인수에 넣는다.',
  args:[['encoding',0,'파일의 인코딩. 기본값 "UTF-8". 한글 Windows 파일은 "CP949"']],ret:'지역 설정 객체.'},
'write_rds':{pkg:'readr',sig:'write_rds(x, file)',why:'R 객체를 R 전용 형식(.rds)으로 저장한다. factor의 순서 같은 정보가 그대로 남는다.',
  args:[['x',1,'저장할 객체'],['file',1,'저장할 파일 경로']],ret:'넣은 객체 x(화면에는 보이지 않는다).'},
'read_rds':{pkg:'readr',sig:'read_rds(file)',why:'.rds 파일을 읽어 저장했던 객체를 그대로 되살린다.',args:[['file',1,'읽을 파일 경로']],ret:'저장했던 객체.'},
'glimpse':{pkg:'dplyr',sig:'glimpse(x)',why:'표의 구조를 한눈에 본다. 행·열 수, 열마다의 자료형과 앞쪽 값.',
  args:[['x',1,'살펴볼 데이터프레임']],ret:'넣은 x(화면에는 보이지 않는다). 구조가 화면에 출력된다.'},
'mutate':{pkg:'dplyr',sig:'mutate(.data, ...)',why:'열을 새로 만들거나 기존 열을 바꾼다. 행의 수는 변하지 않는다.',
  args:[['.data',1,'파이프로 넘겨받는 데이터프레임. 파이프를 쓰면 적지 않는다'],['...',2,'<code>열이름 = 계산식</code> 꼴. 여러 개를 쉼표로 잇는다']],ret:'열이 추가되거나 바뀐 데이터프레임. 원래 데이터는 바뀌지 않으므로 <code>&lt;-</code>로 담아야 남는다.'},
'filter':{pkg:'dplyr',sig:'filter(.data, ...)',why:'조건에 맞는 행만 고른다.',
  args:[['.data',1,'파이프로 넘겨받는 데이터프레임. 파이프를 쓰면 적지 않는다'],['...',2,'행을 고르는 조건. 같다는 <code>==</code>로 쓴다. 여러 조건을 쉼표로 이으면 "그리고"가 된다']],ret:'조건에 맞는 행만 남은 데이터프레임.'},
'count':{pkg:'dplyr',sig:'count(x, ...)',why:'범주별로 행이 몇 개인지 센다.',
  args:[['x',1,'파이프로 넘겨받는 데이터프레임. 파이프를 쓰면 적지 않는다'],['...',0,'셀 기준이 되는 열. 생략하면 전체 행 수를 센다']],ret:'범주와 개수 <code>n</code> 열로 된 데이터프레임.'},
'group_by':{pkg:'dplyr',sig:'group_by(.data, ...)',why:'표를 집단으로 나눈다. 뒤따르는 <code>summarise()</code>가 집단별로 계산된다.',
  args:[['.data',1,'파이프로 넘겨받는 데이터프레임. 파이프를 쓰면 적지 않는다'],['...',2,'집단을 나누는 열']],ret:'집단 정보가 붙은 데이터프레임. 겉모습은 그대로다.'},
'summarise':{pkg:'dplyr',sig:'summarise(.data, ...)',why:'여러 행을 요약 통계량 한 행으로 줄인다. <code>group_by()</code> 뒤에 쓰면 집단마다 한 행이 된다.',
  args:[['.data',1,'파이프로 넘겨받는 데이터프레임. 파이프를 쓰면 적지 않는다'],['...',2,'<code>이름 = 요약 함수(열)</code> 꼴. 예: <code>m = mean(x)</code>']],ret:'요약값으로 된 데이터프레임. 집단마다 한 행.'},
'across':{pkg:'dplyr',sig:'across(.cols, .fns)',why:'같은 계산을 여러 열에 한꺼번에 적용한다. <code>summarise()</code>나 <code>mutate()</code> 안에서 쓴다.',
  args:[['.cols',1,'적용할 열. 열 이름들이나 <code>everything()</code>'],['.fns',2,'적용할 함수. <code>~ sum(is.na(.x))</code>처럼 쓰면 <code>.x</code> 자리에 각 열이 들어간다']],ret:'열마다 계산한 결과 열들.'},
'everything':{pkg:'tidyselect',sig:'everything()',why:'모든 열을 가리킨다. <code>across()</code> 같은 열 선택 자리에 쓴다.',args:[],ret:'모든 열의 선택.'},
'n':{pkg:'dplyr',sig:'n()',why:'지금 집단의 행 수를 센다. <code>summarise()</code>나 <code>mutate()</code> 안에서만 쓴다.',args:[],ret:'정수 하나.'},
'pull':{pkg:'dplyr',sig:'pull(.data, var = -1)',why:'데이터프레임에서 열 하나를 벡터로 꺼낸다. <code>d$열이름</code>과 같다.',
  args:[['.data',1,'파이프로 넘겨받는 데이터프레임. 파이프를 쓰면 적지 않는다'],['var',2,'꺼낼 열의 이름. 생략하면 마지막 열']],ret:'벡터.'},
'select':{pkg:'dplyr',sig:'select(.data, ...)',why:'표에서 필요한 열만 고른다. 적은 순서대로 열이 놓인다.',args:[['.data',1,'파이프로 넘겨받는 데이터프레임. 파이프를 쓰면 적지 않는다'],['...',2,'남길 열의 이름. 쉼표로 잇는다. 앞에 <code>-</code>를 붙이면 그 열을 뺀다']],ret:'고른 열만 남은 데이터프레임. 행의 수는 그대로다.'},
'pivot_wider':{pkg:'tidyr',sig:'pivot_wider(data, names_from = name, values_from = value, names_prefix = "")',why:'세로로 쌓인 긴 모양을 옆으로 펼쳐 넓은 모양으로 바꾼다. <code>pivot_longer()</code>의 반대다.',
  args:[['data',1,'파이프로 넘겨받는 데이터프레임. 파이프를 쓰면 적지 않는다'],['names_from',2,'새 열의 이름이 될 값이 든 열. 기본값은 name 열'],['values_from',2,'새 열에 채울 값이 든 열. 기본값은 value 열'],['names_prefix',0,'새 열 이름 앞에 붙일 글자. 예: "sodium_"']],ret:'행이 줄고 열이 늘어난 넓은 모양의 데이터프레임.'},
'pivot_longer':{pkg:'tidyr',sig:'pivot_longer(data, cols, names_to = "name", values_to = "value", names_prefix = NULL)',why:'옆으로 나란히 있는 열들을 세로로 쌓아 긴 모양으로 바꾼다.',
  args:[['data',1,'파이프로 넘겨받는 데이터프레임. 파이프를 쓰면 적지 않는다'],['cols',1,'세로로 쌓을 열들'],['names_to',0,'원래 열 이름이 들어갈 새 열의 이름. 기본값 "name"'],['values_to',0,'값이 들어갈 새 열의 이름. 기본값 "value"'],['names_prefix',0,'열 이름 앞에서 지울 글자. 예: "sodium_"']],ret:'행이 늘어난 긴 모양의 데이터프레임.'},
'sum':{pkg:'base',sig:'sum(..., na.rm = FALSE)',why:'합을 구한다. 논리값에 쓰면 TRUE의 개수가 된다.',
  args:[['...',2,'숫자 또는 논리값 벡터'],['na.rm',0,'결측을 빼고 계산할지. 기본값 FALSE']],ret:'숫자 하나.'},
'ggplot':{pkg:'ggplot2',sig:'ggplot(data = NULL, mapping = aes())',why:'그림의 바탕을 만든다. 어떤 데이터의 어떤 변수를 축에 놓을지 정하고, 그림의 종류는 <code>+</code>로 더한다.',
  args:[['data',2,'그릴 데이터프레임. 파이프로 넘겨받을 수도 있다'],['mapping',0,'변수와 축의 대응. <code>aes()</code>로 만든다']],ret:'ggplot 객체. 출력하면 그림이 그려지고, 변수에 담아 두었다가 저장할 수 있다.'},
'aes':{pkg:'ggplot2',sig:'aes(x, y, ...)',why:'데이터의 변수를 그림의 요소(가로축, 세로축, 색, 묶음 등)에 대응시킨다.',
  args:[['x',0,'가로축에 놓을 변수'],['y',0,'세로축에 놓을 변수'],['group',0,'선으로 이을 묶음을 정하는 변수'],['sample',0,'Q–Q 그림에 쓸 변수']],ret:'대응 정보. <code>ggplot()</code>이나 geom 함수 안에 넣는다.'},
'geom_histogram':{pkg:'ggplot2',sig:'geom_histogram(bins = 30, binwidth = NULL)',why:'히스토그램 레이어를 더한다. 분포의 모양을 본다.',
  args:[['bins',0,'구간의 수. 기본값 30'],['binwidth',0,'구간의 너비. bins 대신 쓸 수 있다']],ret:'레이어. <code>+</code>로 그림에 더한다.'},
'geom_boxplot':{pkg:'ggplot2',sig:'geom_boxplot(outlier.shape = 19)',why:'상자그림 레이어를 더한다. 집단별 분포를 비교한다.',
  args:[['outlier.shape',0,'이상값 점의 모양. NA로 두면 이상값 점을 그리지 않는다(개별 값을 따로 찍을 때)']],ret:'레이어. <code>+</code>로 그림에 더한다.'},
'geom_jitter':{pkg:'ggplot2',sig:'geom_jitter(width = NULL, alpha = 1)',why:'개별 값을 점으로 찍되 겹치지 않게 좌우로 조금 흩뜨린다.',
  args:[['width',0,'좌우로 흩뜨리는 폭'],['alpha',0,'투명도. 0(투명)에서 1(불투명)']],ret:'레이어. <code>+</code>로 그림에 더한다.'},
'geom_line':{pkg:'ggplot2',sig:'geom_line(alpha = 1)',why:'선 레이어를 더한다. <code>aes(group = )</code>으로 묶은 값끼리 잇는다.',
  args:[['alpha',0,'투명도. 0(투명)에서 1(불투명)']],ret:'레이어. <code>+</code>로 그림에 더한다.'},
'geom_point':{pkg:'ggplot2',sig:'geom_point(alpha = 1, size = 1.5)',why:'점 레이어를 더한다.',
  args:[['alpha',0,'투명도'],['size',0,'점의 크기']],ret:'레이어. <code>+</code>로 그림에 더한다.'},
'stat_qq':{pkg:'ggplot2',sig:'stat_qq()',why:'정규 Q–Q 그림의 점을 찍는다. 변수는 <code>aes(sample = )</code>으로 정한다. 점들이 직선에 가까우면 정규분포에 가깝다.',args:[],ret:'레이어. <code>+</code>로 그림에 더한다.'},
'stat_qq_line':{pkg:'ggplot2',sig:'stat_qq_line()',why:'Q–Q 그림에 기준 직선을 더한다.',args:[],ret:'레이어. <code>+</code>로 그림에 더한다.'},
'labs':{pkg:'ggplot2',sig:'labs(title, x, y)',why:'제목과 축 이름을 붙인다.',
  args:[['title',0,'그림 제목'],['x',0,'가로축 이름. NULL이면 지운다'],['y',0,'세로축 이름']],ret:'이름표 설정. <code>+</code>로 그림에 더한다.'},
'ggsave':{pkg:'ggplot2',sig:'ggsave(filename, plot = last_plot(), width, height, dpi = 300)',why:'그림을 파일로 저장한다. 확장자(.png, .pdf 등)에 따라 형식이 정해진다.',
  args:[['filename',1,'저장할 파일 경로'],['plot',0,'저장할 그림. 기본값은 마지막에 그린 그림'],['width',0,'너비(인치)'],['height',0,'높이(인치)'],['dpi',0,'해상도. 기본값 300']],ret:'저장한 파일 경로(화면에는 보이지 않는다).'},
'font_import':{pkg:'extrafont',sig:'font_import(paths = NULL, pattern = NULL, prompt = TRUE)',why:'컴퓨터에 설치된 트루타입 글꼴을 찾아 R에 등록한다. 컴퓨터마다 한 번만 하면 된다.',
  args:[['paths',0,'글꼴을 찾을 폴더. 기본값은 시스템 글꼴 폴더'],['pattern',0,'등록할 글꼴 파일 이름에 들어 있어야 할 글자. 기본값은 모든 글꼴'],['prompt',0,'진행할지 묻는 질문을 띄울지. 기본값 TRUE. FALSE면 묻지 않고 바로 진행한다']],ret:'없음. 등록 과정이 화면에 출력된다.'},
'loadfonts':{pkg:'extrafont',sig:'loadfonts(device = "pdf", quiet = FALSE)',why:'등록해 둔 글꼴을 그림 장치에 연결한다. R을 새로 켤 때마다 실행한다.',
  args:[['device',0,'연결할 그림 장치. "pdf"(기본값), "postscript", "win"(Windows 화면)'],['quiet',0,'진행 메시지를 숨길지. 기본값 FALSE']],ret:'없음.'},
'fonts':{pkg:'extrafont',sig:'fonts()',why:'등록된 글꼴의 이름을 확인한다. <code>base_family</code>에는 여기 나온 이름을 그대로 적는다.',args:[],ret:'글꼴 이름이 담긴 문자형 벡터.'},
'grep':{pkg:'base',sig:'grep(pattern, x, value = FALSE)',why:'문자형 벡터에서 특정 글자가 들어 있는 원소를 찾는다.',
  args:[['pattern',1,'찾을 글자(정규표현식)'],['x',1,'찾을 대상인 문자형 벡터'],['value',0,'TRUE면 찾은 원소 자체를, FALSE(기본값)면 그 위치 번호를 돌려준다']],ret:'value = TRUE이면 문자형 벡터, 아니면 정수 벡터.'},
'normalizePath':{pkg:'base',sig:'normalizePath(path)',why:'경로를 줄임 없는 전체 경로로 바꿔 보여 준다.',args:[['path',1,'경로 문자열']],ret:'전체 경로 문자열. Windows에서는 역슬래시가 두 개씩 표시된다.'},
'packageVersion':{pkg:'utils',sig:'packageVersion(pkg)',why:'설치된 패키지의 버전을 알려 준다. 패키지가 설치되었는지 확인할 때 쓴다.',args:[['pkg',1,'패키지 이름. 문자열']],ret:'버전 번호. 설치되지 않은 패키지면 오류가 난다.'},
'file.path':{pkg:'base',sig:'file.path(...)',why:'폴더와 파일 이름을 이어 경로 하나로 만든다.',args:[['...',2,'이을 경로 조각들. 문자열']],ret:'경로 문자열.'},
'R.home':{pkg:'base',sig:'R.home(component = "home")',why:'R이 설치된 폴더를 알려 준다.',args:[['component',0,'알고 싶은 하위 폴더. 기본값 "home"은 설치 폴더 자체']],ret:'경로 문자열.'},
'q':{pkg:'base',sig:'q(save = "default")',why:'R을 끝낸다.',args:[['save',0,'작업 공간을 저장할지. "no", "yes", "ask". 묻는 말이 나오면 n을 입력한다']],ret:'없음. R이 종료된다.'},
'theme_set':{pkg:'ggplot2',sig:'theme_set(new)',why:'이후에 그리는 모든 그림의 기본 모양(테마)을 바꾼다.',args:[['new',1,'적용할 테마. 예: <code>theme_gray()</code>']],ret:'바꾸기 전의 테마(화면에는 보이지 않는다).'},
'theme_gray':{pkg:'ggplot2',sig:'theme_gray(base_size = 11, base_family = "")',why:'ggplot2의 기본 테마. 글자 크기와 글꼴을 정할 수 있다.',
  args:[['base_size',0,'기본 글자 크기. 기본값 11'],['base_family',0,'글꼴 이름. 한글이 깨질 때 한글 글꼴을 지정한다']],ret:'테마 객체.'},
'tidy':{pkg:'broom',sig:'tidy(x)',why:'검정 결과를 한 행짜리 표로 바꾼다. 여러 검정의 결과를 모으거나 저장할 때 편하다. broom은 tidyverse와 함께 설치된다.',
  args:[['x',1,'<code>t.test()</code> 등의 결과 객체']],ret:'tibble. 열은 <code>estimate</code> 추정값, <code>statistic</code> t, <code>p.value</code>, <code>parameter</code> 자유도, <code>conf.low</code>, <code>conf.high</code> 등.'},
'df':{pkg:'stats',sig:'df(x, df1, df2)',why:'F 분포의 밀도(확률밀도함수)를 구한다. 분포 곡선을 그릴 때 쓴다.',
  args:[['x',1,'밀도를 구할 값(0 이상)'],['df1',1,'분자의 자유도'],['df2',1,'분모의 자유도']],ret:'x와 같은 길이의 밀도 값.'},
'pf':{pkg:'stats',sig:'pf(q, df1, df2, lower.tail = TRUE)',why:'F 분포의 누적확률 P(F ≤ q)를 구한다. p-value와 검정력을 계산할 때 쓴다.',
  args:[['q',1,'누적확률을 구할 값'],['df1',1,'분자의 자유도'],['df2',1,'분모의 자유도'],['lower.tail',0,'TRUE(기본값)이면 q 이하의 확률, FALSE면 q 초과의 확률']],ret:'0과 1 사이의 확률.'},
'qf':{pkg:'stats',sig:'qf(p, df1, df2, lower.tail = TRUE)',why:'F 분포의 분위수를 구한다. 누적확률이 p가 되는 F 값으로, 기각역의 경계(임계값)를 구할 때 쓴다.',
  args:[['p',1,'누적확률(0과 1 사이). c(0.025, 0.975)처럼 여러 개를 줄 수 있다'],['df1',1,'분자의 자유도'],['df2',1,'분모의 자유도'],['lower.tail',0,'TRUE(기본값)이면 아래쪽 누적확률 기준']],ret:'p와 같은 길이의 F 값.'},
'stat_function':{pkg:'ggplot2',sig:'stat_function(fun, args = list(), n = 101, ...)',why:'함수 하나를 곡선으로 그린다. 확률밀도함수처럼 식으로 주어진 곡선을 데이터 위에 겹칠 때 쓴다.',
  args:[['fun',1,'x를 받아 y를 돌려주는 함수. df처럼 이름만 주거나 function(x) ... 로 직접 적는다'],['args',0,'fun에 넘길 추가 인수의 리스트. 예: list(df1 = 23, df2 = 23)'],['n',0,'곡선을 그릴 때 계산할 점의 수. 기본값 101']],ret:'ggplot에 더하는 레이어.'},
'var.test':{pkg:'stats',sig:'var.test(x, y, ratio = 1, alternative = "two.sided", conf.level = 0.95)',why:'두 집단의 분산의 비에 대한 F 검정. 영가설은 "두 모분산의 비가 ratio(기본값 1)와 같다"이다. 독립표본 t 검정에서 Student와 Welch 중 무엇을 쓸지 정할 때 쓴다.',
  args:[['x',1,'숫자 벡터. 또는 <code>값 ~ 집단</code> 꼴의 공식'],['y',0,'두 번째 숫자 벡터'],['data',0,'공식을 쓸 때의 데이터프레임'],['ratio',0,'영가설에서의 분산의 비. 기본값 1'],['alternative',0,'대안가설의 방향. "two.sided"(기본값), "less", "greater"'],['conf.level',0,'신뢰수준. 기본값 0.95']],
  ret:'검정 결과 리스트(htest). <code>$statistic</code> F 값, <code>$parameter</code> 두 자유도, <code>$p.value</code>, <code>$conf.int</code> 분산의 비의 신뢰구간, <code>$estimate</code> 표본분산의 비.'},
't.test':{pkg:'stats',sig:'t.test(x, y = NULL, alternative = "two.sided", mu = 0, paired = FALSE, var.equal = FALSE, conf.level = 0.95)',why:'t 검정을 한다. 넣는 인수에 따라 단일표본, 독립표본, 대응표본 검정이 된다.',
  args:[['x',1,'숫자 벡터. 또는 <code>값 ~ 집단</code> 꼴의 공식'],['y',0,'두 번째 숫자 벡터. 넣으면 두 표본 검정이 된다'],['data',0,'공식을 쓸 때, 변수들이 들어 있는 데이터프레임'],['mu',0,'영가설의 값(평균 또는 평균 차이). 기본값 0'],['alternative',0,'대안가설의 방향. "two.sided"(기본값), "less", "greater"'],['paired',0,'대응표본이면 TRUE. 기본값 FALSE'],['var.equal',0,'등분산을 가정하면 TRUE(Student). 기본값 FALSE(Welch)'],['conf.level',0,'신뢰수준. 기본값 0.95']],
  ret:'검정 결과 리스트(htest). <code>$statistic</code> t 값, <code>$parameter</code> 자유도, <code>$p.value</code>, <code>$conf.int</code> 신뢰구간, <code>$estimate</code> 평균(차이), <code>$stderr</code> 표준오차.'},
'cohens_d':{pkg:'effectsize',sig:'cohens_d(x, y = NULL, data = NULL, mu = 0, paired = FALSE, pooled_sd = TRUE, ci = 0.95)',why:'Cohen의 d와 그 신뢰구간을 구한다.',
  args:[['x',1,'숫자 벡터. 또는 <code>값 ~ 집단</code> 꼴의 공식'],['y',0,'두 번째 숫자 벡터'],['data',0,'공식을 쓸 때의 데이터프레임'],['mu',0,'비교할 기준값. 기본값 0'],['paired',0,'대응표본이면 TRUE. 이때 d_z를 구한다. 기본값 FALSE'],['pooled_sd',0,'합동 표준편차로 나눌지. 기본값 TRUE'],['ci',0,'신뢰수준. 기본값 0.95']],
  ret:'한 행짜리 데이터프레임. 열은 <code>Cohens_d</code>, <code>CI</code>, <code>CI_low</code>, <code>CI_high</code>.'},
'hedges_g':{pkg:'effectsize',sig:'hedges_g(x, y = NULL, data = NULL, mu = 0, paired = FALSE, pooled_sd = TRUE, ci = 0.95)',why:'Hedges의 g(작은 표본에서의 치우침을 보정한 d)와 그 신뢰구간을 구한다.',
  args:[['x',1,'숫자 벡터. 또는 <code>값 ~ 집단</code> 꼴의 공식'],['y',0,'두 번째 숫자 벡터'],['data',0,'공식을 쓸 때의 데이터프레임'],['ci',0,'신뢰수준. 기본값 0.95']],
  ret:'한 행짜리 데이터프레임. 열은 <code>Hedges_g</code>, <code>CI</code>, <code>CI_low</code>, <code>CI_high</code>.'}
};
const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const wrapFns=h=>h.replace(/([A-Za-z_][A-Za-z0-9._]*)(?=\()/g,m=>FN.hasOwnProperty(m)?`<span class="fn" tabindex="0" data-fn="${m}">${m}</span>`:m);

/* ── 코드 블록: 함수 도움말, 주석 색, 복사 버튼 ── */
document.querySelectorAll('.cb').forEach(cb=>{
  const pre=cb.querySelector('pre'),raw=pre.textContent;
  if(!cb.classList.contains('out')){
    pre.innerHTML=raw.split('\n').map(line=>{const i=line.indexOf('#');
      return i<0?wrapFns(esc(line)):wrapFns(esc(line.slice(0,i)))+'<span class="cm">'+esc(line.slice(i))+'</span>';}).join('\n');
    const b=document.createElement('button');b.type='button';b.className='copy';b.textContent='복사';
    b.addEventListener('click',()=>{const done=()=>{b.textContent='복사됨';setTimeout(()=>b.textContent='복사',1400);};
      // 마지막 수단: 복사가 막힌 환경에서는 코드를 선택해 두어 Ctrl+C로 복사할 수 있게 한다.
      const fb=()=>{const s=getSelection(),r=document.createRange();r.selectNodeContents(pre);s.removeAllRanges();s.addRange(r);b.textContent='선택됨';};
      // 먼저 숨긴 입력칸으로 복사한다. 클릭한 그 자리에서 바로 실행되어, 클립보드 API가 막힌 미리보기 창이나 http 주소에서도 된다.
      const viaInput=()=>{const ta=document.createElement('textarea');ta.value=raw;ta.setAttribute('readonly','');
        ta.style.cssText='position:fixed;top:0;left:0;width:1px;height:1px;padding:0;border:0;opacity:0';
        document.body.appendChild(ta);ta.focus({preventScroll:true});ta.select();ta.setSelectionRange(0,raw.length);
        let ok=false;try{ok=document.execCommand('copy');}catch(e){}
        document.body.removeChild(ta);b.focus({preventScroll:true});return ok;};
      if(viaInput()){done();return;}
      try{navigator.clipboard.writeText(raw).then(done,fb);}catch(e){fb();}});
    cb.appendChild(b);}
});
document.querySelectorAll('main p code, main li code, main td code').forEach(c=>{if(!c.children.length)c.innerHTML=wrapFns(c.innerHTML);});

/* ── 풍선 도움말 ── */
const tip=document.createElement('div');tip.className='tip';tip.id='fn-tip';tip.setAttribute('role','tooltip');tip.hidden=true;document.body.appendChild(tip);
const REQ=['선택','필수','사실상 필수'];let tipEl=null;
function showTip(el){const d=FN[el.dataset.fn];if(!d)return;tipEl=el;
  tip.innerHTML=`<div class="tip-sig">${esc(d.sig)}<span class="tip-pkg">${d.pkg}</span></div><p>${d.why}</p>`+
    (d.args.length?`<table><thead><tr><th>인수</th><th>필수 여부</th><th>설명</th></tr></thead><tbody>`+d.args.map(a=>`<tr><td><code>${a[0]}</code></td><td><span class="req r${a[1]}">${REQ[a[1]]}</span></td><td>${a[2]}</td></tr>`).join('')+`</tbody></table>`:`<p class="tip-none">인수 없이 쓴다.</p>`)+
    `<p><b>반환값</b> ${d.ret}</p>`;
  tip.hidden=false;el.setAttribute('aria-describedby','fn-tip');
  const r=el.getBoundingClientRect(),tw=tip.offsetWidth,th=tip.offsetHeight;
  let y=r.bottom+8;if(y+th>innerHeight-8)y=r.top-th-8>=8?r.top-th-8:innerHeight-th-8;
  tip.style.left=Math.max(8,Math.min(r.left,innerWidth-tw-8))+'px';tip.style.top=Math.max(8,y)+'px';}
function hideTip(){if(tipEl)tipEl.removeAttribute('aria-describedby');tipEl=null;tip.hidden=true;}
const fnOf=e=>e.target.closest&&e.target.closest('.fn');
document.addEventListener('mouseover',e=>{const el=fnOf(e);if(el&&el!==tipEl)showTip(el);});
document.addEventListener('mouseout',e=>{const el=fnOf(e);if(el&&!el.contains(e.relatedTarget))hideTip();});
document.addEventListener('focusin',e=>{const el=fnOf(e);if(el)showTip(el);});
document.addEventListener('focusout',e=>{if(fnOf(e))hideTip();});
document.addEventListener('click',e=>{const el=fnOf(e);if(el)showTip(el);else hideTip();});
document.addEventListener('keydown',e=>{if(e.key==='Escape')hideTip();});
window.addEventListener('scroll',hideTip,{passive:true,capture:true});

/* ── 목차 scroll-spy ── */
(()=>{const links=[...document.querySelectorAll('#rail-nav a')];
  const obs=new IntersectionObserver(es=>es.forEach(en=>{if(en.isIntersecting)links.forEach(l=>l.classList.toggle('on',l.getAttribute('href')==='#'+en.target.id));}),{rootMargin:'-25% 0px -65% 0px'});
  links.forEach((l,i)=>{const t=document.querySelector(l.getAttribute('href'));if(t)obs.observe(t);if(i===0)l.classList.add('on');});})();

/* ── 주소의 #이름이 접힌 상자(details)나 그 안을 가리키면 펼친다 ── */
(()=>{const openByHash=()=>{if(location.hash.length<2)return;let el=null;
    try{el=document.getElementById(decodeURIComponent(location.hash.slice(1)));}catch(e){}
    let opened=false;for(let d=el&&el.closest('details');d;d=d.parentElement&&d.parentElement.closest('details')){if(!d.open){d.open=true;opened=true;}}
    if(opened)el.scrollIntoView();};
  openByHash();window.addEventListener('hashchange',openByHash);})();
