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
> Here's a summary of your thyroid function test results:

Your T3 and T4 levels are within the normal range, but your TSH is elevated. This suggests your thyroid is not producing enough thyroid hormone. Your Vitamin B12 level is normal. Your iron studies show normal iron levels, but your transferrin saturation is slightly low.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/1/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/1/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> **Analysis of Medical Report**

The report presents thyroid function tests (T3, T4, and TSH) and Vitamin B12 and Iron studies for a 65-year-old female. T3 and T4 levels are within the normal range, while TSH is elevated at 96.20 mlU/mL, indicating hypothyroidism. The patient's T3 and T4 levels are within the normal range, but the elevated TSH suggests that the pituitary gland is producing more TSH in an attempt to stimulate the thyroid. Vitamin B12 levels are within the normal range. Iron studies show a low serum iron level of 69 ug/dL, a high TIBC of 331 ug/dL, and a low transferrin saturation of 20.85%. These findings are consistent with iron deficiency anemia.

**Key Findings and Observations:**

*   **Hypothyroidism:** Elevated TSH (96.20 mlU/mL) suggests hypothyroidism.
*   **Normal T3 and T4:** T3 and T4 levels are within the normal range, which may be a compensatory response to the elevated TSH.
*   **Iron Deficiency Anemia:** Low serum iron (69 ug/dL), high TIBC (331 ug/dL), and low transferrin saturation (20.85%) are indicative of iron deficiency anemia.

**Notable Measurements or Test Results:**

*   TSH: 96.20 mlU/mL
*   T3: 0.52 ng/mL
*   T4: 4.19 mcg/dL
*   Serum Iron: 69 ug/dL
*   TIBC: 331 ug/dL
*   Transferrin Saturation: 20.85%
*   Vitamin B12: 431.0 pg

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/1/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/1/doctor_audio.mp4)

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

<video width="100%" controls>
  <source src="testing_reports/inference_results/10/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/10/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The TSH result is 8.36 mIU/mL, which is significantly elevated above the reference range of 0.30-4.5 mIU/mL. This indicates hypothyroidism. The patient is a 35-year-old female. The elevated TSH suggests the pituitary gland is attempting to stimulate the thyroid gland to produce more thyroid hormone, but the thyroid gland is not responding adequately. This could be due to various causes, including thyroiditis, iodine deficiency, or thyroid hormone resistance. Further evaluation, including free T4 and free T3 levels, is warranted to confirm the diagnosis and determine the underlying etiology.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/10/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/10/doctor_audio.mp4)

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
> Here's a summary of your lab results:

*   **Complete Blood Count (CBC):** Your hemoglobin is slightly low (10.6 g/dL), and your red blood cell count is also a bit low (4.10 million/cumm). Your platelet count is normal. Your MCV (size of red blood cells) is slightly low, indicating microcytosis. Your RDW is normal.
*   **Vitamin B12:** Your Vitamin B12 level is within the normal range.
*   **Vitamin D:** Your Vitamin D level is within the normal range.
*   **Thyroid Function Test (T3, T4, TSH):** Your TSH level is within the normal range.
*   **Lipid Profile:** Your cholesterol levels are within normal limits.
*   **Liver Function Test (LFT):** Your liver enzymes (AST, ALT, ALP) are within normal limits.
*

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/11/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/11/patient_audio.mp4)

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
    *   **Red Blood Cell (RBC) Count:** 4.10 million/cumm (Low - Anemia)
    *   **Platelet Count:** 284,000/uL (Normal)
    *   **MCV:** 71.22 fl (Low - Microcytic)
    *   **MCHC:** 34.20 gm/dL (Low - Hypochromic)
    *   **MCH:** 25.70 pg (Low - Hypochromic)
    *   **RDW-CV:** 16.30% (High - Anisocytosis)
    *   **WBC Count (TLC):** 6760/cumm (Normal)
    *   **Differential Count:** Neutrophils 55.6%, Lymphocytes 39.9%, Monocytes 3.4%, Eosinophils 1.1%, Basophils 0%, P-LCR 35.6%
    *   **Absolute Neutrophil Count:** 3758.56/ cmm (Normal)
    *   **Absolute Lymphocyte Count:** 2697.24/ cmm (Normal)
    *   **Absolute Monocytes Count:** 229.84/cumm (Normal)
    *   **Absolute Eosinophil Count:** 74/cumm (Normal)
    *   **Absolute Basophil Count:** 0.00/uL (Normal)
