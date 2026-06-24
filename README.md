# Weather CLI Application 🌦️

A premium command-line Python application that demonstrates Python's `requests` library usage to perform `GET` and `POST` calls, parse JSON payloads, and handle errors robustly.

---

## 🚀 How to Run

### 1. Install Dependencies
Ensure you have the required `requests` library installed. You can install it via:
```bash
pip install -r requirements.txt
```

### 2. Run the CLI

There are two modes to use the application:

#### A. Direct CLI Argument Mode
Pass the city name directly as a command-line argument:
```bash
python weather_cli.py "San Francisco"
```

#### B. Interactive Prompt Mode
Run the application with no arguments to start an interactive prompt loop:
```bash
python weather_cli.py
```
Type `exit` when you want to exit the application.

---

## 🛠️ Concepts Covered

### 1. Making `GET` Requests
- The application resolves a city name to latitude and longitude coordinates using **Open-Meteo's Geocoding API** via a `GET` request:
  ```python
  response = requests.get("https://geocoding-api.open-meteo.com/v1/search", params=params, timeout=10)
  ```
- It retrieves real-time weather metrics using **Open-Meteo's Weather Forecast API** with another `GET` request:
  ```python
  response = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=10)
  ```

### 2. Making `POST` Requests
- To demonstrate `POST` requests, the application provides an option to upload the weather search logs to a mock telemetry server (**httpbin.org**):
  ```python
  response = requests.post("https://httpbin.org/post", json=payload, timeout=10)
  ```
  This transfers a structured JSON payload in the request body.

### 3. Parsing JSON Responses
- Every response returned by these APIs is in JSON format. The application decodes the JSON payload into native Python dictionaries/lists using `.json()`:
  ```python
  data = response.json()
  current_temp = data.get("current", {}).get("temperature_2m")
  ```

### 4. Robust Error Handling
The application covers multiple networking and structural failure points:
- **DNS / Network issues**: Caught via `requests.exceptions.ConnectionError`.
- **Timeouts**: Solved by setting `timeout=10` on all requests and catching `requests.exceptions.Timeout`.
- **HTTP Failures (e.g., 404, 500)**: Automatically raised using `response.raise_for_status()` and caught via `requests.exceptions.HTTPError`.
- **Invalid Input (Geocoding Failure)**: Handles situations where the search term resolves to 0 results.
- **Malformed JSON**: Caught using `ValueError` when decoding `.json()`.
