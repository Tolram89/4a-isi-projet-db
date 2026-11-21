from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from sqlmodel import Session

import crud
import models
from database import create_db_and_tables, engine

password_hasher = PasswordHash.recommended()


def seed_database() -> None:
    create_db_and_tables()
    today = datetime.now(timezone.utc).date()

    with Session(engine) as session:

        admin = crud.get_user_by_username(session, "admin")
        if admin is None:
            admin = crud.create_user(
                session,
                username="admin",
                password_hash=password_hasher.hash("admin123"),
                role=models.UserRole.ADMIN,
            )

        student = crud.get_user_by_username(session, "toto")
        if student is None:
            student = crud.create_user(
                session,
                username="toto",
                password_hash=password_hasher.hash("student123"),
                role=models.UserRole.STANDARD,
            )

        blocked_user = crud.get_user_by_username(session, "bad_student")
        if blocked_user is None:
            blocked_user = crud.create_user(
                session,
                username="bad_student",
                password_hash=password_hasher.hash("student123"),
                role=models.UserRole.STANDARD,
            )
            crud.set_user_blocked(session, blocked_user.id, True)


        categories_names = ["Burgers", "Accompagnements", "Boissons", "Desserts"]
        categories: dict[str, models.Category] = {}
        for name in categories_names:
            cat = crud.get_category_by_name(session, name)
            if cat is None:
                cat = crud.create_category(session, name)
            categories[name] = cat

        products_spec = [
            ("Burger Classique", 8.50, 30, "Steak haché, cheddar, salade, tomate, sauce maison", "Burgers"),
            ("Burger Végétarien", 8.00, 20, "Galette de légumes, cheddar, oignons confits", "Burgers"),
            ("Frites Maison", 3.00, 50, "Portion de frites fraîches", "Accompagnements"),
            ("Cola 33cl", 2.00, 40, "Canette fraîche 33cl", "Boissons"),
            ("Eau Minérale 50cl", 1.50, 60, "Bouteille d'eau plate 50cl", "Boissons"),
            ("Cookie Chocolat", 2.50, 25, "Cookie moelleux aux pépites de chocolat", "Desserts"),
        ]

        products: dict[str, models.Product] = {}
        for name, price, stock, desc, cat_name in products_spec:
            prod = crud.get_product_by_name(session, name)
            if prod is None:
                prod = crud.create_product(
                    session,
                    name=name,
                    price=price,
                    stock=stock,
                    description=desc,
                    category_id=categories[cat_name].id,
                )
            products[name] = prod

        existing_menus = {m.name: m for m in crud.get_all_menus(session, include_deleted=True)}

        menus_spec = [
            (
                "Menu Classique",
                11.50,
                "Burger Classique + Frites Maison + Cola 33cl",
                today,
                None,  # Permanent
                [
                    (products["Burger Classique"].id, 1),
                    (products["Frites Maison"].id, 1),
                    (products["Cola 33cl"].id, 1),
                ],
            ),
            (
                "Menu Veggie",
                11.00,
                "Burger Végétarien + Frites Maison + Eau Minérale 50cl",
                today,
                None,  # Permanent
                [
                    (products["Burger Végétarien"].id, 1),
                    (products["Frites Maison"].id, 1),
                    (products["Eau Minérale 50cl"].id, 1),
                ],
            ),
            (
                "Menu Étudiant Semaine",
                13.00,
                "Formule complète avec dessert offerte cette semaine",
                today,
                today + timedelta(days=7),  # Temporaire (7 jours)
                [
                    (products["Burger Classique"].id, 1),
                    (products["Frites Maison"].id, 1),
                    (products["Cola 33cl"].id, 1),
                    (products["Cookie Chocolat"].id, 1),
                ],
            ),
        ]

        menus: dict[str, models.Menu] = {}
        for name, price, desc, s_date, e_date, items in menus_spec:
            if name not in existing_menus:
                menu = crud.create_menu(
                    session,
                    name=name,
                    price=price,
                    items=items,
                    start_date=s_date,
                    end_date=e_date,
                    description=desc,
                )
            else:
                menu = existing_menus[name]
            menus[name] = menu


        closure_date = today + timedelta(days=14)
        if not crud.is_closure_day(session, closure_date):
            crud.create_closure_day(session, closure_date, reason="Fermeture exceptionnelle")


        if not crud.get_orders_by_user(session, student.id):
            crud.create_order(
                session,
                user_id=student.id,
                pickup_date=today + timedelta(days=1),
                product_items=[(products["Cookie Chocolat"].id, 1)],
                menu_items=[(menus["Menu Classique"].id, 1)],
            )

        print("Base de données initialisée avec succès !")


if __name__ == "__main__":
    seed_database()