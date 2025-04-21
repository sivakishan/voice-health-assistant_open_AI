import pandas as pd

df = pd.read_excel("medical_data.xlsx")

def get_medicine_for_symptom(symptom):
    result = df[df['Symptom'].str.contains(symptom, case=False, na=False)]
    return result[['Medicine', 'Dosage', 'Instructions']].to_dict(orient='records')
