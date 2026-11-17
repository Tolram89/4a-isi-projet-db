# Pol-eat-heck — Base de données (`4a-isi-projet-db`)

Modélisation, schémas SQLite/SQLModel et scripts d'administration de l'application de réservation de menus **Pol-eat-heck**.

## Équipe & Dépôts liés

* **Collaborateurs :** (`@Tolram89`), (`Natkbz`), (`dcr29`)
* **Back-end (FastAPI) :** [4a-isi-projet-back](https://github.com/Natkbz/4a-isi-projet-back) 
* **Front-end (HTML/CSS/JS) :** [4a-isi-projet-front](https://github.com/dcr29/4a-isi-projet-front)

## Conception de la base de données (MLD / UML)

```mermaid
classDiagram
    class User {
        +int id (PK)
        +string username (UK)
        +string password_hash
        +string role
        +bool is_blocked
        +datetime created_at
    }

    class Category {
        +int id (PK)
        +string name (UK)
    }

    class Product {
        +int id (PK)
        +int category_id [0..1] (FK)
        +string name
        +string description [0..1]
        +float price
        +int stock
        +bool is_available
        +bool is_deleted
    }

    class Menu {
        +int id (PK)
        +string name
        +string description [0..1]
        +float price
        +date start_date [0..1]
        +date end_date [0..1]
        +bool is_available
        +bool is_deleted
    }

    class MenuProduct {
        +int menu_id (PK, FK)
        +int product_id (PK, FK)
        +int quantity
    }

    class Order {
        +int id (PK)
        +int user_id (FK)
        +datetime created_at
        +date pickup_date
        +string status
    }

    class OrderProduct {
        +int id (PK)
        +int order_id (FK)
        +int product_id (FK)
        +int quantity
        +float unit_price
    }

    class OrderMenu {
        +int id (PK)
        +int order_id (FK)
        +int menu_id (FK)
        +int quantity
        +float unit_price
    }

    class ClosureDay {
        +int id (PK)
        +date closure_date (UK)
        +string reason [0..1]
    }

    User "1" --> "0..*" Order : places
    Category "1" --> "0..*" Product : categorizes
    Order "1" *-- "0..*" OrderProduct : contains
    OrderProduct "0..*" --> "1" Product : references
    Order "1" *-- "0..*" OrderMenu : contains
    OrderMenu "0..*" --> "1" Menu : references
    Menu "1" *-- "1..*" MenuProduct : consists of
    MenuProduct "0..*" --> "1" Product : includes
```
    
    
    