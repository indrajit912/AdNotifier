# AdNotifier

AdNotifier is a web application developed by [Indrajit Ghosh](https://indrajitghosh.onrender.com), a SRF at SMU, Indian Statistical Institute Bangalore. This application allows users to track the status of job or exam advertisements on specific websites. Users can register, log in, and add advertisement numbers along with website URLs to receive email notifications whenever there are updates related to the specified numbers.

## Getting Started

To use AdNotifier, follow these steps:

1. Register with a valid email address.
2. Log into your account.
3. Start adding advertisement numbers and website URLs to your account.

### Usage Scenarios

1. **Job/Exam Advertisement Tracking**: Users can track the status of their job or exam advertisement numbers on specific websites and receive email notifications for any updates.
2. **Centralized Dashboard**: The user dashboard serves as a central hub for all application advertisements, allowing users to add descriptions to each advertisement.
3. **Effortless Updates**: Users never miss any new updates regarding their job applications, making their lives easier.

## Features

1. **User-Friendly**: Easy to use and reliable.
2. **Secure Password Handling**: User passwords are hashed and securely stored, ensuring privacy.
3. **Email Notifications**: Users receive email notifications for updates related to their specified advertisement numbers.
4. **Telegram Notifications**: Additionally, users can also receive notifications on Telegram by adding their Telegram `user ID` to their account. Stay informed through multiple channels!

## Future Features (Coming Soon)

- **Connect with Friends**: Share unique advertisements with friends and connect seamlessly.
- **Exchange Messages**: Communicate with friends within the application.

## Backend Technology

AdNotifier is built using the Python Flask web framework, providing a robust backend for handling user registration, login, and advertisement tracking. The application stores data in a MySQL database, ensuring data persistence and reliability.

## Frontend Styling

AdNotifier uses Bootstrap for the frontend, along with a custom CSS stylesheet (`style.css`) and a base HTML file (`base.html`). The homepage (`index.html`) has been modified for a more visually appealing design.

## Developer Information

- Developer: Indrajit Ghosh
- Website: [https://indrajitghosh.onrender.com](https://indrajitghosh.onrender.com)
- GitHub: [indrajit912](https://github.com/indrajit912)

## Local Deployment Instructions

To run the application locally, follow these steps:

1. Clone the repository using the following command:
    ```bash
    git clone https://github.com/indrajit912/AdNotifier.git
    ```

2. Navigate to the `AdNotifier` directory:
    ```bash
    cd AdNotifier
    ```

3. Set up a virtual environment and install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Create the database by entering the Flask shell:
    ```bash
    flask shell
    from app import db
    db.create_all()
    ```

5. Create an admin user:
    ```bash
    python manage.py create_admin
    ```

## How to Contribute

If you would like to contribute to AdNotifier, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m 'Add feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
