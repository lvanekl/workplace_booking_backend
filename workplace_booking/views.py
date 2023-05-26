from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Floor, Room, Workplace, Booking, Status
from .serializers import FloorSerializer, FloorDetailSerializer, StatusSerializer, \
    RoomDetailSerializer, BookWorkplaceSerializer


class FloorList(generics.ListAPIView):
    queryset = Floor.objects.all()
    serializer_class = FloorSerializer


class FloorDetail(generics.RetrieveAPIView):
    queryset = Floor.objects.all()
    serializer_class = FloorDetailSerializer


class RoomDetail(generics.RetrieveAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomDetailSerializer


class StatusList(generics.ListAPIView):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer


# TODO вопрос от какого класса наследоваться
class BookWorkplace(generics.UpdateAPIView):
    queryset = Workplace.objects.all()
    serializer_class = BookWorkplaceSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['PUT'])
@permission_classes((permissions.IsAuthenticated,))
def BookMultipleWorkplaces(request):
    date = request.data['date']
    workplaces_ids_list = request.data['workplaces_list']
    boolean_status = request.data['boolean_status']  # забронировать/разбронировать
    # нет проверки, чтоб все рабочие места были в одной комнате
    # нет проверки на валидность айдишников

    if boolean_status == '0':
        # разбронировать
        bad_workplaces = []
        for workplace_id in workplaces_ids_list:
            workplace = Workplace.objects.get(id=workplace_id)
            # если место не забронированно текущим юзером на текущую дату
            if not workplace.bookings.filter(date=date, user=request.user).exists():
                bad_workplaces.append(workplace_id)

        if len(bad_workplaces) != 0:
            # если список плохих мест не пустой
            return Response({'detail': f'Conflict', 'indexes': bad_workplaces, 'date': date,
                             'boolean_status': boolean_status},
                            status=status.HTTP_409_CONFLICT)

        # если все места забронены текущим пользователем, то пробегаемся по ним и разбронируем
        for workplace_id in workplaces_ids_list:
            workplace = Workplace.objects.get(id=workplace_id)
            booking = Booking.objects.get(workplace=workplace, user=request.user, date=date)
            booking.delete()
        return Response({'detail': f'Success', 'indexes': workplaces_ids_list, 'date': date,
                         'boolean_status': boolean_status},
                        status=status.HTTP_200_OK)
    elif boolean_status == '1':
        # забронировать
        bad_workplaces = []
        for workplace_id in workplaces_ids_list:
            workplace = Workplace.objects.get(id=workplace_id)
            # если место сломано или если есть бронирования этого места на эту дату
            if not workplace.is_available or workplace.bookings.filter(date=date).exists():
                bad_workplaces.append(workplace_id)

        if len(bad_workplaces) != 0:
            # если список плохих мест не пустой
            return Response({'detail': f'Conflict', 'indexes': bad_workplaces, 'date': date,
                             'boolean_status': boolean_status},
                            status=status.HTTP_409_CONFLICT)

        # если все места свободны, то пробегаемся по ним и бронируем
        for workplace_id in workplaces_ids_list:
            workplace = Workplace.objects.get(id=workplace_id)
            new_booking = Booking(workplace=workplace, user=request.user, date=date)
            new_booking.save()
        return Response({'detail': f'Success', 'indexes': workplaces_ids_list, 'date': date,
                         'boolean_status': boolean_status},
                        status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes((permissions.IsAdminUser,))
def GenerateStatuses(request):
    workplace_statuses = [{'name': 'FREE', 'color': 'aed4bc'},
                          {'name': 'TAKEN', 'color': 'fc9090'},
                          {'name': 'YOURS', 'color': '3aaeb5'},
                          {'name': 'BROKEN', 'color': 'f5a77a'}]
    created = []
    for workplace_status in workplace_statuses:
        if not Status.objects.filter(name=workplace_status['name']).exists():
            Status(**workplace_status).save()
            created.append(workplace_status['name'])
    if len(created) == 0:
        return Response({'detail': f'No statuses created'},
                        status=status.HTTP_200_OK)
    else:
        return Response({'detail': f'Succesfully created statuses {" ".join(created)}'},
                        status=status.HTTP_200_OK)
