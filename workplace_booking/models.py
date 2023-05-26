from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class Floor(models.Model):
    name = models.CharField(max_length=50)

    width = models.IntegerField(null=True, default=None, blank=True)
    height = models.IntegerField(null=True, default=None, blank=True)

    svg_map = models.FileField(null=True, default=None, upload_to='floor_images/', blank=True)
    png_map = models.FileField(null=True, default=None, upload_to='floor_images/', blank=True)

    default_x_coordinate = models.IntegerField(blank=True, default=0)
    default_y_coordinate = models.IntegerField(blank=True, default=0)

    def __str__(self):
        return self.name


class Room(models.Model):
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=50)
    rows = models.IntegerField()
    columns = models.IntegerField()

    index_on_map = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class Workplace(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='workplaces')
    is_available = models.BooleanField(default=True, verbose_name='is available')
    index = models.IntegerField()
    # room.workplaces => unique ??? я забыл что имел ввиду под этим коментом
    column_id = models.IntegerField(blank=True, null=True)
                                    # validators=[MinValueValidator(0), MaxValueValidator(room.columns-1)])
    row_id = models.IntegerField(blank=True, null=True)
                                 # validators=[MinValueValidator(0), MaxValueValidator(room.rows-1)])

    class Meta:
        unique_together = ('room', 'column_id', 'row_id',)

    def __str__(self):
        return str(self.index)


class Booking(models.Model):
    workplace = models.ForeignKey(Workplace, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()

    def __str__(self):
        return self.user.username + ' ' + str(self.date) + ' ' + str(self.workplace)


class Status(models.Model):
    STATUS_NAME_CHOISES = [
        ('FREE', 'Свободно'),
        ('TAKEN', 'Занято'),
        ('YOURS', 'Забронировано вами'),
        ('BROKEN', 'Недоступно'),
    ]

    name = models.CharField(max_length=6, choices=STATUS_NAME_CHOISES, default='FREE', unique=True)
    color = models.CharField(max_length=6, verbose_name='цвет в hex')

    def __str__(self):
        return self.name
