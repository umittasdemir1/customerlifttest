from flask import Flask, render_template, request
import pandas as pd
import os
from werkzeug.utils import secure_filename
from itertools import combinations
from collections import Counter

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def analiz_menu(df):
    unique_groups = df['ÜRÜN GRUBU'].value_counts()
    group_table = unique_groups.reset_index().rename(columns={'index': 'Ürün Grubu', 'ÜRÜN GRUBU': 'Adet'})

    fatura_urunler = df.groupby("FATURA NO")["ÜRÜN GRUBU"].apply(set).tolist()
    combo_counts = Counter()
    for urunler in fatura_urunler:
        if len(urunler) >= 2:
            for combo in combinations(sorted(urunler), 2):
                combo_counts[combo] += 1
    lift_table = pd.DataFrame(combo_counts.items(), columns=["Ürün Kombinasyonu", "Birlikte Satış"])
    lift_table = lift_table.sort_values(by="Birlikte Satış", ascending=False).reset_index(drop=True)

    return group_table.to_html(index=False), lift_table.to_html(index=False)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            df = pd.read_excel(filepath)
            df.drop_duplicates(subset=["FATURA NO", "ÜRÜN GRUBU"], inplace=True)

            group_html, lift_html = analiz_menu(df)

            return render_template('index.html', result=True, group_html=group_html, lift_html=lift_html)

    return render_template('index.html', result=False)

if __name__ == '__main__':
    app.run(debug=True)
