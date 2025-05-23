import streamlit as st
import pickle
import numpy as np
import os
from fpdf import FPDF
from datetime import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from scipy.special import expit  # sigmoid function
import tempfile

# Ensure reports folder exists
os.makedirs("reports", exist_ok=True)

# Load ML models
models = {
    'Diabetes': pickle.load(open('models/diabetes_model.sav', 'rb')),
    'Heart Disease': pickle.load(open('models/heart_disease_model.sav', 'rb')),
    "Parkinson's": pickle.load(open('models/parkinsons_model.sav', 'rb')),
    'Breast Cancer': pickle.load(open('models/breast_cancer_model.sav', 'rb'))
}

# Logout button in sidebar
with st.sidebar:
    st.title("Sumit HealthCare 🏥")
    st.markdown("---")

    if st.session_state.get("authenticated", False):
        st.success(f"Logged in as *{st.session_state.get('email', '')}*")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.email = None
            st.session_state.doctor_id = None
            st.success("You have been logged out.")
            st.rerun()
    else:
        st.info("🔐 Please log in to access the app features.")

disease_inputs = {
    'Diabetes': [
        'Number of Pregnancies', 'Glucose Level', 'Blood Pressure',
        'Skin Thickness', 'Insulin Level', 'BMI',
        'Diabetes Pedigree Function', 'Age'
    ],
    'Heart Disease': [
        'Age', 'Sex (1=Male, 0=Female)', 'Chest Pain types',
        'Resting Blood Pressure', 'Serum Cholestoral in mg/dl',
        'Fasting Blood Sugar > 120 mg/dl (1 = true; 0 = false)',
        'Resting Electrocardiographic results (0,1,2)',
        'Maximum Heart Rate achieved', 'Exercise Induced Angina (1 = yes; 0 = no)',
        'ST depression', 'Slope of the peak exercise ST segment',
        'Number of major vessels (0-3)', 'Thal (1 = normal; 2 = fixed defect; 3 = reversable defect)'
    ],
    "Parkinson's": [
        'MDVP:Fo(Hz)', 'MDVP:Fhi(Hz)', 'MDVP:Flo(Hz)', 'MDVP:Jitter(%)',
        'MDVP:Jitter(Abs)', 'MDVP:RAP', 'MDVP:PPQ', 'Jitter:DDP',
        'MDVP:Shimmer', 'MDVP:Shimmer(dB)', 'Shimmer:APQ3', 'Shimmer:APQ5',
        'MDVP:APQ', 'Shimmer:DDA', 'NHR', 'HNR', 'RPDE', 'DFA',
        'spread1', 'spread2', 'D2', 'PPE'
    ],
    'Breast Cancer': [
        'Mean Radius', 'Mean Texture', 'Mean Perimeter', 'Mean Area',
        'Mean Smoothness', 'Mean Compactness', 'Mean Concavity',
        'Mean Concave Points', 'Mean Symmetry', 'Mean Fractal Dimension',
        'SE Radius', 'SE Texture', 'SE Perimeter', 'SE Area',
        'SE Smoothness', 'SE Compactness', 'SE Concavity',
        'SE Concave Points', 'SE Symmetry', 'SE Fractal Dimension',
        'Worst Radius', 'Worst Texture', 'Worst Perimeter', 'Worst Area',
        'Worst Smoothness', 'Worst Compactness', 'Worst Concavity',
        'Worst Concave Points', 'Worst Symmetry', 'Worst Fractal Dimension'
    ]
}

