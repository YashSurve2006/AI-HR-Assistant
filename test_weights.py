import sys
sys.path.insert(0, 'backend')
import chatbot
import data_processor
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

q = "How many sick leaves can I take?"
cleaned_q = data_processor.clean_text(q)
processed_q = data_processor.preprocess_text(q)

word_q = chatbot._word_vec.transform([processed_q])
char_q = chatbot._char_vec.transform([processed_q])
sem_q = chatbot._sem_model.encode([cleaned_q], convert_to_numpy=True)

sim_word = cosine_similarity(word_q, chatbot._word_mat).flatten()
sim_char = cosine_similarity(char_q, chatbot._char_mat).flatten()
sim_sem = cosine_similarity(sem_q, chatbot._sem_mat).flatten()

df = chatbot._faq_df.copy()
df['sim_word'] = sim_word
df['sim_char'] = sim_char
df['sim_sem'] = sim_sem

print("--- Testing Semantic-Heavy Weights (Sem: 0.70, Word: 0.15, Char: 0.15) ---")
df['hybrid'] = (0.70 * sim_sem) + (0.15 * sim_word) + (0.15 * sim_char)
top_df = df.sort_values(by='hybrid', ascending=False).head(5)
for idx, row in top_df.iterrows():
    print(f"Q: {row['question']:<55} | Hybrid: {row['hybrid']:.4f} | Sem: {row['sim_sem']:.4f} | Word: {row['sim_word']:.4f} | Char: {row['sim_char']:.4f}")

print("\n--- Testing Pure Semantic Ranker with TF-IDF Rescoring ---")
# If a query contains specific domain words like 'sick', semantic ranking handles intent much better
df['hybrid_sem_first'] = (0.75 * sim_sem) + (0.15 * sim_word) + (0.10 * sim_char)
top_df2 = df.sort_values(by='hybrid_sem_first', ascending=False).head(5)
for idx, row in top_df2.iterrows():
    print(f"Q: {row['question']:<55} | Hybrid: {row['hybrid_sem_first']:.4f} | Sem: {row['sim_sem']:.4f} | Word: {row['sim_word']:.4f} | Char: {row['sim_char']:.4f}")
