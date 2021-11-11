import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    today = str(datetime.date.today())
    current_year = int(today[:4])
    return {
        'year': current_year,
    }