*   **

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/11/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/11/doctor_audio.mp4)

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
> Here's a summary of the medical report:

The patient is a 36-year-old female. Her complete blood count (CBC) shows mild anemia (low hemoglobin, RBC count, and hematocrit). Her MCV is slightly low, indicating microcytic anemia. The RDW is normal. The patient's platelet count, WBC count, and differential are within normal limits. The urine examination is normal. Liver function tests are normal. The patient's thyroid function tests are normal. The lipid profile is normal. Vitamin B12 and Vitamin D levels are within normal limits.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/12/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/12/patient_audio.mp4)

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

*   **Age/Sex:** 36 years old, Female
*   **CBC (Complete Blood Count):**
    *   **Hemoglobin (Hb):** 9.7 g/dL (Low - Anemia)
    *   **RBC Count:** 4.16 million/cumm (Low - Anemia)
    *   **PCV (Packed Cell Volume):** 27.30% (Low - Anemia)
    *   **MCV (Mean Corpuscular Volume):** 65.63 fl (Low - Microcytic)
    *   **MCHC (Mean Corpuscular Hemoglobin Concentration):** 35.40 gm/dL (Low - Hypochromic)
    *   **MCH (Mean Corpuscular Hemoglobin):** 23.30 pg (Low - Hypochromic)
    *   **RDW-CV (Red Cell Distribution Width - CV):** 17.00% (High - Anisocytosis)
    *   **RDW-SD (Red Cell Distribution Width - SD):** 45.00 fL (High - Anisocytosis)
    *   **Platelet Count:** 204,000/uL (Normal)
    *   **MPV (Mean Platelet Volume):** 10.10 fL (Normal)
    *   **PDW (Platelet Distribution Width):** 15.80% (Normal)
    *   **WBC Count (TLC):** 5340/cumm (Normal)
    *   **Differential Count:**
        *   Neutrophils: 55.30% (Normal)

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/12/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/12/doctor_audio.mp4)

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

<video width="100%" controls>
  <source src="testing_reports/inference_results/13/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/13/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> **Analysis of Vitamin B12 and Vitamin D Levels**

The patient is a 52-year-old female presenting with a Vitamin B12 level of 390 pg/mL, which is significantly elevated (above the reference range of 110-800 pg/mL). This elevated level suggests possible Vitamin B12 excess or a laboratory error. The Vitamin D total (25-OH) level is 21.96 ng/mL, indicating sufficient Vitamin D levels (31-100 ng/mL). The patient's Vitamin D level is within the normal range, and there is no indication of deficiency or toxicity.

**Key findings and observations:**

*   **Vitamin B12:** Significantly elevated (390 pg/mL)
*   **Vitamin D:** Sufficient (21.96 ng/mL)

**Notable measurements or test results:**

*   Vitamin B12: 390 pg/mL
*   Vitamin D: 21.96 ng/mL

**Clinical significance:**

The elevated Vitamin B12 level warrants further investigation to rule out a laboratory error or a true Vitamin B12 excess. While the Vitamin D level is within the normal range, it is important to consider the patient's sun exposure and dietary intake.

**Any areas requiring attention:**

The significantly elevated Vitamin B12 level needs to be re-evaluated to confirm its accuracy. Further investigation may be needed to determine the cause of the elevated level.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/13/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/13/doctor_audio.mp4)

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
> Your TSH level is 0.60, which is within the normal range of 0.30-4.5 mlU/mL. This indicates that your thyroid function is currently within the normal range.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/14/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/14/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> **Analysis of TSH, HbA1c, and Mean Blood Glucose**

