
"""
    Manages 
    cross-platform notifications 
    and reminders through emails, SMS, or push notifications, 
    including booking confirmations, 
    reminders, 
    and post-service feedback prompts.


    Responsibilities:
Booking Reminders: Notify customers about upcoming appointments (e.g., one day before, one hour before).
Service Updates: Send updates if there are any changes to the service or partner.
Promotions: Inform customers about discounts, promotions, or new services.
Push Notifications: Send push notifications to customers for booking-related or promotional activities.
Email/SMS Alerts: Manage email and SMS notifications for critical activities (e.g., booking confirmations, cancellations).
Key Models:
Notification: Stores notification data, including type, content, recipient, and status (sent, pending).
Message: Stores email/SMS content or push notification details.
Key Views & Logic:
Send Notification: Logic to trigger notifications (e.g., for booking reminders or updates).
View Notification: Logic for customers to view their notifications in the app.
Push Notification Setup: Logic for setting up and sending push notifications.
Interactions with customer_portal:
The customer_portal app will retrieve and display notifications, send customer-related data to trigger reminders, and show updates (e.g., booking confirmations).

"""