detailed_recommendations = {
    'Diabetes': {
        1: """Positive Diagnosis - At Risk:
- Maintain strict blood glucose monitoring.
- Follow a diabetes-friendly diet rich in fiber, vegetables, and lean proteins.
- Engage in regular physical activity (at least 30 minutes daily).
- Avoid sugary foods and beverages.
- Schedule regular check-ups with your healthcare provider.
- Consider medication adherence and insulin therapy if prescribed.
- Monitor for symptoms like excessive thirst, frequent urination, and fatigue.
""",
        0: """Negative Diagnosis - Not At Risk:
- Maintain a balanced diet and healthy lifestyle to prevent diabetes.
- Continue regular physical activity.
- Monitor blood sugar levels periodically.
- Stay informed about risk factors such as family history or weight changes.
- Schedule routine health screenings.
"""
    },
    'Heart Disease': {
        1: """Positive Diagnosis - At Risk:
- Follow a heart-healthy diet low in saturated fats, cholesterol, and sodium.
- Control blood pressure and cholesterol levels with medication if prescribed.
- Avoid tobacco and limit alcohol consumption.
- Engage in moderate exercise as advised by your cardiologist.
- Manage stress through relaxation techniques or counseling.
- Monitor symptoms such as chest pain, shortness of breath, or palpitations.
- Regular cardiology follow-ups and diagnostic tests are recommended.
""",
        0: """Negative Diagnosis - Not At Risk:
- Maintain a balanced diet and regular exercise routine.
- Avoid smoking and limit alcohol intake.
- Monitor blood pressure and cholesterol levels periodically.
- Manage stress and maintain a healthy weight.
- Schedule regular cardiovascular health check-ups.
"""
    },
    "Parkinson's": {
        1: """Positive Diagnosis - At Risk:
- Consult a neurologist promptly for detailed assessment.
- Discuss medication options that can help manage symptoms.
- Engage in physical therapy to improve mobility and balance.
- Consider occupational therapy for daily activity support.
- Monitor symptoms progression and report any changes immediately.
- Maintain a supportive social and family environment.
""",
        0: """Negative Diagnosis - Not At Risk:
- Maintain an active lifestyle with regular exercise.
- Stay mentally engaged with activities like puzzles or reading.
- Avoid exposure to toxins and harmful chemicals.
- Monitor for any new or worsening symptoms.
- Schedule routine neurological check-ups if risk factors exist.
"""
    },
    'Breast Cancer': {
        1: """Positive Diagnosis - At Risk:
- Schedule an appointment with an oncologist immediately.
- Follow through with recommended diagnostic tests (biopsy, imaging).
- Discuss treatment options including surgery, chemotherapy, or radiation.
- Maintain emotional and psychological support via counseling or support groups.
- Inform family members about genetic risk factors if applicable.
- Follow up regularly and adhere to prescribed treatment plans.
""",
        0: """Negative Diagnosis - Not At Risk:
- Perform regular breast self-examinations.
- Schedule routine mammograms and screenings as per guidelines.
- Maintain a healthy diet and exercise regularly.
- Avoid known carcinogens such as tobacco and excessive alcohol.
- Stay vigilant for any changes or lumps and consult a doctor promptly.
"""
    }
}

def generate_pdf_report(patient_name, age, sex, doctor_email, doctor_id, org_id, disease, input_data, prediction, recommendation,
                        risk_image_path=None, inputbar_image_path=None):
    safe_patient_name = patient_name.replace(" ", "_") if patient_name else "UnknownPatient"
    report_file = f"reports/{safe_patient_name}Medical_Report{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 18)
    pdf.cell(0, 12, "Sumit HealthCare Services", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, "456 Wellness Ave, MedCity, Australia | +61-987-654-321", ln=True, align='C')
    pdf.cell(0, 8, f"Report Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}", ln=True, align='C')
    pdf.ln(12)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Patient & Doctor Information", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Patient Name: {patient_name}", ln=True)
    pdf.cell(0, 8, f"Age: {age}   Sex: {sex}", ln=True)
    pdf.cell(0, 8, f"Doctor Email: {doctor_email}", ln=True)
    pdf.cell(0, 8, f"Doctor ID: {doctor_id}", ln=True)
    pdf.cell(0, 8, f"Organization ID: {org_id}", ln=True)
    pdf.ln(8)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Disease Predicted: {disease}", ln=True)
    pdf.set_font("Arial", '', 12)
    result_text = "Positive (At Risk)" if prediction == 1 else "Negative (Not At Risk)"
    pdf.cell(0, 8, f"Prediction Result: {result_text}", ln=True)
    pdf.ln(8)

    # Add Risk Gauge Image if available
    if risk_image_path and os.path.exists(risk_image_path):
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Risk Probability Gauge:", ln=True)
        pdf.image(risk_image_path, w=160)
        pdf.ln(10)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Input Parameters:", ln=True)

    # Add Input Bar Chart Image if available
    if inputbar_image_path and os.path.exists(inputbar_image_path):
        pdf.image(inputbar_image_path, w=160)
        pdf.ln(10)
    else:
        pdf.set_font("Arial", '', 11)
        for key, value in input_data.items():
            pdf.cell(0, 7, f"{key}: {value}", ln=True)
        pdf.ln(8)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Medical Recommendation:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 8, recommendation)
    pdf.ln(12)

    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 6, "This is an AI-generated report. Please consult a qualified medical professional for diagnosis and treatment.", align='C')

    pdf.output(report_file)
    return report_file


