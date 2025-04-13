from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # 建议使用环境变量

# 管理员凭证（生产环境应使用数据库存储并加密）
ADMIN_USERNAME = "admin_1"
ADMIN_PASSWORD = "admin_1"

DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "bibliography.xlsx")
ALLOWED_EXTENSIONS = {"xlsx", "xls"}  # 允许的 Excel 格式


# 工具函数
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def read_excel_file(file_path):
    try:
        df = pd.read_excel(file_path, engine="openpyxl", header=None)
        df.columns = ["Entry"]
        return df
    except FileNotFoundError:
        flash("Error: Bibliography file not found. Please upload first.")
        return pd.DataFrame()
    except Exception as e:
        flash(f"Error reading Excel file: {str(e)}")
        return pd.DataFrame()


def search_excel(keyword):
    df = read_excel_file(DATA_FILE)
    if df.empty:
        return []
    keyword = keyword.lower()
    results = df[df["Entry"].astype(str).str.lower().str.contains(keyword)]["Entry"].tolist()
    return results


# 路由
@app.route("/")
def home():
    df = read_excel_file(DATA_FILE)
    return render_template("index.html", entry_count=len(df))


@app.route("/search", methods=["POST"])
def search():
    keyword = request.form.get("keyword", "").strip()
    if not keyword:
        return redirect(url_for("home"))
    results = search_excel(keyword)
    return render_template("index.html", keyword=keyword, results=results)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        # 获取表单数据
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        # 验证凭证
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Incorrect username or password")  # 统一错误提示
    
    return render_template("admin_login.html")


@app.route("/admin/dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        if file and allowed_file(file.filename):
            os.makedirs(DATA_FOLDER, exist_ok=True)
            try:
                file.save(DATA_FILE)
                flash("Bibliography updated successfully!")
                return redirect(url_for("admin_dashboard"))
            except Exception as e:
                flash(f"Error saving file: {str(e)}")
        else:
            flash("Invalid file format. Allowed: .xlsx, .xls")
    df = read_excel_file(DATA_FILE)
    return render_template("admin_dashboard.html", entry_count=len(df))


if __name__ == "__main__":
    app.run(debug=True)