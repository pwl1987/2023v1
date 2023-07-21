# app.py
import json
import os

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 默认json文件地址
default_json_path = "/root/kplayer/config.json"
# 默认索引
default_json_index = ["output", "lists", 0, "path"]


def read_json(file_path):
    if not os.path.exists(file_path):
        # 如果JSON文件不存在，则创建一个空的JSON文件
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump({}, file)
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_current_data(json_data, index_path):
    current_data = json_data
    for item in index_path:
        if isinstance(current_data, list):
            item = int(item)  # 将字符串转换为整数索引
        current_data = current_data[item]
    return current_data


@app.get("/")
def read_item(request: Request, json_path: str = default_json_path,
              json_index: str = ".".join(str(item) for item in default_json_index)):
    # 读取指定json文件内容
    json_data = read_json(json_path)

    # 根据索引路径获取索引值
    index_path = json_index.split(".")
    current_data = get_current_data(json_data, index_path)

    # 构造用于页面显示的数据
    display_data = {
        "json_content": json.dumps(json_data, ensure_ascii=False, indent=4),
        "json_path": json_path,
        "json_index": json_index,
        "json_value": current_data
    }

    return templates.TemplateResponse("index.html", {"request": request, "data": display_data})

@app.post("/")
def update_json(request: Request, json_path: str = Form(default=default_json_path),
                json_index: str = Form(default=".".join(str(item) for item in default_json_index)),
                json_content: str = Form(...)):
    try:
        # 将用户输入的json内容保存到指定json文件
        json_data = json.loads(json_content)
        write_json(json_path, json_data)

        # 根据索引路径获取索引值
        index_path = json_index.split(".")
        current_data = get_current_data(json_data, index_path)

        # 构造用于页面显示的数据
        display_data = {
            "json_content": json.dumps(json_data, ensure_ascii=False, indent=4),
            "json_path": json_path,
            "json_index": json_index,
            "json_value": current_data
        }

        return templates.TemplateResponse("index.html", {"request": request, "data": display_data})
    except Exception as e:
        error_msg = f"保存JSON文件失败：{e}"
        return templates.TemplateResponse("index.html", {"request": request, "error_msg": error_msg})


@app.post("/update_index/")
def update_index(request: Request, json_path: str = Form(default=default_json_path), json_index: str = Form(...)):
    try:
        # 读取指定json文件内容
        json_data = read_json(json_path)

        # 更新指定索引的值
        index_path = json_index.split(".")
        current_data = get_current_data(json_data, index_path[:-1])

        # 构造用于页面显示的数据
        display_data = {
            "json_content": json.dumps(json_data, ensure_ascii=False, indent=4),
            "json_path": json_path,
            "json_index": json_index,
            "json_value": current_data
        }

        return templates.TemplateResponse("index.html", {"request": request, "data": display_data})
    except Exception as e:
        error_msg = f"更新索引失败：{e}"
        return templates.TemplateResponse("index.html", {"request": request, "error_msg": error_msg})


@app.post("/get_index_value/")
def get_index_value(request: Request, json_path: str = Form(default=default_json_path), json_index: str = Form(...)):
    try:
        # 读取指定json文件内容
        json_data = read_json(json_path)

        # 根据新提交的索引路径获取新的索引值
        index_path = json_index.split(".")
        current_data = get_current_data(json_data, index_path)

        # 构造用于页面显示的数据
        display_data = {
            "json_content": json.dumps(json_data, ensure_ascii=False, indent=4),
            "json_path": json_path,
            "json_index": json_index,
            "json_value": current_data
        }

        return templates.TemplateResponse("index.html", {"request": request, "data": display_data})
    except Exception as e:
        error_msg = f"获取索引值失败：{e}"
        return templates.TemplateResponse("index.html", {"request": request, "error_msg": error_msg})


@app.post("/update_index_value/")
def update_index_value(request: Request, json_index: str = Form(...), json_value: str = Form(...)):
    try:
        # 读取指定json文件内容
        json_path = default_json_path  # 默认json文件地址
        json_data = read_json(json_path)

        # 更新指定索引的值
        index_path = json_index.split(".")
        current_data = get_current_data(json_data, index_path[:-1])
        current_data[index_path[-1]] = json_value

        # 保存更新后的json数据到指定json文件
        write_json(json_path, json_data)

        # 构造用于页面显示的数据
        display_data = {
            "json_content": json.dumps(json_data, ensure_ascii=False, indent=4),
            "json_path": json_path,
            "json_index": json_index,
            "json_value": json_value
        }

        return templates.TemplateResponse("index.html", {"request": request, "data": display_data})
    except Exception as e:
        error_msg = f"保存索引值失败：{e}"
        return templates.TemplateResponse("index.html", {"request": request, "error_msg": error_msg})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
