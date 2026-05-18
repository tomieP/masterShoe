from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from management.models import Product, ProductVariant, Supplier
import random

class Command(BaseCommand):
    help = 'Seed database with sample products, variants, and users'

    def handle(self, *args, **options):
        # Create groups
        staff_group, _ = Group.objects.get_or_create(name='Staff')
        manager_group, _ = Group.objects.get_or_create(name='Manager')

        # Create users
        staff_user, staff_created = User.objects.get_or_create(
            username='staff',
            defaults={
                'first_name': 'Nhan vien',
                'email': 'staff@example.com',
                'is_staff': True,
                'is_active': True
            }
        )
        if staff_created:
            staff_user.set_password('123456')
            staff_user.save()
            self.stdout.write(self.style.SUCCESS('[OK] Created staff user: staff/123456'))

        staff_user.groups.add(staff_group)

        manager_user, manager_created = User.objects.get_or_create(
            username='manager',
            defaults={
                'first_name': 'Quan ly',
                'email': 'manager@example.com',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )
        if manager_created:
            manager_user.set_password('123456')
            manager_user.save()
            self.stdout.write(self.style.SUCCESS('[OK] Created manager user: manager/123456'))

        manager_user.groups.add(manager_group)

        # # Create suppliers
        # suppliers_data = [
        #     {'name': 'NCC Nike Viet Nam', 'phone': '0901234567', 'address': 'TP.HCM'},
        #     {'name': 'NCC Adidas Viet Nam', 'phone': '0902345678', 'address': 'Ha Noi'},
        #     {'name': 'NCC Puma Viet Nam', 'phone': '0903456789', 'address': 'TP.HCM'},
        #     {'name': 'NCC Converse Viet Nam', 'phone': '0904567890', 'address': 'Da Nang'},
        # ]

        # suppliers = []
        # for supp_data in suppliers_data:
        #     supplier, created = Supplier.objects.get_or_create(
        #         name=supp_data['name'],
        #         defaults={'phone': supp_data['phone'], 'address': supp_data['address']}
        #     )
        #     suppliers.append(supplier)
        #     if created:
        #         self.stdout.write(f'  [+] Supplier: {supplier.name}')

        # # Sample data
        # brands = ['Nike', 'Adidas', 'Puma', 'Converse', 'Vans', 'New Balance', 'Skechers']
        # types = ['The thao', 'Cong so', 'Sandal', 'Chay bo', 'Bong ro']
        # colors = ['Den', 'Trang', 'Xam', 'Xanh', 'Do', 'Vang', 'Cam', 'Tim']
        # sizes = ['35', '36', '37', '38', '39', '40', '41', '42', '43']

        # # Create products and variants
        # products_created = 0
        # variants_created = 0

        # for i in range(1, 41):
        #     code = f'SP{i:04d}'
        #     product, p_created = Product.objects.get_or_create(
        #         code=code,
        #         defaults={
        #             'name': f'Giay {random.choice(brands)} mau {i}',
        #             'brand': random.choice(brands),
        #             'type': random.choice(types),
        #             'subtype': 'Basic',
        #             'description': f'San pham giay dep mau {i} - chat luong tot',
        #             'is_active': True
        #         }
        #     )
        #     if p_created:
        #         products_created += 1
        #         self.stdout.write(f'  [+] Product {i}: {product.name}')

        #     # Create 2-4 random size variants for each product
        #     picked_sizes = random.sample(sizes, k=random.randint(2, 4))
        #     picked_colors = random.sample(colors, k=random.randint(1, 2))

        #     for sz in picked_sizes:
        #         for cl in picked_colors:
        #             # Generate unique SKU
        #             sku = f'{code}-{cl[:2].upper()}-{sz}'

        #             import_price = random.randint(200000, 700000)
        #             selling_price = import_price + random.randint(80000, 250000)

        #             try:
        #                 variant, v_created = ProductVariant.objects.get_or_create(
        #                     product=product,
        #                     color=cl,
        #                     size=sz,
        #                     defaults={
        #                         'import_price': import_price,
        #                         'selling_price': selling_price,
        #                         'sku': sku,
        #                         'stock_quantity': random.randint(5, 70),
        #                         'min_quantity': random.randint(3, 10),
        #                         'is_active': True
        #                     }
        #                 )
        #                 if v_created:
        #                     variants_created += 1
        #             except Exception as e:
        #                 self.stdout.write(f'  [!] Variant error: {e}')

        # self.stdout.write(self.style.SUCCESS(f'\n[DONE] Products: {products_created}, Variants: {variants_created}'))
