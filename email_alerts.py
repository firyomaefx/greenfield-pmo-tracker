import yagmail
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from email_config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT, SMTP_SERVER, SMTP_PORT, ALERT_LEAD_DAYS

# Status mapping for PMP tracking
STATUS_WEIGHTS = {
    "Completed": 100,
    "Planned": 0,
    "Delayed": 0,
    "At Risk": 25,
    "In Progress": 50
}

def calculate_project_health(project):
    """Calculate project health score (0-100%) based on milestone completion."""
    milestones = project.get("milestones", [])
    if not milestones:
        return 0
    
    total_weight = 0
    completed_weight = 0
    
    for i, m in enumerate(milestones):
        # Later milestones have higher weight
        weight = (i + 1) / len(milestones)
        total_weight += weight
        
        if m.get("status") == "Completed":
            completed_weight += weight
        elif m.get("status") == "At Risk":
            completed_weight += weight * 0.25
        elif m.get("status") == "In Progress":
            completed_weight += weight * 0.5
    
    return int((completed_weight / total_weight) * 100) if total_weight > 0 else 0

def get_upcoming_milestones(projects, days=7):
    """Get milestones due within the next N days."""
    upcoming = []
    today = datetime.now()
    
    for project in projects:
        for milestone in project.get("milestones", []):
            target = milestone.get("target", "")
            status = milestone.get("status", "")
            
            if status == "Completed":
                continue
                
            # Try to parse target date
            try:
                # Handle various formats: "2026-Q3", "2026-H2", "2027-Spring"
                if "Q" in target:
                    year, q = target.split("-")
                    q_num = int(q[1])
                    month = (q_num - 1) * 3 + 1
                    target_date = datetime(int(year), month, 15)
                elif "H" in target:
                    year, h = target.split("-")
                    h_num = int(h[1])
                    month = (h_num - 1) * 6 + 1
                    target_date = datetime(int(year), month, 15)
                elif "Spring" in target or "Summer" in target or "Fall" in target or "Winter" in target:
                    year = target.split("-")[0]
                    target_date = datetime(int(year), 3, 15)  # Default to March
                else:
                    continue
                
                days_until = (target_date - today).days
                if 0 <= days_until <= days:
                    upcoming.append({
                        "project": project["company"],
                        "milestone": milestone["milestone"],
                        "target_date": target_date.strftime("%Y-%m-%d"),
                        "days_until": days_until,
                        "status": status
                    })
            except:
                continue
    
    return sorted(upcoming, key=lambda x: x["days_until"])

def get_delayed_milestones(projects):
    """Get milestones that are past due."""
    delayed = []
    today = datetime.now()
    
    for project in projects:
        for milestone in project.get("milestones", []):
            status = milestone.get("status", "")
            
            if status == "Completed":
                continue
            
            target = milestone.get("target", "")
            try:
                if "Q" in target:
                    year, q = target.split("-")
                    q_num = int(q[1])
                    month = (q_num - 1) * 3 + 3  # End of quarter
                    target_date = datetime(int(year), month, 30)
                elif "H" in target:
                    year, h = target.split("-")
                    h_num = int(h[1])
                    month = h_num * 6  # End of half-year
                    target_date = datetime(int(year), month, 30)
                else:
                    continue
                
                if target_date < today and status not in ["Completed", "Delayed"]:
                    delayed.append({
                        "project": project["company"],
                        "milestone": milestone["milestone"],
                        "target_date": target_date.strftime("%Y-%m-%d"),
                        "days_overdue": (today - target_date).days,
                        "status": status
                    })
            except:
                continue
    
    return sorted(delayed, key=lambda x: x["days_overdue"], reverse=True)

def generate_alert_report(projects):
    """Generate a comprehensive alert report."""
    upcoming = get_upcoming_milestones(projects, ALERT_LEAD_DAYS)
    delayed = get_delayed_milestones(projects)
    
    # Calculate overall portfolio health
    total_health = 0
    portfolio_risks = []
    
    for project in projects:
        health = calculate_project_health(project)
        total_health += health
        
        if health < 50:
            portfolio_risks.append({
                "project": project["company"],
                "health": health,
                "risk": "Low completion rate"
            })
    
    avg_health = int(total_health / len(projects)) if projects else 0
    
    return {
        "upcoming_milestones": upcoming,
        "delayed_milestones": delayed,
        "portfolio_health": avg_health,
        "portfolio_risks": portfolio_risks,
        "total_projects": len(projects),
        "at_risk_projects": len(portfolio_risks)
    }

