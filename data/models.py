from django.db import models

choice_type_pilot = (
    ("C", 'КВС'),
    ("S", 'Второй пилот'),
    ("E", 'Бортинженер'),
)

choice_type_sex = (
    ("M", 'Мужчина'),
    ("W", 'Женщина'),
)


class Country(models.Model):
    name = models.CharField(verbose_name="Название", max_length=100, unique=True)
    flag = models.ImageField(verbose_name="Флаг", upload_to='data/country/',
                             default='data/country/no.jpg')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"
        ordering = ["name"]


class Airport(models.Model):
    name = models.CharField(verbose_name="Название", max_length=200, unique=True)
    iata_code = models.CharField(verbose_name="IATA", max_length=3, unique=True)
    icao_code = models.CharField(verbose_name="ICAO", max_length=4, unique=True)
    lat = models.FloatField(verbose_name="Широта", unique=True)
    lng = models.FloatField(verbose_name="Долгота", unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name="Страна")
    logo = models.ImageField(verbose_name="Лого", upload_to='data/airport/',
                      default='data/airport/no.jpg')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Аэропорт"
        verbose_name_plural = "Аэропорты"
        ordering = ["name"]


class AircraftType(models.Model):
    model = models.CharField(verbose_name="Название RU", max_length=200, unique=True)
    icao_code = models.CharField(verbose_name="Код ICAO", max_length=4, unique=True)

    def __str__(self):
        return self.model

    class Meta:
        verbose_name = "Тип самолета"
        verbose_name_plural = "Типы самолетов"
        ordering = ["model"]


class Airline(models.Model):
    name = models.CharField(verbose_name="Название", max_length=200, unique=True)
    iata_code = models.CharField(verbose_name="IATA", max_length=2, unique=True)
    icao_code = models.CharField(verbose_name="ICAO", max_length=3, unique=True)
    logo = models.ImageField(verbose_name="Лого", upload_to='data/airline/',
                      default='data/airline/no.jpg')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Авиакомпания"
        verbose_name_plural = "Авиакомпании"
        ordering = ["name"]


class Aircraft(models.Model):
    reg = models.CharField(verbose_name="Код самолета", max_length=10, unique=True)
    model = models.ForeignKey(AircraftType, on_delete=models.CASCADE, verbose_name="Модель")
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE, verbose_name="Владелец")
    hub = models.ForeignKey(Airport, on_delete=models.CASCADE, verbose_name="Хаб")
    status = models.BooleanField(verbose_name="Активный ли?", default=True)
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
    ratings = models.ManyToManyField(AircraftType, verbose_name="Квалификация")
    hub = models.ForeignKey(Airport, on_delete=models.CASCADE, verbose_name="Хаб")
    foto = models.ImageField(verbose_name="Фото", upload_to='data/person/',
                             default='data/person/no.jpg')

    def __str__(self):
        return self.last_name

    def get_ratings(self):
        return "\n".join([p.products for p in self.product.all()])

    class Meta:
        verbose_name = "Пилот"
        verbose_name_plural = "Пилоты"
        ordering = ["last_name", "first_name"]


class Steward(models.Model):
    first_name = models.CharField(verbose_name="Имя", max_length=50)
    last_name = models.CharField(verbose_name="Фамилия", max_length=50)
    patronymic = models.CharField(verbose_name="Отчество", max_length=50)
    sex = models.CharField(max_length=1, choices=choice_type_sex, verbose_name="Пол")
    hub = models.ForeignKey(Airport, on_delete=models.CASCADE, verbose_name="Хаб")
    foto = models.ImageField(verbose_name="Фото", upload_to='data/person/',
                             default='data/person/no.jpg')

    def __str__(self):
        return self.last_name

    class Meta:
        verbose_name = "Стюард"
        verbose_name_plural = "Стюарды"
        ordering = ["last_name", "first_name"]