from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

choice_type_pilot = (
    ("C", 'КВС'),
    ("S", 'Второй пилот'),
    ("E", 'Бортинженер'),
)

choice_type_status_flight = (
    ("W", 'Ожидание'),
    ("D", 'Вылетел'),
    ("A", 'Прилетел'),
    ("C", 'Отменен'),
)

choice_type_sex = (
    ("M", 'Мужчина'),
    ("W", 'Женщина'),
)


class Country(models.Model):
    name = models.CharField(verbose_name="Название", max_length=100, unique=True)
    flag = models.ImageField(verbose_name="Флаг", upload_to='data/country/',
                             default='data/country/no.jpg')
    priority = models.BooleanField(verbose_name="Приоритет", default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"
        ordering = ["-priority", "name"]


class Airport(models.Model):
    name = models.CharField(verbose_name="Название", max_length=200, unique=True)
    iata_code = models.CharField(verbose_name="IATA", max_length=3, unique=True)
    icao_code = models.CharField(verbose_name="ICAO", max_length=4, unique=True)
    lat = models.FloatField(verbose_name="Широта")
    lng = models.FloatField(verbose_name="Долгота")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name="Страна")
    logo = models.ImageField(verbose_name="Лого", upload_to='data/airport/',
                            default='data/airport/no.jpg')
    priority = models.BooleanField(verbose_name="Приоритет", default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Аэропорт"
        verbose_name_plural = "Аэропорты"
        ordering = ["-priority", "name"]


class AircraftType(models.Model):
    model = models.CharField(verbose_name="Название", max_length=200, unique=True)
    icao_code = models.CharField(verbose_name="Код ICAO", max_length=4, unique=True)
    priority = models.BooleanField(verbose_name="Приоритет", default=False)

    def __str__(self):
        return self.model

    class Meta:
        verbose_name = "Тип самолета"
        verbose_name_plural = "Типы самолетов"
        ordering = ["-priority", "model"]


class Airline(models.Model):
    name = models.CharField(verbose_name="Название", max_length=200, unique=True)
    iata_code = models.CharField(verbose_name="IATA", max_length=2, unique=True)
    icao_code = models.CharField(verbose_name="ICAO", max_length=3, unique=True)
    logo = models.ImageField(verbose_name="Лого", upload_to='data/airline/',
                      default='data/airline/no.jpg')
    account = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    priority = models.BooleanField(verbose_name="Приоритет", default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Авиакомпания"
        verbose_name_plural = "Авиакомпании"
        ordering = ["-priority", "name"]


class Aircraft(models.Model):
    reg = models.CharField(verbose_name="Код самолета", max_length=10, unique=True)
    model = models.ForeignKey(AircraftType, on_delete=models.CASCADE, verbose_name="Модель")
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, verbose_name="Владелец")
    hub = models.ForeignKey(Airport, on_delete=models.CASCADE, verbose_name="Хаб")
    status = models.BooleanField(verbose_name="Активный", default=True)
    foto = models.ImageField(verbose_name="Фото", upload_to='data/aircraft/',
                             default='data/aircraft/no.jpg')

    def __str__(self):
        return self.reg

    class Meta:
        verbose_name = "Самолет"
        verbose_name_plural = "Самолеты"
        ordering = ["reg"]


class Pilot(models.Model):
    first_name = models.CharField(verbose_name="Имя", max_length=50)
    last_name = models.CharField(verbose_name="Фамилия", max_length=50)
    patronymic = models.CharField(verbose_name="Отчество", max_length=50)
    sex = models.CharField(max_length=1, choices=choice_type_sex, verbose_name="Пол")
    type_pilot = models.CharField(max_length=1, choices=choice_type_pilot, default="C", verbose_name="Тип пилота")
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, verbose_name="Авиакомпания")
    ratings = models.ManyToManyField(AircraftType, verbose_name="Квалификация")
    hub = models.ForeignKey(Airport, on_delete=models.CASCADE, verbose_name="Хаб")
    foto = models.ImageField(verbose_name="Фото", upload_to='data/person/',
                             default='data/person/no.jpg')
    active = models.BooleanField(verbose_name="Активный", default=True)

    def __str__(self):
        s = "{} {} {} ({})".format(self.last_name, self.first_name, self.patronymic, self.type_pilot)
        return s

    class Meta:
        verbose_name = "Пилот"
        verbose_name_plural = "Пилоты"
        ordering = ["type_pilot", "airline", "last_name", "first_name"]


class Steward(models.Model):
    first_name = models.CharField(verbose_name="Имя", max_length=50)
    last_name = models.CharField(verbose_name="Фамилия", max_length=50)
    patronymic = models.CharField(verbose_name="Отчество", max_length=50)
    sex = models.CharField(max_length=1, choices=choice_type_sex, verbose_name="Пол")
    hub = models.ForeignKey(Airport, on_delete=models.CASCADE, verbose_name="Хаб")
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, verbose_name="Авиакомпания")
    foto = models.ImageField(verbose_name="Фото", upload_to='data/person/',
                             default='data/person/no.jpg')

    def __str__(self):
        s = "{} {} {}".format(self.last_name, self.first_name, self.patronymic)
        return s

    class Meta:
        verbose_name = "Стюард"
        verbose_name_plural = "Стюарды"
        ordering = ["last_name", "first_name"]


class Route(models.Model):
    number = models.IntegerField(verbose_name="Код")
    from_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, verbose_name="Откуда", related_name='f_a')
    to_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, verbose_name="Куда", related_name='t_a')
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, verbose_name="Авикомпания")
    days_of_week = models.CharField(verbose_name="Дни полета", max_length=7)
    from_scheduled_time = models.TimeField(verbose_name="Плановое время вылета")
    to_scheduled_time = models.TimeField(verbose_name="Плановое время прилета")
    is_international = models.BooleanField(verbose_name="Международный", default=False)
    is_regular = models.BooleanField(verbose_name="Регулярный", default=True)

    def __str__(self):
        s = str(self.number)
        return s

    class Meta:
        verbose_name = "Маршрут"
        verbose_name_plural = "Маршруты"
        ordering = ["airline", "number"]


class Crew(models.Model):
    pic = models.ForeignKey(Pilot, on_delete=models.CASCADE, verbose_name="КВС", related_name="crew_p")
    co_pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE, verbose_name="Второй пилот", related_name="crew_c")
    engineer = models.ForeignKey(Pilot, on_delete=models.CASCADE, verbose_name="Бортмеханик", related_name="crew_e")
    steward = models.ManyToManyField(Steward, verbose_name="Бортпроводники")

    def __str__(self):
        s = "КВС: {} {} {}".format(self.pic.last_name, self.pic.first_name, self.pic.patronymic)
        return s

    class Meta:
        verbose_name = "Экипаж"
        verbose_name_plural = "Экипажи"


class FlightRouteLime(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, verbose_name="Маршрут")
    from_datetime = models.DateTimeField(verbose_name="Ориентировочное время вылета")
    to_datetime = models.DateTimeField(verbose_name="Ориентировочное время прилета")
    actual_from_datetime = models.DateTimeField(verbose_name="Фактическое время вылета")
    actual_to_datetime = models.DateTimeField(verbose_name="Фактическое время прилета")
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE, verbose_name="Персонал")
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, verbose_name="Самолет")

    class Meta:
        verbose_name = "Рейс"
        verbose_name_plural = "Рейсы"
        ordering = ["route"]

