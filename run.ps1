Write-Host "🚀 Démarrage Django"
cd backend
venv\Scripts\activate
Start-Process powershell "python manage.py runserver 8000"

Write-Host "🚀 Démarrage React"
cd ../frontend
Start-Process powershell "npm start"