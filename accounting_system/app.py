from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
import json
from datetime import datetime
import requests
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MySQL配置
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'  # 改成你的MySQL密码
app.config['MYSQL_DB'] = 'accounting_system'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


# 密码哈希
def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


# 首页
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])
        email = request.form.get('email', '')

        cursor = mysql.connection.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                           (username, password, email))
            mysql.connection.commit()
            return redirect(url_for('login'))
        except Exception as e:
            return f"注册失败: {str(e)}"
        finally:
            cursor.close()

    return render_template('register.html')


# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s",
                       (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            return "用户名或密码错误"

    return render_template('login.html')


# 退出
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# 主面板 - 已修改为显示收入、支出、余额
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    # 获取最近10条记录
    cursor.execute("""
        SELECT r.*, c.name as category_name, c.type as category_type
        FROM records r 
        JOIN categories c ON r.category_id = c.id 
        WHERE r.user_id = %s 
        ORDER BY r.record_date DESC, r.id DESC
        LIMIT 10
    """, (user_id,))
    recent_records = cursor.fetchall()

    # 获取本月总收入、支出、余额
    cursor.execute("""
        SELECT 
            -- 本月总收入（正数金额）
            COALESCE(SUM(CASE WHEN c.type = '收入' THEN amount ELSE 0 END), 0) as income,
            -- 本月总支出（金额取绝对值）
            COALESCE(ABS(SUM(CASE WHEN c.type = '支出' THEN amount ELSE 0 END)), 0) as expense,
            -- 本月余额（总收入 + 总支出，因为支出是负数）
            COALESCE(SUM(amount), 0) as balance
        FROM records r 
        JOIN categories c ON r.category_id = c.id 
        WHERE r.user_id = %s 
        AND MONTH(r.record_date) = MONTH(CURDATE())
        AND YEAR(r.record_date) = YEAR(CURDATE())
    """, (user_id,))
    monthly_data = cursor.fetchone()

    # 如果monthly_data是None，设为默认值
    if monthly_data:
        monthly_income = monthly_data['income'] or 0
        monthly_expense = monthly_data['expense'] or 0
        monthly_balance = monthly_data['balance'] or 0
    else:
        monthly_income = monthly_expense = monthly_balance = 0

    # 获取总账单（历史累计）
    cursor.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN c.type = '收入' THEN amount ELSE 0 END), 0) as total_income,
            COALESCE(ABS(SUM(CASE WHEN c.type = '支出' THEN amount ELSE 0 END)), 0) as total_expense,
            COALESCE(SUM(amount), 0) as total_balance
        FROM records r 
        JOIN categories c ON r.category_id = c.id 
        WHERE r.user_id = %s
    """, (user_id,))
    total_data = cursor.fetchone()

    # 如果total_data是None，设为默认值
    if total_data:
        total_income = total_data['total_income'] or 0
        total_expense = total_data['total_expense'] or 0
        total_balance = total_data['total_balance'] or 0
    else:
        total_income = total_expense = total_balance = 0

    cursor.close()

    return render_template('dashboard.html',
                           recent_records=recent_records,
                           monthly_income=monthly_income,
                           monthly_expense=monthly_expense,
                           monthly_balance=monthly_balance,
                           total_income=total_income,
                           total_expense=total_expense,
                           total_balance=total_balance)


# 添加记录
@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        category_id = request.form['category_id']
        amount = float(request.form['amount'])  # 转换为浮点数
        description = request.form['description']
        record_date = request.form['record_date']
        user_id = session['user_id']

        # 调试信息
        print(f"添加记录: user_id={user_id}, category_id={category_id}, amount={amount}")

        cursor.execute("""
            INSERT INTO records (user_id, category_id, amount, description, record_date) 
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, category_id, amount, description, record_date))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('dashboard'))

    # 获取分类列表
    cursor.execute("SELECT * FROM categories WHERE user_id IS NULL OR user_id = %s",
                   (session['user_id'],))
    categories = cursor.fetchall()
    cursor.close()

    return render_template('add_record.html', categories=categories)


# 删除记录
@app.route('/delete_record/<int:record_id>')
def delete_record(record_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM records WHERE id = %s AND user_id = %s",
                   (record_id, session['user_id']))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('dashboard'))


# 报表页面
@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('reports.html')


