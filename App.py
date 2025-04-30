import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import datetime

# Générer les données patient
@st.cache_data
def create_patient_data():
    # Générer les heures toutes les 30 minutes de 00:00 à 16:00
    heures = pd.date_range(start="00:00", end="14:30", freq="30T").strftime("%H:%M")

    debit_propofol = []
    for h in heures:
        hour = int(h.split(":")[0])

        if  hour < 6 or hour >= 22:
            debit = 200  # Night
        elif 8 <= hour < 10:
            debit = 150
        else:
            debit = 100  # Default day rate
        debit_propofol.append(debit)

    def generate_bolus_propofol(hour_index):
        hour = int(heures[hour_index].split(":")[0])
        if hour in [1, 8, 17]:
            nb_bolus = np.random.choice([1, 2], p=[0.4, 0.6])
            dose = sum(5 * np.random.randint(5, 10, size=nb_bolus))  # 25–50 mg en pas de 5
        else:
            nb_bolus = np.random.choice([0, 1, 2], p=[0.8, 0.15, 0.05])
            dose = sum(5 * np.random.randint(2, 4, size=nb_bolus)) if nb_bolus > 0 else 0  # 10–20 mg en pas de 5
        return dose, nb_bolus

    propofol_bolus_data = [generate_bolus_propofol(i) for i in range(len(heures))]
    bolus_doses_propofol = [d for d, n in propofol_bolus_data]
    bolus_freq_propofol = [n for d, n in propofol_bolus_data]
    bolus_cumul_propofol = np.cumsum(bolus_doses_propofol)
    bolus_nb_cumul = np.cumsum(bolus_freq_propofol)
    cumul_perfus_propofol = np.cumsum(debit_propofol)
    total_propofol = bolus_cumul_propofol + cumul_perfus_propofol

    debit_fentanyl = [50] * len(heures)

    def generate_bolus_fentanyl(hour_index):
        hour = int(heures[hour_index].split(":")[0])
        if hour in [1, 8]:
            return 75, 1  # Un bolus de 75 mcg à 1h et 8h
        elif hour_index % np.random.choice([6, 8]) == 0:
            return 75, 1  # Parfois (probabilité sur index)
        else:
            return 0, 0  # Aucun bolus dans d'autres cas

    fentanyl_bolus_data = [generate_bolus_fentanyl(i) for i in range(len(heures))]
    bolus_doses_fentanyl = [d for d, n in fentanyl_bolus_data]
    bolus_freq_fentanyl = [n for d, n in fentanyl_bolus_data]
    bolus_cumul_fentanyl = np.cumsum(bolus_doses_fentanyl)
    perfus_cumul_fentanyl = np.cumsum(debit_fentanyl)
    total_fentanyl = bolus_cumul_fentanyl + perfus_cumul_fentanyl

    creat_values = [np.random.randint(90, 101) if i % 8 == 0 else np.nan for i in range(len(heures))]
    ck_24h = [np.nan] * (len(heures) - 1) + [47]
    triglycerides = [np.nan] * len(heures)

    ph = [round(np.random.uniform(7.30, 7.36), 2) if i % 8 == 0 else np.nan for i in range(len(heures))]
    sodium = [np.random.randint(138, 143) if i % 8 == 0 else np.nan for i in range(len(heures))]
    chlorure = [np.random.randint(100, 103) if i % 8 == 0 else np.nan for i in range(len(heures))]
    bicarbonates = [np.random.randint(22, 26) if i % 8 == 0 else np.nan for i in range(len(heures))]
    albumine = [round(np.random.uniform(30, 32), 1) if i % 8 == 0 else np.nan for i in range(len(heures))]

    # Calcul de l'Anion Gap corrigé
    anion_gap_corrige = []
    for na, cl, hco3, alb in zip(sodium, chlorure, bicarbonates, albumine):
        if not np.isnan(na) and not np.isnan(cl) and not np.isnan(hco3) and not np.isnan(alb):
            ag = na - (cl + hco3)
            ag_corr = round(ag + (0.25 * (40 - alb)), 2)
        else:
            ag_corr = np.nan
        anion_gap_corrige.append(ag_corr)

    df = pd.DataFrame({
        "Heure": heures,
        "Débit Propofol (mg/h)": debit_propofol,
        "Bolus Propofol (mg)": bolus_doses_propofol,
        "Nb Bolus Propofol": bolus_freq_propofol,
        "Cumul Bolus Propofol (mg)": bolus_cumul_propofol,
        "Cumul Nb Bolus Propofol": bolus_nb_cumul,
        "Cumul Total Propofol (mg)": total_propofol,
        "Débit Fentanyl (mcg/h)": debit_fentanyl,
        "Bolus Fentanyl (mcg)": bolus_doses_fentanyl,
        "Nb Bolus Fentanyl": bolus_freq_fentanyl,
        "Cumul Total Fentanyl (mcg)": total_fentanyl,
        "Créatinine (umol/L)": creat_values,
        "CK (U/L)": ck_24h,
        "Triglycérides (mmol/L)": triglycerides,
        "pH": ph,
        "Na⁺ (mmol/L)": sodium,
        "Cl⁻ (mmol/L)": chlorure,
        "HCO₃⁻ (mmol/L)": bicarbonates,
        "Albumine (g/L)": albumine,
        "Anion Gap Corrigé": anion_gap_corrige
    })

    return df

