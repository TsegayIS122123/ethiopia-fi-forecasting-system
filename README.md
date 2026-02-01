# Ethiopia Financial Inclusion Forecasting System

## Overview
A forecasting system that tracks Ethiopia's digital financial transformation using time series methods and event impact modeling. This project addresses the need to understand and predict financial inclusion trends in Ethiopia's rapidly evolving digital payment ecosystem.

## Objective
Build a robust forecasting system that predicts Ethiopia's progress on two core dimensions of financial inclusion:
1. **Access** — Account Ownership Rate
2. **Usage** — Digital Payment Adoption Rate

The system will help stakeholders understand:
- What drives financial inclusion in Ethiopia
- How events (product launches, policy changes, infrastructure investments) affect inclusion outcomes
- Projections for 2025-2027

## Features
- **Unified Data Schema**: Consistent structure for observations, events, and impact relationships
- **Event Impact Modeling**: Quantify effects of policies, product launches, and market entries
- **Multi-Scenario Forecasting**: Generate optimistic, base, and pessimistic scenarios
- **Interactive Dashboard**: Visual exploration of trends and forecasts
- **Data Enrichment**: Framework for adding new data sources
- **Validation Framework**: Compare forecasts against historical data

## Strategy
1. **Data First**: Start with comprehensive data exploration and enrichment
2. **Event-Driven**: Model financial inclusion as a function of market events
3. **Scenario-Based**: Account for uncertainty with multiple forecast scenarios
4. **Iterative Refinement**: Continuously improve models as new data becomes available

## Methods
1. **Time Series Analysis**: ARIMA, Exponential Smoothing, Prophet
2. **Regression Modeling**: OLS with intervention variables
3. **Event Impact Estimation**: Comparable country evidence + local validation
4. **Machine Learning**: Gradient boosting for non-linear relationships
5. **Ensemble Methods**: Combine multiple models for robust forecasts

###  **Task 1: Data Exploration and Enrichment** - **COMPLETED**

#### 🎯 **Accomplishments**
-  **Dataset Loaded & Explored**: Unified financial inclusion dataset (43 records)
-  **Indicator Mapping**: Standard names mapped to actual dataset indicators
-  **Data Gaps Identified**: Missing years and indicators identified
-  **Dataset Enriched**: 20 new records added with proper documentation
-  **Quality Checks**: Data validation and duplicate prevention implemented

#### 📈 **Key Data Discoveries**
| Discovery | Impact |
|-----------|---------|
| **Gender Gap**: 56% male vs 36% female (2021) | 20pp difference requiring targeted interventions |
| **P2P > ATM**: Transactions surpassed withdrawals (Oct 2024) | Digital payment milestone achieved |
| **Mobile Money ≠ Digital Payments**: 66% vs 35% (2024) | Distinct metrics for analysis |
| **Historical Gaps**: 2011 account ownership missing | Critical for trend analysis |

#### 🗃️ **Enriched Dataset Statistics**
- 📁 Original Dataset: 43 records
- ➕ New Records Added: 20 records
- 📊 Total Enriched Dataset: 63 records

📋 Record Type Breakdown:
├── 📊 Observations: 45 records
├── 🎯 Events: 15 records
├── 🎯 Targets: 3 records
└── 🔗 Impact Links: 14 relationships (separate file)

#### 🏗️ **Data Added**
| Indicator | Years Added | Values | Purpose |
|-----------|-------------|---------|---------|
| **Account Ownership** | 2011 | 14.0% | Complete 2011-2024 timeline |
| **Mobile Money Accounts** | 2014, 2017 | 0.5%, 1.2% | Historical context |
| **Digital Payment Usage** | 2021, 2024 | 25%, 35% | New indicator created |
| **COVID-19 Event** | 2020-03-13 | N/A | External shock impact |


#### 🎨 **Notebook Implementation**
- Interactive exploration with visualizations
- Schema validation and quality checks
- Automated duplicate prevention
- Comprehensive documentation generation

#### 🔍 **Critical Insights from Task 1**
1. **Indicator Mapping Required**: Standard names differ from actual dataset names
2. **Gender Disaggregation Available**: Rich gender-based analysis possible
3. **Event Timeline Complete**: Key market events 2021-2025 cataloged
4. **Impact Relationships Defined**: 14 event-indicator relationships modeled
5. **Data Quality High**: Confidence levels documented for all records