# 获取月度数据API（已修改为显示收入、支出、余额）
@app.route('/api/monthly_data')
def monthly_data():
    if 'user_id' not in session:
        return jsonify({'error': '未登录'})

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    # 按月汇总收入、支出、余额
    cursor.execute("""
        SELECT 
            DATE_FORMAT(r.record_date, '%%Y-%%m') as month,
            COALESCE(SUM(CASE WHEN c.type = '收入' THEN amount ELSE 0 END), 0) as income,
            COALESCE(ABS(SUM(CASE WHEN c.type = '支出' THEN amount ELSE 0 END)), 0) as expense,
            COALESCE(SUM(amount), 0) as balance
        FROM records r
        JOIN categories c ON r.category_id = c.id
        WHERE r.user_id = %s
        GROUP BY DATE_FORMAT(r.record_date, '%%Y-%%m')
        ORDER BY month DESC
        LIMIT 12
    """, (user_id,))

    data = cursor.fetchall()
    cursor.close()

    return jsonify(data)


# 获取分类数据API（已修改为显示收入和支出分类）
@app.route('/api/category_data')
def category_data():
    if 'user_id' not in session:
        return jsonify({'error': '未登录'})

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    # 获取所有分类数据，包括收入支出
    cursor.execute("""
        SELECT 
            c.name,
            c.type,
            COALESCE(SUM(r.amount), 0) as total
        FROM records r
        JOIN categories c ON r.category_id = c.id
        WHERE r.user_id = %s
        GROUP BY c.name, c.type
        ORDER BY c.type, ABS(total) DESC
    """, (user_id,))

    data = cursor.fetchall()
    cursor.close()

    return jsonify(data)


# 调试路由：查看数据库状态
@app.route('/db_status')
def db_status():
    cursor = mysql.connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    result = "<h2>数据库状态</h2>"

    for table in tables:
        table_name = table['Tables_in_accounting_system']
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        count = cursor.fetchone()['count']
        result += f"<p>{table_name}: {count} 条记录</p>"

    cursor.close()
    return result


# 数据库查看页面 - 专门给老师展示用
@app.route('/admin/db_view')
def admin_db_view():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()

    # 获取所有表的数据
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    table_data = {}
    for table in tables:
        table_name = table['Tables_in_accounting_system']
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        table_data[table_name] = data

    cursor.close()

    return render_template('db_view.html', table_data=table_data)


# 清空数据（用于演示重新开始）
@app.route('/admin/reset_data')
def admin_reset_data():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()

    try:
        # 禁用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        # 清空所有表
        cursor.execute("TRUNCATE TABLE records")
        cursor.execute("TRUNCATE TABLE users")

        # 重置categories表（保留默认分类）
        cursor.execute("DELETE FROM categories WHERE user_id IS NOT NULL")

        # 启用外键检查
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        mysql.connection.commit()
        cursor.close()

        return "数据已重置！<a href='/admin/db_view'>查看数据库</a>"
    except Exception as e:
        return f"重置失败: {str(e)}"


# ==================== AI功能配置 ====================
# 使用你的DeepSeek API密钥
app.config['DEEPSEEK_API_KEY'] = 'sk-ac57a6323894435483c47ad2c6d66942'
app.config['DEEPSEEK_API_URL'] = 'https://api.deepseek.com/v1/chat/completions'


