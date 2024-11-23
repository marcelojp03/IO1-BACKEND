from flask import Flask, request, jsonify
from scipy.optimize import linprog
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


def simplex_callback(res):
    """Callback para mostrar las matrices y valores durante el proceso simplex."""
    print("Iteration:", res.nit)
    print("Current Tableau:")
    print("Variables:", res.x)
    print("Objective value:", res.fun)

@app.route('/api/simplex/solve', methods=['POST'])
def solve_linear_program():
    # Recibir los datos JSON del cliente
    data = request.get_json()

    # Extraer los datos necesarios del JSON
    num_variables = data.get("numVariables")
    num_restrictions = data.get("numRestrictions")
    objective = data.get("objective")
    objective_function = data.get("objectiveFunction")
    restrictions = data.get("restrictions")

    # Preparar el vector de coeficientes de la función objetivo
    # En linprog, la minimización es por defecto, por lo que si es "maximize", invertimos los signos
    if objective == "maximize":
        c = [-coef for coef in objective_function]
    else:
        c = objective_function

    # Preparar las matrices y vectores para las restricciones
    A = []
    b = []
    for restriction in restrictions:
        coefficients = restriction.get("coefficients")
        inequality = restriction.get("inequality")
        value = restriction.get("value")
        
        # Convertir las restricciones a formato compatible con linprog (<=)
        if inequality == "<=":
            A.append(coefficients)
            b.append(value)
        elif inequality == ">=":
            A.append([-coef for coef in coefficients])
            b.append(-value)
        elif inequality == "=":
            # Para restricciones de igualdad, se deben duplicar con ambos signos
            A.append(coefficients)
            b.append(value)
            A.append([-coef for coef in coefficients])
            b.append(-value)

    # Resolver el problema con scipy.optimize.linprog
    result = linprog(c, A_ub=A, b_ub=b, method='simplex')
    #result = linprog(c, A_ub=A, b_ub=b, method='simplex', callback=simplex_callback)

    # Preparar la respuesta con el resultado de la optimización
    if result.success:
        response = {
            "status": "success",
            "objective_value": -result.fun if objective == "maximize" else result.fun,
            "variables": result.x.tolist()
        }
    else:
        response = {
            "status": "failure",
            "message": result.message
        }

    # Retornar el resultado como JSON
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=9999)