# Charger les données
df = create_patient_data()

# Récupérer la date et l'heure actuelle
current_datetime = datetime.datetime.now()

# Formater la date et l'heure pour l'affichage
current_date = current_datetime.strftime("%Y-%m-%d")
current_time = current_datetime.strftime("%H:%M:%S")

# Afficher la date et l'heure actuelle
st.warning("⚠️Disclaimer: No actual patient data was used. All data is simulated. This app is for demonstration/educational purposes only. Do not use for actual clinical decision-making.⚠️")
st.markdown(f"**Unité de soins intensifs - Chambre X / {current_date} - {current_time}**")
# Vérification : y a-t-il eu une pause (débit = 0) dans la sédation ?
pause_detectee = (df["Débit Propofol (mg/h)"] == 0).any()

st.info("""
### 💉 **Dashboard Sédation / Analgésie**
""")

# Message interactif
if not pause_detectee:
    st.warning("⚠️ Aucun arrêt de sédation détecté depuis minuit.")
else:
    st.success("✅ Pause de sédation détectée.")

# ⏱️ Convertir Heure en datetime pour le tri Altair
df["Heure_dt"] = pd.to_datetime(df["Heure"], format="%H:%M")

# ===============================
# 1. GRAPHIQUE DÉBITS + BOLUS /h
# ===============================
st.subheader("Débits horaires + bolus horaires (Propofol & Fentanyl)")

# Préparer données des débits
df_debit = df[["Heure", "Débit Propofol (mg/h)", "Débit Fentanyl (mcg/h)"]].melt(
    id_vars="Heure", var_name="Médicament", value_name="Débit"
)

# Préparer données des bolus horaires
df_bolus_hr = pd.DataFrame({
    "Heure": df["Heure"].tolist() * 2,
    "Nb Bolus": df["Nb Bolus Propofol"].tolist() + df["Nb Bolus Fentanyl"].tolist(),
    "Médicament": ["Propofol"] * len(df) + ["Fentanyl"] * len(df)
})

# Ligne + scatter pour les débits
line_chart = alt.Chart(df_debit).mark_line(point=True).encode(
    x=alt.X("Heure", sort=None),
    y=alt.Y("Débit", scale=alt.Scale(domain=[0, 250]), sort=None),
    color=alt.Color("Médicament"),
    tooltip=["Heure", "Médicament", "Débit"]
).properties(
    height=300,
)

# Histogramme empilé des bolus par heure
bar_chart = alt.Chart(df_bolus_hr).mark_bar().encode(
    x=alt.X("Heure", sort=None),
    y=alt.Y("Nb Bolus", title="Nombre de bolus"),
    color=alt.Color("Médicament", scale=alt.Scale(domain=["Propofol", "Fentanyl"], range=["lightblue", "lightgreen"])),
    tooltip=["Heure", "Médicament", "Nb Bolus"]
).properties(
    height=100
)

