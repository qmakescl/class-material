"""MNIST 실습 자료(docs/ai/mnist-classifier-practice.html)에 실을 실제 학습 결과를 만든다.

입력  : datasets/mnist/{train,t10k}-{images-idx3,labels-idx1}-ubyte.gz
        (LeCun, Cortes & Burges의 MNIST. 없으면 prepare_mnist_bridge.py 를 먼저 실행해 받는다.)
출력  : docs/assets/data/mnist-practice.js  (window.MNIST_PRACTICE)

계산 내용 — 자료 페이지의 실습과 같은 순서, 같은 설정이다.
- 훈련 60,000장을 시드 고정 무작위로 훈련 54,000 / 검증 6,000 으로 나눈다. 시험 10,000장은 마지막에 한 번만 쓴다.
- 모형 ① 은닉층 신경망(784 → 64 → 10)과 모형 ② 작은 합성곱 신경망(Conv 16 → Conv 32 → Linear 10)을
  같은 설정(미니배치 100, SGD 학습률 0.1)으로 학습하고 에폭마다 훈련 손실·검증 손실·검증 정확도를 기록한다.
- 검증 손실이 가장 낮았던 에폭의 가중치를 남겨 시험 자료를 채점한다(두 모형의 혼동행렬, 오답 사례).
- 시험 사진을 오른쪽으로 0~4칸 밀었을 때의 정확도(두 모형).
- 페이지의 필터 위젯이 쓰는 값: 모형 ②의 첫 합성곱 층 필터 16개와 숫자별 시험 사진 한 장씩.
- 255로 나누는 전처리를 뺐을 때의 결과(모형 ①, 1에폭).
- 모형 ①을 같은 출발점에서 100에폭까지 학습한 기록. 앞 30에폭은 위의 기록과 같고, 그 뒤에 검증 손실이 어떻게 되는지 본다.

PyTorch 로 계산한다. torch 는 저장소 의존성에 넣지 않고 실행할 때만 불러온다.
실행: uv run --with torch python src/python/prepare_mnist_practice.py
같은 컴퓨터·같은 버전에서는 같은 결과가 나온다. 버전이나 CPU 가 다르면 끝자리가 조금 달라질 수 있다.
"""

from __future__ import annotations

import base64
import gzip
import json
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "datasets" / "mnist"
OUT = ROOT / "docs" / "assets" / "data" / "mnist-practice.js"

SEED = 42
N_VAL = 6000
BATCH = 100
LR = 0.1
EPOCHS = {"mlp": 30, "cnn": 15}
LONG_EPOCHS = 100  # 모형 ①을 오래 학습하면 어떻게 되는지 볼 때
SHIFTS = [0, 1, 2, 3, 4]
N_ERRORS = 12


def load_idx(name: str) -> np.ndarray:
    """IDX 형식(gzip)을 읽는다."""
    raw = gzip.decompress((SRC / name).read_bytes())
    dims = raw[3]
    shape = [int.from_bytes(raw[4 + 4 * i: 8 + 4 * i], "big") for i in range(dims)]
    return np.frombuffer(raw, dtype=np.uint8, offset=4 + 4 * dims).reshape(shape)


def make_mlp() -> nn.Sequential:
    return nn.Sequential(nn.Flatten(), nn.Linear(784, 64), nn.ReLU(), nn.Linear(64, 10))


def make_cnn() -> nn.Sequential:
    return nn.Sequential(
        nn.Conv2d(1, 16, 3), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(16, 32, 3), nn.ReLU(), nn.MaxPool2d(2),
        nn.Flatten(), nn.Linear(32 * 5 * 5, 10),
    )


@torch.no_grad()
def evaluate(model: nn.Module, x: torch.Tensor, y: torch.Tensor) -> tuple[float, float, torch.Tensor]:
    """(평균 손실, 정확도, 예측)을 돌려준다. 메모리를 아끼려고 1,000장씩 나눠 계산한다."""
    model.eval()
    loss, preds = 0.0, []
    for s in range(0, len(x), 1000):
        z = model(x[s: s + 1000])
        loss += nn.functional.cross_entropy(z, y[s: s + 1000], reduction="sum").item()
        preds.append(z.argmax(1))
    pred = torch.cat(preds)
    return loss / len(x), (pred == y).float().mean().item(), pred


