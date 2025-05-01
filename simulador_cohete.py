import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def gravedad(alt):
    R = 6371000
    return 9.81 * (R / (R + alt))**2

def densidad_aire(alt):
    if alt < 10000:
        return 1.225 * (1 - alt / 10000)**4.256
    else:
        return 0

def simular_cohete(thrust, dry_mass, fuel_mass, burn_rate, Cd, A, dt):
    mass = dry_mass + fuel_mass
    velocity = 0.0
    altitude = 0.0
    time = 0.0

    datos = []

    while altitude >= 0:
        g = gravedad(altitude)
        rho = densidad_aire(altitude)
        drag = 0.5 * rho * velocity**2 * Cd * A
        drag *= -1 if velocity > 0 else 1

        if fuel_mass > 0:
            actual_thrust = thrust
            fuel_used = min(burn_rate * dt, fuel_mass)
            fuel_mass -= fuel_used
            mass -= fuel_used
        else:
            actual_thrust = 0

        weight = mass * g
        net_force = actual_thrust - weight - drag
        acceleration = net_force / mass
        velocity += acceleration * dt
        altitude += velocity * dt
        time += dt

        datos.append({
            "Tiempo (s)": time,
            "Altura (m)": altitude,
            "Velocidad (m/s)": velocity,
            "Aceleración (m/s²)": acceleration
        })

    return pd.DataFrame(datos)

# --- INTERFAZ DE USUARIO ---
st.title("🚀 Simulador de Vuelo Suborbital")

st.sidebar.header("Parámetros del Cohete")
thrust = st.sidebar.slider("Empuje (N)", 5000, 50000, 20000, step=1000)
dry_mass = st.sidebar.number_input("Masa sin combustible (kg)", 100.0, 10000.0, 1000.0)
fuel_mass = st.sidebar.number_input("Masa de combustible (kg)", 0.0, 10000.0, 500.0)
burn_rate = st.sidebar.number_input("Tasa de consumo de combustible (kg/s)", 0.1, 100.0, 5.0)
Cd = st.sidebar.slider("Coef. de arrastre (Cd)", 0.1, 1.5, 0.5)
A = st.sidebar.number_input("Área frontal (m²)", 0.1, 10.0, 1.0)
dt = st.sidebar.number_input("Paso de tiempo (s)", 0.01, 1.0, 0.1)

if st.button("Simular vuelo"):
    df_simulado = simular_cohete(thrust, dry_mass, fuel_mass, burn_rate, Cd, A, dt)

    st.subheader("📊 Resultados de la Simulación")
    st.write(f"Altura máxima: {df_simulado['Altura (m)'].max():.2f} m")
    st.write(f"Velocidad máxima: {df_simulado['Velocidad (m/s)'].max():.2f} m/s")
    st.write(f"Aceleración máxima: {df_simulado['Aceleración (m/s²)'].max():.2f} m/s²")

    st.line_chart(df_simulado.set_index("Tiempo (s)")[["Altura (m)", "Velocidad (m/s)", "Aceleración (m/s²)"]])

    st.subheader("📁 Comparar con datos reales (opcional)")
    archivo = st.file_uploader("Sube un archivo CSV con columnas: Tiempo (s), Altura (m), Velocidad (m/s)", type=["csv"])
    if archivo:
        df_real = pd.read_csv(archivo)
        st.line_chart({
            "Altura simulada (m)": df_simulado["Altura (m)"].values,
            "Altura real (m)": df_real["Altura (m)"].values[:len(df_simulado)]
        })
