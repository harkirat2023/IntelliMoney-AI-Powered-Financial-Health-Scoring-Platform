export const faqItems = [
  {
    question: "Is IntelliMoney free to use?",
    answer:
      "Yes! IntelliMoney offers a generous free tier that includes expense tracking, AI categorization, budget management, and your financial health score. Premium features like bank sync, AI copilot, and goal planning are available on our Pro plan.",
  },
  {
    question: "How does the AI categorization work?",
    answer:
      "Our ML model uses a TF-IDF vectorizer combined with a logistic regression classifier trained on thousands of labeled transactions. It analyzes merchant names, descriptions, and amounts to predict categories with over 85% accuracy. The model improves over time as you correct predictions.",
  },
  {
    question: "Is my financial data secure?",
    answer:
      "Absolutely. All data is encrypted in transit via TLS 1.3 and at rest using AES-256. We use JWT-based authentication with bcrypt password hashing. Your data never leaves our secure infrastructure without your explicit consent.",
  },
  {
    question: "Can I connect my bank account?",
    answer:
      "Yes! IntelliMoney supports read-only bank connections via secure APIs (Plaid/FinCity). We never have access to move money or modify your accounts. You control what data is shared and can revoke access anytime.",
  },
  {
    question: "What is the Financial Health Score?",
    answer:
      "Your Financial Health Score is a 0–100 rating calculated from four factors: savings rate (35%), budget adherence (30%), expense stability (20%), and discretionary spending risk (15%). It gives you a single number to track your financial wellness over time.",
  },
  {
    question: "How does the AI Copilot work?",
    answer:
      "The AI Copilot uses LangChain and GPT-based models to understand natural language questions about your finances. Ask things like 'What was my biggest expense last month?' or 'Can I afford a \u20b950,000 vacation?' and get instant, personalized answers based on your actual data.",
  },
  {
    question: "Can I export my data?",
    answer:
      "Yes. You can export all your transactions, reports, and insights as CSV or PDF at any time. We believe your data belongs to you.",
  },
  {
    question: "What happens to my data if I cancel?",
    answer:
      "You can download your complete data before canceling. After cancellation, your data is retained for 30 days in case you change your mind, then permanently deleted from our servers.",
  },
];
