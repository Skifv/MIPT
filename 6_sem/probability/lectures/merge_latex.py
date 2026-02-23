import os

def generate_tree_and_merge(root_dir, output_file):
    exclude_dirs = {'build', '.git', '__pycache__'}
    exclude_files = {output_file, 'merge_latex.py', 'tree_merge.py', 'main.pdf', 'main.dvi'}

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write("==================================================\n")
        outfile.write(f"PROJECT STRUCTURE AND CONTENT: {os.path.basename(root_dir)}\n")
        outfile.write("==================================================\n\n")

        # Часть 1: Генерируем визуальное дерево (аналог tree /f)
        outfile.write("DIRECTORY TREE:\n")
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            level = root.replace(root_dir, '').count(os.sep)
            indent = '│   ' * (level)
            outfile.write(f'{indent}├── {os.path.basename(root)}/\n')
            sub_indent = '│   ' * (level + 1)
            for f in files:
                if f not in exclude_files:
                    outfile.write(f'{sub_indent}└── {f}\n')
        
        outfile.write("\n" + "="*50 + "\n")
        outfile.write("FILE CONTENTS:\n")
        outfile.write("="*50 + "\n")

        # Часть 2: Собираем контент
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith('.tex') and file not in exclude_files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, root_dir)
                    
                    outfile.write(f"\n\n[FILE]: {rel_path}\n")
                    outfile.write(f"{'-' * (len(rel_path) + 8)}\n")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"\n[ERROR READING {rel_path}: {e}]\n")
                    
                    outfile.write(f"\n[END OF {rel_path}]\n")

    print(f"Дамп готов: {output_file}")

if __name__ == "__main__":
    generate_tree_and_merge(os.getcwd(), 'project_tree_dump.txt')