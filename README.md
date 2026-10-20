# Just Bid It — Online Auction System

**Just Bid It** is a full-stack online auction platform inspired by marketplaces such as eBay. It enables users to list products, participate in auctions, manage bids, and receive notifications about auction activity.

The platform also includes customer support and administrative tools for managing users, auctions, and sales information.

**[Watch the Project Demo](https://youtu.be/2yrfb0eTMiA)**

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, JavaScript, CSS, React Bootstrap |
| Backend | Python, Flask, REST APIs |
| Database | MySQL, SQLAlchemy |
| Supporting Libraries | React Router, React Toastify, Recharts |
| Development Tools | Git, GitHub, MySQL Workbench |

## Key Features

### User Accounts and Authentication

- User registration and login
- Password hashing and authentication
- Password recovery and reset functionality
- Account-related forms and validation

### Product Listings and Auctions

- Create auction listings with product information and images
- Browse available products
- View detailed product information
- Track auction prices and closing dates
- Manage auction listings

### Manual and Automatic Bidding

- Submit manual bids on auction items
- Configure automatic bidding with maximum bid limits and increments
- Update auction prices based on competing bids
- Maintain bidding history
- Determine auction winners according to bidding results and reserve-price conditions

### Notifications and Alerts

- Notify users when they are outbid
- Alert users when automatic bidding limits are exceeded
- Generate notifications for auction winners
- Display and clear user notifications

### Customer Support and Administration

- Customer support interfaces for managing user requests
- Auction and bid management tools
- Administrative dashboards
- Sales reporting and visualization

## Application Architecture

Just Bid It uses a client-server architecture.

**React frontend**

Provides the user interface for authentication, product listings, bidding, notifications, and administrative workflows.

**Flask backend**

Exposes API endpoints for user accounts, products, bids, notifications, and support features.

**MySQL database**

Stores application data, including users, products, bids, and notifications.

The frontend communicates with the Flask backend through HTTP requests.

## Repository Structure

```text
JustBidIt/
├── client/
│   ├── public/
│   └── src/
│       ├── styles/
│       └── views/
├── server/
│   ├── admin.py
│   ├── auth.py
│   ├── bids.py
│   ├── notifications.py
│   ├── products.py
│   ├── server.py
│   ├── smart_login.py
│   ├── support.py
│   └── uploads/
├── createTable.sql
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

Install the following tools:

- Python 3
- Node.js and npm
- MySQL Server
- MySQL Workbench (recommended for database setup)

### 1. Clone the Repository

```bash
git clone https://github.com/ZebaAfreen02/JustBidIt.git
cd JustBidIt
```

### 2. Configure the Database

Start your local MySQL server.

Open MySQL Workbench and execute the included [`createTable.sql`](createTable.sql) script to create the `aos` database and its tables.

The database connection is currently configured in `server/server.py`.

Update the connection settings to match your local MySQL installation before starting the backend.

### 3. Create a Python Virtual Environment

From the repository root:

```bash
python -m venv venv
```

Activate it.

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
source venv/bin/activate
```

### 4. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

The backend also imports packages such as Flask-SQLAlchemy, Flask-CORS, APScheduler, and a MySQL database driver. These may require additional installation because the current root requirements file does not list every imported dependency.

### 5. Start the Flask Backend

```bash
cd server
python server.py
```

The backend is configured to use port `8000`.

### 6. Start the React Frontend

Open a second terminal in the repository root.

```bash
cd client
npm install
npm start
```

The React development server normally opens at:

`http://localhost:3000`

The frontend's development proxy is configured to forward API requests to:

`http://127.0.0.1:8000`

### 7. Explore the Application

After both servers are running and the database is configured, use the application to explore product listings, create auctions, place bids, and access account features.

**Note:** The project is an academic implementation. Local execution may require additional configuration of dependencies, database credentials, and email functionality. These setup instructions have been reviewed against the source files but have not been tested in a clean environment.

## Security and Configuration

The repository contains development-oriented configuration, including database connection details and email settings.

Before deploying or using this application outside a local development environment:

- Replace hardcoded credentials with environment variables.
- Revoke any previously exposed application passwords.
- Configure database access securely.
- Review authentication, authorization, and input validation.
- Avoid committing private configuration files or credentials.

## Project Demo

A recorded walkthrough of the application is available here:

**[Just Bid It — Demo Video](https://youtu.be/2yrfb0eTMiA)**

## Project Context

Just Bid It was developed as a collaborative academic software project, combining frontend development, backend APIs, relational database design, and auction-management functionality.

The repository is a fork of the original team project:

[shashwatijha/JustBidIt](https://github.com/shashwatijha/JustBidIt)

## Future Improvements

Potential improvements include:

- More comprehensive automated testing
- Stronger deployment and configuration management
- Improved handling of concurrent bids
- Expanded filtering and search capabilities
- More robust notification delivery
- Additional security and accessibility testing
