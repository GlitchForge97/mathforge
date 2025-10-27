from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import random
from datetime import datetime
from fractions import Fraction
from functools import wraps

app = Flask(__name__)
CORS(app)

# In-memory storage for query history
query_history = []

# Utility decorator for error handling
def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({"error": "Invalid input", "message": str(e)}), 400
        except ZeroDivisionError:
            return jsonify({"error": "Division by zero"}), 400
        except Exception as e:
            return jsonify({"error": "Internal server error", "message": str(e)}), 500
    return decorated_function

# Logging function
def log_query(endpoint, data, result):
    query_history.append({
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "input": data,
        "output": result
    })
    if len(query_history) > 100:  # Keep only last 100 queries
        query_history.pop(0)

# ==================== ROOT ENDPOINT ====================
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "MathForge API",
        "version": "1.0.0",
        "description": "A comprehensive mathematical REST API",
        "endpoints": {
            "arithmetic": "/api/arithmetic",
            "algebra": {
                "linear": "/api/algebra/linear",
                "quadratic": "/api/algebra/quadratic"
            },
            "geometry": {
                "circle": "/api/geometry/circle",
                "rectangle": "/api/geometry/rectangle",
                "triangle": "/api/geometry/triangle",
                "cube": "/api/geometry/cube",
                "sphere": "/api/geometry/sphere"
            },
            "statistics": "/api/statistics",
            "quiz": "/api/quiz",
            "history": "/api/history"
        }
    })

# ==================== ARITHMETIC MODULE ====================
@app.route('/api/arithmetic', methods=['POST'])
@handle_errors
def arithmetic():
    data = request.get_json()
    operation = data.get('operation')
    a = data.get('a')
    b = data.get('b')
    
    if operation is None or a is None or b is None:
        return jsonify({"error": "Missing required fields: operation, a, b"}), 400
    
    # Handle fractions
    use_fractions = data.get('fractions', False)
    if use_fractions:
        a = Fraction(a)
        b = Fraction(b)
    else:
        a = float(a)
        b = float(b)
    
    operations = {
        'add': lambda x, y: x + y,
        'subtract': lambda x, y: x - y,
        'multiply': lambda x, y: x * y,
        'divide': lambda x, y: x / y if y != 0 else None
    }
    
    if operation not in operations:
        return jsonify({"error": f"Invalid operation. Choose from: {list(operations.keys())}"}), 400
    
    result = operations[operation](a, b)
    
    if result is None:
        return jsonify({"error": "Division by zero"}), 400
    
    response = {
        "operation": operation,
        "operands": {"a": str(a), "b": str(b)},
        "result": str(result) if use_fractions else float(result),
        "timestamp": datetime.now().isoformat()
    }
    
    log_query("/api/arithmetic", data, response)
    return jsonify(response)

# ==================== ALGEBRA MODULE ====================
@app.route('/api/algebra/linear', methods=['POST'])
@handle_errors
def solve_linear():
    """Solve linear equation: ax + b = 0"""
    data = request.get_json()
    a = float(data.get('a', 0))
    b = float(data.get('b', 0))
    show_steps = data.get('steps', False)
    
    if a == 0:
        return jsonify({"error": "Coefficient 'a' cannot be zero"}), 400
    
    x = -b / a
    
    response = {
        "equation": f"{a}x + {b} = 0",
        "solution": {"x": round(x, 6)},
        "timestamp": datetime.now().isoformat()
    }
    
    if show_steps:
        response["steps"] = [
            f"Given: {a}x + {b} = 0",
            f"Step 1: {a}x = -{b}",
            f"Step 2: x = -{b}/{a}",
            f"Solution: x = {round(x, 6)}"
        ]
    
    log_query("/api/algebra/linear", data, response)
    return jsonify(response)

