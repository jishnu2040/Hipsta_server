from collections import defaultdict
from .models import Appointment
from datetime import datetime,timedelta, date
from django.db.models import Count
from apps.booking.models import Appointment
from apps.partner_portal.models import Employee
from apps.core.models import Service 
from apps.partner_portal.models import PartnerDetail  
from django.contrib.auth import get_user_model 

def get_all_bookings_grouped_by_month():
    """
    Fetch all bookings from the database and group them by month with minimal information.
    """
    # Fetch all appointments
    appointments = Appointment.objects.all()

    # Group bookings by year and month
    grouped_bookings = defaultdict(list)
    for appointment in appointments:
        year_month = f"{appointment.date.year}-{appointment.date.month:02d}"  # Format 'YYYY-MM'
        grouped_bookings[year_month].append({
            'date': appointment.date,
            'status': appointment.status,
        })

    # Convert the grouped bookings to a sorted list of months
    sorted_grouped_bookings = sorted(grouped_bookings.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m"))

    # Convert to desired format: list of dictionaries
    result = [{'month': month, 'bookings': bookings} for month, bookings in sorted_grouped_bookings]

    return result





def get_top_partners_by_bookings():
    """
    Fetch the top 5 partners based on the number of bookings in the last month.
    """
    one_month_ago = date.today() - timedelta(days=30)

    # Query appointments in the last month and count bookings per partner
    top_partners = (
        Appointment.objects.filter(date__gte=one_month_ago, status="booked")
        .values("partner__id", "partner__business_name")  # Use the correct field name
        .annotate(total_bookings=Count("id"))
        .order_by("-total_bookings")[:5]
    )

    # Return formatted data
    return [
        {
            "partner_id": partner["partner__id"],
            "partner_name": partner["partner__business_name"],  # Use the correct field name
            "total_bookings": partner["total_bookings"],
        }
        for partner in top_partners
    ]






User = get_user_model()

# services.py
from datetime import date, timedelta
from apps.booking.models import Appointment
from apps.accounts.models import User  # Import the User model

def get_booking_details_with_names():
    """
    Fetch booking details with human-readable names for partner, customer, employee, and service.
    """
    # Fetch all bookings with related data
    bookings = (
        Appointment.objects.select_related("partner", "service")
        .prefetch_related("employee", "customer")  # Prefetching employee and customer
        .filter(date__gte=date.today() - timedelta(days=30))  # Last 30 days
        .values(
            "id",
            "date",
            "start_time",
            "status",
            "total_amount",
            "payment_method",
            "duration",
            "partner__business_name",  # Partner's business name
            "service__name",  # Service name
            "customer__first_name",  # Fetch customer's first name from User model
            "customer__last_name",  # Fetch customer's last name from User model
            "employee__name",  # Employee name
        )
    )

    # Format results
    formatted_bookings = [
        {
            "id": booking["id"],
            "date": booking["date"],
            "start_time": booking["start_time"],
            "status": booking["status"],
            "total_amount": booking["total_amount"],
            "payment_method": booking["payment_method"],
            "duration": booking["duration"],
            "partner_name": booking["partner__business_name"],
            "service_name": booking["service__name"],
            "customer_name": f"{booking['customer__first_name']} {booking['customer__last_name']}" if booking["customer__first_name"] and booking["customer__last_name"] else "N/A",
            "employee_name": booking["employee__name"] if booking["employee__name"] else "N/A",
        }
        for booking in bookings
    ]

    return formatted_bookings
