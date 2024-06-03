## PDP-scoring-API-testing (Python Developer Professional Course)

### Prerequisites

- Python 3.10+

### Description

This project provides an API for scoring and interest retrieval, utilizing Redis for caching and storage. The API includes methods for calculating scores based on user data and retrieving client interests from a key-value store. Unit tests are present.

### Features
- Online Scoring: Calculates a score based on user data such as phone, email, first name, last name, birthday, and gender.
- Client Interests: Retrieves client interests from a Redis store based on client IDs.
- Caching: Utilizes Redis for caching to improve performance.
- Error Handling: Handles Redis connection errors with retries.
