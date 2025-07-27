# StreetBazaar

StreetBazaar is a web application that connects vendors with suppliers, providing a platform for product catalog browsing, order management, and seamless communication between parties.

## Technologies Used

- Frontend:
  - React 19
  - Tailwind CSS
  - Axios
  - React Router DOM
  - CRACO for configuration overrides
- Backend:
  - Python (details in backend/requirements.txt)
  - FastAPI or Flask (assumed from typical Python backend, please adjust as needed)

## Project Structure

- `frontend/`: React frontend application
- `backend/`: Python backend server
- `frontend/public/index.html`: Main HTML entry point for the React app
- `frontend/src/`: React source code including components, styles, and utilities
- `backend/server.py`: Backend server entry point
- `backend/requirements.txt`: Python dependencies for backend

## Setup Instructions

### Prerequisites

- Node.js (v16 or higher recommended)
- Yarn or npm
- Python 3.8 or higher
- pip for Python package management

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   yarn install
   # or
   npm install
   ```

3. Start the development server:

   ```bash
   yarn start
   # or
   npm start
   ```

4. Open your browser and go to `http://localhost:3000` to view the app.

### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. (Optional but recommended) Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Unix or MacOS
   source venv/bin/activate
   ```

3. Install backend dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:

   ```bash
   python server.py
   ```

5. The backend server will typically run on `http://localhost:8000` (adjust if different).

## Environment Variables

- The frontend expects a `REACT_APP_BACKEND_URL` environment variable to point to the backend API URL.
- You can create a `.env` file in the `frontend` directory with:

  ```
  REACT_APP_BACKEND_URL=http://localhost:8000
  ```

## Usage

- Register as a vendor or supplier.
- Browse the product catalog.
- Vendors can add products to their cart and place orders.
- Suppliers can manage orders and update statuses.

## Build for Production

To create a production build of the frontend:

```bash
cd frontend
yarn build
# or
npm run build
```

The build output will be in the `frontend/build` directory.

## License

Specify your project license here.

---

If you have any questions or need assistance, please contact the project maintainer.