# 安全的AI调用函数
def call_deepseek_api(messages, temperature=0.7, max_tokens=2000):
    """
    调用DeepSeek API的修正版本
    """
    api_key = app.config.get('DEEPSEEK_API_KEY', '')

    # 检查API密钥格式
    if not api_key or not api_key.startswith('sk-'):
        return "⚠️ AI服务配置错误：请检查API密钥格式。"

    # 正确的API端点
    api_url = 'https://api.deepseek.com/v1/chat/completions'

    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        print(f"[AI调试] 调用DeepSeek API: {api_url}")
        print(f"[AI调试] API密钥前8位: {api_key[:8]}...")
        print(f"[AI调试] 请求消息长度: {len(str(messages))}")

        # 发送请求
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=30  # 30秒超时
        )

        print(f"[AI调试] 响应状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"[AI调试] 成功！回复长度: {len(content)} 字符")
                return content
            else:
                print(f"[AI调试] 响应格式异常: {result}")
                return "🤖 AI返回了异常响应格式，请稍后重试。"

        elif response.status_code == 401:
            print("[AI调试] 401错误：API密钥无效")
            return "🔑 API密钥无效或已过期，请检查密钥是否正确。"

        elif response.status_code == 429:
            print("[AI调试] 429错误：请求过频")
            return "⏳ 请求频率过高，请稍后再试。"

        elif response.status_code == 400:
            error_msg = "请求参数错误"
            try:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', error_msg)
            except:
                pass
            print(f"[AI调试] 400错误: {error_msg}")
            return f"📝 请求错误: {error_msg}"

        else:
            print(f"[AI调试] 其他错误: {response.status_code}")
            print(f"[AI调试] 响应内容: {response.text[:200]}")
            return f"❌ HTTP错误 {response.status_code}"

    except requests.exceptions.Timeout:
        print("[AI调试] 请求超时")
        return "⏰ 请求超时，请检查网络连接或稍后重试。"

    except requests.exceptions.ConnectionError as e:
        print(f"[AI调试] 连接错误: {str(e)}")
        return "📡 网络连接失败，请检查网络设置。"

    except requests.exceptions.JSONDecodeError:
        print("[AI调试] JSON解析错误")
        return "📄 响应数据格式错误，请稍后重试。"

    except Exception as e:
        error_msg = str(e)
        print(f"[AI调试] 未知异常: {error_msg}")
        return f"⚠️ 未知错误: {error_msg[:100]}"

# 获取用户财务数据的函数
def get_user_financial_data(user_id, days=90):
    """
    获取用户的财务数据用于AI分析
    """
    cursor = mysql.connection.cursor()

    try:
        # 获取本月数据
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN c.type = '收入' THEN r.amount ELSE 0 END), 0) as income,
                COALESCE(ABS(SUM(CASE WHEN c.type = '支出' THEN r.amount ELSE 0 END)), 0) as expense,
                COALESCE(SUM(r.amount), 0) as balance,
                COUNT(*) as count
            FROM records r 
            JOIN categories c ON r.category_id = c.id 
            WHERE r.user_id = %s 
            AND MONTH(r.record_date) = MONTH(CURDATE())
            AND YEAR(r.record_date) = YEAR(CURDATE())
        """, (user_id,))
        monthly_data = cursor.fetchone()

        # 获取最近N天数据
        cursor.execute("""
            SELECT 
                DATE_FORMAT(r.record_date, '%%Y-%%m-%%d') as date,
                c.name as category,
                c.type,
                r.amount,
                r.description
            FROM records r 
            JOIN categories c ON r.category_id = c.id 
            WHERE r.user_id = %s 
            AND r.record_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            ORDER BY r.record_date DESC
        """, (user_id, days))
        recent_data = cursor.fetchall()

        # 获取分类统计
        cursor.execute("""
            SELECT 
                c.name,
                c.type,
                COUNT(*) as transaction_count,
                SUM(r.amount) as total_amount
            FROM records r 
            JOIN categories c ON r.category_id = c.id 
            WHERE r.user_id = %s 
            GROUP BY c.name, c.type
            ORDER BY ABS(SUM(r.amount)) DESC
        """, (user_id,))
        category_stats = cursor.fetchall()

        # 获取收入支出趋势
        cursor.execute("""
            SELECT 
                DATE_FORMAT(r.record_date, '%%Y-%%m') as month,
                SUM(CASE WHEN c.type = '收入' THEN r.amount ELSE 0 END) as income,
                SUM(CASE WHEN c.type = '支出' THEN r.amount ELSE 0 END) as expense
            FROM records r 
            JOIN categories c ON r.category_id = c.id 
            WHERE r.user_id = %s 
            GROUP BY DATE_FORMAT(r.record_date, '%%Y-%%m')
            ORDER BY month DESC
            LIMIT 6
        """, (user_id,))
        trend_data = cursor.fetchall()

        return {
            'monthly': {
                'income': float(monthly_data['income'] or 0),
                'expense': float(monthly_data['expense'] or 0),
                'balance': float(monthly_data['balance'] or 0),
                'count': monthly_data['count'] or 0
            },
            'recent_data': recent_data,
            'category_stats': category_stats,
            'trend_data': trend_data,
            'total_records': len(recent_data)
        }

    except Exception as e:
        print(f"[AI] 获取财务数据错误: {str(e)}")
        return None
    finally:
        cursor.close()


# ==================== AI路由 ====================

# AI分析主页
@app.route('/ai_analysis')
def ai_analysis():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()

    # 获取AI分析历史
    cursor.execute("""
        SELECT * FROM ai_analysis 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT 5
    """, (session['user_id'],))
    history = cursor.fetchall()

    # 获取财务概览
    financial_data = get_user_financial_data(session['user_id'], 30)

    cursor.close()

    return render_template('ai_analysis.html',
                           history=history,
                           monthly_income=financial_data['monthly']['income'] if financial_data else 0,
                           monthly_expense=financial_data['monthly']['expense'] if financial_data else 0,
                           has_data=financial_data and financial_data['total_records'] > 0)


# 智能账单分析
@app.route('/ai_analyze_bills', methods=['POST'])
def ai_analyze_bills():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'})

    user_id = session['user_id']

    # 获取用户财务数据
    financial_data = get_user_financial_data(user_id, 90)

    if not financial_data or financial_data['total_records'] == 0:
        return jsonify({
            'success': False,
            'message': '没有找到账单数据，请先添加一些收支记录。'
        })

    # 构建AI提示词
    prompt = f"""请分析以下用户的财务数据，并提供专业、实用的建议：

