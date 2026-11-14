"""Medium 글의 생존자 편향 그림에서 비행기만 남긴다.

원본: Mat Wang(@matwang2000), "The Success Stories We See and the Failures We Don't", Medium.
https://medium.com/@matwang2000/the-success-stories-we-see-and-the-failures-we-dont-a47930477498

제목·설명 글자, 화살표, 조종석·엔진을 가리키던 파란 타원을 지우고 비행기 둘레만 잘라
docs/assets/images/survivorship-bias-plane.jpg 로 저장한다. 화살촉이 비행기에 걸쳤던 곳은
좌우 대칭인 반대쪽을 거울로 복사해 메운다. 좌표는 원본(1448×1086) 기준이다.

실행 (저장소 루트에서, OpenCV는 이 스크립트에만 필요해 프로젝트 의존성에 넣지 않았다):
    uv run --no-project --with numpy --with opencv-python-headless \
        python src/python/clean_survivorship_plane.py
"""
import numpy as np, cv2

SRC = "datasets/images/survivorship-bias-medium.png"
OUT = "docs/assets/images/survivorship-bias-plane.jpg"
OUT_WIDTH = 1100

im = cv2.imread(SRC)
if im is None:
    raise SystemExit(f"원본을 읽지 못했다: {SRC}")
H, W = im.shape[:2]
BG = (242, 245, 245)  # BGR

# 1) 화살표: 선과 화살촉을 마스크로 만들어 주변 픽셀로 메운다
mask = np.zeros((H, W), np.uint8)
segs = [((900, 119), (975, 119)), ((900, 119), (762, 170)), ((975, 119), (884, 258)),
        ((183, 567), (229, 461)), ((1025, 637), (763, 705))]
for a, b in segs:
    cv2.line(mask, a, b, 255, 9)
for (tip, back) in [((762, 170), (900, 119)), ((884, 258), (975, 119)),
                    ((229, 461), (183, 567)), ((763, 705), (1025, 637))]:
    t, k = np.array(tip, float), np.array(back, float)
    d = (k - t) / np.linalg.norm(k - t)
    cv2.line(mask, tuple(t.astype(int)), tuple((t + d * 30).astype(int)), 255, 26)

# 2) 파란 강조 타원의 선
b, g, r = [im[:, :, i].astype(int) for i in range(3)]
ell_boxes = [(680, 140, 785, 265), (815, 225, 910, 345)]
for x0, y0, x1, y1 in ell_boxes:
    sub = np.zeros((H, W), bool); sub[y0:y1, x0:x1] = True
    line = sub & (b - r > 28)
    mask |= cv2.dilate(line.astype(np.uint8) * 255, np.ones((5, 5), np.uint8))
im = cv2.inpaint(im, mask, 5, cv2.INPAINT_TELEA)

# 3) 타원 안쪽의 푸른 기운을 회색으로 (금속 동체 색에 맞춤)
for x0, y0, x1, y1 in ell_boxes:
    roi = im[y0:y1, x0:x1].astype(float)
    bb, gg, rr = roi[..., 0], roi[..., 1], roi[..., 2]
    blu = (bb - rr) > 6
    lum = 0.114 * bb + 0.587 * gg + 0.299 * rr
    for c in range(3):
        roi[..., c] = np.where(blu, lum, roi[..., c])
    im[y0:y1, x0:x1] = roi.clip(0, 255).astype(np.uint8)

# 3-1) 화살촉이 비행기에 걸쳤던 곳은 좌우 대칭(축 x=725.5)인 반대쪽을 거울로 복사한다
C2 = 1451  # 2 * 대칭축
for x0, y0, x1, y1 in [(805, 140, 922, 352),   # 오른쪽 안쪽 엔진
                       (756, 136, 806, 194),   # 조종석 오른쪽 (창틀은 건드리지 않음)
                       (752, 682, 800, 728),   # 동체 뒤쪽 오른쪽
                       (200, 440, 252, 490)]:  # 왼쪽 날개 가장자리
    mir = im[y0:y1, C2 - x1 + 1:C2 - x0 + 1][:, ::-1].astype(float)
    cur = im[y0:y1, x0:x1].astype(float)
    # 가장자리 6px에서 원래 그림과 부드럽게 섞어 이음매를 줄인다
    h, w = y1 - y0, x1 - x0
    a = np.ones((h, w), np.float32)
    a = cv2.copyMakeBorder(a[6:-6, 6:-6], 6, 6, 6, 6, cv2.BORDER_CONSTANT, value=0)
    a = cv2.GaussianBlur(a, (13, 13), 0)[..., None]
    im[y0:y1, x0:x1] = (a * mir + (1 - a) * cur).clip(0, 255).astype(np.uint8)

# 4) 글자 영역을 배경색으로 덮는다
for x0, y0, x1, y1 in [(30, 15, 675, 228), (980, 95, 1360, 216),
                       (40, 565, 340, 712), (1025, 615, 1290, 765), (0, 918, 690, H), (752, 918, W, H), (0, 935, W, H)]:
    im[y0:y1, x0:x1] = BG

# 4-1) 꼬리 끝 아래에 남은 회색 상자: 밝은 픽셀만 배경색으로
roi = im[905:935, 680:765]
light = roi.min(axis=2) > 205
roi[light] = BG

# 5) 비행기 둘레만 잘라 낸다
im = im[50:935, 12:1438]
h, w = im.shape[:2]
im = cv2.resize(im, (OUT_WIDTH, round(h * OUT_WIDTH / w)), interpolation=cv2.INTER_AREA)
cv2.imwrite(OUT, im, [cv2.IMWRITE_JPEG_QUALITY, 90])
print(OUT, im.shape[1], "x", im.shape[0])
