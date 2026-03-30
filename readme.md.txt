# 🏥 Hospital Queue Optimization System

### *M/M/c Queueing Theory · Erlang C · Cost Optimization · Real-Time Decision Tool*

---

## 🚀 Live Application

👉 **Use the live dashboard:**
https://hospital-queue-optimizer-7tfvbvffp7efbby6vw5vkb.streamlit.app/

---

## ⚡ Why This Project Matters

In real hospitals, poor staffing decisions lead to:

* ⏳ Long patient wait times
* 😡 Low patient satisfaction
* 💸 Increased operational costs

This project transforms **mathematical queueing theory** into a **real-time decision system** that answers:

> **“How many doctors should be on duty right now?”**

---

## 🎯 Core Objective

Find the **optimal number of doctors (c)** that:

* Minimizes total cost
* Keeps wait time acceptable
* Maintains system stability

---

## 🧠 Mathematical Foundation

This system is modeled as an **M/M/c queue**:

* **Poisson arrivals (λ)** → patients arrive randomly
* **Exponential service (µ)** → doctor service time is variable
* **c servers** → multiple doctors working in parallel

### Key Equations:

* Utilization:
  [
  \rho = \frac{\lambda}{c \cdot \mu}
  ]

* Waiting Probability → *Erlang C Formula*

* Average Wait Time:
  [
  W_q = \frac{P_q}{c\mu - \lambda}
  ]

* Queue Length:
  [
  L_q = \lambda \cdot W_q
  ]

---

## 💡 What This System Does

### 🔍 Real-Time Analytics

* Doctor utilization tracking
* Waiting probability estimation
* Queue length prediction

### 💰 Cost Optimization Engine

* Doctor salary cost
* Patient waiting cost
* **Finds minimum total cost point automatically**

### 📊 Visual Intelligence

* Wait time vs doctors curve
* Utilization thresholds (safe vs overload)
* Cost breakdown analysis

### 🔁 Scenario Simulation

* Peak vs normal demand comparison
* Sensitivity analysis using sliders

### 🧪 Simulation Validation

* Discrete-event simulation
* Validates theoretical M/M/c results

---

## 📸 Dashboard Preview

![Hospital Queue Optimizer](screenshot.png)

---

## 🛠 Tech Stack

| Layer         | Tools                             |
| ------------- | --------------------------------- |
| Frontend      | Streamlit                         |
| Computation   | NumPy, Pandas                     |
| Visualization | Matplotlib                        |
| Modeling      | Queueing Theory (M/M/c, Erlang C) |

---

## ⚙️ Installation

```bash
git clone https://github.com/mayank245956/hospital-queue-optimizer.git
cd hospital-queue-optimizer
pip install -r requirements.txt
```

---

## ▶️ Run Locally

```bash
streamlit run app.py
```

---

## 📊 Example Insight

> With 3 doctors handling 12 patients/hour:

* Utilization ≈ 80%
* Avg wait ≈ 12.9 minutes
* Optimal doctor count = 3
* Total cost minimized

---

## 🚨 Key Takeaways

* Systems break when **ρ ≥ 1 (unstable)**
* Above **85% utilization → risk zone**
* Wait time decreases **non-linearly**
* Optimal staffing exists — not guesswork

---

## 🔮 Future Scope

* 📂 Real hospital dataset integration
* 🤖 ML-based demand prediction
* 🏥 Multi-department queue modeling
* 🚑 Priority queues (emergency vs regular)
* 📡 API integration for real-time hospital data

---

## 👤 Author

**Mayank Pant**

---

## ⭐ Support

If this project helped you understand queueing theory or optimization:

👉 Star the repository
👉 Share with others

---

## 🧠 Final Thought

> Most people *study* queueing theory.
> This project lets you **apply it to real-world decisions.**