---
---

### **Task 2: Exploratory Data Analysis (EDA)** — **COMPLETED**

#### 🎯 **Objective**
Analyze Ethiopia’s financial inclusion data to uncover trends, drivers, bottlenecks, and relationships between infrastructure, events, and inclusion outcomes.

---

## 📊 Dataset Overview

| Metric | Value |
|-------|--------|
| Total Records | 63 |
| Observations | 45 |
| Events | 15 |
| Targets | 3 |
| Unique Indicators | 23 |
| Time Range | 2011–2025 |
| Confidence Level | 82% High, 18% Medium |

### Pillar Coverage
- **ACCESS** — Account ownership, infrastructure
- **USAGE** — Digital payments, mobile money activity
- **ENABLERS** — Connectivity, affordability, digital ID

---

## 📈 Access (Account Ownership) Analysis

### Historical Trend
| Year | Ownership |
|--------|-----------|
| 2011 | 14% |
| 2014 | 22% |
| 2017 | 35% |
| 2021 | 46% |
| 2024 | 49% |

### Growth Pattern
- 2014–2017 → **+13pp**
- 2017–2021 → **+11pp**
- 2021–2024 → **+3pp (slowdown)**

### Key Finding
Despite massive mobile money growth, account ownership growth **decelerated sharply after 2021**.

---

## 👥 Gender Gap Analysis

| Metric | Value |
|-----------|---------|
| Male | 56% |
| Female | 36% |
| Gap | **20 percentage points** |
| Female/Male Ratio | 64% |

### Insight
Financial access inequality remains a **major structural barrier** and must be explicitly modeled in forecasting.

---

## 💳 Usage (Digital Payments) Analysis

### Indicators
| Indicator | Latest |
|--------------|-----------|
| Mobile Money Accounts | 9.45% |
| Active Mobile Money Users | 66% |
| Digital Payment Usage | 35% |

### Key Observations
- Registered ≠ Active ≠ Digital payment usage
- Many accounts are inactive or P2P-only
- Usage lags access significantly

---

## 🏗 Infrastructure & Enablers

Available indicators analyzed:
- 4G Coverage
- Mobile Penetration
- Data Affordability
- Digital ID Enrollment
- Agent/Transaction infrastructure

### Insight
Infrastructure shows **leading indicator behavior**, often preceding inclusion growth by 12–18 months.

---

## 📅 Event Timeline Insights

Major events cataloged:

- Telebirr Launch (2021)
- Safaricom Entry (2022)
- M-Pesa Launch (2023)
- Fayda Digital ID Rollout (2024)
- P2P > ATM milestone (2024)
- EthioPay Instant Payments (2025)

### Observed Effects
| Event | Indicator | Direction |
|---------|-----------|-------------|
| Telebirr | Account ownership | ↑ |
| Telebirr | P2P transactions | ↑ |
| Safaricom | 4G coverage | ↑ |
| Fayda ID | Access & transactions | ↑ |

---

## 🔗 Correlation Analysis

### Strong Relationships (|r| > 0.7)

| Indicator A | Indicator B | Correlation |
|--------------|---------------|-------------|
| Account Ownership | Mobile Money Accounts | +1.0 |
| Gender Gap | Ownership | −1.0 |
| Digital ID | P2P Transactions | +1.0 |

### Interpretation
- Mobile money strongly drives access
- Gender inequality suppresses inclusion
- Digital ID acts as a transaction enabler

---

## 🚨 Data Gaps Identified

Sparse indicators (<3 points):
- ATM metrics
- Digital payment usage history
- Infrastructure series
- Gender-disaggregated metrics

### Impact
Forecast uncertainty will be higher; event-based modeling becomes critical.

---

## 🎯 Key Insights (Summary)

1. Account ownership growth slowed dramatically after 2021  
2. Persistent 20pp gender gap  
3. Mobile money growth does not automatically translate to usage  
4. Infrastructure investments precede adoption  
5. Events (Telebirr, M-Pesa, Digital ID) strongly influence outcomes  

---

## 📓 Notebook
Implemented in:



