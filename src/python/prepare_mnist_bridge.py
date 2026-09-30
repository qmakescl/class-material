"""MNIST로 선형 분류기(소프트맥스 회귀)와 은닉층 1개짜리 신경망을 학습해 자료 페이지용 데이터를 만든다.

입력  : datasets/mnist/{train,t10k}-{images-idx3,labels-idx1}-ubyte.gz
        (LeCun, Cortes & Burges의 MNIST. 파일이 없으면 아래 MIRROR에서 내려받는다.)
출력  : docs/assets/data/mnist-bridge.js  (window.MNIST_BRIDGE)

계산 내용
- 소프트맥스 회귀(784 → 10). 회귀식 10개를 나란히 둔 것과 같아서 가중치를 28×28 그림으로 볼 수 있다.
- 은닉층 신경망(784 → 64 ReLU → 10). 같은 데이터·같은 최적화 설정에서 층 하나를 더한 효과를 비교한다.
- 두 모형의 에폭별 훈련 손실(교차엔트로피)과 시험 정확도. 시험 자료 10,000장은 학습에 쓰지 않는다.
- 페이지에 실을 시험 이미지: 숫자별 앞쪽 3장(고르기용)과 두 모형의 오답 사례.
  선형 모형의 확률은 페이지가 가중치로 직접 계산하고, 신경망 확률만 미리 계산해 싣는다.

난수 시드를 고정해 다시 실행해도 같은 결과가 나온다.
실행: uv run python src/python/prepare_mnist_bridge.py
"""

from __future__ import annotations

import base64
import gzip
import json
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "datasets" / "mnist"
OUT = ROOT / "docs" / "assets" / "data" / "mnist-bridge.js"
MIRROR = "https://ossci-datasets.s3.amazonaws.com/mnist/"
FILES = {
    "train_x": "train-images-idx3-ubyte.gz",
    "train_y": "train-labels-idx1-ubyte.gz",
    "test_x": "t10k-images-idx3-ubyte.gz",
    "test_y": "t10k-labels-idx1-ubyte.gz",
}

SEED = 2026
EPOCHS = 10
BATCH = 100
LR = 0.1
HIDDEN = 64
PICK_PER_DIGIT = 3
N_ERRORS = 12


def load_idx(name: str) -> np.ndarray:
    """IDX 형식(gzip)을 읽는다. 없으면 먼저 내려받는다."""
    path = SRC / name
    if not path.exists():
        SRC.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(MIRROR + name, path)
    raw = gzip.decompress(path.read_bytes())
    dims = raw[3]
    shape = [int.from_bytes(raw[4 + 4 * i: 8 + 4 * i], "big") for i in range(dims)]
    return np.frombuffer(raw, dtype=np.uint8, offset=4 + 4 * dims).reshape(shape)


def softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def cross_entropy(p: np.ndarray, y: np.ndarray) -> float:
    return float(-np.log(p[np.arange(len(y)), y] + 1e-12).mean())


class Linear:
    """소프트맥스 회귀: z = xW + b."""

    def __init__(self, rng: np.random.Generator):
        self.W = np.zeros((784, 10))
        self.b = np.zeros(10)

    def forward(self, x):
        return softmax(x @ self.W + self.b)

    def step(self, x, y1h):
        g = (self.forward(x) - y1h) / len(x)  # dL/dz
        self.W -= LR * (x.T @ g)
        self.b -= LR * g.sum(axis=0)


class MLP:
    """은닉층 하나: h = ReLU(xW1 + b1), z = hW2 + b2. He 초기화."""

    def __init__(self, rng: np.random.Generator):
        self.W1 = rng.normal(0, np.sqrt(2 / 784), (784, HIDDEN))
        self.b1 = np.zeros(HIDDEN)
        self.W2 = rng.normal(0, np.sqrt(2 / HIDDEN), (HIDDEN, 10))
        self.b2 = np.zeros(10)

    def forward(self, x):
        return softmax(np.maximum(0, x @ self.W1 + self.b1) @ self.W2 + self.b2)

    def step(self, x, y1h):
        a = x @ self.W1 + self.b1
        h = np.maximum(0, a)
        g2 = (softmax(h @ self.W2 + self.b2) - y1h) / len(x)
        g1 = (g2 @ self.W2.T) * (a > 0)
        self.W2 -= LR * (h.T @ g2)
        self.b2 -= LR * g2.sum(axis=0)
        self.W1 -= LR * (x.T @ g1)
        self.b1 -= LR * g1.sum(axis=0)


def train(model, xtr, ytr, xte, yte, rng):
    """같은 미니배치 SGD로 학습하고 에폭별 (훈련 손실, 시험 정확도)를 기록한다. 0번은 학습 전."""
    y1h = np.eye(10)[ytr]
    log = []

    def record():
        log.append({
            "loss": round(cross_entropy(model.forward(xtr), ytr), 4),
            "acc": round(float((model.forward(xte).argmax(1) == yte).mean()), 4),
        })

    record()
    for _ in range(EPOCHS):
        order = rng.permutation(len(xtr))
        for s in range(0, len(xtr), BATCH):
            idx = order[s: s + BATCH]
            model.step(xtr[idx], y1h[idx])
        record()
    return log


def b64(img: np.ndarray) -> str:
    return base64.b64encode(img.astype(np.uint8).tobytes()).decode("ascii")


def main() -> None:
    xtr_u8, ytr = load_idx(FILES["train_x"]).reshape(-1, 784), load_idx(FILES["train_y"]).astype(int)
    xte_u8, yte = load_idx(FILES["test_x"]).reshape(-1, 784), load_idx(FILES["test_y"]).astype(int)
    xtr, xte = xtr_u8 / 255.0, xte_u8 / 255.0

    rng = np.random.default_rng(SEED)
    lin = Linear(rng)
    lin_log = train(lin, xtr, ytr, xte, yte, np.random.default_rng(SEED + 1))
    mlp = MLP(rng)
    mlp_log = train(mlp, xtr, ytr, xte, yte, np.random.default_rng(SEED + 1))

    # 페이지는 반올림한 가중치로 확률을 다시 계산하므로, 오답 판정도 반올림한 가중치 기준으로 맞춘다.
    W = np.round(lin.W, 3)
    bl = np.round(lin.b, 3)
    p_lin = softmax(xte @ W + bl)
    p_mlp = mlp.forward(xte)
    pred_lin, pred_mlp = p_lin.argmax(1), p_mlp.argmax(1)

    picks = [int(i) for d in range(10) for i in np.flatnonzero(yte == d)[:PICK_PER_DIGIT]]
    lin_only = np.flatnonzero((pred_lin != yte) & (pred_mlp == yte))[:N_ERRORS]
    both = np.flatnonzero((pred_lin != yte) & (pred_mlp != yte))[:N_ERRORS]
    mlp_only = np.flatnonzero((pred_lin == yte) & (pred_mlp != yte))[:N_ERRORS]

    def sample(i: int) -> dict:
        return {"i": i, "y": int(yte[i]), "px": b64(xte_u8[i]),
                "mlp": [round(float(v), 4) for v in p_mlp[i]]}

    used = sorted(set(picks) | set(map(int, lin_only)) | set(map(int, both)) | set(map(int, mlp_only)))

    def confusion(pred):
        m = np.zeros((10, 10), dtype=int)
        np.add.at(m, (yte, pred), 1)
        return m.tolist()

    data = {
        "source": "MNIST (LeCun, Cortes & Burges). 훈련 60,000장 · 시험 10,000장",
        "setup": {"seed": SEED, "epochs": EPOCHS, "batch": BATCH, "lr": LR, "hidden": HIDDEN,
                  "optimizer": "미니배치 SGD", "scale": "픽셀값 / 255"},
        "nTrain": int(len(ytr)), "nTest": int(len(yte)),
        "linear": {
            "params": 784 * 10 + 10,
            "W": W.T.flatten().tolist(),  # 행 = 숫자 k, 열 = 픽셀 j
            "b": bl.tolist(),
            "log": lin_log,
            "acc": round(float((pred_lin == yte).mean()), 4),
            "perDigit": [round(float((pred_lin[yte == d] == d).mean()), 4) for d in range(10)],
            "confusion": confusion(pred_lin),
        },
        "mlp": {
            "params": 784 * HIDDEN + HIDDEN + HIDDEN * 10 + 10,
            "log": mlp_log,
            "acc": round(float((pred_mlp == yte).mean()), 4),
            "perDigit": [round(float((pred_mlp[yte == d] == d).mean()), 4) for d in range(10)],
        },
        "counts": {
            "linOnly": int(((pred_lin != yte) & (pred_mlp == yte)).sum()),
            "both": int(((pred_lin != yte) & (pred_mlp != yte)).sum()),
            "mlpOnly": int(((pred_lin == yte) & (pred_mlp != yte)).sum()),
        },
        "samples": {str(i): sample(i) for i in used},
        "picks": picks,
        "errors": {"linOnly": list(map(int, lin_only)), "both": list(map(int, both)),
                   "mlpOnly": list(map(int, mlp_only))},
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    OUT.write_text(
        "/* 생성 파일 — 직접 수정하지 않는다.\n"
        "   src/python/prepare_mnist_bridge.py 가 datasets/mnist/ 의 MNIST 원본으로 학습해 만든다. */\n"
        f"window.MNIST_BRIDGE = {body};\n",
        encoding="utf-8",
    )
    print(f"linear acc {data['linear']['acc']}  mlp acc {data['mlp']['acc']}  "
          f"counts {data['counts']}  samples {len(used)}  -> {OUT.relative_to(ROOT)} "
          f"({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
