# Структура проекта (Project Structure)

Проект **Tegugotchi** — виртуальный питомец с REST API, хранением данных в MongoDB и автотестами.

## Дерево папок и файлов

```
pet_project/
├── .github/
│   └── workflows/
│       └── ci.yml          
├── tests/
│   ├── test_pet.py         
│   └── test_api.py         
├── tegugotchi/
│   ├── database
│   │   └── __init__.py
│   ├── __init__.py
│   ├── pet
│   │   └── __init__.py
│   └── server
│       └── __init__.py
├── main.py                 
├── .gitignore              
├── requirements.txt        
└── README.md               
```

## Ветки разработки

```
main
├── dev
│    ├── backend
│    │   └── database
│    ├── build
│    ├── frontend
│    └── tests
```

## Что за что отвечает

| Папка / файл | Назначение |
|---|---|
| `app/` | Основной код приложения: логика питомца, работа с базой данных, сервер. |
| `app/pet/` | **Бизнес-логика** — класс `Pet` (кормление, игры, уровень голода и счастья). |
| `app/database/` | Слой работы с **MongoDB** через PyMongo. |
| `app/server/` | **REST API** — HTTP-сервер, принимающий запросы и обращающийся к логике и базе. |
| `tests/` | Автотесты: юнит-тесты логики и интеграционные тесты API. |
| `.github/workflows/` | **CI/CD** — автоматические проверки при каждом пуше на GitHub. |
| `main.py` | Точка входа для ручного запуска и отладки. |
| `.gitignore` | Файлы и папки, которые не попадают в репозиторий. |
| `README.md` | Главная страница проекта: описание эндпоинтов и инструкция по запуску. |

## Где что искать

- **Бизнес-логика** → `tegugotchi/pet/`
- **База данных** → `tegugotchi/database/`
- **API** → `tegugotchi/server/`
- **Тесты** → `tests/`
- **Документация** → `docs/`
