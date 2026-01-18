Тестирование

2. Как микросервисы обычно общаются между собой в Kubernetes?
- [ ] A) Через общий том (volume)  
- [ ] B) Через прямой доступ к файловой системе другого Pod’а  
- [ ] C) По DNS-имени Service’а (например, http://user-service:8000)  
- [ ] D) Через shared memory

<details>
<summary>Показать ответ</summary>

C — каждый Service в Kubernetes автоматически получает DNS-имя. Микросервисы обращаются друг к другу по этому имени, а kube-proxy обеспечивает маршрутизацию трафика.
</details>
4. Какая команда покажет логи упавшего контейнера, который уже перезапущен?
- [ ] A) kubectl logs <pod>  
- [ ] B) kubectl logs <pod> --previous  
- [ ] C) kubectl describe pod <pod>  
- [ ] D) kubectl get events

<details>
<summary>Показать ответ</summary>

B — флаг --previous позволяет получить логи предыдущего экземпляра контейнера в Pod’е, что критично при отладке падений.
</details>