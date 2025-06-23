# 📝 CMS — A Developer-Centric Publishing Tool

A lightweight, modern CMS built with Django 5 and Vite, inspired by [dev.to](https://dev.to). This tool is designed for **developers and internal teams** to draft, share, and collaborate on technical ideas, blog posts, or team discussions — before they go public.

## 🚀 Features

- ✍️ **Markdown-based editor** with [Toast UI Editor](https://ui.toast.com/tui-editor)
- 🏷️ **Taggable content** using `django-taggit`
- 🔒 **User authentication**
- 🧠 **Draft-first publishing flow** — write before you're ready to share
- 🐛 Debug support via `django-debug-toolbar`
- 🖼️ Media uploads (images, avatars) via `Pillow`
- 📧 Email notifications with `django-anymail`
- 🧵 Team-focused UX — perfect for internal dev communications

## 🧰 Tech Stack

### Backend
- **Python 3.10**
- **Django 5.1.7**
- **MySQL** as the primary database
- **Markdown** rendering
- **Django Debug Toolbar** for dev insights
- **Environment config** via `python-decouple`

### Frontend
- **Vite 6** for fast bundling
- **Tailwind CSS 4** for utility-first styling
- **Alpine.js** for interactivity
- **Toast UI Editor** for rich markdown editing
- **Flatpickr** for date/time inputs
- **JS-Cookie** for client-side state handling

## 🛠️ Installation

### 1. Clone the Repo
```bash
git clone https://github.com/andrew-saeed/cms.git
cd cms
```

### 2. Dev - Backend Setup (Django)
```bash
# Install pipenv if not already installed
pip install pipenv

# Install dependencies and auto-create virtual environment
pipenv install

# Create a `.env` file with your settings
cp .env.example .env

# Activate the pipenv shell
pipenv shell

# Set up the database
python manage.py migrate

# Run the dev server
python manage.py runserver
```

### 3. Dev - Frontend Setup (Vite)
```bash
cd theme/vite
npm install
npm run dev  
```

## 📄 License
This project is licensed under the MIT License.

## 🤝 Contribution
Feel free to fork the repository and submit pull requests.

## 📬 Contact
For any inquiries, reach out to andrewsaeed95@gmail.com