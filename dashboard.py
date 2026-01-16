"""
================================================================================
            CLOUD RFID ATTENDANCE SYSTEM - WEB DASHBOARD
================================================================================

Real-time web dashboard for monitoring RFID attendance system. Displays
live activity feed, attendance statistics and student records with an
attractive modern UI.

================================================================================
"""

from flask import Flask, render_template_string
import pymysql
from datetime import datetime
import pytz

app = Flask(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================
DB_HOST = '34.29.88.122'
DB_USER = 'liyana'
DB_PASS = '123456'
DB_NAME = 'attendance_db'

def get_db_connection():
    """Establish MySQL database connection."""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

# ============================================================================
# ENHANCED UI TEMPLATE
# ============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>RFID Attendance Dashboard</title>
    
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <meta http-equiv="refresh" content="5">

    <style>
        :root {
            --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-success: linear-gradient(135deg, #0cebeb 0%, #20e3b2 100%);
            --gradient-danger: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --gradient-info: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --gradient-dark: linear-gradient(135deg, #434343 0%, #000000 100%);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            background: linear-gradient(to bottom right, #f8f9fa, #e9ecef);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }

        /* Animated Background Pattern */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle at 20% 50%, rgba(102, 126, 234, 0.05) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.05) 0%, transparent 50%);
            z-index: 0;
            pointer-events: none;
        }

        .container { position: relative; z-index: 1; }

        /* Glassmorphism Navbar */
        .navbar {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(20px) saturate(180%);
            border-bottom: 1px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            padding: 1.2rem 0;
        }

        .navbar-brand {
            font-weight: 800;
            font-size: 1.5rem;
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .navbar-brand i {
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
        }

        /* Live Status Badge */
        .status-badge {
            background: rgba(16, 185, 129, 0.1);
            border: 2px solid rgba(16, 185, 129, 0.3);
            padding: 0.5rem 1.2rem;
            border-radius: 50px;
            font-weight: 600;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .pulse-dot {
            width: 10px;
            height: 10px;
            background: #10b981;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { 
                transform: scale(1);
                box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
            }
            50% { 
                transform: scale(1.1);
                box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
            }
        }

        /* Stats Cards with Hover Effects */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            background: white;
            border-radius: 24px;
            padding: 2rem;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border: 1px solid rgba(255, 255, 255, 0.5);
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: var(--gradient);
            opacity: 0;
            transition: opacity 0.3s;
        }

        .stat-card:hover {
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        }

        .stat-card:hover::before {
            opacity: 1;
        }

        .stat-icon {
            width: 70px;
            height: 70px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            margin-bottom: 1.5rem;
            background: var(--gradient);
            color: white;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        }

        .stat-value {
            font-size: 3rem;
            font-weight: 800;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1;
            margin-bottom: 0.5rem;
        }

        .stat-label {
            font-size: 0.95rem;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stat-trend {
            margin-top: 1rem;
            font-size: 0.85rem;
            color: #10b981;
            font-weight: 600;
        }

        /* Main Content Card */
        .content-card {
            background: white;
            border-radius: 24px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
            overflow: hidden;
            margin-bottom: 3rem;
        }

        .card-header-modern {
            background: linear-gradient(to right, #f8f9fa, #ffffff);
            padding: 2rem;
            border-bottom: 2px solid #f3f4f6;
        }

        .card-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1f2937;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .card-title i {
            background: var(--gradient-primary);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .refresh-btn {
            background: white;
            border: 2px solid #e5e7eb;
            padding: 0.6rem 1.5rem;
            border-radius: 12px;
            font-weight: 600;
            color: #6b7280;
            transition: all 0.3s;
        }

        .refresh-btn:hover {
            background: var(--gradient-primary);
            color: white;
            border-color: transparent;
            transform: rotate(180deg);
        }

        /* Table Styling */
        .table-modern {
            margin: 0;
        }

        .table-modern thead th {
            background: #f9fafb;
            color: #374151;
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 1.5rem 2rem;
            border: none;
        }

        .table-modern tbody tr {
            border-bottom: 1px solid #f3f4f6;
            transition: all 0.2s;
        }

        .table-modern tbody tr:hover {
            background: linear-gradient(to right, #f9fafb, #ffffff);
            transform: scale(1.01);
        }

        .table-modern td {
            padding: 1.5rem 2rem;
            vertical-align: middle;
            border: none;
        }

        /* User Identity Cell */
        .user-cell {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .user-avatar {
            width: 50px;
            height: 50px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            flex-shrink: 0;
        }

        .avatar-success {
            background: linear-gradient(135deg, #0cebeb20, #20e3b220);
            color: #059669;
            border: 2px solid #0cebeb40;
        }

        .avatar-danger {
            background: linear-gradient(135deg, #f093fb20, #f5576c20);
            color: #dc2626;
            border: 2px solid #f5576c40;
        }

        .user-info h6 {
            margin: 0;
            font-weight: 700;
            color: #1f2937;
            font-size: 0.95rem;
        }

        .user-info small {
            color: #9ca3af;
            font-size: 0.8rem;
        }

        /* UID Badge */
        .uid-badge {
            background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
            color: #4b5563;
            padding: 0.5rem 1rem;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-weight: 600;
            font-size: 0.85rem;
            border: 1px solid #d1d5db;
        }

        /* Status Badges */
        .status-badge-success {
            background: linear-gradient(135deg, #d1fae5, #a7f3d0);
            color: #065f46;
            padding: 0.5rem 1.2rem;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.8rem;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            border: 2px solid #6ee7b7;
        }

        .status-badge-danger {
            background: linear-gradient(135deg, #fecdd3, #fca5a5);
            color: #991b1b;
            padding: 0.5rem 1.2rem;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.8rem;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            border: 2px solid #fb7185;
        }

        /* Timestamp */
        .timestamp {
            color: #6b7280;
            font-weight: 600;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }
            
            .table-modern {
                font-size: 0.85rem;
            }
            
            .table-modern td, .table-modern th {
                padding: 1rem;
            }
        }

        /* Loading Animation */
        @keyframes shimmer {
            0% { background-position: -1000px 0; }
            100% { background-position: 1000px 0; }
        }

        .loading {
            animation: shimmer 2s infinite;
            background: linear-gradient(to right, #f3f4f6 4%, #e5e7eb 25%, #f3f4f6 36%);
            background-size: 1000px 100%;
        }
    </style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar fixed-top">
    <div class="container">
        <div class="navbar-brand">
            <i class="fa-solid fa-shield-halved"></i>
            <span>RFID Attendance System</span>
        </div>
        <div class="status-badge">
            <div class="pulse-dot"></div>
            <span>System Live</span>
        </div>
    </div>
</nav>

<!-- Main Content -->
<div class="container" style="margin-top: 120px; padding-bottom: 3rem;">
    
    <!-- Stats Cards -->
    <div class="stats-grid">
        <!-- Present Today -->
        <div class="stat-card" style="--gradient: var(--gradient-success);">
            <div class="stat-icon">
                <i class="fa-solid fa-user-check"></i>
            </div>
            <div class="stat-value">{{ stats.present_today }}</div>
            <div class="stat-label">Present Today</div>
            <div class="stat-trend">
                <i class="fa-solid fa-arrow-up"></i> Unique Check-ins
            </div>
        </div>

        <!-- Total Records -->
        <div class="stat-card" style="--gradient: var(--gradient-primary);">
            <div class="stat-icon">
                <i class="fa-solid fa-database"></i>
            </div>
            <div class="stat-value">{{ stats.total_unique_scanned }}</div>
            <div class="stat-label">Total Cards Scanned</div>
            <div class="stat-trend">
                <i class="fa-solid fa-chart-line"></i> All-time Records
            </div>
        </div>
    </div>

    <!-- Activity Feed -->
    <div class="content-card">
        <div class="card-header-modern">
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
                <h2 class="card-title">
                    <i class="fa-solid fa-clock-rotate-left"></i>
                    Recent Activity Feed
                </h2>
                <button class="refresh-btn" onclick="window.location.reload();">
                    <i class="fa-solid fa-arrows-rotate"></i>
                </button>
            </div>
        </div>
        
        <div class="table-responsive">
            <table class="table table-modern">
                <thead>
                    <tr>
                        <th>User Identity</th>
                        <th>Card UID</th>
                        <th>Status</th>
                        <th>Timestamp (GMT+8)</th>
                    </tr>
                </thead>
                <tbody>
                    {% for log in logs %}
                    <tr>
                        <td>
                            <div class="user-cell">
                                {% if log.name %}
                                <div class="user-avatar avatar-success">
                                    <i class="fa-solid fa-user"></i>
                                </div>
                                <div class="user-info">
                                    <h6>{{ log.name }}</h6>
                                    <small>Registered Student</small>
                                </div>
                                {% else %}
                                <div class="user-avatar avatar-danger">
                                    <i class="fa-solid fa-user-slash"></i>
                                </div>
                                <div class="user-info">
                                    <h6 style="color: #dc2626;">Unknown Card</h6>
                                    <small>Unauthorized Access</small>
                                </div>
                                {% endif %}
                            </div>
                        </td>
                        <td>
                            <span class="uid-badge">{{ log.uid }}</span>
                        </td>
                        <td>
                            {% if 'Present' in log.status %}
                            <span class="status-badge-success">
                                <i class="fa-solid fa-circle-check"></i>
                                GRANTED
                            </span>
                            {% else %}
                            <span class="status-badge-danger">
                                <i class="fa-solid fa-circle-xmark"></i>
                                DENIED
                            </span>
                            {% endif %}
                        </td>
                        <td>
                            <div class="timestamp">
                                <i class="fa-regular fa-clock"></i>
                                {{ log.timestamp }}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main dashboard route - displays attendance statistics and recent logs."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Fetch recent logs with student names
            sql_logs = """
            SELECT logs.id, logs.uid, logs.status, logs.timestamp, students.name 
            FROM logs 
            LEFT JOIN students ON logs.uid = students.uid 
            ORDER BY logs.timestamp DESC 
            LIMIT 10
            """
            cursor.execute(sql_logs)
            logs = cursor.fetchall()

            # Calculate statistics with Malaysia timezone
            malaysia_tz = pytz.timezone('Asia/Kuala_Lumpur')
            today_date = datetime.now(malaysia_tz).strftime('%Y-%m-%d')

            # Present today (unique valid students)
            sql_today = "SELECT COUNT(DISTINCT uid) as count FROM logs WHERE status='Present' AND DATE(timestamp) = %s"
            cursor.execute(sql_today, (today_date,))
            present_today = cursor.fetchone()['count']

            # Total unique cards scanned (all time)
            cursor.execute("SELECT COUNT(DISTINCT uid) as count FROM logs")
            total_unique_scanned = cursor.fetchone()['count']

            stats = {
                "present_today": present_today,
                "total_unique_scanned": total_unique_scanned
            }

        conn.close()
        return render_template_string(HTML_TEMPLATE, logs=logs, stats=stats)
    
    except Exception as e:
        return f"""
        <div style='min-height:100vh; display:flex; align-items:center; justify-content:center; 
                    font-family:Inter,sans-serif; background:#f3f4f6;'>
            <div style='background:white; padding:3rem; border-radius:20px; box-shadow:0 10px 40px rgba(0,0,0,0.1);
                        max-width:500px; text-align:center;'>
                <i class='fa-solid fa-triangle-exclamation' style='font-size:4rem; color:#ef4444; margin-bottom:1rem;'></i>
                <h3 style='color:#1f2937; margin-bottom:1rem;'>System Error</h3>
                <p style='color:#6b7280;'>{e}</p>
            </div>
        </div>
        """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)