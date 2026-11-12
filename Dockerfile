# 1. BASE IMAGE
FROM python:3.11-slim

# 2. WORKING DIRECTORY OF CONTAINER
WORKDIR /code

# 3. COPY REQUIREMENTS FILE
COPY req.txt .

RUN pip install --no-cache-dir -r req.txt

# 4. COPY APP FOLDER
COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]