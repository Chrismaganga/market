# Local Marketplace App

A local-first marketplace application similar to Gumtree or Facebook Marketplace, built with Django REST Framework backend and React Native frontend.

## Features

### Core Features

- **User Authentication**: Secure user registration, login, and profile management
- **Categories**: Organized product/service categorization
- **Geo-based Search**: Location-based listing discovery
- **Listings**: Create, edit, and manage marketplace listings
- **Search & Filters**: Advanced search with multiple filter options

### Advanced Features

- **Payments**: Stripe integration for secure transactions
- **Chat System**: Real-time messaging between users
- **Moderation Panel**: Admin tools for content moderation
- **Image Upload**: Support for multiple images per listing
- **Favorites**: Save and manage favorite listings
- **Notifications**: Real-time notifications for messages and updates

## Tech Stack

### Backend

- **Django 4.2+**: Web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Database
- **Redis**: Caching and session storage
- **Celery**: Background task processing
- **Stripe**: Payment processing
- **Channels**: WebSocket support for real-time features

### Frontend

- **React Native**: Cross-platform mobile app
- **Expo**: Development platform
- **Redux Toolkit**: State management
- **React Navigation**: Navigation
- **Socket.io**: Real-time communication

## Project Structure

```
market/
├── backend/                 # Django REST API
│   ├── marketplace/         # Main Django project
│   ├── apps/               # Django applications
│   │   ├── users/          # User authentication & profiles
│   │   ├── listings/       # Marketplace listings
│   │   ├── categories/     # Product categories
│   │   ├── chat/           # Messaging system
│   │   ├── payments/       # Payment processing
│   │   └── moderation/     # Admin moderation tools
│   ├── requirements.txt    # Python dependencies
│   └── manage.py
├── frontend/               # React Native app
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── screens/        # App screens
│   │   ├── navigation/     # Navigation setup
│   │   ├── store/          # Redux store
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   ├── package.json
│   └── app.json
├── docs/                   # Documentation
└── docker-compose.yml      # Development environment
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL
- Redis
- Expo CLI

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npx expo start
```

### Environment Variables

Create `.env` files in both backend and frontend directories with:

- Database credentials
- Stripe API keys
- Redis connection
- JWT secret keys

## API Documentation

The API documentation is available at `/api/docs/` when the backend is running.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