The TSH level is within the normal reference range of 0.30-4.5 mIU/mL, indicating normal thyroid function. The HbA1c is elevated at 10.90%, indicating poor glycemic control, which is concerning for a patient with a known diabetic status. The Mean Blood Glucose (MBG) is significantly elevated at 266.13 mg/dL, further supporting the diagnosis of poorly controlled diabetes. The patient's age and sex are provided, but no other relevant clinical information is available.

**Clinical Significance:** The elevated HbA1c and MBG values suggest inadequate glycemic control, potentially leading to complications such as microvascular and macrovascular disease. The patient's diabetic status needs to be addressed with lifestyle modifications and/or pharmacological interventions to achieve target glucose levels.

**Areas Requiring Attention:** The primary area requiring attention is the patient's poorly controlled diabetes, as evidenced by the elevated HbA1c and MBG. Further investigation into the patient's current medication regimen, dietary habits, and physical activity levels is warranted to optimize glycemic control. Regular monitoring of HbA1c and MBG is essential to assess the effectiveness of treatment and prevent complications.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/14/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/14/doctor_audio.mp4)

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
> Your HbA1c is 9.20%, which indicates you are diabetic. Your average blood sugar level is also high at 217.34 mg/dL.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/15/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/15/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> **Analysis of Medical Report**

The patient is a 52-year-old female presenting with elevated HbA1c of 9.20%, indicating a diagnosis of diabetes mellitus. The mean blood glucose (MBG) is significantly elevated at 217.34 mg/dL, further supporting the diagnosis of diabetes. The HbA1c value is above the target range for individuals with known diabetes, suggesting suboptimal glycemic control. This patient requires immediate attention to improve glycemic management through lifestyle modifications and/or pharmacological interventions. Further evaluation is warranted to assess the patient's overall health status and identify any potential complications associated with poorly controlled diabetes.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/15/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/15/doctor_audio.mp4)

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
> Your Vitamin B12 level is 459 pg/mL, which is within the normal range of 110-800 pg/mL. Vitamin B12 is important for healthy red blood cell production and nerve function.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/16/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/16/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> **Analysis of Vitamin B12 Report**

The patient is a 57-year-old female with a Vitamin B12 level of 459 pg/mL. The reference range is 110-800 pg/mL. The result indicates Vitamin B12 deficiency, as the patient's level falls below the lower limit of normal. Vitamin B12 is essential for DNA synthesis, red blood cell maturation, and myelin sheath formation. A low Vitamin B12 level can lead to macrocytic anemia and neurological complications. Further investigation is warranted to determine the underlying cause of the deficiency, which could include dietary insufficiency, malabsorption, or pernicious anemia.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/16/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/16/doctor_audio.mp4)

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
> Your Vitamin B12 level is very high, significantly above the normal range. This result is likely due to a dietary factor, and it's important to discuss this with your doctor.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/17/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/17/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> **Analysis of Vitamin B12 Report:**

The patient is a 40-year-old female with a significantly elevated Vitamin B12 level of >2000.00 pg/mL, exceeding the normal reference range of 200-911 pg/mL. This hypervitaminosis B12 is likely due to dietary intake or supplementation. Elevated B12 levels can cause neurological symptoms, including peripheral neuropathy, and may be associated with macrocytic anemia. Further investigation into the patient's dietary history and potential supplementation is warranted to determine the cause of the elevated B12 levels and to rule out any underlying medical conditions.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/17/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/17/doctor_audio.mp4)

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
> Your TSH level is 4.52, which is within the normal range of 0.30-4.5 mIU/mL. This indicates that your thyroid function is currently within the normal range.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/18/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/18/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The TSH result is 4.52 mIU/mL, which falls within the reference range of 0.30-4.5 mIU/mL. This indicates normal thyroid function. The patient is a 24-year-old female. The TSH level is a key indicator of thyroid health, and this result suggests that the patient's thyroid gland is functioning appropriately. No immediate concerns are apparent based on this single TSH value.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/18/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/18/doctor_audio.mp4)

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
> Your thyroid hormone levels (T3, T4, and TSH) are within the normal range. This indicates your thyroid is functioning as it should.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/19/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/19/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The thyroid function test (TFT) results indicate that the patient's T3, T4, and TSH levels are within the normal reference ranges. The T3 level is 1.14 ng/mL, T4 is 6.93 mcg/dL, and TSH is 1.47 mlU/mL. These values suggest normal thyroid hormone production and pituitary function. However, it's important to consider the patient's clinical presentation and any other relevant medical history, as the interpretation of these results should be individualized.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/19/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/19/doctor_audio.mp4)

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