@app.route('/api/algebra/quadratic', methods=['POST'])
@handle_errors
def solve_quadratic():
    """Solve quadratic equation: ax² + bx + c = 0"""
    data = request.get_json()
    a = float(data.get('a', 0))
    b = float(data.get('b', 0))
    c = float(data.get('c', 0))
    show_steps = data.get('steps', False)
    
    if a == 0:
        return jsonify({"error": "Coefficient 'a' cannot be zero"}), 400
    
    discriminant = b**2 - 4*a*c
    
    response = {
        "equation": f"{a}x² + {b}x + {c} = 0",
        "discriminant": round(discriminant, 6),
        "timestamp": datetime.now().isoformat()
    }
    
    if discriminant > 0:
        x1 = (-b + math.sqrt(discriminant)) / (2*a)
        x2 = (-b - math.sqrt(discriminant)) / (2*a)
        response["solutions"] = {
            "type": "two_real",
            "x1": round(x1, 6),
            "x2": round(x2, 6)
        }
        if show_steps:
            response["steps"] = [
                f"Given: {a}x² + {b}x + {c} = 0",
                f"Discriminant: Δ = b² - 4ac = {round(discriminant, 6)}",
                f"x = (-b ± √Δ) / 2a",
                f"x₁ = ({-b} + √{discriminant}) / {2*a} = {round(x1, 6)}",
                f"x₂ = ({-b} - √{discriminant}) / {2*a} = {round(x2, 6)}"
            ]
    elif discriminant == 0:
        x = -b / (2*a)
        response["solutions"] = {
            "type": "one_real",
            "x": round(x, 6)
        }
        if show_steps:
            response["steps"] = [
                f"Given: {a}x² + {b}x + {c} = 0",
                f"Discriminant: Δ = 0 (one solution)",
                f"x = -b / 2a = {-b} / {2*a} = {round(x, 6)}"
            ]
    else:
        real_part = -b / (2*a)
        imag_part = math.sqrt(-discriminant) / (2*a)
        response["solutions"] = {
            "type": "complex",
            "x1": f"{round(real_part, 6)} + {round(imag_part, 6)}i",
            "x2": f"{round(real_part, 6)} - {round(imag_part, 6)}i"
        }
        if show_steps:
            response["steps"] = [
                f"Given: {a}x² + {b}x + {c} = 0",
                f"Discriminant: Δ = {round(discriminant, 6)} (complex roots)",
                f"x = (-b ± i√|Δ|) / 2a",
                f"x₁ = {round(real_part, 6)} + {round(imag_part, 6)}i",
                f"x₂ = {round(real_part, 6)} - {round(imag_part, 6)}i"
            ]
    
    log_query("/api/algebra/quadratic", data, response)
    return jsonify(response)

# ==================== GEOMETRY MODULE ====================
@app.route('/api/geometry/circle', methods=['POST'])
@handle_errors
def circle():
    data = request.get_json()
    radius = float(data.get('radius', 0))
    
    if radius <= 0:
        return jsonify({"error": "Radius must be positive"}), 400
    
    response = {
        "shape": "circle",
        "radius": radius,
        "area": round(math.pi * radius**2, 6),
        "circumference": round(2 * math.pi * radius, 6),
        "diameter": round(2 * radius, 6),
        "timestamp": datetime.now().isoformat()
    }
    
    log_query("/api/geometry/circle", data, response)
    return jsonify(response)

@app.route('/api/geometry/rectangle', methods=['POST'])
@handle_errors
def rectangle():
    data = request.get_json()
    length = float(data.get('length', 0))
    width = float(data.get('width', 0))
    
    if length <= 0 or width <= 0:
        return jsonify({"error": "Dimensions must be positive"}), 400
    
    response = {
        "shape": "rectangle",
        "length": length,
        "width": width,
        "area": round(length * width, 6),
        "perimeter": round(2 * (length + width), 6),
        "diagonal": round(math.sqrt(length**2 + width**2), 6),
        "timestamp": datetime.now().isoformat()
    }
    
    log_query("/api/geometry/rectangle", data, response)
    return jsonify(response)

@app.route('/api/geometry/triangle', methods=['POST'])
@handle_errors
def triangle():
    data = request.get_json()
    base = float(data.get('base', 0))
    height = float(data.get('height', 0))
    side_a = float(data.get('side_a', base))
    side_b = float(data.get('side_b', base))
    
    if base <= 0 or height <= 0:
        return jsonify({"error": "Base and height must be positive"}), 400
    
    response = {
        "shape": "triangle",
        "base": base,
        "height": height,
        "area": round(0.5 * base * height, 6),
        "perimeter": round(base + side_a + side_b, 6),
        "timestamp": datetime.now().isoformat()
    }
    
    log_query("/api/geometry/triangle", data, response)
    return jsonify(response)

@app.route('/api/geometry/cube', methods=['POST'])
@handle_errors
def cube():
    data = request.get_json()
    side = float(data.get('side', 0))
    
    if side <= 0:
        return jsonify({"error": "Side length must be positive"}), 400
    
    response = {
        "shape": "cube",
        "side": side,
        "volume": round(side**3, 6),
        "surface_area": round(6 * side**2, 6),
        "space_diagonal": round(side * math.sqrt(3), 6),
        "timestamp": datetime.now().isoformat()
    }
    
    log_query("/api/geometry/cube", data, response)
    return jsonify(response)

@app.route('/api/geometry/sphere', methods=['POST'])
@handle_errors
def sphere():
    data = request.get_json()
    radius = float(data.get('radius', 0))
    
    if radius <= 0:
        return jsonify({"error": "Radius must be positive"}), 400
    
    response = {
        "shape": "sphere",
        "radius": radius,
        "volume": round((4/3) * math.pi * radius**3, 6),
        "surface_area": round(4 * math.pi * radius**2, 6),
        "timestamp": datetime.now().isoformat()
    }
    
    log_query("/api/geometry/sphere", data, response)
    return jsonify(response)