def train(model: nn.Module, epochs: int, xtr, ytr, xva, yva, gen: torch.Generator) -> tuple[list[dict], int]:
    """미니배치 SGD로 학습한다. 에폭마다 기록하고, 검증 손실이 가장 낮았던 에폭의 가중치를 모형에 남긴다."""
    opt = torch.optim.SGD(model.parameters(), lr=LR)
    loss_fn = nn.CrossEntropyLoss()
    log, best, best_state = [], 0, None

    def record() -> None:
        tl, _, _ = evaluate(model, xtr, ytr)
        vl, va, _ = evaluate(model, xva, yva)
        log.append({"train": round(tl, 4), "val": round(vl, 4), "acc": round(va, 4)})

    record()  # 0번 = 학습 전
    for epoch in range(1, epochs + 1):
        model.train()
        order = torch.randperm(len(xtr), generator=gen)
        for s in range(0, len(xtr), BATCH):
            idx = order[s: s + BATCH]
            loss = loss_fn(model(xtr[idx]), ytr[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
        record()
        if best_state is None or log[epoch]["val"] < log[best]["val"]:
            best, best_state = epoch, {k: v.clone() for k, v in model.state_dict().items()}
    model.load_state_dict(best_state)
    return log, best


def shift_right(x: torch.Tensor, k: int) -> torch.Tensor:
    """사진을 오른쪽으로 k칸 민다. 왼쪽에 생긴 빈 칸은 0(흰 종이)으로 채운다."""
    if k == 0:
        return x
    out = torch.zeros_like(x)
    out[..., k:] = x[..., :-k]
    return out


def b64(img: np.ndarray) -> str:
    return base64.b64encode(img.astype(np.uint8).tobytes()).decode("ascii")


def main() -> None:
    torch.manual_seed(SEED)
    xtr_u8, ytr_all = load_idx("train-images-idx3-ubyte.gz"), load_idx("train-labels-idx1-ubyte.gz")
    xte_u8, yte_np = load_idx("t10k-images-idx3-ubyte.gz"), load_idx("t10k-labels-idx1-ubyte.gz")

    # (장 수, 채널 1, 세로 28, 가로 28), 0~1
    x_all = torch.tensor(xtr_u8, dtype=torch.float32).unsqueeze(1) / 255
    y_all = torch.tensor(ytr_all, dtype=torch.long)
    xte = torch.tensor(xte_u8, dtype=torch.float32).unsqueeze(1) / 255
    yte = torch.tensor(yte_np, dtype=torch.long)

    gen = torch.Generator().manual_seed(SEED)
    order = torch.randperm(len(x_all), generator=gen)
    va_idx, tr_idx = order[:N_VAL], order[N_VAL:]
    xtr, ytr, xva, yva = x_all[tr_idx], y_all[tr_idx], x_all[va_idx], y_all[va_idx]

    results = {}
    for name, make in (("mlp", make_mlp), ("cnn", make_cnn)):
        model = make()
        t0 = time.time()
        log, best = train(model, EPOCHS[name], xtr, ytr, xva, yva, gen)
        secs = time.time() - t0
        _, acc, pred = evaluate(model, xte, yte)
        shift = [round(evaluate(model, shift_right(xte, k), yte)[1], 4) for k in SHIFTS]
        results[name] = {"model": model, "pred": pred, "data": {
            "params": sum(p.numel() for p in model.parameters()),
            "epochs": EPOCHS[name], "log": log, "best": best,
            "acc": round(acc, 4), "errors": int((pred != yte).sum()), "shift": shift,
            "seconds": round(secs),
        }}
        print(f"{name}: params {results[name]['data']['params']:,}  best epoch {best}  "
              f"val {log[best]['val']:.4f}/{log[best]['acc']:.4f}  test {acc:.4f}  shift {shift}  {secs:.0f}s")
        print("   val loss:", " ".join(f"{r['val']:.3f}" for r in log))
        print("   train loss:", " ".join(f"{r['train']:.3f}" for r in log))

    pm, pc = results["mlp"]["pred"], results["cnn"]["pred"]
    for r in results.values():  # 혼동행렬: 행 = 정답, 열 = 모형의 답
        conf = np.zeros((10, 10), dtype=int)
        np.add.at(conf, (yte_np, r["pred"].numpy()), 1)
        r["data"]["confusion"] = conf.tolist()
    wrong = torch.nonzero(pc != yte).flatten()[:N_ERRORS].tolist()
    picks = [int(np.flatnonzero(yte_np == d)[0]) for d in range(10)]
    conv1 = results["cnn"]["model"][0]

    # 전처리를 빼면 어떻게 되는가: 255로 나누지 않은 채(0~255) 모형 ①을 같은 설정으로 1에폭만 학습한다.
    raw_model = make_mlp()
    raw_log, _ = train(raw_model, 1, xtr * 255, ytr, xva * 255, yva, torch.Generator().manual_seed(SEED))
    print("raw 0~255, 1 epoch:", raw_log)

    # 오래 학습하면: 시드를 되돌려 모형 ①과 같은 초깃값·같은 섞는 순서에서 출발해 100에폭까지 간다.
    torch.manual_seed(SEED)
    long_model = make_mlp()
    gen_long = torch.Generator().manual_seed(SEED)
    torch.randperm(len(x_all), generator=gen_long)  # 자료를 나눌 때 쓴 난수만큼 넘긴다
    long_log, long_best = train(long_model, LONG_EPOCHS, xtr, ytr, xva, yva, gen_long)
    assert long_log[: EPOCHS["mlp"] + 1] == results["mlp"]["data"]["log"], "앞 30에폭이 모형 ①의 기록과 달라졌다"
    print(f"mlp {LONG_EPOCHS} epochs: best {long_best} val {long_log[long_best]['val']:.4f}  last val {long_log[-1]['val']:.4f} train {long_log[-1]['train']:.4f}")

    data = {
        "source": "MNIST (LeCun, Cortes & Burges). 훈련 60,000장 · 시험 10,000장",
        "setup": {"seed": SEED, "nTrain": len(tr_idx), "nVal": len(va_idx), "nTest": len(yte),
                  "batch": BATCH, "lr": LR, "optimizer": "미니배치 SGD", "scale": "픽셀값 / 255",
                  "torch": torch.__version__.split("+")[0]},
        "counts": {"train": np.bincount(ytr.numpy(), minlength=10).tolist(),
                   "val": np.bincount(yva.numpy(), minlength=10).tolist(),
                   "test": np.bincount(yte_np, minlength=10).tolist()},
        "shifts": SHIFTS,
        "mlp": results["mlp"]["data"],
        "cnn": results["cnn"]["data"],
        "mlpLong": {"epochs": LONG_EPOCHS, "log": long_log, "best": long_best},
        "raw255": {"val": raw_log[1]["val"], "acc": raw_log[1]["acc"]},  # 255로 나누지 않고 1에폭
        "compare": {"both": int(((pm != yte) & (pc != yte)).sum()),
                    "mlpOnly": int(((pm != yte) & (pc == yte)).sum()),
                    "cnnOnly": int(((pm == yte) & (pc != yte)).sum())},
        "filters": {"w": [[round(v, 3) for v in f.flatten().tolist()] for f in conv1.weight.detach()],
                    "b": [round(v, 3) for v in conv1.bias.detach().tolist()]},
        "picks": [{"i": i, "y": int(yte_np[i]), "px": b64(xte_u8[i])} for i in picks],
        "wrong": [{"i": i, "y": int(yte_np[i]), "cnn": int(pc[i]), "mlp": int(pm[i]), "px": b64(xte_u8[i])}
                  for i in wrong],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    OUT.write_text(
        "/* 생성 파일 — 직접 수정하지 않는다.\n"
        "   src/python/prepare_mnist_practice.py 가 datasets/mnist/ 의 MNIST 원본으로 학습해 만든다. */\n"
        f"window.MNIST_PRACTICE = {body};\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")
    print("counts train", data["counts"]["train"], "compare", data["compare"])


if __name__ == "__main__":
    main()
