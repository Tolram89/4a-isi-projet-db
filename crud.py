from sqlmodel import select, Session
import models
from typing import Optional
from datetime import date, datetime, timezone

#----User ----------
def create_user(session: Session, username: str, password_hash: str, role: models.UserRole = models.UserRole.STANDARD) -> models.User:
    existing = get_user_by_username(session, username)
    if existing is not None:
        raise ValueError(f"User '{username}' already exist.")

    user = models.User(username=username, role=role, password_hash=password_hash)
    session.add(user)
    session.commit()
    session.refresh(user) #refresh l'id de sqlite
    return user

def get_user_by_id(session: Session, user_id: int) -> Optional[models.User]:
    return session.get(models.User, user_id)
    

def get_user_by_username(session: Session, username: str) -> Optional[models.User]:
    statement = select(models.User).where(models.User.username == username)
    return session.exec(statement).first()

def get_all_users(session: Session)-> list[models.User]:
    statement = select(models.User)
    return session.exec(statement).all()
    
def set_user_blocked(session: Session, user_id: int, is_blocked: bool) -> models.User:
    user = get_user_by_id(session, user_id)
    if user is None:
        raise LookupError(f"User '{user_id}' did not exist.")

    user.is_blocked = is_blocked
    session.add(user)
    session.commit()
    session.refresh(user) #refresh l'id de sqlite
    return user


#-----------Category -------
def create_category(session: Session, name: str) -> models.Category :
    existing = get_category_by_name(session, name)
    if existing is not None:
        raise ValueError(f"Category : '{name}' already exist.")

    category = models.Category(name=name)
    session.add(category)
    session.commit()
    session.refresh(category) #refresh l'id de sqlite
    return category

def get_category_by_name(session: Session, name: str) -> Optional[models.Category]:
    statement = select(models.Category).where(models.Category.name == name)
    return session.exec(statement).first()

def get_all_categories(session: Session) -> list[models.Category] :
    statement = select(models.Category)
    return session.exec(statement).all()

#---------Product-------------
def create_product(session: Session, name: str, price: float, 
                   stock: int, description: Optional[str] = None, 
                   category_id: Optional[int] = None, is_available: bool = True) -> models.Product :
    existing_product = get_product_by_name(session, name)
    if existing_product is not None:
        raise ValueError(f"Product : '{name}' already exist.")
    if category_id is not None:
        existing_category = session.get(models.Category, category_id)
        if existing_category is  None:
                raise ValueError(f"Category : '{category_id}' did not exist.")

    product = models.Product(name=name, price=price, stock=stock, 
                             description=description, category_id=category_id, is_available=is_available)
    session.add(product)
    session.commit()
    session.refresh(product) #refresh l'id de sqlite
    return product

def get_product_by_name(session: Session, name: str) -> Optional[models.Product]:
    statement = select(models.Product).where(models.Product.name == name)
    return session.exec(statement).first()

def get_product_by_id(session: Session, product_id: int) -> Optional[models.Product]:
    return session.get(models.Product, product_id)

def get_all_products(session: Session, include_deleted: bool = False) -> list[models.Product] :
    if(not include_deleted):
        statement = select(models.Product).where(models.Product.is_deleted == False)
    else :
        statement = select(models.Product)
    return session.exec(statement).all()

def update_product(session: Session, product_id: int, **updates) -> models.Product :
    product = session.get(models.Product, product_id)
    if product is None or product.is_deleted:
        raise LookupError(f"Product {product_id} not found.")

    forbidden_fields = {"id", "is_deleted"}
    for key, value in updates.items():
        if key == "category_id":
            category_id = value
            if category_id is not None:
                existing_category = session.get(models.Category, category_id)
                if existing_category is  None:
                        raise ValueError(f"Category : '{category_id}' did not exist.")
        if key not in forbidden_fields and value is not None and hasattr(product, key):
            setattr(product, key, value)

    session.add(product)
    session.commit()
    session.refresh(product)
    return product

def delete_product(session: Session, product_id: int) -> models.Product:
    product = get_product_by_id(session, product_id)
    if product is None:
        raise LookupError(f"Product '{product_id}' did not exist.")

    product.is_deleted = True
    product.is_available = False
    session.add(product)
    session.commit()
    session.refresh(product) #refresh l'id de sqlite
    return product


