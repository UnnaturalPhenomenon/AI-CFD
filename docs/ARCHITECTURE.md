# Project Architecture

## 목표 경계

장기 목표는 다음 solution operator입니다.

\[
\mathcal{G}(\Omega, BC, IC, material, source) \rightarrow (u,v,w,p,T,\ldots)
\]

현재 P0 단계는 AI 도구 운용 기반만 다룹니다. PyFluent 실행, 데이터셋 생성, FNO 학습은 후속 TASK로 각각 분리합니다.

## 계층

| 계층 | 책임 | 초기 경로 |
|---|---|---|
| Simulation | Fluent 세션, BC, solve, field 추출 | `src/pyansys_operator/simulation/` |
| Sampling | Sobol/LHS/validation cases | `src/pyansys_operator/sampling/` |
| Dataset | schema, interpolation, normalization | `src/pyansys_operator/dataset/` |
| Models | U-Net, FNO, physics-regularized FNO | `src/pyansys_operator/models/` |
| Physics | continuity, energy, conservation losses | `src/pyansys_operator/physics/` |
| Validation | Fluent truth, field and conservation errors | `src/pyansys_operator/validation/` |

## 단계별 게이트

| 단계 | 산출물 | 다음 단계 진입 조건 |
|---|---|---|
| P0 | AI 작업·리뷰 플랫폼 | `ai.ps1 check` 및 dry run 성공 |
| V0.1 | PyFluent 세션 smoke test | 시작·정보 확인·정상 종료 반복 가능 |
| V0.2 | 단일 2D channel 자동 계산 | 한 명령으로 case load→solve→save |
| V0.3 | field 추출 schema | `x,y,u,v,p,T`와 metadata 저장 |
| V1 | fixed-geometry supervised baseline | held-out field error 보고 |
| V2 | BC field operator | 미학습 BC profile 검증 |
| V3 | geometry/SDF 입력 | 미학습 형상 검증 |
| V4+ | transient, 3D, compressible, EM/MHD | 이전 단계 보존성 검증 통과 |

## 예정 저장소 지도

```text
configs/
src/pyansys_operator/
  simulation/
  sampling/
  dataset/
  models/
  physics/
  validation/
tests/
data/                 # generated; ignored by Git
outputs/              # generated; ignored by Git
.ai/
```

빈 구현 디렉터리는 해당 TASK가 시작될 때 생성합니다. 이렇게 해야 초기 플랫폼이 아직 결정되지 않은 Fluent 버전, mesh 표현, 저장 포맷에 성급하게 결합되지 않습니다.

