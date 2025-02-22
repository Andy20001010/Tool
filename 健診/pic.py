import pandas as pd
import matplotlib.pyplot as plt
from tkinter import filedialog, Tk

def select_file():
    root = Tk()
    root.withdraw()  # 隱藏主視窗
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    if not file_path:
        raise ValueError("No file selected.")
    return file_path

def save_risk_counts_chart(file_path):
    # 讀取 Excel 檔案
    df = pd.read_excel(file_path)

    # 確保必要的欄位存在
    required_columns = ['Host', 'Risk']
    if not all(column in df.columns for column in required_columns):
        raise ValueError(f"The file must contain the following columns: {', '.join(required_columns)}")

    # 計算每個 Host 的風險等級次數
    risk_counts = df[df['Risk'].isin(['Medium', 'High', 'Critical'])].groupby(['Host', 'Risk']).size().unstack(fill_value=0)

    # 定義顏色對應
    color_map = {
        'Medium': '#FFD700',  # 黃色
        'High': '#FF4500',    # 紅色
        'Critical': '#8B0000' # 深紅色
    }

    # 繪製並排柱狀圖
    ax = risk_counts.plot(kind='bar', figsize=(10, 6), color=[color_map[risk] for risk in risk_counts.columns], width=0.8)

    plt.title('Risk Counts per Host')
    plt.xlabel('Host')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Risk Level')
    plt.tight_layout()

    # 儲存圖表為 .jpg
    output_file = file_path.replace('.xlsx', '_risk_counts.jpg')
    plt.savefig(output_file)
    plt.close()
    print(f"Risk counts chart saved as {output_file}")

def main():
    try:
        file_path = select_file()
        save_risk_counts_chart(file_path)
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
