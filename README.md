### Настройка
* Настроить config.py
 * Установить зависимости
  * Выполнить миграции

### API
* Увидеть вопросы опроса 

```
/api/poll/<int:poll_id>
```
Ответ:
```
[
    {
        "questions": {
            "id": 6,
            "type": "text",
            "question": "Точно?4"
        }
    },
    {
        "questions": {
            "id": 7,
            "type": "variants",
            "question": "Сколько?4",
            "multiple_answers": true,
            "options": [
                {
                    "id": 7,
                    "value": "13"
                },
                {
                    "id": 8,
                    "value": "23"
                },
                {
                    "id": 9,
                    "value": "33"
                }
            ]
        }
    }
    ,
    {
        "questions": {
            "id": 8,
            "type": "variants",
            "question": "Сколько?4",
            "multiple_answers": flse,
            "options": [
                {
                    "id": 10,
                    "value": "13"
                },
                {
                    "id": 11,
                    "value": "23"
                },
                {
                    "id": 12,
                    "value": "33"
                }
            ]
        }
    }
]
```
* Отправить ответы на сервер
```
/api/poll/<int:poll_id>/answer
{
	"user_login": "admin",
	"answers": [
		{
			"question_id": 6,
			"text_answer": "apiTest"
		},
		{
			"question_id": 7,
			"multiple_answers": [7, 8]
		},
		{
			"question_id": 8,
			"select_answer": 10
		}
	]
}
```
### Не сделал
* Vue.js приложение для Frontend-части
* Динамическое добавление вопросов и вариантов ответов
* Верстку