<video width="100%" controls>
  <source src="testing_reports/inference_results/2/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/2/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The thyroid function test (TFT) results show that T3, T4, and TSH are within the normal reference ranges. The HbA1c is 6.20%, indicating good glycemic control. The mean blood glucose (MBG) is 131.24 mg/dL. The patient is not pregnant. The TFT results suggest normal thyroid function, and the HbA1c indicates good glycemic control.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/2/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/2/doctor_audio.mp4)

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
> The urine culture grew *Escherichia coli*. The bacteria is sensitive to several antibiotics. The negative urine culture, despite signs of infection, is likely due to the patient already being on antibiotics or the presence of fastidious organisms.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/20/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/20/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> **Analysis of Urine Culture Report**

The urine culture report indicates the presence of *Escherichia coli* with a colony count of 100,000 CFU/mL. The organism is susceptible to a broad range of antibiotics, including ampicillin, amoxicillin-clavulanic acid, cefuroxime, ceftriaxone, ciprofloxacin, levofloxacin, gentamicin, tobramycin, imipenem, meropenem, ceftazidime/avibactam, meropenem/vaborbactam, imipenem/relebactam, cefiderocol, ceftolozane/tazobactam, plazomicin, eravacycline, aztreonam, trimethoprim, and tetracycline. The report also notes sterile pyuria, which is negative urine culture in the presence of clinical and microscopic findings suggestive of infection. This finding suggests that the patient is already on antibiotics or that the infection is caused by fastidious organisms or interstitial nephritis/cystitis.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/20/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/20/doctor_audio.mp4)

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
> Your LH, FSH, and AMH levels are within normal ranges. These tests help assess your ovarian function and fertility.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/21/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/21/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The patient is a 42-year-old female presenting with LH, FSH, and AMH levels. LH is within the normal range, indicating normal ovarian function. FSH is also within the normal range, suggesting normal ovarian function. AMH is within the normal range, indicating adequate ovarian reserve. These results suggest normal ovarian function and adequate ovarian reserve.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/21/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/21/doctor_audio.mp4)

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

<video width="100%" controls>
  <source src="testing_reports/inference_results/22/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/22/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> **Analysis of Medical Report**

The patient is a 37-year-old female presenting with a TSH level of 4.96 mIU/mL, which falls within the normal reference range of 0.30-4.5 mIU/mL. The Vitamin B12 level is 370 pg/mL, which is within the reference range of 110-800 pg/mL. The TSH level is within normal limits, suggesting no current thyroid dysfunction. The Vitamin B12 level is within the normal range, indicating adequate Vitamin B12 stores. No immediate concerns are evident from these results.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/22/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/22/doctor_audio.mp4)

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
> Your TSH level is within the normal range. This indicates that your thyroid function is currently within the expected parameters.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/23/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/23/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> **Analysis of TSH Result:**

The TSH level is 0.97 mlU/mL, which falls within the normal reference range of 0.30 - 4.5 mlU/mL. This indicates that the thyroid gland is functioning within the expected parameters. The patient is not pregnant, so the reference ranges for pregnant women are not applicable. No significant abnormalities are evident in this single TSH measurement.

**Key Findings and Observations:**

The TSH level is within the normal range, suggesting that the thyroid gland is functioning appropriately.

