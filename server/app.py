import random

from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = "super-secret-api-token"

# Mock data for demonstration replace it with actual data retrieval logic
all_events = [{"id": i, "event": f"Event {i}"} for i in range(1, 101)]


# Mock data for demonstration replace it with actual data retrieval logic
def get_mocked_events(start_id: int, stop_id: int):
    return [{"id": i, "event": f"Event {i}"} for i in range(start_id, stop_id)]


def _should_fail_with_server_error() -> bool:
    if random.random() < 0.1:
        return True
    return False


# Global variable to store the special event
special_event = None


@app.route("/events", methods=["POST"])
def store_special_event():
    global special_event

    # API key validation
    api_key = request.headers.get("API-Key")
    if api_key != API_KEY:
        return "Unauthorized", 401

    # Parse the raw text payload
    event_data = request.data.decode("utf-8").strip()
    if not event_data:
        return "Invalid request payload", 400
    else:
        special_event = event_data
        return "Special event stored", 201


@app.route("/events", methods=["GET"])
def events():
    global special_event

    # API key validation
    api_key = request.headers.get("API-Key")
    if api_key != API_KEY:
        return "Unauthorized", 401

    if _should_fail_with_server_error():
        return "Internal Server Error", 500

    # Get pagination parameters from the query string
    page = request.args.get("page", 0, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    # Calculate start and end indices for the items on the current page
    start_id, stop_id = page * per_page, (page + 1) * per_page
    paginated_events = []
    if special_event:
        paginated_events.append({"id": start_id, "event": special_event})
        start_id += 1
        special_event = None
    paginated_events += get_mocked_events(start_id, stop_id)

    total_events = len(paginated_events)
    total_pages = (total_events + per_page - 1) // per_page

    return (
        jsonify(
            {
                "events": paginated_events,
                "page": page,
                "per_page": per_page,
                "total_events": total_events,
                "total_pages": total_pages,
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
