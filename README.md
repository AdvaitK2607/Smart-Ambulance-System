# 🚑 Smart Ambulance Triage & Dispatch System

A hybrid emergency response system that classifies patient severity and prioritizes ambulance dispatch based on medical urgency. The system uses a Decision Tree machine learning model along with a priority queue–based dispatch mechanism to ensure faster and more accurate emergency handling.

---

## 📌 Project Overview

Traditional ambulance dispatch often operates on a first-come-first-serve basis, which can delay treatment for critical patients.  
This project introduces an **intelligent triage system** that:

- Analyzes patient symptoms
- Classifies severity level
- Assigns priority to the case
- Recommends dispatch order for ambulances

This helps ensure that patients with higher medical need are served first.

---

## 🧠 Triage Model (Decision Tree)

We constructed a **clinically guided synthetic dataset** of 400 patient cases, derived from a 1,024-case combinatorial feature space.  
This dataset:
- Covers realistic symptom combinations
- Avoids medically contradictory conditions
- Ensures meaningful model learning without overfitting

The **Decision Tree classifier** is used to classify cases into severity categories (Low / Moderate / High / Critical).

---

## 🚑 Priority-Based Ambulance Dispatch

Once severity is determined, each case enters a **priority queue**, where:
- Higher severity → Higher priority
- Ambulances are dispatched based on urgency, not arrival order

This ensures **efficient and life-saving response sequencing**.

---

## 🛠️ Tech Stack

| Component | Tools Used |
|----------|------------|
| Programming Language | Python |
| Model Development | Scikit-Learn, Pandas, NumPy |
| Data Handling | Synthetic dataset construction |
| Dispatch Logic | Priority Queue Algorithm |
| Evaluation | Confusion Matrix & Accuracy Score |

---

## 📁 Project Structure