def main():
    if not st.session_state.get("authenticated"):
        st.warning("Please log in to access the predictor.")
        st.stop()

    st.title("🩺 Multi-Disease Prediction Dashboard")

    with st.expander("🔎 Patient Information"):
        patient_name = st.text_input("Patient Name")
        patient_age = st.number_input("Patient Age", min_value=1, max_value=120)
        patient_sex = st.selectbox("Patient Sex", ["Male", "Female", "Other"])

    disease = st.selectbox("Select Disease to Predict", list(models.keys()))
    input_fields = disease_inputs[disease]

    st.subheader(f"🧪 Enter details for {disease} prediction")
    inputs = {}
    for field in input_fields:
        value = st.number_input(field, step=0.0001, format="%.6f")
        inputs[field] = value

    if st.button("Predict"):
        if not patient_name:
            st.error("Please enter the patient's name.")
            st.stop()

        input_array = np.array(list(inputs.values())).reshape(1, -1)
        model = models[disease]
        prediction = model.predict(input_array)[0]

        risk_percent = None
        prob_error = False

        if disease == 'Breast Cancer':
            prediction = 1 - prediction  # This will flip 0 to 1 and 1 to 0

        try:
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(input_array)
                if disease == 'Breast Cancer':
                    risk_percent = probs[0][0] * 100
                else:
                    risk_percent = probs[0][1] * 100
            elif hasattr(model, "decision_function"):
                dec_score = model.decision_function(input_array)[0]
                risk_prob = expit(dec_score)  # sigmoid
                if disease == 'Breast Cancer':
                    risk_percent = (1 - risk_prob) * 100
                else:
                    risk_percent = risk_prob * 100
        except Exception:
            prob_error = True

        if prediction == 1:
            st.error(f"⚠ {disease} Prediction: Positive (At Risk)")
        else:
            st.success(f"✅ {disease} Prediction: Negative (Not At Risk)")

        # Show risk gauge chart if available and save it to temp
        risk_image_path = None
        if risk_percent is not None:
            st.subheader("📈 Risk Probability Gauge")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk_percent,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"{disease} Risk Probability (%)"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "crimson"},
                    'steps': [
                        {'range': [0, 40], 'color': "lightgreen"},
                        {'range': [40, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': risk_percent
                    }
                }
            ))
            st.plotly_chart(fig_gauge, use_container_width=True)

            # Save gauge chart as PNG image for PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                risk_image_path = tmpfile.name
                fig_gauge.write_image(risk_image_path, scale=2)
        else:
            if prob_error:
                st.warning("Risk probability gauge could not be generated due to model limitations or error.")
            else:
                st.info("Risk probability data not available for this model.")

        recommendation = detailed_recommendations[disease][prediction]

        # Generate input parameters bar chart and save image for PDF
        st.subheader("📊 Input Parameters Visualization")
        fig_bar, ax = plt.subplots(figsize=(8, max(4, len(inputs) * 0.3)))
        ax.barh(list(inputs.keys()), list(inputs.values()), color='skyblue')
        ax.set_xlabel('Values')
        ax.set_title(f'Input Parameters for {disease} Prediction')
        plt.tight_layout()
        st.pyplot(fig_bar)

        inputbar_image_path = None
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            inputbar_image_path = tmpfile.name
            fig_bar.savefig(inputbar_image_path, bbox_inches='tight')
            plt.close(fig_bar)  # Close figure to free memory

        # Generate PDF report with embedded images
        report_path = generate_pdf_report(
            patient_name=patient_name,
            age=patient_age,
            sex=patient_sex,
            doctor_email=st.session_state.get('email', 'unknown@example.com'),
            doctor_id=st.session_state.get('doctor_id', 'UnknownID'),
            org_id="HealthCare-001",
            disease=disease,
            input_data=inputs,
            prediction=prediction,
            recommendation=recommendation,
            risk_image_path=risk_image_path,
            inputbar_image_path=inputbar_image_path
        )

        with open(report_path, "rb") as f:
            st.download_button("📄 Download Detailed Medical Report (PDF)", f,
                               file_name=os.path.basename(report_path),
                               mime="application/pdf")

        # Clean up temporary images after download button is rendered
        def cleanup_files(*filepaths):
            import time
            import threading
            def delayed_remove(paths):
                import os
                import time
                time.sleep(10)  # wait a bit before deleting so file is ready
                for p in paths:
                    try:
                        os.remove(p)
                    except Exception:
                        pass
            thread = threading.Thread(target=delayed_remove, args=(filepaths,))
            thread.start()
        cleanup_files(risk_image_path, inputbar_image_path)

if __name__ == "__main__":
    main()