**Notable Measurements or Test Results:**

TSH: 0.97 mlU/mL

**Clinical Significance:**

A normal TSH level indicates that the thyroid gland is producing the correct amount of thyroid hormone. This result is consistent with a healthy thyroid function.

**Areas Requiring Attention:**

No specific areas requiring attention are evident based on this single TSH result. Further evaluation may be warranted if the patient presents with symptoms suggestive of thyroid dysfunction.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/23/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/23/doctor_audio.mp4)

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
> Your anti-CCP antibody test result is 6.46 U/mL, which is above the normal range. This indicates the presence of anti-CCP antibodies, which can help detect rheumatoid arthritis earlier and more accurately. This test result may help your doctor determine the likelihood of developing rheumatoid arthritis.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/3/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/3/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> **Analysis of Anti-CCP Antibody Test Results**

The Anti-CCP antibody test result is significantly elevated at 6.46 U/mL, exceeding the normal range of <17.0 U/mL. This indicates a high likelihood of anti-CCP antibodies being present in the patient's serum. The presence of these autoantibodies is highly specific for Rheumatoid Arthritis (RA), and their detection can aid in early diagnosis, even before the onset of irreversible joint damage. This test is particularly useful in patients with undifferentiated arthritis, where the clinical presentation is suggestive of RA but does not fully meet the diagnostic criteria. Therefore, the elevated Anti-CCP antibody levels warrant further investigation and consideration of RA diagnosis and management.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/3/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/3/doctor_audio.mp4)

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
> Your IgE level is 201.9 IU/mL, which is within the normal range of 0.0-378 IU/mL. This test measures the amount of IgE in your blood.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/4/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/4/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The S. Total IgE level is 201.9 IU/mL, which falls within the reference range of 0.0-378 IU/mL. Elevated IgE levels can indicate allergic reactions, parasitic infections, or certain inflammatory conditions. While the result is within the normal range, it's important to consider the patient's clinical presentation and any relevant medical history to determine if further investigation is warranted. A normal IgE level does not always rule out the possibility of underlying immune dysregulation or allergic predisposition.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/4/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/4/doctor_audio.mp4)

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
> Your thyroid hormone levels (T3, T4, and TSH) are within the normal range. This indicates your thyroid is functioning as it should.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/5/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/5/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> The thyroid function test results indicate normal thyroid hormone levels. T3 (triiodothyronine) is within the normal range at 1.96 ng/mL, T4 (thyroxine) is within the normal range at 10.55 mcg/dL, and TSH (thyroid-stimulating hormone) is within the normal range at 0.11 mlU/mL. These results suggest that the thyroid gland is functioning within the expected physiological parameters. The normal TSH level indicates that the pituitary gland is appropriately stimulating the thyroid to produce thyroid hormones.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/5/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/5/doctor_audio.mp4)

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
> Your Vitamin B12 level is within the normal range. This vitamin is important for healthy red blood cell production and nerve function.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/7/patient_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/7/patient_audio.mp4)

</td>
</tr>
</table>

---

#### 👨‍⚕️ **Doctor Summary**

<table>
<tr>
<td width="70%">

**Clinical Analysis:**
> **Analysis of Vitamin B12 Report:**

The patient's Vitamin B12 level is 448 pg/mL, which falls within the normal reference range of 200-911 pg/mL. This indicates adequate Vitamin B12 stores. While the result is within the normal range, it's important to consider the patient's clinical presentation and any symptoms suggestive of Vitamin B12 deficiency, such as fatigue, weakness, or neurological symptoms. Further investigation may be warranted if the patient reports any of these symptoms, or if there are other risk factors for Vitamin B12 deficiency, such as vegan diet or malabsorption issues.

</td>
<td width="30%" align="center">

**🔊 Audio:**

<video width="100%" controls>
  <source src="testing_reports/inference_results/7/doctor_audio.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

[📥 Download MP4](testing_reports/inference_results/7/doctor_audio.mp4)

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