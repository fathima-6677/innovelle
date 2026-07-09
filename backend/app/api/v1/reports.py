from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, Response
from app.core.security import get_current_user
from app.core.dynamodb import db
import io
import csv
import datetime

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/{wearer_id}")
def generate_report(wearer_id: str, period: str = "weekly", format: str = "pdf", current_user: dict = Depends(get_current_user)):
    """Generate weekly/monthly analytics report summarizing stress, alerts, and geofence adherence"""
    # 1. Fetch wearer profile
    wearer_profile = db.get_item(f"WEARER#{wearer_id}", "PROFILE")
    if not wearer_profile:
        raise HTTPException(status_code=404, detail="Wearer profile not found")

    # 2. Fetch recent alerts and communication logs
    alerts = db.query_gsi1(f"WEARER#{wearer_id}", "ALERT#")
    comms = db.query_by_pk(f"WEARER#{wearer_id}", "COMMLOG#")
    telemetry = db.query_by_pk(f"WEARER#{wearer_id}", "TELEMETRY#")

    title = f"AutiGuard Safety Analytics Report - {wearer_profile.get('first_name')} {wearer_profile.get('last_name')}"
    timestamp_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if format == "csv":
        # Output a CSV log of alerts
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Report Title", title])
        writer.writerow(["Generated At", timestamp_str])
        writer.writerow(["Period", period])
        writer.writerow([])
        writer.writerow(["--- ALERTS LOG ---"])
        writer.writerow(["Alert ID", "Type", "Severity", "Status", "Timestamp"])
        for item in alerts:
            writer.writerow([
                item.get("alert_id"),
                item.get("type"),
                item.get("severity"),
                item.get("ack_status"),
                item.get("timestamp")
            ])
        writer.writerow([])
        writer.writerow(["--- COMMUNICATION TIMELINE LOG ---"])
        writer.writerow(["Event ID", "Category Code", "Timestamp"])
        for item in comms:
            writer.writerow([
                item.get("event_id"),
                item.get("category_code"),
                item.get("SK", "").replace("COMMLOG#", "")
            ])
        
        output.seek(0)
        return Response(content=output.getvalue(), media_type="text/csv", headers={
            "Content-Disposition": f"attachment; filename=autiguard_report_{wearer_id}.csv"
        })

    # PDF Output using ReportLab
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
    except ImportError:
        # Fallback if ReportLab is missing
        return Response(content=f"ReportLab not installed. Summary: {title}. Period: {period}. Alerts: {len(alerts)} items.", media_type="text/plain")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    story = []

    # Palette definitions matching "Professional AWS Cloud" styles
    navy_primary = colors.HexColor("#0F1B2D")
    orange_accent = colors.HexColor("#FF9900")
    teal_accent = colors.HexColor("#00A1C9")
    gray_bg = colors.HexColor("#F4F6F9")

    # Document Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=navy_primary,
        spaceAfter=15
    )
    meta_style = ParagraphStyle(
        'MetaText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor("#555555"),
        spaceAfter=20
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=teal_accent,
        spaceBefore=15,
        spaceAfter=10
    )

    story.append(Paragraph("AutiGuard Safety Report", title_style))
    story.append(Paragraph(f"Wearer: <b>{wearer_profile.get('first_name')} {wearer_profile.get('last_name')}</b> | Period: {period.capitalize()}", meta_style))
    story.append(Paragraph(f"Generated on {timestamp_str}", meta_style))
    story.append(Spacer(1, 10))

    # Metric summary calculations
    total_alerts = len(alerts)
    unacked = sum(1 for a in alerts if a.get("ack_status") == "unacknowledged")
    comms_count = len(comms)
    
    # Simple metric table
    summary_data = [
        ["Metric Summary", "Count"],
        ["Total Safety Warnings", str(total_alerts)],
        ["Unacknowledged Incidents", str(unacked)],
        ["Non-Verbal Comm Assist Presses", str(comms_count)]
    ]
    t = Table(summary_data, colWidths=[200, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), navy_primary),
        ('TEXTCOLOR', (0,0), (1,0), colors.white),
        ('FONTNAME', (0,0), (1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('BACKGROUND', (0,1), (-1,-1), gray_bg),
        ('GRID', (0,0), (-1,-1), 1, colors.white)
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # Alerts history section
    story.append(Paragraph("Critical Safety Alert Logs", section_style))
    alert_headers = [["Type", "Severity", "Timestamp", "Status"]]
    for item in alerts[:10]: # Limit to last 10
        alert_headers.append([
            item.get("type", "Unknown"),
            item.get("severity", "Info").upper(),
            item.get("timestamp")[:16],
            item.get("ack_status", "Active")
        ])
    
    if len(alert_headers) > 1:
        at = Table(alert_headers, colWidths=[120, 70, 150, 100])
        at.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), teal_accent),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, gray_bg]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey)
        ]))
        story.append(at)
    else:
        story.append(Paragraph("No critical alerts logged for this period.", styles['Normal']))

    # Comm logs history section
    story.append(Spacer(1, 15))
    story.append(Paragraph("Non-Verbal Need History", section_style))
    comm_headers = [["Need Category", "Timestamp"]]
    for item in comms[:10]:
        comm_headers.append([
            item.get("category_code"),
            item.get("SK", "").replace("COMMLOG#", "")[:16]
        ])
    
    if len(comm_headers) > 1:
        ct = Table(comm_headers, colWidths=[150, 200])
        ct.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), navy_primary),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, gray_bg]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey)
        ]))
        story.append(ct)
    else:
        story.append(Paragraph("No need category triggers recorded during this period.", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=autiguard_report_{wearer_id}.pdf"
    })
