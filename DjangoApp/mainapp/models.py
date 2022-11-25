from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Scheme(models.Model):
    class Meta:
        verbose_name = 'Схема'
        verbose_name_plural = 'Схемы'

    number = models.IntegerField("Номер")

    def __str__(self):
        return f'Схема {self.number}'

    def get_profit(self):
        profit = round(sum([profit.cost for profit in self.flight.all()]) - \
                      sum([profit.expenses for profit in self.flight.all()]))
        self.profit = profit
        return profit

    def get_daily_profit(self):
        days = sum([profit.downtime_loading for profit in self.flight.all()]) + \
               sum([profit.downtime_uploading for profit in self.flight.all()]) + \
               sum([profit.travel_time for profit in self.flight.all()])
        daily_profit = self.get_profit() / round(days, 2)
        self.daily_profit = daily_profit
        return daily_profit

    @receiver(post_save, sender='mainapp.Flight')
    def create_node(sender, instance, created, **kwargs):
        if created:
            flight = Flight.objects.filter(van=instance.van)
            instance.index = len(flight) - 1

            if not (Scheme.objects.all()):
                scheme = Scheme.objects.create(number=1)
                instance.scheme = scheme
                instance.save()
                return
            else:
                scheme = Scheme.objects.latest('number')
                van = [fl.van for fl in scheme.flight.all()][0]
                if van == instance.van:
                    instance.scheme = scheme

                elif len(flight) > 1:
                    instance.scheme = flight[0].scheme
                else:
                    scheme = Scheme.objects.create(number=scheme.number + 1)
                    instance.scheme = scheme
                instance.save()
                return


class Flight(models.Model):
    class Meta:
        verbose_name = 'Рейс'
        verbose_name_plural = 'Рейсы'
        ordering = ['van', 'date', 'gruj']

    OBJECT = [
        ('gruj', 'ГРУЖ'),
        ('por', 'ПОР'),
    ]
    ROAD = [
        ('jvs', 'ЮВС'),
        ('dvs', 'ДВС'),
        ('okt', 'ОКТ'),
        ('zcb', 'ЗСБ'),
        ('gor', 'ГОР'),
        ('msc', 'МСК'),
        ('ckv', 'СКВ'),
        ('cvr', 'СВР'),
        ('zab', 'ЗАБ'),
        ('krc', 'КРС'),
    ]
    scheme = models.ForeignKey(Scheme, verbose_name="Схема", on_delete=models.CASCADE, related_name='flight',
                               null=True, blank=True)
    index = models.IntegerField("Индекс", blank=True, null=True)
    date = models.DateTimeField(verbose_name='Погрузка')
    van = models.IntegerField("Вагон")
    gruj = models.CharField("Груж\\пор", max_length=15, choices=OBJECT, default='gruj')
    start_road = models.CharField("Дорога отправления", max_length=10, choices=ROAD, default='msc')
    destination_road = models.CharField("Дорога назначения", max_length=10, choices=ROAD, default='msc')
    cost = models.DecimalField('Стоимость 1 груж. рейса', decimal_places=2, max_digits=12, default=0)
    downtime_loading = models.FloatField('Простой под погрузкой, сут.', default=0)
    downtime_uploading = models.FloatField('Простой под выгрузкой, сут.', default=0)
    travel_time = models.FloatField('Время в пути, сут.', default=1)
    distance_road = models.IntegerField("Расстояние, км")
    expenses = models.DecimalField('Затраты на 1 порож. рейс', decimal_places=2, max_digits=12, default=0)
    station_start_id = models.IntegerField("Код станции отпр(5)")
    station_destination_id = models.IntegerField("Код станции назн. (5)")

    def __str__(self):
        return f'Рейс от {self.date} вагон №{self.van}'



