import streamlit as st
import pandas as pd
import snowflake.connector
import plost

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.sidebar.header('Decarbonization Dashboard')

def get_snowflake_data(query):
    conn = snowflake.connector.connect(
        user='YOUR_USER',
        password='YOUR_PASSWORD',
        account='YOUR_ACCOUNT'
    )
    cur = conn.cursor()
    cur.execute(query)
    df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
    cur.close()
    conn.close()
    return df

# Fetch data
energy_data = get_snowflake_data("""
    SELECT DATE, 
           SUM(TOTAL_ELECTRICITY_CONSUMPTION) AS TOTAL_ENERGY_KWH, 
           SUM(TOTAL_ELECTRICITY_CONSUMPTION) * 0.4 AS TOTAL_CO2_EMISSIONS_KG 
    FROM KAGGLE_DATABASE_ELECTR.SCH_DB_ELECTR_BUILDINGDATA.BUILDINGDATA 
    GROUP BY DATE ORDER BY DATE;
""")

heating_cooling_data = get_snowflake_data("""
    SELECT DATE, 
           SUM(ZONE_SENSIBLE_HEATING) AS TOTAL_HEATING_LOAD, 
           SUM(ZONE_SENSIBLE_COOLING) AS TOTAL_COOLING_LOAD, 
           SUM(TOTAL_COOLING) AS TOTAL_COOLING_ENERGY 
    FROM KAGGLE_DATABASE_ELECTR.SCH_DB_ELECTR_BUILDINGDATA.BUILDINGDATA 
    GROUP BY DATE ORDER BY DATE;
""")

occupancy_data = get_snowflake_data("""
    SELECT DATE, 
           SUM(OCCUPANCY) AS TOTAL_OCCUPANCY, 
           SUM(TOTAL_ELECTRICITY_CONSUMPTION) AS TOTAL_ENERGY_KWH 
    FROM KAGGLE_DATABASE_ELECTR.SCH_DB_ELECTR_BUILDINGDATA.BUILDINGDATA 
    GROUP BY DATE ORDER BY DATE;
""")

building_efficiency_data = get_snowflake_data("""
    SELECT DATE, 
           AVG(GLAZING) AS AVG_GLAZING, 
           AVG(WALLS) AS AVG_WALLS, 
           AVG(ROOFS) AS AVG_ROOFS, 
           SUM(TOTAL_ELECTRICITY_CONSUMPTION) AS TOTAL_ENERGY_KWH 
    FROM KAGGLE_DATABASE_ELECTR.SCH_DB_ELECTR_BUILDINGDATA.BUILDINGDATA 
    GROUP BY DATE ORDER BY DATE;
""")

solar_gains_data = get_snowflake_data("""
    SELECT DATE, 
           SUM(SOLAR_GAINS_INTERIOR_WINDOWS) AS INTERIOR_SOLAR_GAINS, 
           SUM(SOLAR_GAINS_EXTERIOR_WINDOWS) AS EXTERIOR_SOLAR_GAINS, 
           SUM(TOTAL_ELECTRICITY_CONSUMPTION) AS TOTAL_ENERGY_KWH 
    FROM KAGGLE_DATABASE_ELECTR.SCH_DB_ELECTR_BUILDINGDATA.BUILDINGDATA 
    GROUP BY DATE ORDER BY DATE;
""")

st.markdown("### Key Metrics")
col1, col2 = st.columns(2)
col1.metric("Total Energy Consumption (kWh)", f"{energy_data['TOTAL_ENERGY_KWH'].sum():,.0f}")
col2.metric("Total CO2 Emissions (kg)", f"{energy_data['TOTAL_CO2_EMISSIONS_KG'].sum():,.0f}")

st.markdown("### Energy Consumption & Emissions Over Time")
st.line_chart(energy_data, x='DATE', y=['TOTAL_ENERGY_KWH', 'TOTAL_CO2_EMISSIONS_KG'])

st.markdown("### Heating & Cooling Load Analysis")
st.line_chart(heating_cooling_data, x='DATE', y=['TOTAL_HEATING_LOAD', 'TOTAL_COOLING_LOAD', 'TOTAL_COOLING_ENERGY'])

st.markdown("### Occupancy Impact on Energy Consumption")
st.line_chart(occupancy_data, x='DATE', y=['TOTAL_OCCUPANCY', 'TOTAL_ENERGY_KWH'])

st.markdown("### Building Envelope Efficiency")
st.line_chart(building_efficiency_data, x='DATE', y=['AVG_GLAZING', 'AVG_WALLS', 'AVG_ROOFS', 'TOTAL_ENERGY_KWH'])

st.markdown("### Solar Gains Impact on Energy Consumption")
st.line_chart(solar_gains_data, x='DATE', y=['INTERIOR_SOLAR_GAINS', 'EXTERIOR_SOLAR_GAINS', 'TOTAL_ENERGY_KWH'])

st.sidebar.markdown('''
---
Created with ❤️ for Sustainability.
''')
