from flask import Flask, render_template, request, session, jsonify, redirect, url_for

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura_2024"

# Lista fija de usuarios registrados
USUARIOS = {
    "admin":    "admin123",
    "juan":     "juan456",
    "maria":    "maria789",
    "carlos":   "carlos000",
    "franquito": "54321"
}

# ─────────────────────────────────────────────────────────────
# Página de login (GET muestra el formulario)
# ─────────────────────────────────────────────────────────────
@app.route("/")
@app.route("/login")
def login():
    if "usuario" in session:
        return redirect(url_for("ventas"))
    return render_template("login.html")


# ─────────────────────────────────────────────────────────────
# Autenticación vía AJAX (POST /autenticar)
# ─────────────────────────────────────────────────────────────
@app.route("/autenticar", methods=["POST"])
def autenticar():
    datos = request.get_json()
    usuario = datos.get("usuario", "").strip().lower()
    clave   = datos.get("clave", "").strip()

    if usuario in USUARIOS and USUARIOS[usuario] == clave:
        # Crear variables de sesión
        session["usuario"]         = usuario          # nombre del usuario
        session["suma_cantidades"] = 0                # acumulado de cantidades
        session["suma_precios"]    = 0.0              # acumulado de precios unitarios
        return jsonify({"ok": True, "redirect": url_for("ventas")})

    return jsonify({"ok": False, "mensaje": "Usuario o contraseña incorrectos."})


# ─────────────────────────────────────────────────────────────
# Página de ventas (GET)
# ─────────────────────────────────────────────────────────────
@app.route("/ventas")
def ventas():
    if "usuario" not in session:
        return redirect(url_for("login"))
    return render_template("ventas.html", usuario=session["usuario"])


# ─────────────────────────────────────────────────────────────
# Registrar venta vía AJAX (POST /registrar_venta)
# Acumula cantidad y precio unitario en sesión
# ─────────────────────────────────────────────────────────────
@app.route("/registrar_venta", methods=["POST"])
def registrar_venta():
    if "usuario" not in session:
        return jsonify({"ok": False, "mensaje": "Sesión expirada."}), 401

    datos = request.get_json()
    try:
        cantidad = int(datos["cantidad"])
        precio   = float(datos["precio"])
        if cantidad <= 0 or precio <= 0:
            raise ValueError
    except (KeyError, ValueError, TypeError):
        return jsonify({"ok": False, "mensaje": "Valores inválidos. Ingrese números positivos."})

    session["suma_cantidades"] += cantidad
    session["suma_precios"]    += precio
    # Forzar que Flask detecte el cambio en la sesión
    session.modified = True

    return jsonify({
        "ok": True,
        "mensaje": f"Venta registrada. Acumulado → Cantidad: {session['suma_cantidades']} | Suma precios: {session['suma_precios']:.2f}"
    })


# ─────────────────────────────────────────────────────────────
# Calcular promedio de precios vía AJAX (GET /promedio_precio)
# promedio = suma_precios / suma_cantidades
# ─────────────────────────────────────────────────────────────
@app.route("/promedio_precio")
def promedio_precio():
    if "usuario" not in session:
        return jsonify({"ok": False, "mensaje": "Sesión expirada."}), 401

    suma_cant    = session.get("suma_cantidades", 0)
    suma_precios = session.get("suma_precios", 0.0)

    if suma_cant == 0:
        return jsonify({"ok": False, "mensaje": "No hay ventas registradas aún."})

    promedio = suma_precios / suma_cant
    return jsonify({
        "ok":       True,
        "usuario":  session["usuario"],
        "promedio": round(promedio, 2)
    })


# ─────────────────────────────────────────────────────────────
# Cerrar sesión
# ─────────────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