# ==================== STATISTICS MODULE ====================
@app.route('/api/statistics', methods=['POST'])
@handle_errors
def statistics():
    data = request.get_json()
    dataset = data.get('data', [])
    
    if not dataset or not isinstance(dataset, list):
        return jsonify({"error": "Invalid dataset. Provide an array of numbers."}), 400
    
    dataset = [float(x) for x in dataset]
    n = len(dataset)
    
    # Mean
    mean_val = sum(dataset) / n
    
    # Median
    sorted_data = sorted(dataset)
    if n % 2 == 0:
        median_val = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
    else:
        median_val = sorted_data[n//2]
    
    # Mode
    from collections import Counter
    freq = Counter(dataset)
    max_freq = max(freq.values())
    mode_val = [k for k, v in freq.items() if v == max_freq]
    
    # Variance and Standard Deviation
    variance_val = sum((x - mean_val)**2 for x in dataset) / n
    std_dev_val = math.sqrt(variance_val)
    
    # Range
    range_val = max(dataset) - min(dataset)
    
    response = {
        "dataset_size": n,
        "mean": round(mean_val, 6),
        "median": round(median_val, 6),
        "mode": mode_val if len(mode_val) < n else "No mode",
        "variance": round(variance_val, 6),
        "standard_deviation": round(std_dev_val, 6),
        "range": round(range_val, 6),
        "min": min(dataset),
        "max": max(dataset),
        "timestamp": datetime.now().isoformat()
    }
    
    log_query("/api/statistics", data, response)
    return jsonify(response)

# ==================== QUIZ MODULE ====================
@app.route('/api/quiz', methods=['GET'])
@handle_errors
def generate_quiz():
    """Generate a random math quiz question"""
    quiz_types = ['arithmetic', 'algebra', 'geometry']
    quiz_type = request.args.get('type', random.choice(quiz_types))
    
    if quiz_type == 'arithmetic':
        a = random.randint(1, 100)
        b = random.randint(1, 100)
        op = random.choice(['add', 'subtract', 'multiply'])
        
        operations = {
            'add': ('+', a + b),
            'subtract': ('-', a - b),
            'multiply': ('×', a * b)
        }
        
        symbol, answer = operations[op]
        
        return jsonify({
            "type": "arithmetic",
            "question": f"What is {a} {symbol} {b}?",
            "answer_id": f"{quiz_type}_{a}_{b}_{op}",
            "difficulty": "easy"
        })
    
    elif quiz_type == 'algebra':
        a = random.randint(1, 10)
        b = random.randint(-20, 20)
        answer = -b / a
        
        return jsonify({
            "type": "linear_equation",
            "question": f"Solve for x: {a}x + {b} = 0",
            "answer_id": f"algebra_{a}_{b}",
            "difficulty": "medium"
        })
    
    elif quiz_type == 'geometry':
        radius = random.randint(1, 20)
        answer = round(math.pi * radius**2, 2)
        
        return jsonify({
            "type": "geometry",
            "question": f"What is the area of a circle with radius {radius}?",
            "answer_id": f"circle_{radius}",
            "difficulty": "medium",
            "unit": "square units"
        })

@app.route('/api/quiz/validate', methods=['POST'])
@handle_errors
def validate_quiz():
    """Validate quiz answer"""
    data = request.get_json()
    answer_id = data.get('answer_id', '')
    user_answer = float(data.get('answer', 0))
    
    parts = answer_id.split('_')
    
    if parts[0] == 'arithmetic':
        a, b, op = int(parts[1]), int(parts[2]), parts[3]
        operations = {
            'add': a + b,
            'subtract': a - b,
            'multiply': a * b
        }
        correct_answer = operations[op]
        
    elif parts[0] == 'algebra':
        a, b = int(parts[1]), int(parts[2])
        correct_answer = -b / a
        
    elif parts[0] == 'circle':
        radius = int(parts[1])
        correct_answer = round(math.pi * radius**2, 2)
    else:
        return jsonify({"error": "Invalid answer_id"}), 400
    
    is_correct = abs(user_answer - correct_answer) < 0.01
    
    return jsonify({
        "correct": is_correct,
        "user_answer": user_answer,
        "correct_answer": round(correct_answer, 6),
        "message": "Correct! Well done!" if is_correct else "Incorrect. Try again!"
    })

# ==================== HISTORY MODULE ====================
@app.route('/api/history', methods=['GET'])
def get_history():
    """Retrieve query history"""
    limit = int(request.args.get('limit', 20))
    return jsonify({
        "total_queries": len(query_history),
        "history": query_history[-limit:]
    })

@app.route('/api/history/clear', methods=['DELETE'])
def clear_history():
    """Clear query history"""
    global query_history
    count = len(query_history)
    query_history = []
    return jsonify({
        "message": f"Cleared {count} queries from history",
        "timestamp": datetime.now().isoformat()
    })

# ==================== SERVER ====================
if __name__ == '__main__':
    print("🔥 MathForge API is running!")
    print("📚 Documentation available at http://localhost:5000/")
    app.run(debug=True, host='0.0.0.0', port=5000)
