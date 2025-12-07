import csv

drug_names = set()

with open('drugbank vocabulary.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 6:
            continue
        # 主名称
        main_name = row[2].strip()
        if main_name and main_name != "":
            drug_names.add(main_name)
        
        # 别名（第6列，可能含多个，用 | 分隔）
        synonyms_str = row[5]
        if synonyms_str:
            synonyms = [s.strip() for s in synonyms_str.split('|')]
            for syn in synonyms:
                if syn and not syn.startswith("DB") and not syn.replace('-', '').isdigit():
                    drug_names.add(syn)

# 去除无效项（如纯数字、空行）
drug_names = {name for name in drug_names if name and not name.isdigit()}

# 写入文件
with open('drug_pos_name.txt', 'w', encoding='utf-8') as f:
    for name in sorted(drug_names):
        f.write(name + '\n')

print(f"✅ 成功生成 drug_pos_name.txt，共 {len(drug_names)} 个药品名称。")