## 用户财务概览
- 本月收入：¥{financial_data['monthly']['income']:.2f}
- 本月支出：¥{financial_data['monthly']['expense']:.2f}
- 本月余额：¥{financial_data['monthly']['balance']:.2f}
- 最近90天记录：{financial_data['total_records']}条

## 主要收支分类
"""

    for stat in financial_data['category_stats'][:10]:
        amount = float(stat['total_amount'] or 0)
        if amount != 0:
            sign = "+" if amount > 0 else ""
            prompt += f"- {stat['name']}({stat['type']}): {sign}¥{abs(amount):.2f}\n"

    prompt += """
## 请从以下方面分析：
1. **消费习惯分析**：指出主要的消费类别和可能的节省空间
2. **收入结构分析**：评估收入来源是否健康
3. **储蓄率评估**：根据收支情况评估储蓄是否合理
4. **实用建议**：给出3-5条具体可行的改进建议
5. **风险提示**：提醒潜在的财务风险

## 回复要求：
- 使用中文回复，语气友好、专业
- 使用通俗易懂的语言，避免复杂金融术语
- 格式清晰，使用适当的标题和列表
- 给出具体、可执行的建议
- 如果有异常支出请明确指出"""

    # 调用DeepSeek API
    messages = [
        {
            "role": "system",
            "content": "你是一个专业的财务顾问，擅长分析个人财务数据，提供实用的省钱和理财建议。请用中文回复，语气友好专业。"
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    ai_response = call_deepseek_api(messages, temperature=0.7)

    # 保存到数据库
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO ai_analysis (user_id, analysis_type, user_input, ai_response)
        VALUES (%s, %s, %s, %s)
    """, (user_id, '账单分析', '智能账单分析', ai_response))
    mysql.connection.commit()
    cursor.close()

    return jsonify({
        'success': True,
        'analysis': ai_response,
        'financial_summary': {
            'income': financial_data['monthly']['income'],
            'expense': financial_data['monthly']['expense'],
            'balance': financial_data['monthly']['balance']
        }
    })


