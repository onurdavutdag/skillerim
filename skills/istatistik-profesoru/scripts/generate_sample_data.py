# Skill testi için örnek veri setleri oluşturur

import pandas as pd
import numpy as np

np.random.seed(42)

# Senaryo 1: İki grup karşılaştırması
tedavi = np.random.normal(75, 10, 30)
kontrol = np.random.normal(65, 12, 30)
df_iki_grup = pd.DataFrame({
    'grup': ['tedavi'] * 30 + ['kontrol'] * 30,
    'skor': np.concatenate([tedavi, kontrol])
})
df_iki_grup.to_csv('ornek_iki_grup.csv', index=False)

# Senaryo 2: Korelasyon
yas = np.random.randint(20, 65, 50)
skor = yas * 0.8 + np.random.normal(0, 5, 50)
df_korelasyon = pd.DataFrame({'yas': yas, 'test_skoru': skor})
df_korelasyon.to_csv('ornek_korelasyon.csv', index=False)

# Senaryo 3: Üç grup (ANOVA)
diyet_a = np.random.normal(5, 1.5, 25)
diyet_b = np.random.normal(7, 2, 25)
diyet_c = np.random.normal(4, 1.2, 25)
df_anova = pd.DataFrame({
    'diyet': ['A'] * 25 + ['B'] * 25 + ['C'] * 25,
    'kilo_kaybi': np.concatenate([diyet_a, diyet_b, diyet_c])
})
df_anova.to_csv('ornek_anova.csv', index=False)

print("Örnek veri setleri oluşturuldu.")
