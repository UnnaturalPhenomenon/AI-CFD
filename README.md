# PyAnsys AI Project Platform

PyAnsys 기반 CFD 데이터 생성 및 neural-operator 프로젝트를 시작하기 위한 Windows용 저장소 골격입니다. 이 버전의 목적은 해석이나 ML 구현이 아니라 **Codex와 Claude Code가 같은 Git 저장소를 최소 컨텍스트로 이어받는 실행 기반**을 만드는 것입니다.

## 포함된 구성

| 파일 | 역할 |
|---|---|
| `AGENTS.md` | Codex의 최소 작업 규칙 |
| `CLAUDE.md` | Claude Code의 읽기 전용 리뷰 규칙 |
| `.ai/TASK.md` | 현재 작업의 단일 진실 공급원 |
| `.ai/REVIEW.md` | Claude 리뷰 결과; 스크립트가 갱신 |
| `ai.ps1` | 사용자가 실행하는 단일 진입점 |
| `scripts/ai-cycle.ps1` | Codex → Claude → Codex 제어 |
| `scripts/Test-AiEnvironment.ps1` | 설치·Git·API 과금 위험 점검 |
| `docs/ARCHITECTURE.md` | PyAnsys–dataset–operator 장기 구조 |

## 1. Windows에 배치

압축을 프로젝트로 사용할 폴더에 풉니다. PowerShell에서 해당 폴더로 이동한 뒤 Git 저장소를 만듭니다.

```powershell
cd C:\work\pyansys-ai-platform
git init
git add .
git commit -m "chore: initialize AI work platform"
```

Codex CLI와 Claude Code는 각자 **구독 계정 로그인 방식**으로 먼저 로그인해 둡니다. 이 플랫폼은 API 키를 설정하거나 저장하지 않습니다.

## 2. 환경 확인

```powershell
.\ai.ps1 check
```

`OPENAI_API_KEY` 또는 `ANTHROPIC_API_KEY`가 현재 프로세스에 있으면 별도 API 과금을 피하기 위해 실행을 차단합니다. API 키 사용을 의도한 경우에만 다음처럼 우회할 수 있습니다.

```powershell
.\ai.ps1 check -AllowApiKeys
```

PowerShell 실행 정책 때문에 차단되면 현재 사용자 범위에서 로컬 스크립트를 허용합니다.

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 3. 첫 작업 작성

`.ai/TASK.template.md`를 참고하여 `.ai/TASK.md`를 작성합니다. Goal, Scope, Inputs, Requirements, Verify, Done을 모두 채운 뒤 첫 줄만 다음처럼 바꿉니다.

```text
STATUS: READY
```

`VERIFY`에는 반드시 사람이 같은 환경에서 재실행할 수 있는 명령을 넣습니다.

## 4. 실행

전체 1회 사이클:

```powershell
.\ai.ps1 full
```

실제 도구를 실행하지 않고 명령 흐름만 점검:

```powershell
.\ai.ps1 full -DryRun
```

단계별 실행:

```powershell
.\ai.ps1 implement
.\ai.ps1 review
.\ai.ps1 fix
```

`full`은 다음 순서로 동작합니다.

1. Codex가 `.ai/TASK.md`만 기준으로 구현하고 검증합니다.
2. Claude Code가 Sonnet/low effort와 plan 권한으로 Git diff를 리뷰합니다.
3. 스크립트가 Claude의 텍스트를 `.ai/REVIEW.md`에 저장합니다.
4. 결과가 정확히 `PASS`이면 종료합니다.
5. 문제가 있으면 Codex가 유효한 지적만 수정하고 검증한 뒤 종료합니다.

자동 재리뷰나 무한 수정 루프는 의도적으로 넣지 않았습니다. 중요한 변경은 `git diff`와 `.ai/REVIEW.md`를 사람이 확인한 뒤 필요할 때 `review`를 한 번 더 실행하십시오.

Codex 실행은 현재 공식 CLI가 권장하는 `--sandbox workspace-write`를 사용하고 세션을 저장하지 않는 `--ephemeral`로 시작합니다. Claude 리뷰도 `--no-session-persistence`와 최대 4턴 제한을 사용합니다. 따라서 이전 대화가 누적되지 않고 각 단계가 저장소의 TASK와 diff만 다시 읽습니다.

## 5. 권장 작업 단위

- 작업 하나당 `.ai/TASK.md` 하나
- 구현 파일 1–4개와 대응 테스트 정도로 범위 제한
- 작업 완료 후 커밋하고 다음 작업은 새 Codex/Claude 세션에서 시작
- 큰 Fluent 결과와 학습 데이터는 Git에 넣지 않음
- 비밀값, 라이선스 정보, API 키는 TASK나 로그에 기록하지 않음

## 다음 마일스톤

플랫폼 확인 후 첫 실제 작업은 `V0.1 PyFluent 연결 스모크 테스트`가 적절합니다. 목표는 Fluent를 한 번 시작하고 버전·세션 정보를 확인한 뒤 항상 정상 종료하는 작은 테스트이며, 아직 geometry·solver·ML 코드는 포함하지 않습니다.
