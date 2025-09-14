# ICF Healthcare Insights Dashboard

This is a backend (FastAPI, Langchain/Langgraph) and frontend (Vue.js) app demonstrating a dashboard for analyzing patient feedback on an EHR using AI.

## Setup Instructions

This project uses Docker to run all dependencies -- make sure you have Docker installed on your system.

First, copy the `.env.example` file and rename it as `.env`. Inside the `.env` file, update the placeholders like "ANTHROPIC_API_KEY=your_anthropic_api_key_here" to your actual credentials.

Run the following command to start up the applications:

```sh
docker-compose up --build --abort-on-container-exit --remove-orphans
```

The frontend application is served on http://127.0.0.1:3000/.

You can also visit a backend OpenAPI UI at http://127.0.0.1:8000/docs to test API endpoints.

In the [backend/data](./backend/data) folder, there are some examples of feedback text you can submit to the app.

To shutdown the application and (optionally) remove all data you created, run: 
```sh
docker-compose down --remove-orphans && docker volume rm icf-database
```