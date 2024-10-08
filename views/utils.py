from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
import textwrap

EXCLUDED_FIELDS = {}


def parse_json_tree(restaurant, tree_widget):
    root_name = restaurant.get("name", "Unnamed Restaurant")
    root_item = QTreeWidgetItem([root_name])


    font = QFont()
    font.setBold(True)
    root_item.setFont(0, font)
    root_item.setForeground(0, QColor("#2b00d8"))

    tree_widget.addTopLevelItem(root_item)


    for key, value in restaurant.items():
        if key not in EXCLUDED_FIELDS:
            parse_json(key, value, root_item)


def parse_json(key, value, parent):
    if isinstance(value, dict):
        item = QTreeWidgetItem([key])
        parent.addChild(item)
        for k, v in value.items():
            if k not in EXCLUDED_FIELDS:
                parse_json(k, v, item)
    elif isinstance(value, list):
        if key not in EXCLUDED_FIELDS:
            if len(value) == 0:
                item = QTreeWidgetItem([key, "Empty Array"])
            else:
                item = QTreeWidgetItem([key, "Array"])
                item.setForeground(1, QColor("white"))
            item.setForeground(0, QColor("blue"))
            parent.addChild(item)
            for i, v in enumerate(value):
                parse_json(f"[{i}]", v, item)
    else:
        text = str(value) if value or value == 0 else "No value"
        wrapped_text = "\n".join(textwrap.wrap(text, width=100)) if len(text) > 100 else text
        item = QTreeWidgetItem([key, wrapped_text])
        item.setFlags(item.flags() | Qt.ItemIsEditable)

        if wrapped_text == "No value":
            item.setForeground(1, QColor("red"))

        parent.addChild(item)


def tree_to_dict(item):

    result = {}

    for i in range(item.childCount()):
        child = item.child(i)
        key = child.text(0)
        value = child.text(1)

        if child.childCount() > 0:

            if value == "Array" or value == "Empty Array":
                array_data = []
                for j in range(child.childCount()):
                    array_child = child.child(j)
                    if array_child.childCount() > 0:
                        array_data.append(tree_to_dict(array_child))
                    else:
                        array_data.append(convert_value(array_child.text(1)))
                result[key] = array_data  #
            else:

                result[key] = tree_to_dict(child)
        else:

            result[key] = convert_value(value)

    return result



def convert_value(value):
    if isinstance(value, str):
        value = value.replace("\n", " ")


    if value == "Empty Array":
        return []
    elif value == "No value" or value == "" or value == "null":
        return ""
    elif value.lower() == "false":
        return False
    elif value.lower() == "true":
        return True
    try:
        # Thử chuyển thành float nếu có dấu chấm thập phân
        if '.' in value:
            return float(value)
        # Nếu không, thử chuyển sang int
        return int(value)
    except ValueError:
        # Nếu không chuyển đổi được thành số, giữ nguyên chuỗi
        return value



def ensure_default_values(data):
    """Đảm bảo rằng các trường có giá trị null được thay bằng giá trị mặc định như chuỗi rỗng."""
    for key, value in data.items():
        if isinstance(value, dict):
            ensure_default_values(value)
        elif value is None:
            data[key] = ""
        elif isinstance(value, list):

            for i in range(len(value)):
                if isinstance(value[i], dict):
                    ensure_default_values(value[i])
                elif value[i] is None:
                    value[i] = ""

    return data


def process_tree_item(item):
    """Xử lý toàn bộ cây và trả về dữ liệu đã được làm sạch và chuyển đổi."""
    data = tree_to_dict(item)
    cleaned_data = ensure_default_values(data)
    return cleaned_data


