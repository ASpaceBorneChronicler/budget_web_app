from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Sample data (in-memory for simplicity)
items = []


@app.route('/')
def index():
    return render_template('trial2.html', items=items)


@app.route('/add_item', methods=['POST'])
def add_item():
    # Fetch the new item from the JSON request
    new_item = request.json.get('item')
    if new_item:
        items.append(new_item)
        # Return the updated items list as JSON
        return jsonify(items=items)
    return jsonify({'error': 'No item provided'}), 400


if __name__ == '__main__':
    app.run(debug=True)