# 财务规划建议
@app.route('/ai_financial_plan', methods=['POST'])
def ai_financial_plan():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'})

    user_id = session['user_id']
    data = request.get_json()
    target = data.get('target', '一般储蓄')

    # 获取用户财务数据
    financial_data = get_user_financial_data(user_id, 90)

    if not financial_data or financial_data['total_records'] == 0:
        return jsonify({
            'success': False,
            'message': '没有找到账单数据，请先添加一些收支记录。'
        })

    # 构建规划提示词
    prompt = f"""请根据用户的财务数据制定【{target}】规划：

## 用户当前财务情况
- 月均收入：¥{financial_data['monthly']['income']:.2f}
- 月均支出：¥{financial_data['monthly']['expense']:.2f}
- 当前月余额：¥{financial_data['monthly']['balance']:.2f}
- 消费记录数：{financial_data['total_records']}条（最近90天）

## 请制定详细的【{target}】规划，包括：
1. **目标设定**：明确的、可衡量的财务目标
2. **时间规划**：合理的实现时间表
3. **预算分配**：建议的收入分配比例（生活必需、娱乐、储蓄等）
4. **具体行动计划**：每月/每周的具体执行步骤
5. **预期效果**：坚持执行可以带来的改变
6. **风险提示**：需要注意的事项和潜在风险
7. **进度跟踪**：如何监控规划执行情况

## 回复要求：
- 使用中文回复，提供实用的、可执行的建议
- 使用表格或列表让内容更清晰
- 给出具体的金额建议
- 考虑用户的实际情况（普通工薪阶层）
- 鼓励性语气，增强用户信心"""

    # 调用DeepSeek API
    messages = [
        {
            "role": "system",
            "content": "你是一个专业的财务规划师，擅长制定个人财务规划和预算方案。请用中文回复，提供具体可行的建议。"
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    ai_response = call_deepseek_api(messages, temperature=0.7)

    # 保存到数据库
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO ai_analysis (user_id, analysis_type, user_input, ai_response)
        VALUES (%s, %s, %s, %s)
    """, (user_id, '财务规划', f'{target}规划', ai_response))
    mysql.connection.commit()
    cursor.close()

    return jsonify({
        'success': True,
        'plan': ai_response,
        'target': target
    })


# 智能问答
@app.route('/ai_chat', methods=['POST'])
def ai_chat():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'})

    user_id = session['user_id']
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'success': False, 'message': '消息不能为空'})

    # 获取用户财务数据用于上下文
    financial_data = get_user_financial_data(user_id, 30)

    # 构建上下文
    context = ""
    if financial_data and financial_data['total_records'] > 0:
        context = f"""用户财务背景信息：
- 本月收入：¥{financial_data['monthly']['income']:.2f}
- 本月支出：¥{financial_data['monthly']['expense']:.2f}
- 本月余额：¥{financial_data['monthly']['balance']:.2f}
- 最近记录：{financial_data['total_records']}条

用户问题：{user_message}

请根据用户的财务背景信息，专业、友好地回答用户的问题。如果问题与财务无关，可以礼貌地表示你主要擅长财务咨询。"""
    else:
        context = f"""用户问题：{user_message}

请作为财务顾问回答用户的问题，如果问题与财务无关，可以礼貌地表示你主要擅长财务咨询。"""

    # 调用DeepSeek API
    messages = [
        {
            "role": "system",
            "content": "你是一个专业的财务顾问，帮助用户解答关于记账、理财、预算、省钱、投资等方面的问题。请用中文回复，语气友好专业。"
        },
        {
            "role": "user",
            "content": context
        }
    ]

    ai_response = call_deepseek_api(messages, temperature=0.8, max_tokens=1500)

    # 保存到数据库
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO ai_analysis (user_id, analysis_type, user_input, ai_response)
        VALUES (%s, %s, %s, %s)
    """, (user_id, '智能问答', user_message, ai_response))
    mysql.connection.commit()
    cursor.close()

    return jsonify({
        'success': True,
        'response': ai_response
    })


# 获取AI历史记录
@app.route('/api/ai_history')
def ai_history():
    if 'user_id' not in session:
        return jsonify({'error': '未登录'})

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id, analysis_type, user_input, 
               SUBSTRING(ai_response, 1, 100) as preview,
               created_at
        FROM ai_analysis 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT 20
    """, (session['user_id'],))
    history = cursor.fetchall()
    cursor.close()

    return jsonify(history)


# 获取AI分析详情
@app.route('/api/ai_detail/<int:analysis_id>')
def ai_detail(analysis_id):
    if 'user_id' not in session:
        return jsonify({'error': '未登录'})

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT ai_response 
        FROM ai_analysis 
        WHERE id = %s AND user_id = %s
    """, (analysis_id, session['user_id']))
    detail = cursor.fetchone()
    cursor.close()

    if detail:
        return jsonify({'success': True, 'response': detail['ai_response']})
    else:
        return jsonify({'success': False, 'message': '记录不存在'})


# 删除AI记录
@app.route('/ai_delete/<int:analysis_id>')
def ai_delete(analysis_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    cursor.execute("""
        DELETE FROM ai_analysis 
        WHERE id = %s AND user_id = %s
    """, (analysis_id, session['user_id']))
    mysql.connection.commit()
    cursor.close()

    return redirect(url_for('ai_analysis'))


# AI功能测试接口
@app.route('/ai_test')
def ai_test():
    """测试AI连接是否正常"""
    try:
        messages = [
            {"role": "system", "content": "你是一个测试助手，请简单回答。"},
            {"role": "user", "content": "你好，请回复'AI连接正常'来确认服务可用。"}
        ]

        response = call_deepseek_api(messages, temperature=0.7, max_tokens=100)

        return jsonify({
            'success': True,
            'message': 'AI服务连接正常',
            'response': response,
            'api_key_format': '正确' if app.config['DEEPSEEK_API_KEY'].startswith('sk-') else '错误'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'AI服务连接失败',
            'error': str(e)
        })
if __name__ == '__main__':
    app.run(debug=True, port=5000)