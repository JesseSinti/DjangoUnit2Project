# The Rift 🎟️

**The Rift** is a full-stack event management and ticketing web application that allows organizations to host events and users to discover, purchase, and manage tickets seamlessly. Each purchased ticket is delivered digitally with a unique QR code for secure event admission, and payments are processed using Stripe.

---

## 📌 Project Overview

- **Project Name:** The Rift  
- **Project Dates:**  
  - Start: December 15, 2025  
  - End: January 9, 2026  

### 👥 Collaborators
- **Kaden Norlander** – Core functionality, authentication, dashboards, documentation  
- **Jesse Sintikakis** – Backend logic, models, search, filters, purchasing system, CRUD, policy pages  
- **Jack Mossberg** – Frontend Specialist, focusing on styles and javascript functionality

---

## 🎯 Goals

- Create a visually polished and intuitive web application  
- Implement smooth navigation and user experience  
- Combine all learned web development techniques  
- Simulate a real-world, professional-grade application  

---

## 🎯 Target Audience

The Rift is designed for anyone seeking entertainment, including:
- Concerts
- Sporting events
- Comedy shows
- Live theater

The platform supports:
- **Customers** purchasing tickets  
- **Organization Admins** managing events and staff  
- **Organization Members** assisting with event management  

---

## 👤 User Roles

### Organization Admins
- Create and manage events
- Manage ticket inventory
- Approve or remove organization members

### Organization Members
- View and assist with event management
- Limited administrative privileges

### Customers
- Browse events
- Purchase tickets
- View purchase history and spending analytics

---

## 🔑 Key Features

- Role-based authentication and dashboards  
- Organization membership management with approval workflow  
- Event creation with multiple ticket tiers  
- Shopping cart system  
- Stripe-powered secure payments  
- Automatic ticket generation with QR codes  
- Email delivery of digital tickets  
- Search and filtering for events  
- Admin analytics and member management  

---

## 🧠 System Architecture Highlights

### Authentication & Access Control
- Custom decorators enforce admin-only access
- Role-based login redirects users to appropriate dashboards

### Event Management
- Multi-step event creation (event details → ticket tiers)
- Real-time ticket availability calculations

### Checkout & Payments
- Stripe Checkout Sessions
- Supports both single-ticket and cart-based purchases
- Secure fulfillment using atomic database transactions

### Ticket Fulfillment
- Unique ticket records generated per purchase
- QR codes created per ticket
- Automatic email delive
