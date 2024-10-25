# Usage

## First time setup
```bash
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## If project is already setup
```bash
.\env\Scripts\activate
python manage.py migrate
python manage.py runserver
```

## If you want to check the website on your phone
1. Run server on 0.0.0.0:8000
    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```
2. Find your PC's local IP with ipconfig (usually something like 192.168.0.101)
3. Add the local IP to ALLOWED_HOSTS in finance-management-system/project/settings.py
4. While connected to the same network as PC, connect to that IP with same port on your phone (for example 192.168.0.101:8000)

# Linting
Formatting = process which checks/fixes indentation, spacing and similar. Can be fixed automatically

Linting = process which checks for rules (snake_case for variables for example). Cannot be automatically fixed

Setup uses 3 linters and formatters in this process, you can run it locally or commit it to github and it will automatically run:

1. DJlint will automatically format django files (.html)
2. Black will automatically format python files
3. (if it runs on github) If changes were made, it will fix the files and commits them to repo
4. DJlint will run lint, which will show you linting problems in .html files that you should to fix
5. Flake8 will run lint, which will show you linting problems in .py files that you should to fix

## Linting locally

### Automatically fix formatting in html files
```bash
djlint . --reformat
```

### Automatically fix formatting in python files
```bash
black .
```

### Check for linting problems in html files
```bash
djlint . --lint
```

### Check for linting problems in python files
```bash
flake8
```

## Resources

[Google doc](https://docs.google.com/document/d/1CBFf9SYnnrxeE0lQ2UtjCQK5ZHMXkhcF/edit?usp=sharing&ouid=106305257367534443251&rtpof=true&sd=true)

[UI mockup](https://www.figma.com/design/eYu9ELOc3WdKGwBth3F1sO/Untitled?node-id=0-1&node-type=canvas)

## UML diagram

```mermaid
classDiagram
    class User {
        +String username
        +String password
        +String email
        +String first_name
        +String last_name
        +boolean is_staff
        +boolean is_active
        +boolean is_superuser
        +Date last_login
        +Date date_joined
    }

    class UserProfile {
        +User user
        +double balance
        +NotificationMode global_notification_mode 
    }
    
    class Category {
        +UserProfile user
        +String name
    }

    class Transaction {
        +String name
        +double amount
        +Date created_at
        +Date performed_at
        +Category category
        +String description
    }
    
    class RecurringTransaction {
        +TimeInterval interval
    }
    
    class Budget {
        +String name
        +UserProfile owner
        +Date created_at
        +Date exceeded_at
        +double limit
        +Date period_start
        +Date period_end
        +String description
    }
    
    class NotificationMode {
        <<enumeration>>
        NONE
        APP
        EMAIL
        APP_EMAIL
    }
    
    class TimeInterval {
        <<enumeration>>
        DAY
        WEEK
        MONTH
        YEAR
    }
    
    class BudgetRole {
        <<enumeration>>
        PARTICIPANT
        OBSERVER
    }
    
    class BudgetPermission {
        <<enumeration>>
        VIEW
        EDIT
    }
    
    class BudgetNotificationSettings {
        +Boolean on_exceeded
        +Boolean on_limit_change
        +Boolean on_transaction
        +NotificationMode notification_mode 
    }
    
    class SharedBudget {
        +Budget budget
        +UserProfile shared_with
        +BudgetPermission permission
        +BudgetRole role
        +BudgetNotificationSettings notification_settings
    }
    
    class Notification {
        +UserProfile receiver
        +String subject
        +String message
        +Date sent_at
        +Boolean is_read
    }

    Transaction "1" --> "0..1" Category : "has"
    Transaction "N" --* "1" UserProfile : "owns"
    RecurringTransaction --|> Transaction
    Notification "N" --* "1" UserProfile : "owns"
    UserProfile "0..1" --* "1" User : "owns"
    UserProfile "N" *-- "M" Category : "owns"
    NotificationMode <-- UserProfile
    NotificationMode <-- BudgetNotificationSettings
    TimeInterval <-- RecurringTransaction
    SharedBudget "N" --* "1" Budget : "owns"
    SharedBudget "N" --> "1" UserProfile : "shared_with"
    SharedBudget "1" --> "1" BudgetNotificationSettings
    BudgetRole <-- SharedBudget
    BudgetPermission <-- SharedBudget
    Budget "N" --* "1" UserProfile : "owns"
    Budget "N" --> "M" Category : "has"
```
