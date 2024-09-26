from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# In-memory list to store items
items = []


@app.route('/')
def index():
    return render_template('trial.html', items=items)


@app.route('/add', methods=['POST'])
def add_item():
    new_item = request.json.get('item')  # Fetch the item from the JSON request
    if new_item:
        items.append(new_item)
        return jsonify({'success': True, 'item': new_item})  # Return the new item as JSON
    return jsonify({'success': False}), 400  # Return error if no item found


if __name__ == '__main__':
    app.run(debug=True)