# ----------- Menu -----------
def get_menu_available_stock(menu: models.Menu) -> int:
    if not menu.menu_products:
        return 0
    stocks = []
    for mp in menu.menu_products:
        if mp.product is None or mp.product.is_deleted or not mp.product.is_available:
            return 0
        stocks.append(mp.product.stock // mp.quantity)
    return min(stocks)


def create_menu(
    session: Session,
    name: str,
    price: float,
    items: list[tuple[int, int]],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    description: Optional[str] = None,
    is_available: bool = True,
) -> models.Menu:
    if not items:
        raise ValueError("A menu must contain at least one product.")
    if end_date is not None and start_date is not None and end_date < start_date:
        raise ValueError("end_date cannot be earlier than start_date.")

    for product_id, quantity in items:
        if quantity < 1:
            raise ValueError("Product quantity in a menu must be at least 1.")
        product = session.get(models.Product, product_id)
        if product is None or product.is_deleted:
            raise LookupError(f"Product '{product_id}' not found.")

    menu = models.Menu(
        name=name,
        price=price,
        start_date=start_date or datetime.now(timezone.utc).date(),
        end_date=end_date,
        description=description,
        is_available=is_available,
    )
    session.add(menu)
    session.flush()  # Génère menu.id sans fermer la transaction

    for product_id, quantity in items:
        session.add(models.MenuProduct(menu_id=menu.id, product_id=product_id, quantity=quantity))

    session.commit()
    session.refresh(menu)
    return menu


def get_menu_by_id(session: Session, menu_id: int) -> Optional[models.Menu]:
    return session.get(models.Menu, menu_id)


def get_all_menus(session: Session, include_deleted: bool = False) -> list[models.Menu]:
    if not include_deleted:
        statement = select(models.Menu).where(models.Menu.is_deleted == False)
    else:
        statement = select(models.Menu)
    return session.exec(statement).all()


def update_menu(
    session: Session,
    menu_id: int,
    items: Optional[list[tuple[int, int]]] = None,
    **updates,
) -> models.Menu:
    menu = session.get(models.Menu, menu_id)
    if menu is None or menu.is_deleted:
        raise LookupError(f"Menu '{menu_id}' not found.")

    forbidden_fields = {"id", "is_deleted"}
    for key, value in updates.items():
        if key not in forbidden_fields and value is not None and hasattr(menu, key):
            setattr(menu, key, value)

    if menu.end_date is not None and menu.start_date is not None and menu.end_date < menu.start_date:
        raise ValueError("end_date cannot be earlier than start_date.")

    if items is not None:
        if not items:
            raise ValueError("A menu must contain at least one product.")
        for product_id, quantity in items:
            if quantity < 1:
                raise ValueError("Product quantity in a menu must be at least 1.")
            product = session.get(models.Product, product_id)
            if product is None or product.is_deleted:
                raise LookupError(f"Product '{product_id}' not found.")

        for old_mp in list(menu.menu_products):
            session.delete(old_mp)
        session.flush()

        for product_id, quantity in items:
            session.add(models.MenuProduct(menu_id=menu.id, product_id=product_id, quantity=quantity))

    session.add(menu)
    session.commit()
    session.refresh(menu)
    return menu


def delete_menu(session: Session, menu_id: int) -> models.Menu:
    menu = session.get(models.Menu, menu_id)
    if menu is None or menu.is_deleted:
        raise LookupError(f"Menu '{menu_id}' not found.")

    menu.is_deleted = True
    menu.is_available = False
    session.add(menu)
    session.commit()
    session.refresh(menu)
    return menu


# ----------- ClosureDay -----------
def create_closure_day(session: Session, closure_date: date, reason: Optional[str] = None) -> models.ClosureDay:
    statement = select(models.ClosureDay).where(models.ClosureDay.closure_date == closure_date)
    if session.exec(statement).first() is not None:
        raise ValueError(f"Closure day '{closure_date}' already exists.")

    closure = models.ClosureDay(closure_date=closure_date, reason=reason)
    session.add(closure)
    session.commit()
    session.refresh(closure)
    return closure


def get_all_closure_days(session: Session) -> list[models.ClosureDay]:
    statement = select(models.ClosureDay).order_by(models.ClosureDay.closure_date)
    return session.exec(statement).all()


def is_closure_day(session: Session, target_date: date) -> bool:
    statement = select(models.ClosureDay).where(models.ClosureDay.closure_date == target_date)
    return session.exec(statement).first() is not None


def delete_closure_day(session: Session, closure_id: int) -> None:
    closure = session.get(models.ClosureDay, closure_id)
    if closure is None:
        raise LookupError(f"ClosureDay '{closure_id}' not found.")

    session.delete(closure)
    session.commit()

# ----------- Order -----------
def create_order(
    session: Session,
    user_id: int,
    pickup_date: date,
    product_items: Optional[list[tuple[int, int]]] = None,
    menu_items: Optional[list[tuple[int, int]]] = None,
) -> models.Order:
    product_items = product_items or []
    menu_items = menu_items or []

    if not product_items and not menu_items:
        raise ValueError("An order must contain at least one product or menu.")

    user = session.get(models.User, user_id)
    if user is None:
        raise LookupError(f"User '{user_id}' not found.")
    if user.is_blocked:
        raise ValueError("Blocked users cannot place orders.")

    today = datetime.now(timezone.utc).date()
    if pickup_date < today:
        raise ValueError("pickup_date cannot be in the past.")
    if is_closure_day(session, pickup_date):
        raise ValueError(f"Restaurant is closed on {pickup_date}.")

    required_stock: dict[int, int] = {}
    resolved_products: list[tuple[models.Product, int]] = []
    resolved_menus: list[tuple[models.Menu, int]] = []

    for product_id, quantity in product_items:
        if quantity < 1:
            raise ValueError("Product quantity must be at least 1.")
        product = session.get(models.Product, product_id)
        if product is None or product.is_deleted:
            raise LookupError(f"Product '{product_id}' not found.")
        if not product.is_available:
            raise ValueError(f"Product '{product.name}' is currently unavailable.")

        resolved_products.append((product, quantity))
        required_stock[product.id] = required_stock.get(product.id, 0) + quantity

    for menu_id, quantity in menu_items:
        if quantity < 1:
            raise ValueError("Menu quantity must be at least 1.")
        menu = session.get(models.Menu, menu_id)
        if menu is None or menu.is_deleted:
            raise LookupError(f"Menu '{menu_id}' not found.")
        if not menu.is_available:
            raise ValueError(f"Menu '{menu.name}' is currently unavailable.")
        if menu.start_date > pickup_date or (menu.end_date is not None and menu.end_date < pickup_date):
            raise ValueError(f"Menu '{menu.name}' is not valid for {pickup_date}.")

        resolved_menus.append((menu, quantity))
        for mp in menu.menu_products:
            if mp.product is None or mp.product.is_deleted or not mp.product.is_available:
                raise ValueError(f"Menu '{menu.name}' contains an unavailable product.")
            required_stock[mp.product_id] = required_stock.get(mp.product_id, 0) + (mp.quantity * quantity)

    products_to_update: list[tuple[models.Product, int]] = []
    for prod_id, needed in required_stock.items():
        product = session.get(models.Product, prod_id)
        if product is None or product.stock < needed:
            name = product.name if product else str(prod_id)
            raise ValueError(f"Insufficient stock for product '{name}'.")
        products_to_update.append((product, needed))

    order = models.Order(user_id=user_id, pickup_date=pickup_date)
    session.add(order)
    session.flush()

    for product, quantity in resolved_products:
        session.add(
            models.OrderProduct(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=product.price,
            )
        )

    for menu, quantity in resolved_menus:
        session.add(
            models.OrderMenu(
                order_id=order.id,
                menu_id=menu.id,
                quantity=quantity,
                unit_price=menu.price,
            )
        )

    for product, needed in products_to_update:
        product.stock -= needed
        session.add(product)

    session.commit()
    session.refresh(order)
    return order


def get_order_by_id(session: Session, order_id: int) -> Optional[models.Order]:
    return session.get(models.Order, order_id)


def get_orders_by_user(session: Session, user_id: int) -> list[models.Order]:
    statement = (
        select(models.Order)
        .where(models.Order.user_id == user_id)
        .order_by(models.Order.created_at.desc())
    )
    return session.exec(statement).all()


def get_all_orders(
    session: Session,
    status: Optional[models.OrderStatus] = None,
    pickup_date: Optional[date] = None,
) -> list[models.Order]:
    statement = select(models.Order)
    if status is not None:
        statement = statement.where(models.Order.status == status)
    if pickup_date is not None:
        statement = statement.where(models.Order.pickup_date == pickup_date)
    statement = statement.order_by(models.Order.pickup_date, models.Order.created_at)
    return session.exec(statement).all()


def update_order_status(
    session: Session,
    order_id: int,
    new_status: models.OrderStatus,
) -> models.Order:
    order = session.get(models.Order, order_id)
    if order is None:
        raise LookupError(f"Order '{order_id}' not found.")

    if order.status != models.OrderStatus.PENDING:
        raise ValueError(f"Cannot change status of an order already '{order.status.value}'.")

    if new_status == models.OrderStatus.PENDING:
        return order

    if new_status == models.OrderStatus.CANCELLED:
        for op in order.order_products:
            if op.product is not None:
                op.product.stock += op.quantity
                session.add(op.product)

        for om in order.order_menus:
            if om.menu is not None:
                for mp in om.menu.menu_products:
                    if mp.product is not None:
                        mp.product.stock += mp.quantity * om.quantity
                        session.add(mp.product)

    order.status = new_status
    session.add(order)
    session.commit()
    session.refresh(order)
    return order