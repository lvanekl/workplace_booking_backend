from rest_framework import serializers
from .models import Floor, Room, Workplace, Booking, Status


class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name',)
        model = Floor


class FloorDetailSerializer(serializers.ModelSerializer):
    rooms_info = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'name', 'width', 'height',
                  'svg_map', 'png_map', 'default_x_coordinate', 'default_y_coordinate',
                  'rooms_info',)
        model = Floor

    def get_rooms_info(self, floor):
        return [RoomSerializer(room).data for room in floor.rooms.all()]


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'index_on_map',)
        model = Room


class RoomDetailSerializer(serializers.ModelSerializer):
    workplaces_info = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'name',
                  'rows', 'columns',
                  'workplaces_info',)
        model = Room

    def get_workplaces_info(self, room):
        return [WorkplaceSerializer(workplace, context=self.context).data for workplace in room.workplaces.all()]


class WorkplaceSerializer(serializers.ModelSerializer):
    # возвращает информацию о рабочем месте. если передается параметр date в url запросе
    # то возвращает статус на текущую дату
    status_by_date = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'index',
                  'column_id', 'row_id',
                  'status_by_date',)
        model = Workplace

    def get_status_by_date(self, workplace):
        date = self.context['request'].query_params.get('date')
        user = self.context['request'].user
        # date = self.context['request'].data.get('date')
        if date is None:
            return None
        else:
            # если у рабочего места статус "недоступно для работы"
            if not workplace.is_available:
                status = Status.objects.get(name='BROKEN')

            # если место забронировано текущим юзером
            elif not user.is_anonymous and workplace.bookings.filter(date=date, user=user).exists():
                status = Status.objects.get(name='YOURS')

            # если есть объекты booking относящиеся к этому месту и к этой дате, то статус занято
            elif workplace.bookings.filter(date=date).exists():
                status = Status.objects.get(name='TAKEN')

            # иначе статус свободно
            else:
                status = Status.objects.get(name='FREE')

            return StatusSerializer(status).data


class StatusSerializer(serializers.ModelSerializer):
    # возвращает полное описание статуса, но без id. Кажется он не нужен просто
    # оно выглядит так {“status_name”:”FREE”, “color”:”000000”}
    class Meta:
        fields = ('name', 'color',)
        model = Status


class BookWorkplaceSerializer(serializers.ModelSerializer):
    date = serializers.DateField()
    boolean_status = serializers.BooleanField(initial=False)
    booking_status = serializers.SerializerMethodField(method_name='book_workplace')

    class Meta:
        fields = ('date', 'boolean_status', 'booking_status', )
        model = Workplace

    def book_workplace(self, workplace):
        # эндпоинт предусматривает ситуации
        #    а) Пользователь не вошел в аккаунт
        #    б) При бронировании
        #        1) Место сломано
        #           (Workplace {workplace} is broken. Choose another one.)
        #        2) Данное место занято
        #           (Workplace {workplace} is already booked at {date} by another user)
        #        3) Данное место свободно => занимаем
        #           (Successfully created a new booking. You have booked workplace {workplace} at {date})
        #    в) При "разбронировании"
        #        1) Место и так свободно
        #           (Workplace {workplace} is not booked at {date} yet. You can book it.)
        #        2) Место занято другим пользователем => этот не может отменить бронь
        #           (Workplace {workplace} is booked at {date} by another user. You can’t unbook it.)
        #        3) Место занято текущим пользователем => удаляем его бронь
        #           (Your booking on workplace {workplace} at {date} have been successfully deleted. Now everyone can book it)

        date = self.context['request'].data.get('date')
        boolean_status = self.context['request'].data.get('boolean_status')

        # если просят забронировать
        if boolean_status:
            if not workplace.is_available:
                return f'Workplace {workplace} is broken. Choose another one.'

            bookings_today = Booking.objects.filter(date=date)
            user = self.context['request'].user

            # политика партии поменялась)), теперь один юзер может бронировать несколько мест
            # # если уже есть объект бронирования на эту дату и от этого юзера
            # if bookings_today.filter(user=user).count() == 1:
            #     booking_today_by_this_user = bookings_today.get(user=user)
            #     return f'You already have booked workplace {booking_today_by_this_user.workplace} at {date}. ' \
            #            f'New booking was not created'

            # если пустой список, то успешно бронируем
            if bookings_today.filter(workplace=workplace).count() == 0:
                # создаем объект бронирования и возвращаем "успех"
                Booking.objects.create(workplace=workplace, user=user, date=date)
                return f'Successfully created a new booking. You have booked workplace {workplace} at {date}'

            # если не пустой, то говорим, что бронь не удалась
            else:
                return f'Workplace {workplace} is already booked at {date} by another user'
        # если просят разбронировать
        else:
            bookings_on_current_workplace_today = Booking.objects.filter(workplace=workplace, date=date)
            user = self.context['request'].user

            # если пустой список, то говорим, что бронирования на эту дату нет, его нельзя удалить
            if bookings_on_current_workplace_today.count() == 0:
                return f'Workplace {workplace} is not booked at {date} yet. You can book it.'

            # если бронирование есть, но не от этого пользователя
            elif bookings_on_current_workplace_today.filter(user=user).count() == 0:
                return f'Workplace {workplace} is booked at {date} by another user. You can\'t unbook it.'

            # если не пустой список, то удаляем объект
            else:
                bookings_on_current_workplace_today.filter(user=user).delete()
                return f'Your booking on workplace {workplace} at {date} have been successfully deleted. ' \
                       f'Now everyone can book it'
