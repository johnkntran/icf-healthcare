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

## What Was Prioritized and Why
- On the backend, I prioritized security by encrypting the user's feedback data stored in the database (encryption at rest). The LLM checkpoints are also encrypted, and all PKs are UUIDs (non-incrementing IDs). I also wanted to demonstrate a realistic LLM workflow (hence Langgraph).
- On the frontend, I tried to make a point to keep modular component architecture and to implement the chart.

## What you would implement with 1 additional hour
- HTTPS for encryption in transit
- Streaming token responses via websocket/SSE, so UI isn't waiting 5+ seconds for LLM Insight creation -- not trivial.
- Build out other CRUD methods (Update, Delete, etc.)
- Real login/auth, not just a Username box.
- Leverage Postgres connection pooling
- More error handling: e.g. feedback assigned with non-existent user, etc.
- Postgres supports UUID data type natively, would probably use that instead of VARCHAR(36)
- Langgraph store and checkpoint `setup()` method just needs to happen once so we can move that logic somewhere else, not in the request cycle.
- Implement retry logic on graph nodes: Can add a retry policy when specifying a Node in Langgraph, it's basically a one liner. Just didn't have to time to test it.
- Cache similar queries to reduce API calls: If we convert queries to embeddings and store the queries and their results in a vector database, we can run a similarity search to see if we have any "similar" queries already submitted (e.g. some threshold of k-similarity score). Then we can return a cached result if we get a similarity hit. -- not trivial.

## Security/compliance considerations you'd raise with the team
- Althought there isn't any login functionality in this demo app (it's just a username text box), if we actually **did** store passwords in our system, it is very hard to do this securely. Even with encryption, etc.
- For demonstration, we passed `usernames` around in this demo. However in real life, we would want to pass around something like a JWT to securely identify the user (to create Feedbacks, Insights, etc.).

## Additional metrics recommended for tracking to measure customer success
- Follow up or reply from healthcare provider to make things right (for negative feedback), the ultimate customer success metric.
- Likes/Upvotes given for other posts, where appropriate (e.g. PII considerations).
- Number of feedbacks given per user, measure of engagement.
- Proportion of positive/negative sentiments.
- Running list of action items from Insights automatically added to Kanban/Jira/etc.

## Any assumptions made
- Didn't use an ORM in this implementation. Just used a raw AsyncPG cursor to hydrate Pydantic models. This accomplishes both speed and versatility. You'll find most existing Python ORMs (Django, SQLAlchemy, etc.) aren't built for async or generate awful, inefficient SQL under the hood. My recommendation would be to avoid an ORM if possible.

## Any data privacy concerns you'd flag
- Although we ask the LLM to scrub PII in its output, we're still actually sending that PII up to OpenAI/Anthropic in the first place, which is questionable. Should scrub that data internally before sending out externally.
- User should be notified how their feedback is used, where it's stored, when it's deleted, etc.

## Security considerations for production deployment
- Secrets should be kept securely in something like AWS Secret Store, HashiCorp Vault, etc.
- Make sure SSL certs are up to date and not expired when deploying to Prod.
- Ensure CORS is properly setup for Prod environment and only Frontend's domain is whitelisted to hit Backend's API.
- Ensure staff only have access to Prod DB/Deployment Secrets/etc. on a need-to-know basis.

## Compliance considerations (HIPAA, etc.) you'd want to discuss
- We'd want to do a risk audit and get the CISO involved to adhere to HIPAA policies.
- Role based access credentials (RBACs) for folks working on the app, and clear functions for devs, product managers, ops, etc. on what roles/access creds they need to do their job.
- Obfuscating PII by using randomized identifiers (e.g. referring to Customer 3 instead of by their name). Keeping mapping of randomized identifiers (which can be used more freely) and their actual customer mapping (only used securely) in separate databases with different RBACs so they're not co-located.

## How you'd approach data retention/deletion policies
- We'd discuss which data needs to be retained and for how long.
- We'd need to figure out a disposal method for securely wiping data from systems.
- Clear offboarding policies so folks who've moved on do not retain access to data, or copies of development data/code on their laptop, email, etc.
