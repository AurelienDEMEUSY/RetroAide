from fpdf import FPDF
import re
import os
import json

def sanitize(text) -> str:
    if text is None:
        return ""
    text = str(text)
    replacements = {
        "’": "'",
        "œ": "oe",
        "Œ": "OE",
        "—": "-",
        "–": "-",
        "«": '"',
        "»": '"',
        "“": '"',
        "”": '"',
        "…": "...",
        "€": "euros",
        "°": ".",
        "\u202f": " ",
        "\u00a0": " ",
        "➡️": "->",
        "➡": "->",
    }
    for o, n in replacements.items():
        text = text.replace(o, n)
    return text

class FactureRetraitePDF(FPDF):
    def __init__(self, nom_utilisateur="[NOM_UTILISATEUR]", id_dossier="123456"):
        super().__init__()
        self.nom_utilisateur = sanitize(nom_utilisateur)
        self.id_dossier = sanitize(id_dossier)

    def header(self):
        # Filigrane
        self.set_font("helvetica", "B", 50)
        self.set_text_color(245, 245, 245)
        with self.local_context(fill_opacity=1.0):
            with self.rotation(45, x=105, y=148):
                self.text(x=10, y=120, text=f"CONFIDENTIEL - {self.nom_utilisateur}")
                self.text(x=-30, y=210, text=f"CONFIDENTIEL - {self.nom_utilisateur}")

        if self.page_no() == 1:
            # En-tête
            self.set_font("helvetica", "B", 24)
            self.set_text_color(30, 60, 100)
            self.cell(0, 12, "RAPPORT DE SYNTHÈSE RETRAITE", align="C", new_x="LMARGIN", new_y="NEXT")
            
            self.set_draw_color(30, 60, 100)
            self.set_line_width(0.8)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)
            
            self.set_font("helvetica", "", 10)
            self.set_text_color(100, 100, 100)
            self.cell(0, 5, sanitize(f"RÉFÉRENCE DOSSIER : {self.id_dossier}"), align="R", new_x="LMARGIN", new_y="NEXT")
            self.ln(6)
        else:
            self.set_font("helvetica", "B", 10)
            self.set_text_color(30, 60, 100)
            self.cell(0, 8, sanitize(f"Rapport de synthèse - {self.nom_utilisateur} (Réf: {self.id_dossier})"), align="R", new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(30, 60, 100)
            self.set_line_width(0.3)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        texte_footer = f"Généré par RetroAide - Document strictement personnel - Page {self.page_no()}/{{nb}}"
        self.cell(0, 5, sanitize(texte_footer), align="C")


    # ---- Méthodes de formatting ----
    def section_title(self, texte):
        self.ln(4)
        self.set_fill_color(240, 245, 250)
        self.set_text_color(30, 60, 100)
        self.set_font("helvetica", "B", 12)
        safe_text = sanitize(texte).upper()
        self.cell(0, 8, f"  {safe_text}", fill=True, border="L", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def sub_title(self, texte):
        self.ln(2)
        self.set_font("helvetica", "B", 11)
        self.set_text_color(30, 60, 100)
        self.cell(0, 6, sanitize(texte), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def key_value_row(self, key, value, bold_value=True):
        self.set_font("helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        safe_key = sanitize(key)
        
        # Ajuster exactement la largeur de la clef
        w = self.get_string_width(safe_key) + 2
        self.cell(w, 6, safe_key)
        
        if bold_value:
            self.set_font("helvetica", "B", 10)
            self.set_text_color(20, 20, 20)
        else:
            self.set_font("helvetica", "", 10)
            self.set_text_color(40, 40, 40)
            
        self.multi_cell(0, 6, sanitize(value), new_x="LMARGIN", new_y="NEXT")

    def paragraph(self, texte, italic=False):
        style = "I" if italic else ""
        self.set_font("helvetica", style, 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, sanitize(texte), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def info_box(self, texte):
        self.ln(2)
        self.set_fill_color(255, 250, 240)
        self.set_draw_color(240, 200, 150)
        self.set_font("helvetica", "", 10)
        self.set_text_color(80, 50, 30)
        
        old_l = self.l_margin
        self.set_left_margin(15)
        self.set_x(15)
        self.multi_cell(0, 5, sanitize(texte), border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.set_left_margin(old_l)
        self.ln(3)

    def hr(self):
        self.ln(3)
        self.set_draw_color(220, 220, 220)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)

    def checklist_step_title(self, step_str):
        self.ln(2)
        self.set_font("helvetica", "B", 10)
        self.set_text_color(30, 60, 100)
        self.cell(0, 6, sanitize(step_str), new_x="LMARGIN", new_y="NEXT")

    def checklist_detail(self, detail):
        old_l = self.l_margin
        self.set_left_margin(15)
        self.set_x(15)
        self.set_font("helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 5, sanitize(detail), new_x="LMARGIN", new_y="NEXT")
        self.set_left_margin(old_l)

    def checklist_link(self, url):
        old_l = self.l_margin
        self.set_left_margin(15)
        self.set_x(15)
        self.set_font("helvetica", "I", 9)
        self.set_text_color(100, 120, 180)
        self.cell(0, 5, sanitize(f"Lien : {url}"), new_x="LMARGIN", new_y="NEXT")
        self.set_left_margin(old_l)
        self.ln(2)

    def signature_block(self, ville, date):
        self.ln(8)
        self.set_font("helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        safe_ville = sanitize(ville) if ville else "...................."
        safe_date = sanitize(date) if date else "...................."
        
        self.cell(0, 6, f"Fait à {safe_ville}, le {safe_date}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, "Signature de l'intéressé(e) :", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(15)

    def disclaimer(self):
        self.ln(5)
        self.set_font("helvetica", "B", 9)
        self.set_text_color(180, 50, 30)
        self.cell(0, 5, sanitize("MENTION LÉGALE & AVERTISSEMENT"), new_x="LMARGIN", new_y="NEXT")
        
        self.set_font("helvetica", "", 8)
        self.set_text_color(80, 80, 80)
        texte = (
            "RetroAide est un outil d'information pédagogique. Les résultats contenus dans ce "
            "document sont des estimations basées sur les informations déclaratives de votre profil, "
            "modélisées de manière simplifiée. Ils ne constituent en aucun cas une base officielle, "
            "ni un avis juridique, ni une décision d'attribution. Pour toute démarche officielle de "
            "liquidation, veuillez consulter directement les caisses concernées (ex. CNAV, Agirc-Arrco)."
        )
        self.multi_cell(0, 4, sanitize(texte), border="T", new_x="LMARGIN", new_y="NEXT")


def generate_pdf(data_input, output_path: str = "rapport_synthese.pdf") -> str:
    if isinstance(data_input, str):
        try:
            data = json.loads(data_input)
        except json.JSONDecodeError:
            print("Erreur: Le format JSON fourni n'est pas valide.")
            return ""
    else:
        data = data_input

    identity = data.get("identity", {})
    nom = identity.get("nom_utilisateur", "Non renseigné")
    id_dossier = str(identity.get("id_dossier", "000000"))[:8]
    ville = identity.get("ville_signature", "Non renseignée")
    date_sig = identity.get("date_signature", "Date non renseignée")

    md_content = data.get("markdown", {}).get("document_complet", "")
    
    pdf = FactureRetraitePDF(nom_utilisateur=nom, id_dossier=id_dossier)
    pdf.alias_nb_pages()
    pdf.add_page()

    if identity and id_dossier != "000000":
        pdf.section_title("1. IDENTITÉ ET RÉFÉRENCES")
        pdf.key_value_row("Nom de l'utilisateur :", nom)
        pdf.key_value_row("Identifiant de dossier :", id_dossier)
        pdf.key_value_row("Date de l'analyse :", date_sig)
        pdf.key_value_row("Lieu :", ville)

    if not md_content:
        pdf.paragraph("Aucune donnée d'analyse fournie.")
        pdf.output(output_path)
        return output_path

    lines = md_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('## '):
            pdf.section_title(line[3:])
            
        elif line.startswith('### '):
            pdf.sub_title(line[4:].replace('**', ''))
            
        elif line.startswith('# '):
            pass  
            
        elif line.startswith('- **') and ' : ' in line:
            parts = line.rsplit(' : ', 1)
            if len(parts) == 2:
                key = parts[0][2:].replace('**', '').strip()
                val = parts[1]
                # Enlever _(...)_
                val = re.sub(r'\s*_\(.*?\)_', '', val)
                val = val.replace('**', '').replace('*', '').strip().strip('_')
                pdf.key_value_row(key + " :", val)
            else:
                pdf.paragraph("- " + line[2:].replace('**', ''))
                
        elif line.startswith('- Lien : <') or line.startswith('- Lien: <'):
            try:
                url = line.split('<')[1].split('>')[0]
                pdf.checklist_link(url)
            except IndexError:
                pdf.paragraph(line)
                
        elif line.startswith('- '):
            text = line[2:].replace('**', '')
            if text.startswith('Demandez') or text.startswith('Utilisez') or text.startswith('Un conseiller'):
                pdf.checklist_detail(text)
            else:
                pdf.paragraph("- " + text)
                
        elif re.match(r'^\d+\. \*\*', line):
            text = line.replace('**', '')
            pdf.checklist_step_title(text)

        elif line.startswith('> '):
            text = line[2:].replace('**', '').strip('_').strip('*').strip()
            pdf.info_box(text)
            
        elif line.startswith('---'):
            pdf.hr()
            
        elif line.startswith("{'") and line.endswith("'}"):
            pdf.set_font("courier", "", 8)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 4, sanitize(line), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
            
        else:
            text = line.replace('**', '')
            if (text.startswith('_') and text.endswith('_')) or (text.startswith('*') and text.endswith('*')):
                pdf.paragraph(text.strip('_*'), italic=True)
            else:
                pdf.paragraph(text)

    pdf.signature_block(ville, date_sig)
    pdf.disclaimer()
    pdf.output(output_path)
    return output_path
