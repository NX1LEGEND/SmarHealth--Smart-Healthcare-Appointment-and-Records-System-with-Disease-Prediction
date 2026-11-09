from django import forms


class DiabetesPredictionForm(forms.Form):
    pregnancies = forms.IntegerField(
        label="Pregnancies",
        initial=1,
        min_value=0,
        max_value=20,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 1 (0 for males)'}),
        help_text="Number of pregnancies (enter 0 for males or no pregnancies)"
    )
    glucose = forms.FloatField(
        label="Fasting Blood Glucose (mg/dL)",
        initial=110.0,
        min_value=40.0,
        max_value=350.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Normal fasting is 70 - 100 mg/dL'}),
        help_text="Plasma glucose concentration (2 hours in an oral glucose tolerance test)"
    )
    blood_pressure = forms.FloatField(
        label="Diastolic Blood Pressure (mm Hg)",
        initial=72.0,
        min_value=40.0,
        max_value=200.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Normal is 60 - 80 mm Hg'}),
        help_text="Diastolic blood pressure reading (lower number)"
    )
    skin_thickness = forms.FloatField(
        label="Triceps Skinfold Thickness (mm)",
        initial=22.0,
        min_value=0.0,
        max_value=99.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Typical: 15 - 35 mm'}),
        help_text="Triceps skin fold thickness in millimeters"
    )
    insulin = forms.FloatField(
        label="2-Hour Serum Insulin (µU/mL)",
        initial=85.0,
        min_value=0.0,
        max_value=900.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Normal: 16 - 166 µU/mL'}),
        help_text="Two-hour postprandial serum insulin concentration"
    )
    bmi = forms.FloatField(
        label="Body Mass Index (BMI)",
        initial=26.4,
        min_value=12.0,
        max_value=65.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'e.g. 24.5'}),
        help_text="Weight in kg / (height in meters)²"
    )
    diabetes_pedigree = forms.FloatField(
        label="Diabetes Pedigree Function Score",
        initial=0.35,
        min_value=0.05,
        max_value=3.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'e.g. 0.45'}),
        help_text="Genetic score based on family history of diabetes (0.1 to 2.5)"
    )
    age = forms.IntegerField(
        label="Patient Age (Years)",
        initial=35,
        min_value=18,
        max_value=110,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 42'}),
        help_text="Age in completed solar years"
    )


class HeartDiseasePredictionForm(forms.Form):
    age = forms.IntegerField(
        label="Age",
        initial=52,
        min_value=20,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 52'})
    )
    sex = forms.ChoiceField(
        label="Sex",
        choices=[(1, 'Male'), (0, 'Female')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cp = forms.ChoiceField(
        label="Chest Pain Type",
        choices=[
            (0, 'Typical Angina (chest pressure during exertion)'),
            (1, 'Atypical Angina (unrelated chest discomfort)'),
            (2, 'Non-Anginal Pain (sharp or burning pain)'),
            (3, 'Asymptomatic (no chest discomfort reported)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select the clinical category of chest discomfort"
    )
    trestbps = forms.IntegerField(
        label="Resting Blood Pressure (mm Hg)",
        initial=128,
        min_value=80,
        max_value=240,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 120'}),
        help_text="Resting blood pressure upon hospital admission"
    )
    chol = forms.IntegerField(
        label="Serum Cholesterol (mg/dL)",
        initial=215,
        min_value=100,
        max_value=600,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 210'}),
        help_text="Total serum cholesterol (Desirable: < 200 mg/dL)"
    )
    fbs = forms.ChoiceField(
        label="Fasting Blood Sugar > 120 mg/dL",
        choices=[(0, 'No (Normal <= 120 mg/dL)'), (1, 'Yes (Elevated > 120 mg/dL)')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    restecg = forms.ChoiceField(
        label="Resting Electrocardiogram (ECG) Results",
        choices=[
            (0, 'Normal'),
            (1, 'ST-T Wave Abnormality (T-wave inversions/ST elevation)'),
            (2, 'Left Ventricular Hypertrophy (Estes criteria)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    thalach = forms.IntegerField(
        label="Maximum Heart Rate Achieved (bpm)",
        initial=150,
        min_value=60,
        max_value=220,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 155'}),
        help_text="Peak heart rate measured during stress test"
    )
    exang = forms.ChoiceField(
        label="Exercise Induced Angina",
        choices=[(0, 'No'), (1, 'Yes')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Does physical exercise trigger chest pain?"
    )
    oldpeak = forms.FloatField(
        label="ST Depression Induced by Exercise (Oldpeak)",
        initial=0.8,
        min_value=0.0,
        max_value=8.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'e.g. 1.2'}),
        help_text="ST segment depression relative to rest baseline in mm"
    )
    slope = forms.ChoiceField(
        label="Slope of Peak Exercise ST Segment",
        choices=[
            (0, 'Upsloping'),
            (1, 'Flat'),
            (2, 'Downsloping (High Risk indicator)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    ca = forms.ChoiceField(
        label="Number of Major Vessels Colored by Fluoroscopy",
        choices=[(0, '0 vessels'), (1, '1 vessel'), (2, '2 vessels'), (3, '3 vessels')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Fluoroscopy vessel count showing calcification (0 - 3)"
    )
    thal = forms.ChoiceField(
        label="Thalassemia Blood Disorder Status",
        choices=[
            (1, 'Normal (No defect)'),
            (2, 'Fixed Defect (Previous injury)'),
            (3, 'Reversible Defect (Active ischemia)'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
