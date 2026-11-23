# JustBidIt

JustBidIt is a four-person course project built with React, Flask, and MySQL. Users can browse and list auctions, place manual or automatic bids, review bid history, and receive auction notifications. The project also includes customer support and administrator workflows for account management and sales reporting.

[Watch the original course-project demo](https://youtu.be/2yrfb0eTMiA)

## Project contributions

Zeba Afreen contributed to the auction browsing and product detail interfaces, bidding and bid history, and bid notifications. This repository is a fork of the [original team project](https://github.com/shashwatijha/JustBidIt).

## Local setup

1. Use a fresh MySQL 8 development database. Run `createTable.sql` to create the `aos` schema and load demo listings. The script drops and recreates tables, so use a disposable local instance. The listings use the original demo assets and dates. Create a new listing with a future closing date to try bidding.
2. Create a Python virtual environment and install the backend with `python -m pip install -r requirements.txt`.
3. Export the following environment variables in the shell that starts Flask.

   | Variable | Value |
   | --- | --- |
   | `FLASK_SECRET_KEY` | A fresh random signing key. Generate one locally with `python -c "import secrets; print(secrets.token_hex(32))"`. |
   | `DATABASE_URL` | A SQLAlchemy URL such as `mysql+mysqlconnector://USER:PASSWORD@127.0.0.1:3306/aos`. URL-encode special characters in credentials. |
   | `GMAIL_SENDER_EMAIL`, `GMAIL_APP_PASSWORD` | Required for email-based password reset. Use a dedicated, current app password. |
   | `FRONTEND_URL` | Password reset link origin. Defaults to `http://localhost:3000`. |

4. From `server/`, run `python server.py`. Flask listens on port 8000.
5. From `client/`, run `npm ci` and `npm start`, then open `http://localhost:3000`. The React development server proxies API requests to Flask.

## Accounts and password resets

Sign up through the app for a customer account. Customers with legacy passwords should use the password reset email. Customer representatives can request an administrator-managed reset. For a fresh installation or a legacy administrator, a local database operator can use the following from the Python environment to produce a Werkzeug hash from a hidden prompt:

```sh
python -c "from getpass import getpass; from werkzeug.security import generate_password_hash; print(generate_password_hash(getpass('New admin password: ')))"
```

Use a parameterized database query or MySQL Workbench's table editor to insert the administrator's username and the generated hash into `admins`, or update `password_hash` for the existing administrator. Administrators can then provision customer representatives through the application.

Listing uploads accept JPEG, PNG, and WebP images up to 10 MB and 16 megapixels.

The development setup uses HTTP on localhost. Keep signing keys, database credentials and SMTP credentials outside Git. Revoke any Gmail app password previously committed to the repository.