# Combinaison débit + histogramme en vertical
combined_chart = alt.vconcat(line_chart, bar_chart).resolve_scale(
    color="independent"
)
st.altair_chart(combined_chart, use_container_width=True)

# === Diviser en quart de travail ===
def get_shift(hour):
    if hour >= 0 and hour <= 7:  # Nuit (00:00 - 07:45)
        return "Nuit"
    elif hour >= 8 and hour <= 15:  # Jour (08:00 - 15:45)
        return "Jour"
    else:  # Soir (15:45 - 23:45)
        return "Soir"

# Appliquer la fonction pour déterminer le quart de travail de chaque heure
df['Shift'] = df['Heure'].apply(lambda h: get_shift(int(h.split(":")[0])))

# Calculer le nombre total de bolus par quart de travail et la quantité totale en mg
shift_bolus = df.groupby('Shift').agg(
    Nb_Bolus_Propofol=('Nb Bolus Propofol', 'sum'),
    Total_Propofol_Mg=('Bolus Propofol (mg)', 'sum'),
    Nb_Bolus_Fentanyl=('Nb Bolus Fentanyl', 'sum'),
    Total_Fentanyl_Mcg=('Bolus Fentanyl (mcg)', 'sum')
).reset_index()

# Affichage des bolus par quart
st.subheader("📊 Nombre de bolus par quart de travail")

# Choisir le quart de travail à afficher
quart_de_travail = st.selectbox("Sélectionnez un quart de travail", options=["Nuit", "Jour", "Soir"])

# Vérification si les données pour le quart sélectionné existent
shift_data = shift_bolus[shift_bolus['Shift'] == quart_de_travail]

if shift_data.empty:
    st.write(f"Aucune donnée disponible pour le quart de travail '{quart_de_travail}' pour le moment. 😕")
else:
    # Affichage des résultats pour le quart de travail sélectionné
    bolus_quart = shift_data.iloc[0]  # On récupère la première ligne (car il y a qu'une seule ligne par shift)
    
    # Mise en forme et affichage
    st.markdown(f"### 🕒 Quart de travail : **{quart_de_travail}**")
    
    # Mise en page avec des colonnes
    col1, col2 = st.columns(2)
    
    # Colonne 1 : Propofol
    with col1:
        st.markdown("**Propofol**")
        st.write(f"🔹 **Nombre de bolus** : {bolus_quart['Nb_Bolus_Propofol']}")
        st.write(f"🔹 **Quantité totale** : {bolus_quart['Total_Propofol_Mg']} mg")
    
    # Colonne 2 : Fentanyl
    with col2:
        st.markdown("**Fentanyl**")
        st.write(f"🔹**Nombre de bolus** : {bolus_quart['Nb_Bolus_Fentanyl']}")
        st.write(f"🔹**Quantité totale** : {bolus_quart['Total_Fentanyl_Mcg']} mcg")

# ===============================
# 2. CUMULS DOSES (axes inversés)
# ===============================
st.subheader("Cumul des doses (bolus et perfusions)")

col1, col2 = st.columns(2)

# --------- PROPofol ----------
with col1:
    df_prop_cumul = pd.DataFrame({
        "Heure": df["Heure"],
        "Bolus": df["Cumul Bolus Propofol (mg)"],
        "Perfusion": df["Cumul Total Propofol (mg)"] - df["Cumul Bolus Propofol (mg)"],
        "Bolus Cumulé": df["Cumul Nb Bolus Propofol"]
    })
    df_prop_melted = df_prop_cumul.melt(id_vars=["Heure", "Bolus Cumulé"], value_name="Dose", var_name="Type")

    color_prop = alt.Scale(domain=["Bolus", "Perfusion"], range=["lightblue", "blue"])

    area_prop = alt.Chart(df_prop_melted).mark_bar().encode(
        y=alt.Y("Heure", sort=None),
        x=alt.X("Dose"),
        color=alt.Color("Type", scale=color_prop),
        tooltip=["Heure", "Type", "Dose"]
    )

    line_bolus_prop = alt.Chart(df_prop_cumul).mark_line(strokeDash=[4, 4], color="darkred").encode(
        y=alt.Y("Heure", sort=None),
        x=alt.X("Bolus Cumulé"),
        tooltip=["Heure", "Bolus Cumulé"]
    )

    st.altair_chart((area_prop + line_bolus_prop).properties(
        width=350, height=500, title="Cumul Propofol (mg)"
    ), use_container_width=True)

