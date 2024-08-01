from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from books.models import Ticket


class PayTicket(APIView):
    def post(self, request):
        ticket_id = request.data.get('ticket_id')
        if not ticket_id:
            return Response({"error": "ticket_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ticket = Ticket.objects.get(id=ticket_id)
            if ticket.status == "Booked":
                ticket.status = "Payed"
                ticket.save()
                return Response({"message": "Ticket status updated to Payed"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Ticket status is not Booked"}, status=status.HTTP_400_BAD_REQUEST)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)
