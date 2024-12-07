from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app


__all__ = ('celery_app',)




# Yes, your current approach is one of the best practices in Django for structuring large monolithic applications. It balances modularity, separation of concerns, and scalability while staying maintainable in the context of a monolithic architecture. Here's why this is an excellent choice:

# Why Your Approach is Great
# Separation of Concerns:

# User-role-based apps (customer_portal, partner_portal, admin_panel) ensure workflows are modular and focused on specific user groups.
# Domain-specific apps (booking, payment, notification, analytics) centralize shared functionalities, avoiding duplication.
# Scalability and Maintainability:

# As your project grows, the modularity simplifies adding new features or refactoring.
# Teams can work on separate apps without stepping on each other’s toes.
# Industry Alignment:

# Many Django projects adopt a similar approach, as it maps well to business needs and Django's app-based architecture.
# Centralized Database:

# The use of a single database keeps development simpler while leveraging Django’s ORM for model relationships across apps.
# Flexibility for Future Migration:

# If needed, you can break domain-specific apps (like notification or payment) into microservices with minimal impact on the rest of the system.
