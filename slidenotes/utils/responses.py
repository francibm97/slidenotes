from flask import jsonify

def jsonify_success(response):
    return jsonify({"success": True, "data": response})

def jsonify_error(error_code=400, error_description=None):
    return jsonify({"success": False,
                    "error": {
                        "code": error_code,
                        "description": error_description
                        }
                    })
