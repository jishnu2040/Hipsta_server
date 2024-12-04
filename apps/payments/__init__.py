
"""
    Handles all payment processing and integrations (e.g., Stripe, Razorpay), 
    transaction tracking, 
    invoices, 
    discounts, 
    and loyalty rewards application.


     Payments App:
The payments app will handle the processing of payments for services and the management of transaction histories.

Responsibilities:
Payment Gateway Integration: Handle payments through external services like Stripe, PayPal, or bank APIs.
Transaction History: Store and retrieve transaction records for customers (payments, refunds, etc.).
Refund Logic: Handle the logic for processing refunds if a customer cancels an appointment.
Invoicing: Generate invoices for completed services or bookings.
Payment Status: Track and update the status of payments (e.g., pending, successful, failed).
Key Models:
Payment: Stores payment details, including amount, status, method, and transaction ID.
Invoice: Stores invoicing data related to completed payments.
Refund: Stores data related to refunds for bookings or services.
Key Views & Logic:
Create Payment: Logic to initiate payments through the chosen payment gateway.
View Payment History: Display past transactions, including successful and failed payments.
Refund Payment: Logic for processing payment refunds.
Handle Payment Failures: Logic for managing payment errors or failures.
Interactions with customer_portal:
The customer_portal app will trigger payments for booking confirmations, show payment history, and notify customers about successful or failed payments.

"""