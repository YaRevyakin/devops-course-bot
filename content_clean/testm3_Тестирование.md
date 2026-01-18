Тестирование

2. Какой файл описывает сборку Docker-образа?
- [ ] A) docker-compose.yml  
- [ ] B) deployment.yaml  
- [ ] C) Dockerfile  
- [ ] D) Chart.yaml

<details>
<summary>Показать ответ</summary>

C — Dockerfile содержит инструкции для сборки образа (FROM, COPY, RUN, CMD и т.д.).
</details>
4. Что делает команда *docker build -t myapp:v1 .*?
- [ ] A) Запускает контейнер из образа  
- [ ] B) Собирает Docker-образ с тегом myapp:v1  
- [ ] C) Отправляет образ в registry  
- [ ] D) Удаляет старые образы

<details>
<summary>Показать ответ</summary>

B — docker build создаёт образ на основе Dockerfile в текущей директории и присваивает ему тег myapp:v1.
</details>