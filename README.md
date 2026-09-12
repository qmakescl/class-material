# Class Material

수업에서 사용할 정적 HTML 자료를 관리하고 GitHub Pages로 배포하는
프로젝트입니다. 실제 사이트 파일은 `docs/`에 있습니다.

## 로컬 미리보기

Python 3.12와 [`uv`](https://docs.astral.sh/uv/)가 필요합니다.

```sh
uv sync
uv run python main.py
```

브라우저에서 <http://127.0.0.1:8000>을 열어 확인합니다. 다른 포트를
사용하려면 `uv run python main.py --port 8080`처럼 실행합니다.

## 자료 편집

- 페이지 내용: `docs/index.html`
- 공통 스타일: `docs/assets/styles.css`
- 이미지와 첨부 자료: `docs/assets/` 아래에 추가

GitHub Pages의 프로젝트 사이트 경로에서도 동작하도록 내부 링크에는 `/`로
시작하는 절대 경로 대신 상대 경로를 사용합니다.

## GitHub Pages 배포

`main` 브랜치에 `docs/` 또는 Pages 워크플로 변경 사항이 푸시되면
`.github/workflows/deploy-pages.yml`이 사이트를 자동 배포합니다. Actions
탭에서 수동으로 실행할 수도 있습니다.

최초 한 번은 GitHub 저장소의 **Settings → Pages → Build and deployment →
Source**를 **GitHub Actions**로 설정해야 합니다. 배포가 완료되면 사이트는
다음 주소에서 제공됩니다.

<https://qmakescl.github.io/class-material/>
