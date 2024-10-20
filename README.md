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

## Linting
Format = process which checks/fixes indentation, spacing and similar. Can be fixed automatically

Linting = process which checks for rules (snake_case for variables for example). Cannot be automatically fixed

Setup uses 3 linters and formatters.

DJlint will automatically format django files (.html), then it will run lint, which will show you linting problems in .html files that you should to fix.

After that, Black will automatically format python files, then Flake8 will run lint, which will show you linting problems in .py files that you should to fix.

### Linting locally

#### Check formatting problems in html files
```bash
djlint . --check
```

#### Automatically fix formatting in html files
```bash
djlint . --reformat
```

#### Check for linting problems in html files
```bash
djlint . --lint
```

#### Automatically fix formatting problems in python files
```bash
black .
```

#### Check for linting problems in python files
```bash
flake8
```


## If you want to check it on the phone
```bash
python manage.py runserver 0.0.0.0:8000
```
1. Find your PC's local IP with ipconfig
2. Add it to ALLOWED_HOSTS in finance-management-system/project/settings.py
3. Connect to that IP with same port on your phone

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
        +uint interval_seconds
        +Date start_at
        +Date end_at
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
        +String message
        +Date sent_at
        +Boolean is_read
    }

    Transaction "1" --> "0..1" Category : "has"
    Transaction "N" --* "1" UserProfile : "owns"
    RecurringTransaction --|> Transaction
    Notification "N" --* "1" UserProfile : "owns"
    UserProfile "0..1" --* "1" User : "owns"
    UserProfile "1" *-- "N" Category : "owns"
    NotificationMode <-- UserProfile
    NotificationMode <-- BudgetNotificationSettings
    SharedBudget "N" --* "1" Budget : "owns"
    SharedBudget "N" --> "1" UserProfile : "shared_with"
    SharedBudget "1" --> "1" BudgetNotificationSettings
    BudgetRole <-- SharedBudget
    BudgetPermission <-- SharedBudget
    Budget "N" --* "1" UserProfile : "owns"
    Budget "1" --> "N" Category : "has"
```
