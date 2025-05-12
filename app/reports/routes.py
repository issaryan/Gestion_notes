# app/reports/routes.py

from flask import send_file, jsonify
from io import BytesIO
import pandas as pd
from flask_jwt_extended import jwt_required, get_jwt
from functools import wraps
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook

from . import reports_bp
from ..extensions import db
from ..models import Note, Etudiant, Matiere, User

def role_required(*allowed_roles):
    """Décorateur pour limiter l'accès aux rôles spécifiés"""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') not in allowed_roles:
                return jsonify({'message': 'Accès non autorisé'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def _fetch_notes_data():
    """Récupère les données des notes avec les relations"""
    query = (
        db.session.query(
            Etudiant.matricule.label('Matricule'),
            User.nom.label('Nom'),
            Matiere.nom.label('Matiere'),
            Note.note.label('Note'),
            Note.date_saisie.label('Date')
        )
        .join(Note, Etudiant.id == Note.etudiant_id)
        .join(User, Etudiant.user_id == User.id)
        .join(Matiere, Note.matiere_id == Matiere.id)
    )
    return pd.read_sql(query.statement, db.session.bind)

def _add_calculations(df):
    """Ajoute les calculs de moyenne et appréciation"""
    df['Moyenne'] = df.groupby('Matricule')['Note'].transform('mean').round(2)
    df['Appréciation'] = df['Note'].apply(
        lambda x: 'CA' if x > 10 else 'CANT' if x >= 7 else 'NC'
    )
    return df

@reports_bp.route('/notes/csv', methods=['GET'])
@role_required('ADMIN', 'ENSEIGNANT')
def export_notes_csv():
    """Export CSV des notes"""
    try:
        df = _add_calculations(_fetch_notes_data())
        buffer = BytesIO()
        df.to_csv(buffer, index=False, encoding='utf-8-sig')
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name='notes_export.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/notes/excel', methods=['GET'])
@role_required('ADMIN', 'ENSEIGNANT')
def export_notes_excel():
    """Export Excel des notes"""
    try:
        df = _add_calculations(_fetch_notes_data())
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Notes')
            writer.book.save(buffer)
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='notes_export.xlsx'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/notes/pdf', methods=['GET'])
@role_required('ADMIN', 'ENSEIGNANT')
def export_notes_pdf():
    """Export PDF des notes"""
    try:
        df = _add_calculations(_fetch_notes_data())
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        # Titre
        elements.append(Paragraph("Rapport des Notes Académiques", styles['Title']))
        elements.append(Paragraph(" ", styles['Normal']))
        
        # Conversion DataFrame en liste pour le tableau
        data = [df.columns.tolist()] + df.values.tolist()
        
        # Création du tableau
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='notes_export.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500