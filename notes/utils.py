from datetime import datetime

from bson import ObjectId

"""Рекурсивная функция для сериализации данных, преобразующая объекты MongoDB и datetime в строковые представления."""


def serialize_data(data):

    if isinstance(data, list):
        return [serialize_data(item) for item in data]
    if isinstance(data, dict):
        return {key: serialize_data(value) for key, value in data.items()}
    if isinstance(data, ObjectId):
        return str(data)
    if isinstance(data, datetime):
        return data.isoformat()
    return data
