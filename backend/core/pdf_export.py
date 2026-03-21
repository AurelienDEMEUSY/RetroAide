"""
Génération PDF du rapport de synthèse retraite (fpdf2).

Ce module convertit le ``document_complet`` markdown en PDF formaté,
avec identité, disclaimer légal et filigrane confidentiel.
"""

from __future__ import annotations

import json
import logging
import re
from io import BytesIO
from typing import Any, BinaryIO, Union

from fpdf import FPDF

logger = logging.getLogger(__name__)


def sanitize(text: Any) -> str:
    """Remplace les caractères Unicode non supportés par fpdf2 (latin-1)."""
    if text is None:
        return ""
    text = str(text)
    replacements = {
        "\u2019": "'",
        "\u0153": "oe",
        "\u0152": "OE",
        "\u2014": "-",
        "\u2013": "-",
        "\u00ab": '"',
        "\u00bb": '"',
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u20ac": "euros",
        "\u00b0": ".",
        "\u202f": " ",
        "\u00a0": " ",
        "\u27a1\ufe0f": "->",
        "\u27a1": "->",
    }
    for o, n in replacements.items():
        text = text.replace(o, n)
    return text


class FactureRetraitePDF(FPDF):
    """PDF A4 du rapport de synthèse retraite avec filigrane et mise en page professionnelle."""

    def __init__(self, nom_utilisateur: str = "[NOM_UTILISATEUR]", id_dossier: str = "123456") -> None:
        super().__init__()
        self.nom_utilisateur = sanitize(nom_utilisateur)
        self.id_dossier = sanitize(id_dossier)

    def header(self) -> None:
        """En-tête avec filigrane confidentiel et titre ou référence dossier."""
        # Filigrane
        self.set_font("helvetica", "B", 50)
        self.set_text_color(245, 245, 245)
        # Rendre le texte non sélectionnable / non interactif
        self._out("/Artifact <</Subtype /Watermark /Type /Pagination>> BDC")
        with self.local_context(fill_opacity=1.0):
            with self.rotation(45, x=105, y=148):
                self.text(x=10, y=120, text=f"CONFIDENTIEL - {self.nom_utilisateur}")
                self.text(x=-30, y=210, text=f"CONFIDENTIEL - {self.nom_utilisateur}")
        self._out("EMC")

        if self.page_no() == 1:
            self._render_first_page_header()
        else:
            self._render_continuation_header()

    def _render_first_page_header(self) -> None:
        """Titre principal centré sur la première page."""
        self.set_font("helvetica", "B", 24)
        self.set_text_color(30, 60, 100)
        self.cell(0, 12, "RAPPORT DE SYNTH\u00c8SE RETRAITE", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 60, 100)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)
        self.set_font("helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, sanitize(f"R\u00c9F\u00c9RENCE DOSSIER : {self.id_dossier}"), align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(6)

    def _render_continuation_header(self) -> None:
        """En-tête compact pour les pages suivantes."""
        self.set_font("helvetica", "B", 10)
        self.set_text_color(30, 60, 100)
        self.cell(0, 8, sanitize(f"Rapport de synth\u00e8se - {self.nom_utilisateur} (R\u00e9f: {self.id_dossier})"), align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 60, 100)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self) -> None:
        """Pied de page avec numéro et mention RetroAide."""
        self.set_y(-15)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        texte_footer = f"G\u00e9n\u00e9r\u00e9 par RetroAide - Document strictement personnel - Page {self.page_no()}/{{nb}}"
        self.cell(0, 5, sanitize(texte_footer), align="C")

    # ---- Méthodes de formatting ----

    def section_title(self, texte: str) -> None:
        """Titre de section (bandeau bleu, texte capitalisé)."""
        self.ln(4)
        self.set_fill_color(240, 245, 250)
        self.set_text_color(30, 60, 100)
        self.set_font("helvetica", "B", 12)
        safe_text = sanitize(texte).upper()
        self.cell(0, 8, f"  {safe_text}", fill=True, border="L", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def sub_title(self, texte: str) -> None:
        """Sous-titre (gras bleu, sans bandeau)."""
        self.ln(2)
        self.set_font("helvetica", "B", 11)
        self.set_text_color(30, 60, 100)
        self.cell(0, 6, sanitize(texte), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def key_value_row(self, key: str, value: str, bold_value: bool = True) -> None:
        """Ligne clé : valeur (ex. « Nom : Dupont »)."""
        self.set_font("helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        safe_key = sanitize(key)
        w = self.get_string_width(safe_key) + 2
        self.cell(w, 6, safe_key)
        if bold_value:
            self.set_font("helvetica", "B", 10)
            self.set_text_color(20, 20, 20)
        else:
            self.set_font("helvetica", "", 10)
            self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6, sanitize(value), new_x="LMARGIN", new_y="NEXT")

    def paragraph(self, texte: str, italic: bool = False) -> None:
        """Paragraphe de texte courant."""
        style = "I" if italic else ""
        self.set_font("helvetica", style, 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, sanitize(texte), new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def info_box(self, texte: str) -> None:
        """Encadré d'information (fond jaune pâle)."""
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

    def hr(self) -> None:
        """Ligne de séparation horizontale."""
        self.ln(3)
        self.set_draw_color(220, 220, 220)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(3)

    def checklist_step_title(self, step_str: str) -> None:
        """Titre d'une étape de checklist (gras bleu)."""
        self.ln(2)
        self.set_font("helvetica", "B", 10)
        self.set_text_color(30, 60, 100)
        self.cell(0, 6, sanitize(step_str), new_x="LMARGIN", new_y="NEXT")

    def checklist_detail(self, detail: str) -> None:
        """Détail indenté d'une étape de checklist."""
        old_l = self.l_margin
        self.set_left_margin(15)
        self.set_x(15)
        self.set_font("helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 5, sanitize(detail), new_x="LMARGIN", new_y="NEXT")
        self.set_left_margin(old_l)

    def checklist_link(self, url: str) -> None:
        """Lien indenté sous un élément de checklist."""
        old_l = self.l_margin
        self.set_left_margin(15)
        self.set_x(15)
        self.set_font("helvetica", "I", 9)
        self.set_text_color(100, 120, 180)
        self.cell(0, 5, sanitize(f"Lien : {url}"), new_x="LMARGIN", new_y="NEXT")
        self.set_left_margin(old_l)
        self.ln(2)

    def signature_block(self, ville: str, date: str) -> None:
        """Bloc de signature en bas de document."""
        self.ln(8)
        self.set_font("helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        safe_ville = sanitize(ville) if ville else "...................."
        safe_date = sanitize(date) if date else "...................."
        self.cell(0, 6, f"Fait \u00e0 {safe_ville}, le {safe_date}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 6, "Signature de l'int\u00e9ress\u00e9(e) :", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(15)

    def disclaimer(self) -> None:
        """Mention légale obligatoire (PRD §9)."""
        self.ln(5)
        self.set_font("helvetica", "B", 9)
        self.set_text_color(180, 50, 30)
        self.cell(0, 5, sanitize("MENTION L\u00c9GALE & AVERTISSEMENT"), new_x="LMARGIN", new_y="NEXT")
        self.set_font("helvetica", "", 8)
        self.set_text_color(80, 80, 80)
        texte = (
            "RetroAide est un outil d'information p\u00e9dagogique. Les r\u00e9sultats contenus dans ce "
            "document sont des estimations bas\u00e9es sur les informations d\u00e9claratives de votre profil, "
            "mod\u00e9lis\u00e9es de mani\u00e8re simplifi\u00e9e. Ils ne constituent en aucun cas une base officielle, "
            "ni un avis juridique, ni une d\u00e9cision d'attribution. Pour toute d\u00e9marche officielle de "
            "liquidation, veuillez consulter directement les caisses concern\u00e9es (ex. CNAV, Agirc-Arrco)."
        )
        self.multi_cell(0, 4, sanitize(texte), border="T", new_x="LMARGIN", new_y="NEXT")


# ---------------------------------------------------------------------------
# Markdown → PDF renderer (sous-fonctions extraites)
# ---------------------------------------------------------------------------

def _render_h2(pdf: FactureRetraitePDF, line: str) -> None:
    """Rend un titre ## en section_title."""
    pdf.section_title(line[3:])


def _render_h3(pdf: FactureRetraitePDF, line: str) -> None:
    """Rend un titre ### en sub_title."""
    pdf.sub_title(line[4:].replace("**", ""))


def _render_key_value_bullet(pdf: FactureRetraitePDF, line: str) -> None:
    """Rend ``- **Clé** : valeur`` en key_value_row."""
    parts = line.rsplit(" : ", 1)
    if len(parts) == 2:
        key = parts[0][2:].replace("**", "").strip()
        val = parts[1]
        val = re.sub(r"\s*_\(.*?\)_", "", val)
        val = val.replace("**", "").replace("*", "").strip().strip("_")
        pdf.key_value_row(key + " :", val)
    else:
        pdf.paragraph("- " + line[2:].replace("**", ""))


def _render_link_bullet(pdf: FactureRetraitePDF, line: str) -> None:
    """Rend ``- Lien : <url>`` en checklist_link."""
    try:
        url = line.split("<")[1].split(">")[0]
        pdf.checklist_link(url)
    except IndexError:
        pdf.paragraph(line)


def _render_plain_bullet(pdf: FactureRetraitePDF, line: str) -> None:
    """Rend un tiret ``- texte`` en paragraphe ou checklist_detail."""
    text = line[2:].replace("**", "")
    if text.startswith(("Demandez", "Utilisez", "Un conseiller")):
        pdf.checklist_detail(text)
    else:
        pdf.paragraph("- " + text)


def _render_numbered_step(pdf: FactureRetraitePDF, line: str) -> None:
    """Rend ``1. **Titre**`` en checklist_step_title."""
    pdf.checklist_step_title(line.replace("**", ""))


def _render_blockquote(pdf: FactureRetraitePDF, line: str) -> None:
    """Rend ``> texte`` en info_box."""
    text = line[2:].replace("**", "").strip("_").strip("*").strip()
    pdf.info_box(text)


def _render_dict_line(pdf: FactureRetraitePDF, line: str) -> None:
    """Rend une ligne brute de type dict stringifié en police fixe."""
    pdf.set_font("courier", "", 8)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 4, sanitize(line), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)


def _render_generic_text(pdf: FactureRetraitePDF, line: str) -> None:
    """Rend du texte brut, italique si entouré de _ ou *."""
    text = line.replace("**", "")
    if (text.startswith("_") and text.endswith("_")) or (text.startswith("*") and text.endswith("*")):
        pdf.paragraph(text.strip("_*"), italic=True)
    else:
        pdf.paragraph(text)


def _render_markdown_line(pdf: FactureRetraitePDF, line: str) -> None:
    """Dispatch une ligne markdown vers le bon renderer."""
    if line.startswith("## "):
        _render_h2(pdf, line)
    elif line.startswith("### "):
        _render_h3(pdf, line)
    elif line.startswith("# "):
        pass  # titre h1 ignoré (déjà dans l'en-tête PDF)
    elif line.startswith("- **") and " : " in line:
        _render_key_value_bullet(pdf, line)
    elif line.startswith("- Lien : <") or line.startswith("- Lien: <"):
        _render_link_bullet(pdf, line)
    elif line.startswith("- "):
        _render_plain_bullet(pdf, line)
    elif re.match(r"^\d+\. \*\*", line):
        _render_numbered_step(pdf, line)
    elif line.startswith("> "):
        _render_blockquote(pdf, line)
    elif line.startswith("---"):
        pdf.hr()
    elif line.startswith("{'") and line.endswith("'}"):
        _render_dict_line(pdf, line)
    else:
        _render_generic_text(pdf, line)


# ---------------------------------------------------------------------------
# Fonctions d'assemblage
# ---------------------------------------------------------------------------

def _coerce_report_dict(data_input: Union[str, dict[str, Any]]) -> dict[str, Any]:
    """Convertit un JSON string en dict si nécessaire."""
    if isinstance(data_input, str):
        try:
            return json.loads(data_input)
        except json.JSONDecodeError:
            return {}
    return data_input


def _emit_pdf(
    pdf: FactureRetraitePDF,
    ville: str,
    date_sig: str,
    target: Union[str, BinaryIO],
) -> Union[str, bytes]:
    """Ajoute signature + disclaimer puis écrit le PDF dans ``target``."""
    pdf.signature_block(ville, date_sig)
    pdf.disclaimer()
    if isinstance(target, BytesIO):
        pdf.output(target)
        return target.getvalue()
    pdf.output(target)
    return target


def _build_report_pdf_body(
    data: dict[str, Any],
    target: Union[str, BinaryIO],
) -> Union[str, bytes]:
    """Construit le corps du PDF à partir du dict rapport (identity + markdown)."""
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
        pdf.section_title("1. IDENTIT\u00c9 ET R\u00c9F\u00c9RENCES")
        pdf.key_value_row("Nom de l'utilisateur :", nom)
        pdf.key_value_row("Identifiant de dossier :", id_dossier)
        pdf.key_value_row("Date de l'analyse :", date_sig)
        pdf.key_value_row("Lieu :", ville)

    if not md_content:
        pdf.paragraph("Aucune donn\u00e9e d'analyse fournie.")
        return _emit_pdf(pdf, ville, date_sig, target)

    for line in md_content.split("\n"):
        line = line.strip()
        if not line:
            continue
        _render_markdown_line(pdf, line)

    return _emit_pdf(pdf, ville, date_sig, target)


def generate_pdf_bytes(data_input: Union[str, dict[str, Any]]) -> bytes:
    """Génère le PDF en mémoire (réponse HTTP)."""
    data = _coerce_report_dict(data_input)
    if not data and isinstance(data_input, str):
        return b""
    buf = BytesIO()
    out = _build_report_pdf_body(data, buf)
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    return buf.getvalue()

