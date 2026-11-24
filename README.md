# JustBidIt — Online Auction Platform

JustBidIt is a full-stack online auction platform developed as a four-person academic team project using **React, Flask, and MySQL**. Inspired by online marketplaces like eBay, the application allows users to create and browse auction listings, place manual and automatic bids, track bidding history, and receive real-time auction notifications.

The platform also includes customer representative and administrator functionalities for user management, customer support, auction oversight, and sales reporting.

**[Watch Project Demo](https://youtu.be/2yrfb0eTMiA)**

## Tech Stack

| Category | Technologies |
|---|---|
| Frontend | React, JavaScript, CSS, React Bootstrap, React Router, Recharts |
| Backend | Python, Flask, REST APIs, SQLAlchemy |
| Database | MySQL, MySQL Workbench |
| Background Tasks | APScheduler |
| Security | Werkzeug Password Hashing, Session Authentication, CSRF Protection |
| Tools | Git, GitHub |

## My Contributions

I contributed to the development and improvement of JustBidIt across frontend functionality, backend bidding workflows, application security, and testing.

- **Auction Browsing & Product Details:** Developed React interfaces for browsing auction listings and viewing detailed product information.
- **Bidding Engine:** Implemented backend functionality for manual and automatic bidding, bid history tracking, and bid validation.
- **Notifications:** Developed bid-related notification functionality to keep users informed about auction activity.
- **Authentication & Authorization:** Strengthened account security through password hashing, session-based authentication, role-based access controls, and login rate limiting.
- **Application Security:** Implemented CSRF protection, secure image upload validation, environment-based credential management, and improved password-reset handling.
- **Testing & Reliability:** Added backend and frontend tests, strengthened bidding validation, and corrected bid timestamp handling.
- **Documentation & Maintenance:** Improved dependency management, local setup instructions, and repository organization.

*JustBidIt was developed collaboratively by a four-person team. This repository is my fork of the [original team project](https://github.com/shashwatijha/JustBidIt), with my contributions and subsequent improvements.*

## Key Features

- **Auction Listings:** Create, browse, and view product listings with descriptions, images, starting prices, and auction deadlines.
- **Manual & Automatic Bidding:** Place bids manually or configure automatic bidding with maximum limits and bid increments.
- **Bid History:** Track bidding activity and view previous bids.
- **Auction Notifications:** Receive notifications related to bidding activity and auction outcomes.
- **User Authentication:** Secure customer registration and login with password hashing and session-based authentication.
- **Role-Based Access Control:** Separate functionality for customers, customer representatives, and administrators.
- **Customer Support & Administration:** Manage users, handle customer requests, and access sales reporting functionality.
- **Security & Validation:** CSRF protection, login rate limiting, validated bidding requests, and restricted image uploads.

## Local Setup

### Prerequisites

- Python 3.10 or later
- Node.js 18 or later
- MySQL 8

### 1. Set Up the Database

Use a fresh MySQL 8 development database.

Run `createTable.sql` to create the `aos` database schema and load sample auction listings.

**Important:** This script drops and recreates tables. Run it only against a disposable local database.

The included listings use original demo assets and dates. Create a new listing with a future closing date to test bidding.

### 2. Install Backend Dependencies

Create and activate a Python virtual environment, then install the dependencies from the repository root:

```bash
python -m pip install -r requirements.txt
```

### 3. Configure Environment Variables

Set the following environment variables in the shell used to start Flask.

| Variable | Description |
|---|---|
| `FLASK_SECRET_KEY` | Random secret key used to sign sessions and protect application state |
| `DATABASE_URL` | SQLAlchemy connection URL for the MySQL database |
| `GMAIL_SENDER_EMAIL` | Gmail address used to send password-reset emails |
| `GMAIL_APP_PASSWORD` | Current, dedicated Gmail app password for email functionality |
| `FRONTEND_URL` | Frontend origin for password-reset links; defaults to `http://localhost:3000` |

Generate a secure Flask secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Example database URL format:

```text
mysql+mysqlconnector://USER:PASSWORD@127.0.0.1:3306/aos
```

URL-encode special characters in database credentials. Never commit actual credentials to Git.

### 4. Start the Backend

From the `server/` directory:

```bash
python server.py
```

The Flask backend runs on:

`http://localhost:8000`

### 5. Start the Frontend

From the `client/` directory:

```bash
npm ci
npm start
```

Open:

`http://localhost:3000`

The React development server proxies API requests to Flask.

## Running Tests

### Backend Tests

Backend tests use an in-memory SQLite database and do not require a running MySQL instance or environment variables.

From the repository root:

```bash
cd server
python -m unittest discover -s tests
```

### Frontend Tests

From the repository root:

```bash
cd client
CI=true npm test
```

## Bidding Rules

- **Minimum Bid:** The first bid must meet or exceed the listing's starting price. Subsequent bids must exceed the current price.
- **Auction Availability:** Bids are accepted only while an auction is open and before its closing date.
- **Automatic Bidding:** Automatic bids require a positive increment and a maximum bid amount no lower than the opening bid.
- **Bid Competition:** The automatic bidding mechanism increases bids according to the configured increment until it exceeds competing bids or reaches the maximum.
- **Auction Closure:** A background task checks for ended auctions every 10 seconds.
- **Winner Notifications:** When an auction closes, the winning bidder is notified if the highest bid meets the reserve price or no reserve price is specified.

## Accounts & Password Resets

Customers can create accounts directly through the application.

For existing accounts with legacy passwords, customers should use the password-reset email functionality. Customer representatives can request an administrator-managed password reset.

### Administrator Setup

For a fresh installation or an existing administrator requiring a password update, generate a Werkzeug password hash locally:

```bash
python -c "from getpass import getpass; from werkzeug.security import generate_password_hash; print(generate_password_hash(getpass('New admin password: ')))"
```

Use a parameterized database query or MySQL Workbench's table editor to insert the administrator's username and generated password hash into the `admins` table, or update the `password_hash` field for an existing administrator.

Administrators can then create customer representative accounts through the application.

## Security Notes

- Passwords are stored using Werkzeug password hashing.
- Session-based authentication and role-based authorization protect user-specific and administrative endpoints.
- CSRF protection is applied to state-changing requests.
- Login and password-reset endpoints include rate limiting.
- Auction bids are validated to prevent invalid amounts, bids on closed auctions, and bids on nonexistent listings.
- Image uploads are restricted to valid JPEG, PNG, and WebP files, with limits of 10 MB and 16 megapixels.
- Sensitive credentials are configured through environment variables rather than hardcoded in the application.
- A Gmail app password previously exposed in the repository has been revoked. Historical commits may still contain the revoked credential.

**Note:** The local development environment uses HTTP on localhost. Keep database credentials, signing keys, and SMTP credentials outside version control.

---

**Project Type:** Academic Team Project — Rutgers University  
**Team Size:** 4  
**Repository:** Personal fork of the original team project
