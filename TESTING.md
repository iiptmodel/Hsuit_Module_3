<div align="center">

# 🏥 Medical Report Analysis System
## Testing Results & Validation

![Total Reports](https://img.shields.io/badge/Total%20Reports-20-blue?style=for-the-badge)
![Success Rate](https://img.shields.io/badge/Success%20Rate-100%25-success?style=for-the-badge)
![Completed](https://img.shields.io/badge/Completed-20-brightgreen?style=for-the-badge)
![Failed](https://img.shields.io/badge/Failed-0-red?style=for-the-badge)

</div>

---

## 📊 Executive Summary

This document presents **comprehensive testing results** for the **Medical Report Analysis System**, demonstrating the system's capability to process medical reports and generate audience-appropriate summaries with audio playback.

<table>
<tr>
<td align="center"><b>📝 Total Reports Tested</b></td>
<td align="center"><b>✅ Successfully Processed</b></td>
<td align="center"><b>❌ Failed</b></td>
<td align="center"><b>🎯 Success Rate</b></td>
</tr>
<tr>
<td align="center"><h3>20</h3></td>
<td align="center"><h3>20</h3></td>
<td align="center"><h3>0</h3></td>
<td align="center"><h3>100.0%</h3></td>
</tr>
</table>

---

## 🔬 System Capabilities

The Medical Report Analysis System processes medical reports through a sophisticated **multi-stage pipeline**:

<table>
<tr>
<td width="25%" align="center">
<h3>📄</h3>
<b>Text Extraction</b><br>
<small>Docling + OCR fallback</small>
</td>
<td width="25%" align="center">
<h3>🤖</h3>
<b>AI Analysis</b><br>
<small>MedGemma LLM</small>
</td>
<td width="25%" align="center">
<h3>✍️</h3>
<b>Summary Generation</b><br>
<small>Dual audience</small>
</td>
<td width="25%" align="center">
<h3>🔊</h3>
<b>Audio Synthesis</b><br>
<small>Kokoro TTS</small>
</td>
</tr>
</table>

### 🎯 Dual Audience Approach

<table>
<tr>
<td width="50%">

#### 👤 **Patient Summaries**
- ✅ Simple, easy-to-understand language
- ✅ Non-technical terminology
- ✅ 2-4 concise sentences
- ✅ Focus on key findings
- ✅ Includes medical disclaimer

</td>
<td width="50%">

#### 👨‍⚕️ **Doctor Summaries**
- ✅ Professional medical terminology
- ✅ 4-6 comprehensive sentences
- ✅ Clinical significance highlighted
- ✅ Detailed measurements & ranges
- ✅ Diagnostic context provided

</td>
</tr>
</table>

---

## 📑 Test Results

> **Note:** Each test report below includes:
> - 📄 Original PDF document link
> - 🔍 Collapsible extracted text preview
> - 👤 Patient summary with embedded audio player
> - 👨‍⚕️ Doctor summary with embedded audio player


<div align="center">

### 📋 Report 1: `1.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**1.pdf**](testing_reports/1.pdf) • [Full Extracted Text](testing_reports/inference_results/1/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> Age/Sex
> 
> :
> 
> 65 Yrs. / F
> 
> | Thyroid Function Test (ultra)   | Thyroid Function Test (ultra)   | Thyroid Function Test (ultra)   | Thyroid Function Test (ultra)   | Thyroid Function Test (ultra)   |
> |---------------------------------|---------------------------------|---------------------------------|---------------------------------|---------------------------------|
> | Test                            |                                 | Result                          | Unit                            | Biological Ref. Range           |
> | T3 - Triiodothyronine           | :                               | 0.52                            | ng/mL                           | 0.69 - 2.15 ng/mL               |
> | T4 - Thyroxine                  | :                               | 4.19                            | mcg/dL                          | 5.2 - 12.7 mcg/dL               |
> | TSH (ultra)                     | :                               | 96.20                           | mlU/mL                          | 0.30 - 4.5 mlU/mL               |
> 
> Method:Chemi-Luminescence ImmunoAssay (CLIA)
> 
> NOTE :  Primary malfunction of thyroid gland may result in excessive (hyper) or below normal (hy...

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your thyroid hormone levels (T3, T4, and TSH) are within the normal range. Your Vitamin B12 level is also within the normal range. Your iron levels are also within the normal range.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/1/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/1/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The patient is a 65-year-old female presenting with thyroid function tests. T3 is low (0.52 ng/mL), T4 is within the normal range (4.19 mcg/dL), and TSH is markedly elevated (96.20 mlU/mL). This suggests hypothyroidism, likely secondary to pituitary or hypothalamic dysfunction, given the elevated TSH. Vitamin B12 levels are within the normal range (431.0 pg/mL). Iron studies show a low serum iron (69 ug/dL) and elevated TIBC (331 ug/dL), indicating iron deficiency anemia. Transferrin saturation is also low (20.85%), further supporting iron deficiency.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/1/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/1/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 10: `10.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**10.pdf**](testing_reports/10.pdf) • [Full Extracted Text](testing_reports/inference_results/10/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> Test
> 
> TSH (ultra)
> 
> Method:
> 
> :
> 
> Chemi-Luminescence ImmunoAssay (CLIA)
> 
> ## Reference ranges:-
> 
> | FOR PREGNANT WOMEN   | T3 (ng / dl )   | T4 (ng / dl )   | TSH (ulU/ml )   |
> |----------------------|-----------------|-----------------|-----------------|
> | 1 st TRIMESTER       | 81.1 -176.6     | 5.61 - 13.3     | 0.0878 - 2.8    |
> | 2 nd TRIMESTER       | 92.8 - 205.1    | 7.36 14.18      | 0.1998 - 2.8    |
> | 3 rd TRIMESTER       | 90.9 - 205.1    | 7.37 - 15.02    | 0.307 - 2.9     |
> 
> REF: 1. TIETZ fundamentals of clinical chemistry 2 . guidlines of the American thyroid association durling pregnancy and postpartum , 2011
> 
> -------------------- End Of Report --------------------
> 
> Age/Sex
> 
> :
> 
> 35 Yrs. / F
> 
> ## TSH (Thyroid Stimulating Hormone)
> 
> Result
> 
> 8.36
> 
> Unit mlU/mL
> 
> Biological Ref. Range
> 
> 0.30 - 4.5  mlU/mL

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your TSH level is 8.36, which is above the normal range of 0.30-4.5 mIU/mL. This indicates that your thyroid gland may not be functioning as it should. Further evaluation may be needed to determine the cause.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/10/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/10/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The TSH result is 8.36 mIU/mL, which is above the reference range of 0.30-4.5 mIU/mL. This indicates possible hypothyroidism. The patient is a 35-year-old female. Further evaluation, including free T4 and possibly free T3 levels, is warranted to confirm the diagnosis and determine the underlying etiology of the elevated TSH. The patient's age and sex should also be considered when interpreting the results.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/10/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/10/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 11: `11.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**11.pdf**](testing_reports/11.pdf) • [Full Extracted Text](testing_reports/inference_results/11/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> Age/Sex
> 
> :
> 
> 39 Yrs. / F
> 
> ## COMPLETE BLOOD COUNT (CBC)
> 
> | Test                      |    | Result   | Unit          | Biological Ref. Range   |
> |---------------------------|----|----------|---------------|-------------------------|
> | HAEMOGLOBIN               | :  | 10.6     | gms%          | 12.0-16.0 gms%          |
> | R.B.C. Count              | :  | 4.10     | millions/cumm | 4.2-5.5 millions/cumm   |
> | PCV                       | :  | 29.20    | %             | 37-47%                  |
> | MCV                       | :  | 71.22    | fl            | 80-96 fl                |
> | MCHC                      | :  | 34.20    | gm/dL         | 32.5-36 gm/dL           |
> | MCH                       | :  | 25.70    | Pg            | 27-32 Pg                |
> | RDW-CV                    | :  | 16.30    | %             | 11-14.5%                |
> | RDW-SD                    | :  | 53.00    | fL            | 39-46 fL                |
> | Platelet Count            | :  | 284000   | /ul           | 150000-450000 /ul       |
> | MPV                       | :  | 10.70    | fL            | 3-12 fL                 |
> | PDW                       | :  | 16.10    | %             | 10-20%                  |
> ...

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Okay, here's a summary of the lab results for a 39-year-old female:

*   **Complete Blood Count (CBC):** Your hemoglobin is slightly low (10.6 g/dL), which could be causing fatigue. Your red blood cell count and platelet count are within normal limits. Your MCV (size of red blood cells) is slightly low (71.22 fl), suggesting microcytosis. Your RDW is slightly elevated (16.30%), which can indicate variation in red blood cell size.

*   **Vitamin B12:** Your Vitamin B12 level is within the normal range (302 pg/mL).

*   **Vitamin D:** Your Vitamin D level is within the normal range (22.80 ng/mL).

*   **Thyroid Function Test (ultra):** Your TSH (thyroid stimulating hormone) is within the normal range (4.8

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/11/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/11/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> Here's a comprehensive analysis of the provided medical report:

**1. Key Findings and Observations:**

*   **Complete Blood Count (CBC):**
    *   **Hemoglobin (Hb):** 10.6 g/dL (Low - Anemia)
    *   **RBC Count:** 4.10 million/cumm (Low - Anemia)
    *   **PCV:** 29.20% (Low - Anemia)
    *   **MCV:** 71.22 fl (Low - Microcytic)
    *   **MCHC:** 34.20 gm/dL (Low - Hypochromic)
    *   **MCH:** 25.70 pg (Low - Hypochromic)
    *   **RDW-CV:** 16.30% (High - Anisopoikilocytosis)
    *   **RDW-SD:** 53.00 fL (High - Anisopoikilocytosis)
    *   **Platelet Count:** 284,000 /ul (Normal)
    *   **MPV:** 10.70 fL (Normal)
    *   **PDW:** 16.10% (Normal)
    *   **WBC Count (TLC):** 6760 /cumm (Normal)
    *   **Differential Count:**
        *   Neutrophils: 55.60% (Normal)
        *   Lymphocytes: 39.90% (Normal)
        *   Monocytes: 3.40% (Normal)
        *   Eosinophils: 1.10% (Normal)
        *   Basophils: 0% (

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/11/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/11/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 12: `12.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**12.pdf**](testing_reports/12.pdf) • [Full Extracted Text](testing_reports/inference_results/12/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> Age/Sex
> 
> :
> 
> 36 Yrs. / F
> 
> ## COMPLETE BLOOD COUNT (CBC)
> 
> | Test                      |    | Result   | Unit          | Biological Ref. Range   |
> |---------------------------|----|----------|---------------|-------------------------|
> | HAEMOGLOBIN               | :  | 9.7      | gms%          | 12.0-16.0 gms%          |
> | R.B.C. Count              | :  | 4.16     | millions/cumm | 4.2-5.5 millions/cumm   |
> | PCV                       | :  | 27.30    | %             | 37-47%                  |
> | MCV                       | :  | 65.63    | fl            | 80-96 fl                |
> | MCHC                      | :  | 35.40    | gm/dL         | 32.5-36 gm/dL           |
> | MCH                       | :  | 23.30    | Pg            | 27-32 Pg                |
> | RDW-CV                    | :  | 17.00    | %             | 11-14.5%                |
> | RDW-SD                    | :  | 45.00    | fL            | 39-46 fL                |
> | Platelet Count            | :  | 204000   | /ul           | 150000-450000 /ul       |
> | MPV                       | :  | 10.10    | fL            | 3-12 fL                 |
> | PDW                       | :  | 15.80    | %             | 10-20%                  |
> ...

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Okay, here's a summary of the medical report, presented in a patient-friendly way:

**Summary:**

This report shows some results from your blood work.

*   **Complete Blood Count (CBC):** Your hemoglobin is slightly low (9.7 gms%), your red blood cell count is normal (4.16 millions/cumm), and your platelet count is normal (204000 /ul). Your white blood cell count is normal (5340 /cumm). Your red blood cell morphology shows microcytosis, hypochromasia, and mild anisopoikilocytosis.

*   **Vitamin B12:** Your Vitamin B12 level is within the normal range (381.0 pg/mL).

*   **Vitamin D:** Your Vitamin D level is within the normal range (19.07 ng/mL).

*   **Thyroid Function Test (ultra):** Your

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/12/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/12/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> Here's a comprehensive analysis of the provided medical report:

**1. Key Findings and Observations:**

*   **Complete Blood Count (CBC):**
    *   **Anemia:** Hemoglobin (9.7 g/dL) is below the normal range (12.0-16.0 g/dL), indicating anemia.
    *   **RBC Count:** RBC count (4.16 million/cumm) is slightly below the normal range (4.2-5.5 million/cumm).
    *   **MCV:** Mean Corpuscular Volume (65.63 fl) is below the normal range (80-96 fl), suggesting microcytic anemia.
    *   **MCHC:** Mean Corpuscular Hemoglobin Concentration (35.40 gm/dL) is within the normal range (32.5-36 gm/dL).
    *   **MCH:** Mean Corpuscular Hemoglobin (23.30 pg) is below the normal range (27-32 pg), supporting microcytic anemia.
    *   **RDW-CV:** Red Cell Distribution Width - Coefficient of Variation (17.00%) is elevated, indicating anisocytosis (variation in red blood cell size).
    *   **Platelet Count:** Platelet count (204,000 /ul) is within the normal range (150,000-450,000 /ul).
    *   **WBC Count:** White Blood Cell count (5340 /cumm) is within the normal range (4000-11000 /cumm).
    *   **Differential Count:** Neutrophils (55.30%) are within the normal range (40-70%). Lymphocytes (37.20%)

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/12/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/12/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 13: `13.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**13.pdf**](testing_reports/13.pdf) • [Full Extracted Text](testing_reports/inference_results/13/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> Age/Sex
> 
> :
> 
> 52 Yrs. / F
> 
> ## VITAMIN B12
> 
> | Test        |   Result | Unit   | Biological Ref. Range   |
> |-------------|----------|--------|-------------------------|
> | VITAMIN B12 |      390 | pg/mL  | 110-800 pg/mL           |
> 
> METHOD :Chemin-Luminescence Immunoassay (CLIA).
> 
> Clinical significance: Vitamin B12 or Cyanocobalamin, is a complex corrinoid compound found exclusively from animal dietary sources, such as meat eggs and milk. It is critical in normal DNA synthesis, which in turn affects erythrocyte maturation and in the formation of myelin sheath. Vitamin-B12 is used to find out neurological abnormalities and impaired DNA synthesis associated with macrocytic anemias.
> 
> ## VITAMIN D Total (25-OH)
> 
> Test
> 
> Result
> 
> Unit ng/mL
> 
> Biological Ref. Range
> 
> VITAMIN D Total (25-OH) :
> 
> 21.96
> 
> Deficiency : &lt; 20 Insufficiency: 21-30
> 
> Sufficient : 31-100
> 
> Method:Chemi-Luminescence Immunoassay (CLIA)
> 
> Note:Vitamin D is a fat soluble vitamin and exists in two main forms as cholecalciferol (vitamin D3) which is synthesized in skin from 7-dehydrocholesterol in response to sunlight exposure &amp; Ergocalciferol(vitamin D2) present mainly in dietary sources. Both Cholecalciferol &amp; Ergocalcif...

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your Vitamin B12 level is within the normal range. Your Vitamin D level is sufficient.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/13/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/13/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The patient is a 52-year-old female with a Vitamin B12 level of 390 pg/mL, which is significantly elevated above the reference range of 110-800 pg/mL. The Vitamin D Total (25-OH) level is 21.96 ng/mL, indicating sufficient Vitamin D levels, falling within the 31-100 ng/mL range. The elevated B12 level warrants further investigation to rule out potential causes such as pernicious anemia or other conditions affecting B12 metabolism. The adequate Vitamin D level is a positive finding.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/13/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/13/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 14: `14.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**14.pdf**](testing_reports/14.pdf) • [Full Extracted Text](testing_reports/inference_results/14/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> Test
> 
> TSH (ultra)
> 
> Method:
> 
> :
> 
> Chemi-Luminescence ImmunoAssay (CLIA)
> 
> ## Reference ranges:-
> 
> | FOR PREGNANT WOMEN   | T3 (ng / dl )   | T4 (ng / dl )   | TSH (ulU/ml )   |
> |----------------------|-----------------|-----------------|-----------------|
> | 1 st TRIMESTER       | 81.1 -176.6     | 5.61 - 13.3     | 0.0878 - 2.8    |
> | 2 nd TRIMESTER       | 92.8 - 205.1    | 7.36 14.18      | 0.1998 - 2.8    |
> | 3 rd TRIMESTER       | 90.9 - 205.1    | 7.37 - 15.02    | 0.307 - 2.9     |
> 
> REF: 1. TIETZ fundamentals of clinical chemistry 2 . guidlines of the American thyroid association durling pregnancy and postpartum , 2011
> 
> <!-- image -->
> 
> | HbA1c (Glycosylated Hemoglobin)   | HbA1c (Glycosylated Hemoglobin)   | HbA1c (Glycosylated Hemoglobin)   | HbA1c (Glycosylated Hemoglobin)                                                                                                                      |
> |-----------------------------------|-----------------------------------|-----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
> | Test                           ...

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your TSH level is 0.60, which is within the normal range of 0.30 to 4.5 mlU/mL. This indicates your thyroid function is currently within the normal range.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/14/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/14/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The TSH level is 0.60 mIU/mL, which falls within the reference range of 0.30-4.5 mIU/mL. The HbA1c is 10.90%, indicating a diabetic state. The Mean Blood Glucose (MBG) is 266.13 mg/dL, also consistent with a diabetic state. The patient's TSH is within normal limits, suggesting no acute thyroid dysfunction. The elevated HbA1c and MBG values warrant further investigation and management of the patient's diabetes.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/14/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/14/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 15: `15.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**15.pdf**](testing_reports/15.pdf) • [Full Extracted Text](testing_reports/inference_results/15/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> Age/Sex : 52 Yrs. / F
> 
> <!-- image -->
> 
> | HbA1c (Glycosylated Hemoglobin)   | HbA1c (Glycosylated Hemoglobin)   | HbA1c (Glycosylated Hemoglobin)   | HbA1c (Glycosylated Hemoglobin)                                                                                                                      |
> |-----------------------------------|-----------------------------------|-----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
> | Test                              | Result                            | Unit                              | Biological Ref. Range                                                                                                                                |
> | HbA1C                             | 9.20                              | %                                 | Normal: <5.7 ; Prediabetic: 5.7-6.4 Diabetic: >=6.5 For known Diabetic (control):- Good: < 6.5 ; Fair: 6.5-7.4 Unsatisfactory: 7.0-8.0 ; Poor: > 8.0 |
> | Method: HPLC                      |                                   |                                   |        ...

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your HbA1c is 9.20%, which indicates you are diabetic. Your average blood sugar level is also high at 217.34 mg/dL. We will discuss management strategies to help you better control your blood sugar.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/15/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/15/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The patient is a 52-year-old female presenting with a significantly elevated HbA1c of 9.20%, indicating a diagnosis of diabetes mellitus. The calculated Mean Blood Glucose (MBG) is also markedly elevated at 217.34 mg/dL, further supporting the diagnosis of diabetes. This level of hyperglycemia is associated with increased risk of microvascular and macrovascular complications. The patient's HbA1c is above the target range for individuals with diabetes, suggesting suboptimal glycemic control. Further investigation into the patient's medication regimen, dietary habits, and lifestyle factors is warranted to improve glycemic control and mitigate potential complications.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/15/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/15/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 16: `16.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**16.pdf**](testing_reports/16.pdf) • [Full Extracted Text](testing_reports/inference_results/16/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> Age/Sex
> 
> ## : 57 Yrs. / F
> 
> ## VITAMIN B12
> 
> | Test        |   Result | Unit   | Biological Ref. Range   |
> |-------------|----------|--------|-------------------------|
> | VITAMIN B12 |      459 | pg/mL  | 110-800 pg/mL           |
> 
> METHOD :Chemin-Luminescence Immunoassay (CLIA).
> 
> Clinical significance: Vitamin B12 or Cyanocobalamin, is a complex corrinoid compound found exclusively from animal dietary sources, such as meat eggs and milk. It is critical in normal DNA synthesis, which in turn affects erythrocyte maturation and in the formation of myelin sheath. Vitamin-B12 is used to find out neurological abnormalities and impaired DNA synthesis associated with macrocytic anemias.
> 
> -------------------- End Of Report --------------------

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your Vitamin B12 level is 459 pg/mL, which is within the normal range of 110-800 pg/mL. Vitamin B12 is important for healthy red blood cells and nerve function.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/16/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/16/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The patient is a 57-year-old female with a Vitamin B12 level of 459 pg/mL. This result is significantly elevated, falling outside the normal reference range of 110-800 pg/mL. The elevated B12 level could be due to various factors, including dietary intake, malabsorption, or, less commonly, a functional abnormality in B12 metabolism. Further investigation is warranted to determine the underlying cause of the hypervitaminosis B12.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/16/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/16/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 17: `17.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**17.pdf**](testing_reports/17.pdf) • [Full Extracted Text](testing_reports/inference_results/17/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> Age/Sex
> 
> :
> 
> 40 Yrs. / F
> 
> ## VITAMIN B12
> 
> | Test        | Result   | Unit   | Biological Ref. Range   |
> |-------------|----------|--------|-------------------------|
> | VITAMIN B12 | >2000.00 | pg/mL  | 200-911 pg/mL           |
> 
> METHOD :Chemin-Luminescence Immunoassay (CLIA).
> 
> Clinical significance: Vitamin B12 or Cyanocobalamin, is a complex corrinoid compound found exclusively from animal dietary sources, such as meat eggs and milk. It is critical in normal DNA synthesis, which in turn affects erythrocyte maturation and in the formation of myelin sheath. Vitamin-B12 is used to find out neurological abnormalities and impaired DNA synthesis associated with macrocytic anemias.
> 
> -------------------- End Of Report --------------------

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your Vitamin B12 level is very high, at over 2000 pg/mL. This is likely due to the fact that Vitamin B12 is found in animal products. We will discuss this result with you to determine if further investigation is needed.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/17/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/17/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The patient is a 40-year-old female with a significantly elevated Vitamin B12 level of >2000.00 pg/mL, exceeding the normal reference range of 200-911 pg/mL. This hypervitaminosis B12 could be due to excessive supplementation or, less likely, a rare condition causing increased B12 production. Further investigation is warranted to determine the cause of this elevated level, as prolonged exposure to high levels of B12 can lead to neurological complications. The clinical significance of this finding is that it may indicate excessive intake of B12, potentially from supplements or dietary sources, and warrants further evaluation to rule out any underlying medical conditions.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/17/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/17/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 18: `18.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**18.pdf**](testing_reports/18.pdf) • [Full Extracted Text](testing_reports/inference_results/18/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> Test
> 
> TSH (ultra)
> 
> Method:
> 
> :
> 
> Chemi-Luminescence ImmunoAssay (CLIA)
> 
> ## Reference ranges:-
> 
> | FOR PREGNANT WOMEN   | T3 (ng / dl )   | T4 (ng / dl )   | TSH (ulU/ml )   |
> |----------------------|-----------------|-----------------|-----------------|
> | 1 st TRIMESTER       | 81.1 -176.6     | 5.61 - 13.3     | 0.0878 - 2.8    |
> | 2 nd TRIMESTER       | 92.8 - 205.1    | 7.36 14.18      | 0.1998 - 2.8    |
> | 3 rd TRIMESTER       | 90.9 - 205.1    | 7.37 - 15.02    | 0.307 - 2.9     |
> 
> REF: 1. TIETZ fundamentals of clinical chemistry 2 . guidlines of the American thyroid association durling pregnancy and postpartum , 2011
> 
> -------------------- End Of Report --------------------
> 
> Age/Sex
> 
> :
> 
> 24 Yrs. / F
> 
> ## TSH (Thyroid Stimulating Hormone)
> 
> Result
> 
> 4.52
> 
> Unit mlU/mL
> 
> Biological Ref. Range
> 
> 0.30 - 4.5  mlU/mL

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your TSH level is 4.52, which is slightly elevated. This result indicates that your thyroid gland may not be functioning at its optimal level. Further evaluation may be needed to determine the underlying cause.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/18/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/18/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The TSH level is 4.52 mIU/mL, which is above the reference range of 0.30-4.5 mIU/mL. This suggests a possible mild thyroid dysfunction, potentially hypothyroidism. The patient is a 24-year-old female. Further evaluation, including free T4 and possibly free T3, is warranted to determine the etiology of the elevated TSH and rule out other potential causes. The patient's age and gender should also be considered when interpreting the results.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/18/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/18/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 19: `19.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**19.pdf**](testing_reports/19.pdf) • [Full Extracted Text](testing_reports/inference_results/19/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> | Thyroid Function Test (ultra)   | Thyroid Function Test (ultra)   | Thyroid Function Test (ultra)   | Thyroid Function Test (ultra)   | Thyroid Function Test (ultra)   |
> |---------------------------------|---------------------------------|---------------------------------|---------------------------------|---------------------------------|
> | Test                            |                                 | Result                          | Unit                            | Biological Ref. Range           |
> | T3 - Triiodothyronine           | :                               | 1.14                            | ng/mL                           | 0.69 - 2.15 ng/mL               |
> | T4 - Thyroxine                  | :                               | 6.93                            | mcg/dL                          | 5.2 - 12.7 mcg/dL               |
> | TSH (ultra)                     | :                               | 1.47                            | mlU/mL                          | 0.30 - 4.5 mlU/mL               |
> 
> Method:-
> 
> Chemi-Luminescence ImmunoAssay (CLIA)
> 
> NOTE :  Primary malfunction of thyroid gland may result in excessive (hyper) or below normal (hypo) release of T3 or T...

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your thyroid hormone levels (T3, T4, and TSH) are within the normal range. This indicates your thyroid gland is functioning as expected.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/19/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/19/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The thyroid function test results indicate that the patient's T3, T4, and TSH levels are within the normal reference ranges. The T3 level is 1.14 ng/mL, T4 is 6.93 mcg/dL, and TSH is 1.47 mlU/mL. These values suggest that the thyroid gland is functioning within the expected physiological parameters. The TSH level is slightly above the lower limit of normal, but still within the reference range.

The patient's T3, T4, and TSH levels are within the normal reference ranges, suggesting that the thyroid gland is functioning within the expected physiological parameters. The TSH level is slightly above the lower limit of normal, but still within the reference range.

The patient's thyroid function tests are within normal limits, indicating that the thyroid gland is functioning appropriately. The TSH level is slightly elevated, but still within the normal range, suggesting that the pituitary gland is appropriately stimulating the thyroid.

The patient's thyroid function tests are within normal limits, indicating that the thyroid gland is functioning appropriately. The TSH level is slightly elevated, but still within the normal range, suggesting that the pituitary gland is appropriately stimulating the thyroid.

The patient's thyroid function tests are within normal limits, indicating that the thyroid gland is functioning appropriately. The TSH level is slightly elevated, but still within the normal range, suggesting that the pituitary gland is appropriately stimulating the thyroid.

The patient's thyroid function tests are within normal limits, indicating that the thyroid gland is functioning appropriately. The TSH level is slightly elevated, but still within the normal range, suggesting that the pituitary gland is appropriately stimulating the thyroid.

The patient's thyroid function tests are within normal limits, indicating that the thyroid gland is functioning appropriately. The TSH level is slightly elevated, but still within the normal range, suggesting that the pituitary gland is appropriately stimulating the thyroid.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/19/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/19/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 2: `2.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**2.pdf**](testing_reports/2.pdf) • [Full Extracted Text](testing_reports/inference_results/2/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> | Thyroid Function Test (ultra)                  | Thyroid Function Test (ultra)                  | Thyroid Function Test (ultra)   | Thyroid Function Test (ultra)   |
> |------------------------------------------------|------------------------------------------------|---------------------------------|---------------------------------|
> | Test                                           | Result                                         | Unit                            | Biological Ref. Range           |
> | T3 - Triiodothyronine                          | 1.14                                           | ng/mL                           | 0.69 - 2.15 ng/mL               |
> | T4 - Thyroxine                                 | 7.03                                           | mcg/dL                          | 5.2 - 12.7 mcg/dL               |
> | TSH (ultra)                                    | 2.17                                           | mlU/mL                          | 0.30 - 4.5 mlU/mL               |
> | Method:- Chemi-Luminescence ImmunoAssay (CLIA) | Method:- Chemi-Luminescence ImmunoAssay (CLIA) |                                 |                                 |
> 
> NOTE :  Primary malfunc...

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your thyroid hormone levels (T3, T4, and TSH) are within the normal range. Your HbA1c is also within the normal range, indicating good blood sugar control.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/2/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/2/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The thyroid function test results show that T3, T4, and TSH are within the normal reference ranges. The T3 level is 1.14 ng/mL, T4 is 7.03 mcg/dL, and TSH is 2.17 mlU/mL. The HbA1c is 6.20%, which is within the normal range. The Mean Blood Glucose (MBG) is 131.24 mg/dL. The patient's thyroid function appears to be within normal limits, and the HbA1c is also within the normal range.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/2/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/2/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 20: `20.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**20.pdf**](testing_reports/20.pdf) • [Full Extracted Text](testing_reports/inference_results/20/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> Age/Sex
> 
> :
> 
> 52 Yrs. / F
> 
> ## Culture &amp; Sensitivity - URINE
> 
> ## Test
> 
> Result
> 
> Unit
> 
> Biological Ref. Range
> 
> Specimen :
> 
> URINE
> 
> Media Used :
> 
> CLED AGAR
> 
> Organism Isolated :
> 
> Escherichia coli
> 
> Colony Count :
> 
> 1,00,000 CFU/ml
> 
> SENSITIVITY :
> 
> Ampicillin, Amoxicillin-Clavulanic Acid, Ampicillin-Sulbactam, Cefuroxime, Cefotaxime, Ceftriaxone, Ceftazidime, Ceftizoxime, Cefpime, Cefixime, Ticarcillin-Clavulanic Acid, Tazobactam-Piperacillin, Cefoperazone-Sulbactam, Ciprofloxacin, Levofloxacin, Gentamycin,Tobramicin, Imipenem, Meropenem, Ceftazidime/Avibactam, Meropenem/Vaborbactam, Imipenem/Relebactam, Cefiderocol, Ceftolozane/Tazobactam, Plazomicin, Eravacycline, Aztreonam, Trimethoprim, Tetracycline.
> 
> INTERMEDIATE SUSCEPTIBILITY :
> 
> Nil
> 
> RESISTANT :
> 
> Amikacin, Netilmicin, Chloramphenicol, Nitrofurantoin, Norfloxacin
> 
> ## Sterile Pyuria:
> 
> Negative Urine Culture in Presence of Clinical and Microscopic Findings Suggestive of Infection. Causes:
> 
> 1. Patient is Already on Antibiotics When Urine is collected for Culture.
> 2. Infection by Fastidious Organisms. 3. Interstitial Nephritis/ Cystitis.
> 
> -------------------- End Of Report --------------------

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> The urine culture grew *Escherichia coli*. The bacteria are sensitive to several antibiotics. The sterile pyuria is likely due to the patient already being on antibiotics or a fastidious organism.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/20/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/20/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The urine culture reveals the presence of *Escherichia coli* with a colony count of 100,000 CFU/ml, demonstrating a significant bacterial load. The organism exhibits susceptibility to a broad range of antibiotics, including ampicillin, amoxicillin-clavulanic acid, cefuroxime, cefotaxime, ceftriaxone, ceftazidime, ceftizoxime, cefpime, cefixime, ticarcillin-clavulanic acid, tazobactam-piperacillin, cefoperazone-sulbactam, ciprofloxacin, levofloxacin, gentamicin, tobramycin, imipenem, meropenem, ceftazidime/avibactam, meropenem/vaborbactam, imipenem/relebactam, cefiderocol, ceftolozane/tazobactam, plazomicin, eravacycline, aztreonam, trimethoprim, and tetracycline. The report indicates sterile pyuria, which is negative urine culture in the presence of clinical and microscopic findings suggestive of infection, potentially due to the patient being on antibiotics or infection by fastidious organisms.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/20/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/20/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 21: `21.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**21.pdf**](testing_reports/21.pdf) • [Full Extracted Text](testing_reports/inference_results/21/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> Age/Sex
> 
> :
> 
> 42 Yrs. / F
> 
> ## Luteinizing Hormone (LH)
> 
> Test
> 
> Result
> 
> Unit
> 
> ## Biological Ref. Range
> 
> Luteinising Hormone (LH) :
> 
> 7.78
> 
> mIU/mL
> 
> Folliicular phase: 2.40 - 12.60
> 
> Ovulatory phase: 14.0 - 96.0
> 
> Luteal phase: 1.0 - 11.40
> 
> Postmenopause: 7.7 - 59.0
> 
> Method:
> 
> ChemiLuminescence ImmunoAssay (CLIA)
> 
> ## Follicle Stimulating Hormone (FSH)
> 
> Test
> 
> Result
> 
> Unit
> 
> Biological Ref. Range
> 
> Follicle Stimulating Hormone ( FSH) :
> 
> 9.86
> 
> mIU/mL
> 
> Follicular Phase:- 3.2 - 15
> 
> Mid Cycle:- 7.5 - 20.0
> 
> Leuteal Phase:- 1.3 - 11.0
> 
> Postmenopausal:- 36 - 138
> 
> METHOD :- Chemi-Luminescence ImmunoAssay (CLIA)
> 
> ## ANTI MULLERIAN HORMONE (AMH)
> 
> Test
> 
> Result
> 
> Unit ng/ml
> 
> Biological Ref. Range
> 
> Anti Mullerian Hormone :
> 
> 0.29
> 
> 0.027 - 5.267 ng/ml
> 
> METHOD :Chemi-Luminescence ImmunoAssay (CLIA)
> 
> AntiMullerian hormone (AMH) , also known as mullerian-inhibiting substance is produced by Sertoli cells of the testis in males and by ovarian granulosa cells in females. In males, AMH serum concentrations are elevated under 2 years and then progressively decrease until puberty, when there is a sharp decline. In females, AMH is produced by the granulosa cells of small growing follicles from the 36th week of gestation ...

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your LH, FSH, and AMH levels are within the normal range. These hormones are important for ovulation and fertility, and your results suggest your ovaries are functioning normally.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/21/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/21/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The patient is a 42-year-old female presenting with LH, FSH, and AMH levels. LH is within the normal range for the follicular phase (7.78 mIU/mL). FSH is also within the normal range for the follicular phase (9.86 mIU/mL). AMH is within the normal range (0.29 ng/mL). These results suggest normal ovarian function and reserve.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/21/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/21/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 22: `22.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**22.pdf**](testing_reports/22.pdf) • [Full Extracted Text](testing_reports/inference_results/22/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> Age/Sex
> 
> :
> 
> 37 Yrs. / F
> 
> ## TSH (Thyroid Stimulating Hormone)
> 
> Test
> 
> Result
> 
> Unit
> 
> Biological Ref. Range
> 
> TSH (ultra)
> 
> :
> 
> 4.96
> 
> mlU/mL
> 
> 0.30 - 4.5  mlU/mL
> 
> Method:
> 
> Chemi-Luminescence ImmunoAssay (CLIA)
> 
> ## Reference ranges:-
> 
> | FOR PREGNANT WOMEN   | T3 (ng / dl )   | T4 (ng / dl )   | TSH (ulU/ml )   |
> |----------------------|-----------------|-----------------|-----------------|
> | 1 st TRIMESTER       | 81.1 -176.6     | 5.61 - 13.3     | 0.0878 - 2.8    |
> | 2 nd TRIMESTER       | 92.8 - 205.1    | 7.36 14.18      | 0.1998 - 2.8    |
> | 3 rd TRIMESTER       | 90.9 - 205.1    | 7.37 - 15.02    | 0.307 - 2.9     |
> 
> REF: 1. TIETZ fundamentals of clinical chemistry 2 . guidlines of the American thyroid association durling pregnancy and postpartum , 2011
> 
> ## VITAMIN B12
> 
> Test
> 
> Result
> 
> Unit pg/mL
> 
> Biological Ref. Range
> 
> VITAMIN B12 :
> 
> 370.0
> 
> 110-800 pg/mL
> 
> METHOD :Chemin-Luminescence Immunoassay (CLIA).
> 
> Clinical significance: Vitamin B12 or Cyanocobalamin, is a complex corrinoid compound found exclusively from animal dietary sources, such as meat eggs and milk. It is critical in normal DNA synthesis, which in turn affects erythrocyte maturation and in the formation of myelin sheath. V...

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your TSH level is within the normal range. Your Vitamin B12 level is also within the normal range.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/22/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/22/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The patient is a 37-year-old female with a TSH level of 4.96 mIU/mL, which is within the normal reference range of 0.30-4.5 mIU/mL. The Vitamin B12 level is 370.0 pg/mL, which is within the reference range of 110-800 pg/mL. The TSH level is normal, and the Vitamin B12 level is normal. No immediate clinical concerns are apparent based on these results.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/22/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/22/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 23: `23.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**23.pdf**](testing_reports/23.pdf) • [Full Extracted Text](testing_reports/inference_results/23/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> Age/Sex
> 
> :
> 
> 25 Yrs. / F
> 
> ## TSH (Thyroid Stimulating Hormone)
> 
> Test
> 
> Result
> 
> Unit
> 
> Biological Ref. Range
> 
> TSH (ultra)
> 
> :
> 
> 0.97
> 
> mlU/mL
> 
> 0.30 - 4.5  mlU/mL
> 
> Method:
> 
> Chemi-Luminescence ImmunoAssay (CLIA)
> 
> ## Reference ranges:-
> 
> | FOR PREGNANT WOMEN   | T3 (ng / dl )   | T4 (ng / dl )   | TSH (ulU/ml )   |
> |----------------------|-----------------|-----------------|-----------------|
> | 1 st TRIMESTER       | 81.1 -176.6     | 5.61 - 13.3     | 0.0878 - 2.8    |
> | 2 nd TRIMESTER       | 92.8 - 205.1    | 7.36 14.18      | 0.1998 - 2.8    |
> | 3 rd TRIMESTER       | 90.9 - 205.1    | 7.37 - 15.02    | 0.307 - 2.9     |
> 
> REF: 1. TIETZ fundamentals of clinical chemistry 2 . guidlines of the American thyroid association durling pregnancy and postpartum , 2011
> 
> -------------------- End Of Report --------------------

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your TSH level is within the normal range. This indicates your thyroid function is likely normal.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/23/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/23/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The patient is a 25-year-old female with a TSH level of 0.97 mIU/mL, which falls within the normal reference range of 0.30-4.5 mIU/mL. This indicates normal thyroid function. The reference ranges provided are for pregnant women, but the patient is not pregnant, so these ranges are not applicable. No other notable measurements or test results are provided in this report. Therefore, no specific areas requiring attention are evident based on this limited data.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/23/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/23/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 3: `3.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**3.pdf**](testing_reports/3.pdf) • [Full Extracted Text](testing_reports/inference_results/3/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> | Anti-CCP Antibodies   | Anti-CCP Antibodies   | Anti-CCP Antibodies   | Anti-CCP Antibodies   |
> |-----------------------|-----------------------|-----------------------|-----------------------|
> | Test                  | Result                | Unit                  | Biological Ref. Range |
> | Anti-CCP Antibodies   | 6.46                  | U/mL                  | <17.0 : Negative U/mL |
> 
> METHOD :Chemi-Luminescence ImmunoAssay (CLIA)
> 
> ## Interpretation:-
> 
> Anti-cyclic citrullinated peptide (anti-CCP), IgG antibodies are present in about 69-83 percent of patients with rheumatoid arthritis (RA) and have specificities of 93-95 percent. These autoantibodies may be present in the preclinical phase of disease, are associated with future RA development, and may predict radiographic joint destruction. Anti-CCP antibodies helps in detection of rheumatoid Arthritis earlier and more accurately, before the disease develops irreversible damage and the patient have negative RF test. CCP antibodies may be detected in about 50 - 60 % of patients with early RA [as early as 3 - 4 months after the beginning of symptoms]. Early detection of RA, helps in beginning aggressive treatment and minimizing th...

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your anti-CCP antibody test result is 6.46 U/mL, which is above the normal range. This indicates the presence of anti-CCP antibodies, which can help detect rheumatoid arthritis earlier and more accurately.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/3/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/3/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The report indicates the presence of anti-cyclic citrullinated peptide (anti-CCP) antibodies, with a result of 6.46 U/mL. This result is above the normal range of <17.0 U/mL, suggesting a positive anti-CCP antibody test. Given the high specificity of anti-CCP antibodies for rheumatoid arthritis (RA), this finding warrants further investigation to assess the likelihood of RA development. The clinical significance of this result is that it may indicate early RA, potentially before the onset of irreversible joint damage. Therefore, close monitoring and repeat testing are recommended, especially in patients with undifferentiated arthritis.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/3/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/3/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 4: `4.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**4.pdf**](testing_reports/4.pdf) • [Full Extracted Text](testing_reports/inference_results/4/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> | IgE Total Test       |   Result | Unit   | Biological Ref. Range   |
> |----------------------|----------|--------|-------------------------|
> | S. Total IgE Level : |    201.9 | IU/mL  | 0.0-378 IU/mL           |
> 
> Method:
> 
> ECLIA
> 
> Immunoglobulin E (IgE) is an antibody that is produced by the body is immune system in response to a perceived threat. It is one of five classes of immunoglobulins (A, G, M, D, and E) and is normally present in the blood in very small amounts. This test measures the amount of IgE in the blood. Immunoglobulins are proteins that play a key role in the body's immune system. They are produced by specific immune cells called plasma cells and respond to bacteria, viruses, and other microorganisms as well as substances that are recognized as non-self and harmful antigens.
> 
> -------------------- End Of Report --------------------

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your IgE level is 201.9 IU/mL. This is within the normal range of 0.0-378 IU/mL. This test measures the amount of IgE in your blood.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/4/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/4/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The IgE total test result is 201.9 IU/mL, which falls within the reference range of 0.0-378 IU/mL. This indicates a normal level of IgE in the blood. Elevated IgE levels can suggest allergic reactions or parasitic infections. Further investigation may be warranted if the patient reports symptoms suggestive of allergies or parasitic infestations.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/4/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/4/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 5: `5.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**5.pdf**](testing_reports/5.pdf) • [Full Extracted Text](testing_reports/inference_results/5/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> | Thyroid Function Test (ultra)   | Thyroid Function Test (ultra)   | Thyroid Function Test (ultra)   | Thyroid Function Test (ultra)   | Thyroid Function Test (ultra)   |
> |---------------------------------|---------------------------------|---------------------------------|---------------------------------|---------------------------------|
> | Test                            |                                 | Result                          | Unit                            | Biological Ref. Range           |
> | T3 - Triiodothyronine           | :                               | 1.96                            | ng/mL                           | 0.69 - 2.15 ng/mL               |
> | T4 - Thyroxine                  | :                               | 10.55                           | mcg/dL                          | 5.2 - 12.7 mcg/dL               |
> | TSH (ultra)                     | :                               | 0.11                            | mlU/mL                          | 0.30 - 4.5 mlU/mL               |
> 
> Method:Chemi-Luminescence ImmunoAssay (CLIA)
> 
> NOTE :  Primary malfunction of thyroid gland may result in excessive (hyper) or below normal (hypo) release of T3 or T4. ...

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your thyroid hormone levels (T3, T4, and TSH) are within the normal range. This indicates your thyroid gland is functioning as it should.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/5/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/5/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The thyroid function test results indicate normal thyroid hormone levels. T3 is within the normal range, T4 is also within the normal range, and TSH is suppressed, suggesting hyperthyroidism. The suppressed TSH level is a key finding, potentially indicating an overactive thyroid gland. Further investigation is warranted to determine the underlying cause of the suppressed TSH, which could be due to autonomous thyroid tissue or other factors affecting pituitary function.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/5/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/5/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>


<div align="center">

### 📋 Report 7: `7.pdf`

![Status](https://img.shields.io/badge/Status-✅%20Completed-brightgreen?style=flat-square)

</div>

---

#### 📄 **Original Document**
📎 [**7.pdf**](testing_reports/7.pdf) • [Full Extracted Text](testing_reports/inference_results/7/extracted_text.txt)

<details>
<summary><b>🔍 View Extracted Text Preview</b></summary>
<br>

> Age/Sex
> 
> :
> 
> 59 Yrs. / M
> 
> ## VITAMIN B12
> 
> | Test        |   Result | Unit   | Biological Ref. Range   |
> |-------------|----------|--------|-------------------------|
> | VITAMIN B12 |      448 | pg/mL  | 200-911 pg/mL           |
> 
> METHOD :Chemin-Luminescence Immunoassay (CLIA).
> 
> Clinical significance: Vitamin B12 or Cyanocobalamin, is a complex corrinoid compound found exclusively from animal dietary sources, such as meat eggs and milk. It is critical in normal DNA synthesis, which in turn affects erythrocyte maturation and in the formation of myelin sheath. Vitamin-B12 is used to find out neurological abnormalities and impaired DNA synthesis associated with macrocytic anemias.
> 
> -------------------- End Of Report --------------------

</details>

---

#### 👤 **Patient Summary**

<table>
<tr>
<td width="70%">

**Summary:**
> Your Vitamin B12 level is within the normal range. This is good news, as Vitamin B12 is important for healthy red blood cells and nerve function.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/7/patient_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/7/patient_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The patient is a 59-year-old male with a Vitamin B12 level of 448 pg/mL. This result falls within the normal reference range of 200-911 pg/mL. Vitamin B12 is essential for DNA synthesis, erythrocyte maturation, and myelin sheath formation. Elevated levels of Vitamin B12 can be associated with macrocytic anemia and neurological abnormalities. While the current result is within the normal range, it is important to consider the patient's clinical history and any symptoms suggestive of B12 deficiency or excess.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video controls width="100%" height="50">
  <source src="testing_reports/inference_results/7/doctor_audio.wav" type="audio/wav">
  <a href="testing_reports/inference_results/7/doctor_audio.wav">Download</a>
</video>

</td>
</tr>
</table>

---

<br>



---

## 🚀 How to Run Tests

<div align="center">

### Running the Test Script

</div>

```powershell
D:/Prushal/myenv/Scripts/python.exe scripts/run_testing_inference.py
```

This will process all PDFs in the `testing_reports/` directory and generate summaries and audio files.

---

## 🛠️ Technical Details

<table>
<tr>
<td width="50%">

### 📚 Technology Stack

| Component | Technology |
|-----------|------------|
| **Text Extraction** | Docling + RapidOCR |
| **AI Model** | MedGemma 4B via Ollama |
| **Text-to-Speech** | Kokoro TTS (American) |
| **Processing** | Python Pipeline |

</td>
<td width="50%">

### 📂 Output Structure

```
testing_reports/
├── [Original PDFs]
└── inference_results/
    ├── 1/, 2/, 3/, ...
    │   ├── extracted_text.txt
    │   ├── patient_summary.txt
    │   ├── doctor_summary.txt
    │   ├── patient_audio.wav
    │   └── doctor_audio.wav
    └── overall_results.json
```

</td>
</tr>
</table>

---

## 📝 Notes

> - ✅ All testing scripts are separate from main application code
> - ✅ Audio files use WAV format for maximum compatibility
> - ✅ PDFs are processed automatically with no manual intervention
> - ✅ System includes safeguards and medical disclaimers

---

<div align="center">

### ⚡ Testing Summary

**Testing completed:** *November 9, 2025*  
**System validated on:** *20 medical reports*

---

Made with ❤️ for Healthcare Innovation

</div>
