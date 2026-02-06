import os
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class RandomLoadRequest(BaseModel):
    """Запрос на запись случайной нагрузки в Google-таблицу."""

    employee: str = Field(..., description="Идентификатор сотрудника (например, 'rustam' или 'zheka').")
    value: int = Field(..., ge=1, le=5, description="Число в диапазоне 1–5, сгенерированное рандомайзером.")


def _load_employee_config() -> Dict[str, Dict[str, str]]:
    """Формирует маппинг сотрудник → (spreadsheet_id, range) из переменных окружения.

    Используются следующие переменные окружения:
    - BALANCER_RUSTAM_SPREADSHEET_ID
    - BALANCER_RUSTAM_RANGE
    - BALANCER_ZHEKA_SPREADSHEET_ID
    - BALANCER_ZHEKA_RANGE
    """

    return {
        "rustam": {
            "spreadsheet_id": os.getenv("BALANCER_RUSTAM_SPREADSHEET_ID", "").strip(),
            "range": os.getenv("BALANCER_RUSTAM_RANGE", "").strip(),
        },
        "zheka": {
            "spreadsheet_id": os.getenv("BALANCER_ZHEKA_SPREADSHEET_ID", "").strip(),
            "range": os.getenv("BALANCER_ZHEKA_RANGE", "").strip(),
        },
    }


EMPLOYEE_CONFIG = _load_employee_config()


def get_sheets_service():
    """Создает клиент Google Sheets по сервисному аккаунту.

    Требуется переменная окружения:
    - GOOGLE_SERVICE_ACCOUNT_FILE — путь к JSON-файлу сервисного аккаунта.
    """

    service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    if not service_account_file:
        raise RuntimeError(
            "Не задан путь к файлу сервисного аккаунта. "
            "Установите переменную окружения GOOGLE_SERVICE_ACCOUNT_FILE."
        )

    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES
    )
    # cache_discovery=False исключает использование локального cache-файла
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)


app = FastAPI(title="ROC Balancer Backend", version="1.0.0")

# Базовая настройка CORS. При необходимости сузьте список доменов.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.post("/api/balance/random-load")
async def write_random_load(payload: RandomLoadRequest):
    """Записывает число 1–5 в Google-таблицу для указанного сотрудника.

    Само число уже сгенерировано на фронтенде и передано в поле `value`.
    """

    employee_id = payload.employee.lower().strip()
    config = EMPLOYEE_CONFIG.get(employee_id)

    if config is None:
        raise HTTPException(
            status_code=400,
            detail=f"Неизвестный сотрудник: {payload.employee!r}. "
            "Ожидаются идентификаторы 'rustam' или 'zheka'.",
        )

    spreadsheet_id = config.get("spreadsheet_id")
    cell_range = config.get("range")

    if not spreadsheet_id or not cell_range:
        raise HTTPException(
            status_code=500,
            detail=(
                "Не настроены параметры Google-таблицы для сотрудника "
                f"{employee_id!r}. Проверьте переменные окружения "
                "BALANCER_RUSTAM_SPREADSHEET_ID / BALANCER_RUSTAM_RANGE или "
                "BALANCER_ZHEKA_SPREADSHEET_ID / BALANCER_ZHEKA_RANGE."
            ),
        )

    try:
        service = get_sheets_service()
        body = {"values": [[payload.value]]}

        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=cell_range,
            valueInputOption="RAW",
            body=body,
        ).execute()

    except HTTPException:
        # Пробрасываем уже подготовленные ошибки FastAPI
        raise
    except Exception:
        # Не логируем подробности, чтобы не утекли чувствительные данные.
        raise HTTPException(
            status_code=500,
            detail="Не удалось записать значение в Google-таблицу. "
            "Проверьте права сервисного аккаунта и корректность ID/диапазона.",
        )

    return {"status": "ok"}


@app.get("/health")
async def healthcheck():
    """Простой healthcheck для мониторинга."""

    return {"status": "ok"}

