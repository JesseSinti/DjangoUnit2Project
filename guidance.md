User
 ├── username
 ├── email
 └── is_organizer (Boolean)
Event
 ├── organizer (FK -> User)
 ├── title
 ├── description
 ├── banner_image
 ├── location
 ├── start_time / end_time
 ├── capacity
 └── created_at
TicketTier
 ├── event (FK -> Event)
 ├── name (VIP, General, etc.)
 ├── price
 ├── quantity
Order
 ├── user (FK -> User)
 ├── event (FK -> Event)
 ├── total_price
 └── timestamp
Ticket
 ├── order (FK -> Order)
 ├── tier (FK -> TicketTier)
 ├── uuid (unique)
 ├── qr_code_image
 └── is_used
3:46
Week 1:
:heavy_check_mark: Models
:heavy_check_mark: User auth
:heavy_check_mark: Event CRUD
:heavy_check_mark: Ticket tier system
Week 2:
:heavy_check_mark: Checkout flow
:heavy_check_mark: Ticket generation
:heavy_check_mark: QR codes
:heavy_check_mark: My tickets page
Week 3:
:heavy_check_mark: Organizer dashboard
:heavy_check_mark: Ticket scanning
:heavy_check_mark: Search + filters
:heavy_check_mark: Polish UI