def send_email_alert(report, test_mode=False):
    """Send email alert with the report."""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("⚠️ Email credentials not configured. Check email_config.py or .env file.")
        print("Skipping email send in test mode.")
        return False
    
    if test_mode:
        recipient = EMAIL_SENDER  # Send to self in test mode
    else:
        recipient = EMAIL_RECIPIENT or EMAIL_SENDER
    
    try:
        # Initialize yagmail
        yag = yagmail.SMTP(EMAIL_SENDER, EMAIL_PASSWORD, host=SMTP_SERVER, port=SMTP_PORT)
        
        # Build email content
        subject = f"🏭 Greenfield Project Alert | {datetime.now().strftime('%Y-%m-%d')} | Health: {report['portfolio_health']}%"
        
        # HTML Body
        html_body = f"""
        <h1>🏭 Greenfield Factory Project Dashboard Alert</h1>
        <p>Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        
        <h2>📊 Portfolio Health: {report['portfolio_health']}%</h2>
        <p>Total Projects: {report['total_projects']} | At Risk: {report['at_risk_projects']}</p>
        
        <hr>
        
        <h2>⏰ Upcoming Milestones (Next {ALERT_LEAD_DAYS} Days)</h2>
        """
        
        if report['upcoming_milestones']:
            html_body += "<table border='1' cellpadding='10' style='border-collapse: collapse; width: 100%;'>"
            html_body += "<th style='background: #1a472a; color: white;'>Project</th>"
            html_body += "<th style='background: #1a472a; color: white;'>Milestone</th>"
            html_body += "<th style='background: #1a472a; color: white;'>Target Date</th>"
            html_body += "<th style='background: #1a472a; color: white;'>Days Until</th>"
            html_body += "<th style='background: #1a472a; color: white;'>Status</th>"
            
            for item in report['upcoming_milestones']:
                html_body += f"""
                <tr>
                    <td>{item['project']}</td>
                    <td>{item['milestone']}</td>
                    <td>{item['target_date']}</td>
                    <td style='color: #f39c12; font-weight: bold;'>{item['days_until']} days</td>
                    <td>{item['status']}</td>
                </tr>
                """
            html_body += "</table>"
        else:
            html_body += "<p>✅ No upcoming milestones in the next {ALERT_LEAD_DAYS} days.</p>"
        
        html_body += "<hr>"
        
        # Delayed milestones
        html_body += "<h2>🚨 Delayed Milestones</h2>"
        if report['delayed_milestones']:
            html_body += "<table border='1' cellpadding='10' style='border-collapse: collapse; width: 100%;'>"
            html_body += "<th style='background: #c0392b; color: white;'>Project</th>"
            html_body += "<th style='background: #c0392b; color: white;'>Milestone</th>"
            html_body += "<th style='background: #c0392b; color: white;'>Target Date</th>"
            html_body += "<th style='background: #c0392b; color: white;'>Days Overdue</th>"
            html_body += "<th style='background: #c0392b; color: white;'>Status</th>"
            
            for item in report['delayed_milestones']:
                html_body += f"""
                <tr>
                    <td>{item['project']}</td>
                    <td>{item['milestone']}</td>
                    <td>{item['target_date']}</td>
                    <td style='color: #e74c3c; font-weight: bold;'>{item['days_overdue']} days</td>
                    <td>{item['status']}</td>
                </tr>
                """
            html_body += "</table>"
        else:
            html_body += "<p>✅ No delayed milestones.</p>"
        
        html_body += "<hr>"
        
        # Portfolio risks
        if report['portfolio_risks']:
            html_body += "<h2>⚠️ Portfolio Risk Alerts</h2>"
            html_body += "<ul>"
            for risk in report['portfolio_risks']:
                html_body += f"<li><strong>{risk['project']}</strong>: Health {risk['health']}% - {risk['risk']}</li>"
            html_body += "</ul>"
        
        html_body += "<hr>"
        html_body += "<p><em>This is an automated alert from the Greenfield Factory Project Tracker.</em></p>"
        html_body += "<p><em>To update settings, edit email_config.py or the .env file.</em></p>"
        
        # Send email
        yag.send(to=recipient, subject=subject, contents=[html_body])
        yag.close()
        
        print(f"✅ Email alert sent successfully to {recipient}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False

def test_email_config():
    """Test email configuration without sending."""
    print("🔍 Checking email configuration...")
    
    if not EMAIL_SENDER:
        print("❌ EMAIL_SENDER not set")
        return False
    if not EMAIL_PASSWORD:
        print("❌ EMAIL_PASSWORD not set")
        return False
    
    print(f"✅ Email Sender: {EMAIL_SENDER}")
    print(f"✅ SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"✅ Alert Lead Time: {ALERT_LEAD_DAYS} days")
    print(f"✅ Check Interval: 24 hours")
    
    return True

if __name__ == "__main__":
    print("🏭 Greenfield Factory Project Email Alert System")
    print("=" * 50)
    
    # Test configuration
    test_email_config()
    
    # Load projects
    from dashboard import get_default_projects
    projects = get_default_projects()
    
    # Generate report
    report = generate_alert_report(projects)
    
    print(f"\n📊 Portfolio Health: {report['portfolio_health']}%")
    print(f"📅 Upcoming Milestones: {len(report['upcoming_milestones'])}")
    print(f"🚨 Delayed Milestones: {len(report['delayed_milestones'])}")
    
    # Send test email
    if input("\nSend test email? (y/n): ").lower() == 'y':
        send_email_alert(report, test_mode=True)
