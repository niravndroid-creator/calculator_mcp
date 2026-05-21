import azure.functions as func
import json
import sys
import os
from pathlib import Path

# Add parent directory to path to import server module
sys.path.insert(0, str(Path(__file__).parent.parent))

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function wrapper for Calculator MCP Server
    
    Supported operations:
    - POST /api/calculator/add: {"a": 5, "b": 3}
    - POST /api/calculator/subtract: {"a": 10, "b": 3}
    - POST /api/calculator/multiply: {"a": 4, "b": 5}
    - POST /api/calculator/divide: {"a": 20, "b": 4}
    """
    try:
        # Get operation from route parameter
        operation = req.route_params.get('operation')
        
        # Parse request body
        try:
            req_body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Get operands
        a = req_body.get('a')
        b = req_body.get('b')
        
        if a is None or b is None:
            return func.HttpResponse(
                json.dumps({"error": "Missing required parameters 'a' and 'b'"}),
                mimetype="application/json",
                status_code=400
            )
        
        # Get data type configuration
        from server import SUPPORTED_TYPES, validate_number
        
        # Validate numbers based on configuration
        try:
            a = validate_number(float(a))
            b = validate_number(float(b))
        except ValueError as e:
            return func.HttpResponse(
                json.dumps({"error": str(e)}),
                mimetype="application/json",
                status_code=400
            )
        
        # Perform operation
        result = None
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return func.HttpResponse(
                    json.dumps({"error": "Division by zero is not allowed"}),
                    mimetype="application/json",
                    status_code=400
                )
            result = a / b
        else:
            return func.HttpResponse(
                json.dumps({
                    "error": f"Unknown operation: {operation}",
                    "supported_operations": ["add", "subtract", "multiply", "divide"]
                }),
                mimetype="application/json",
                status_code=400
            )
        
        # Return result
        return func.HttpResponse(
            json.dumps({
                "operation": operation,
                "a": a,
                "b": b,
                "result": result,
                "data_types_config": SUPPORTED_TYPES
            }),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": f"Internal server error: {str(e)}"}),
            mimetype="application/json",
            status_code=500
        )