# --------- FENTanyl ----------
with col2:
    df_fent_cumul = pd.DataFrame({
        "Heure": df["Heure"],
        "Bolus": df["Cumul Total Fentanyl (mcg)"] - np.cumsum(df["Débit Fentanyl (mcg/h)"]),
        "Perfusion": np.cumsum(df["Débit Fentanyl (mcg/h)"]),
        "Bolus Cumulé": np.cumsum(df["Nb Bolus Fentanyl"])
    })
    df_fent_melted = df_fent_cumul.melt(id_vars=["Heure", "Bolus Cumulé"], value_name="Dose", var_name="Type")

    color_fent = alt.Scale(domain=["Bolus", "Perfusion"], range=["lightgreen", "green"])

    area_fent = alt.Chart(df_fent_melted).mark_bar().encode(
        y=alt.Y("Heure", sort=None),
        x=alt.X("Dose"),
        color=alt.Color("Type", scale=color_fent),
        tooltip=["Heure", "Type", "Dose"]
    )

    line_bolus_fent = alt.Chart(df_fent_cumul).mark_line(strokeDash=[4, 4], color="darkgreen").encode(
        y=alt.Y("Heure", sort=None),
        x=alt.X("Bolus Cumulé"),
        tooltip=["Heure", "Bolus Cumulé"]
    )

    st.altair_chart((area_fent + line_bolus_fent).properties(
        width=350, height=500, title="Cumul Fentanyl (mcg)"
    ), use_container_width=True)

# === LABO : extraire les 2 dernières valeurs non-NaN pour chaque paramètre ===
def get_last_two_valid(series):
    valid = series.dropna()
    if len(valid) >= 2:
        return valid.iloc[-2], valid.iloc[-1]
    elif len(valid) == 1:
        return np.nan, valid.iloc[-1]
    else:
        return np.nan, np.nan

def calculate_variation(prev, curr):
    if pd.isna(prev) or pd.isna(curr) or prev == 0:
        return "—", ""
    delta = curr - prev
    variation_pct = (delta / prev) * 100
    fleche = "⬆️" if delta > 0 else ("⬇️" if delta < 0 else "→")
    return f"{variation_pct:.1f}%", fleche

# Fonction pour obtenir l'heure de la dernière valeur valide
def get_last_value_and_time(series):
    valid = series.dropna()
    if len(valid) > 0:
        last_value = valid.iloc[-1]
        last_time = df.loc[valid.index[-1], 'Heure']  # Prendre l'heure associée à la dernière valeur
        return last_value, last_time
    else:
        return np.nan, "—"

# Paramètres à afficher
params = ["pH", "Anion Gap Corrigé", "HCO₃⁻ (mmol/L)", "CK (U/L)", "Créatinine (umol/L)", "Triglycérides (mmol/L)"]

# Construction du tableau
table_data = []
for param in params:
    prev, curr = get_last_two_valid(df[param])
    variation, fleche = calculate_variation(prev, curr)
    last_value, last_time = get_last_value_and_time(df[param])  # Extraire la dernière valeur et son heure
    
    table_data.append({
        "Paramètre": param,
        "Valeur actuelle": f"{curr:.2f}" if not pd.isna(curr) else "—",
        "Variation (%)": f"{variation} {fleche}" if variation != "—" else "—",
        "Dernière heure de mesure": last_time  # Ajouter l'heure du dernier enregistrement
    })

# Affichage du tableau avec l'heure des derniers résultats de laboratoire
st.markdown("### 🧪 Derniers résultats de laboratoire")
st.table(pd.DataFrame(table_data))
