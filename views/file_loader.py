from PyQt5.QtWidgets import QFileDialog
import json5

def load_json_file(parent):
    file_dialog = QFileDialog(parent)
    file_path, _ = file_dialog.getOpenFileName(parent, "Open JSON File", "", "JSON Files (*.json)")
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            try:
                return json5.loads(file_content)
            except Exception as e:
                print(f"Failed to parse JSON: {str(e)}")
                return []
        except FileNotFoundError:
            print("File not found. Please check the file path.")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
    return []
