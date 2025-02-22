import pandas as pd
from tkinter import filedialog, ttk
import tkinter as tk

# Function 1: Host and Risk type analysis, with proper 'None' handling
def analyze_risk_by_host(df, writer):
    risk_types = ['Critical', 'High', 'Medium', 'Low', 'None']
    host_risk_counts = {col: [] for col in ['Host'] + risk_types}

    df_unique_by_host_and_plugin = df.drop_duplicates(subset=['Host', 'Plugin ID'])
    grouped = df_unique_by_host_and_plugin.groupby('Host')

    for host, group in grouped:
        host_risk_counts['Host'].append(host)
        total_count = len(group)
        other_risks_count = 0
        for risk in risk_types[:-1]:
            count = (group['Risk'] == risk).sum()
            host_risk_counts[risk].append(count)
            other_risks_count += count
        
        none_count = total_count - other_risks_count
        host_risk_counts['None'].append(none_count)

    result_df_analysis = pd.DataFrame(host_risk_counts)
    result_df_analysis.to_excel(writer, sheet_name='風險數量列表', index=False)

# Function 2: Filter Risk >= Low, with proper sorting
def filter_risk_above_low(df, writer, separate_file_path=None):
    risk_levels = ['Low', 'Medium', 'High', 'Critical']
    df_unique_by_host_and_plugin = df.drop_duplicates(subset=['Host', 'Plugin ID'])
    filtered_df = df_unique_by_host_and_plugin[df_unique_by_host_and_plugin['Risk'].isin(risk_levels)]
    result_df_filter = filtered_df[['Plugin ID', 'Risk', 'Host', 'Name']]
    result_df_filter['Risk'] = pd.Categorical(result_df_filter['Risk'], categories=risk_levels, ordered=True)
    result_df_filter = result_df_filter.sort_values('Risk', ascending=False)

    # 寫入主 Excel
    result_df_filter.to_excel(writer, sheet_name='弱點列表', index=False)

    # 如果需要單獨輸出該結果的 Excel
    if separate_file_path:
        with pd.ExcelWriter(separate_file_path, engine='xlsxwriter') as separate_writer:
            result_df_filter.to_excel(separate_writer, sheet_name='弱點列表', index=False)

# Function 3: Extract Risk >= Low data, remove duplicate ids, and format vertically with spacing
def extract_vertical_risk_data_with_spacing(df, writer):
    risk_levels = ['Low', 'Medium', 'High', 'Critical']
    # 去除重複的 Plugin ID
    df_unique = df.drop_duplicates(subset=['Plugin ID'])
    # 篩選 Risk 欄位符合風險等級的資料
    filtered_df = df_unique[df_unique['Risk'].isin(risk_levels)]
    # 設定風險等級的順序
    filtered_df['Risk'] = pd.Categorical(filtered_df['Risk'], categories=risk_levels, ordered=True)
    # 根據風險等級排序，從高到低
    filtered_df = filtered_df.sort_values('Risk', ascending=False)
    
    # 準備所需欄位
    columns = ['Risk', 'Name', 'CVE', 'Plugin ID', 'Description', 'Solution', 'See Also']
    result = []

    # 組織數據為直式格式，並在每個弱點之間加入空白行
    for _, row in filtered_df.iterrows():
        for col in columns:
            result.append([col, row[col]])  # 每個欄位作為直式顯示
        result.append(['', ''])  # 插入空白行

    # 轉換為 DataFrame
    result_df_vertical = pd.DataFrame(result, columns=['Field', 'Value'])

    # 將結果寫入 Excel
    result_df_vertical.to_excel(writer, sheet_name='弱點說明表格', index=False, header=False)

# Function 4: Count occurrences of each risk level from previous data, remove duplicate IDs
def count_risk_levels(df, writer):
    risk_levels = ['Critical', 'High', 'Medium', 'Low']
    df_unique = df.drop_duplicates(subset=['Plugin ID'])
    risk_counts = df_unique['Risk'].value_counts().reindex(risk_levels).fillna(0).astype(int)
    result_df_counts = pd.DataFrame({'Var1': risk_levels, 'Freq': risk_counts.values})
    result_df_counts.to_excel(writer, sheet_name='弱點數量', index=False)

# Main function to handle Excel writing and call the functions
def run_analysis_and_filter():
    root = tk.Tk()
    root.attributes('-topmost', True)  # 將視窗置頂
    root.title("選擇檔案與測試類型")
    root.geometry("400x300")

    # 檔案選擇
    file_path_var = tk.StringVar()

    def select_file():
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        file_path_var.set(file_path)

    file_label = tk.Label(root, text="請選擇檔案：")
    file_label.pack(pady=10)

    file_button = tk.Button(root, text="選擇檔案", command=select_file)
    file_button.pack(pady=5)

    file_path_display = tk.Label(root, textvariable=file_path_var, wraplength=350, fg="blue")
    file_path_display.pack(pady=5)

    # 測試類型選擇
    test_type_var = tk.StringVar(value="初測")

    test_label = tk.Label(root, text="請選擇測試類型：")
    test_label.pack(pady=10)

    test_type_options = ["初測", "複測"]
    for option in test_type_options:
        rb = tk.Radiobutton(root, text=option, variable=test_type_var, value=option)
        rb.pack(anchor="w", padx=20)

    def confirm_and_process():
        file_path = file_path_var.get()
        if not file_path:
            tk.messagebox.showerror("錯誤", "請選擇檔案！")
            return

        test_type = test_type_var.get()
        save_path = f"合併結果_{test_type}.xlsx"
        separate_risk_file_path = f"弱點列表_{test_type}.xlsx"

        df = pd.read_csv(file_path)

        with pd.ExcelWriter(save_path, engine='xlsxwriter') as writer:
            analyze_risk_by_host(df, writer)
            filter_risk_above_low(df, writer, separate_file_path=separate_risk_file_path)
            extract_vertical_risk_data_with_spacing(df, writer)
            count_risk_levels(df, writer)

        print(f"Results saved to {save_path}")
        print(f"Filtered risk list saved to {separate_risk_file_path}")
        root.destroy()

    confirm_button = tk.Button(root, text="確認並執行", command=confirm_and_process, bg="lightgreen")
    confirm_button.pack(pady=20)

    root.mainloop()

run_analysis_and_filter()
