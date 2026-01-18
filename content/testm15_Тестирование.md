---
tags:
  - mod15
  - testmod
---
# Тестирование

### 1. Какой инструмент обеспечивает GitOps-подход в Kubernetes?

- [ ] A) Helm
- [ ] B) Kustomize
- [ ] C) ArgoCD
- [ ] D) Terraform

<details>
<summary>▶ Показать ответ</summary>

✅ **C) ArgoCD**

ArgoCD — это специализированный инструмент для GitOps, который автоматически синхронизирует состояние кластера с желаемым состоянием из Git-репозитория. Helm и Kustomize — это инструменты деплоя, но не обеспечивают автоматическую синхронизацию. Terraform управляет инфраструктурой, но не Kubernetes-приложениями через Git.
</details>
---
### 2. Что делает External Secrets Operator (ESO)?

- [ ] A) Шифрует все Kubernetes Secrets
- [ ] B) Автоматически создает Secret в Kubernetes на основе внешнего хранилища (Vault, AWS Secrets Manager)
- [ ] C) Удаляет старые секреты
- [ ] D) Генерирует случайные пароли

<details>
<summary>▶ Показать ответ</summary>

✅ **B) Автоматически создает Secret в Kubernetes на основе внешнего хранилища (Vault, AWS Secrets Manager)**

ESO — это оператор, который следит за ресурсами `ExternalSecret` и создаёт/обновляет стандартные Kubernetes `Secret` на основе данных из Vault или облачных провайдеров. Это позволяет безопасно доставлять секреты без их хранения в Git.

</details>
---
### 3. Какой компонент Service Mesh отвечает за шифрование трафика между сервисами?

- [ ] A) Ingress Controller
- [ ] B) mTLS (mutual TLS)
- [ ] C) Load Balancer
- [ ] D) Prometheus

<details>
<summary>▶ Показать ответ</summary>

✅ **B) mTLS (mutual TLS)**

mTLS — это механизм взаимной аутентификации и шифрования, реализованный в sidecar-прокси (Envoy в Istio, Linkerd-proxy). Он гарантирует, что трафик между сервисами защищён и подписан, без участия приложений.

</details>
---
### 4. Какой инструмент лучше всего подходит для анализа расходов в Kubernetes?

- [ ] A) Prometheus
- [ ] B) Grafana
- [ ] C) Kubecost
- [ ] D) Trivy

<details>
<summary>▶ Показать ответ</summary>

✅ **C) Kubecost**

Kubecost — специализированный инструмент для мониторинга затрат в Kubernetes. Он показывает стоимость каждого namespace, pod, контейнера, а также предлагает рекомендации по оптимизации. Prometheus и Grafana — для метрик, Trivy — для уязвимостей.

</details>
---
### 5. Что означает "Policy as Code" в контексте DevOps?

- [ ] A) Написание политики безопасности в Word-документе
- [ ] B) Автоматическая проверка IaC и конфигураций через декларативные правила (например, OPA/Gatekeeper)
- [ ] C) Хранение политик в Confluence
- [ ] D) Ручная проверка кода перед мержем

<details>
<summary>▶ Показать ответ</summary>

✅ **B) Автоматическая проверка IaC и конфигураций через декларативные правила (например, OPA/Gatekeeper)**

Policy as Code — это подход, при котором правила безопасности, соответствия и лучших практик описываются в виде кода (например, Rego для OPA), версионируются в Git и автоматически применяются в CI/CD или admission control. Это позволяет «сдвигать безопасность влево».

</details>
---
