from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
import razorpay
from razorpay.errors import SignatureVerificationError
from apps.partner_portal.models import SubscriptionPlan, PartnerDetail, Subscription

class CreateRazorpayOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            plan_id = request.data.get('plan_id')
            if not plan_id:
                return Response({"error": "Plan ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the selected subscription plan
            plan = SubscriptionPlan.objects.get(id=plan_id)

            # Razorpay client initialization
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Convert Decimal to float and calculate amount in paise
            amount_in_paise = int(float(plan.price) * 100)

            # Create Razorpay order
            order_data = {
                "amount": amount_in_paise,
                "currency": "INR",
                "receipt": f"rcpt_{str(request.user.id)[:30]}",  # Shortened to fit within 40 characters
                "notes": {"user_id": str(request.user.id), "plan_name": plan.name},
            }
            razorpay_order = client.order.create(order_data)
            # Return the order details
            return Response({
                "order_id": razorpay_order['id'],
                "amount": razorpay_order['amount'],
                "currency": razorpay_order['currency'],
                "plan_name": plan.name,
            }, status=status.HTTP_200_OK)

        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "The selected plan does not exist."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Data from the frontend
            razorpay_order_id = request.data.get('razorpay_order_id')
            razorpay_payment_id = request.data.get('razorpay_payment_id')
            razorpay_signature = request.data.get('razorpay_signature')

            if not (razorpay_order_id and razorpay_payment_id and razorpay_signature):
                return Response({"error": "All payment details are required."}, status=status.HTTP_400_BAD_REQUEST)

            # Initialize Razorpay client
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

            # Verify payment signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            })

            # Get the partner details
            partner = PartnerDetail.objects.get(user=request.user)
            subscription = partner.subscription

            # If the partner doesn't have a subscription, create one
            if not subscription:
                # Optionally, you can add logic to select a default plan for the partner
                # Assuming you have a default plan or the plan can be fetched dynamically
                plan = SubscriptionPlan.objects.first()  # Example, replace with the correct plan logic
                subscription = Subscription.objects.create(partner=partner, plan=plan, status="active")

            # If the subscription is already active
            elif subscription.status == "active":
                return Response({"error": "Your subscription is already active."}, status=status.HTTP_400_BAD_REQUEST)

            # Activate the subscription
            subscription.activate()

            return Response({
                "message": "Subscription activated successfully.",
                "status": subscription.status,
                "start_date": subscription.start_date,
                "end_date": subscription.end_date
            }, status=status.HTTP_200_OK)

        except PartnerDetail.DoesNotExist:
            return Response({"error": "Partner details not found."}, status=status.HTTP_404_NOT_FOUND)
        except SignatureVerificationError:
            return Response({"error": "Payment verification failed."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)