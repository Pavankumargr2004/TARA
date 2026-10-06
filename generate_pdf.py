import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_number(self, page_count):
        if self._pageNumber == 1:
            return  # Skip header/footer on title page
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Header
        self.drawString(54, 750, "AutoSec TARA Assistant — Complete Presentation Script & Project Guide")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 742, 612 - 54, 742)
        
        # Footer
        self.line(54, 48, 612 - 54, 48)
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 34, page_text)
        self.drawString(54, 34, "CONFIDENTIAL & PROPRIETARY — AUTOSEC TARA PROJECT")
        self.restoreState()

def build_pdf(filename="AutoSec_TARA_Assistant_Presentation_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#1E293B")     # Deep Navy Slate
    SECONDARY = colors.HexColor("#0F766E")   # Teal accent
    ACCENT = colors.HexColor("#0284C7")      # Bright Blue
    TEXT_DARK = colors.HexColor("#0F172A")   # Dark charcoal
    BG_LIGHT = colors.HexColor("#F8FAFC")    # Slate tint
    BORDER_COLOR = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_DARK,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_DARK,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=TEXT_DARK
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white
    )

    script_spoken = ParagraphStyle(
        'ScriptSpoken',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E3A8A"),
        leftIndent=10,
        spaceAfter=4
    )

    script_action = ParagraphStyle(
        'ScriptAction',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#991B1B"),
        leftIndent=10,
        spaceAfter=6
    )

    story = []

    # -------------------------------------------------------------------------
    # COVER / TITLE BLOCK
    # -------------------------------------------------------------------------
    story.append(Paragraph("AutoSec TARA Assistant", title_style))
    story.append(Paragraph("Complete Presentation Script, Technical Guide & Demo Handbook<br/><i>Automated ISO/SAE 21434 & UNECE R155/R156 Cybersecurity Workbench</i>", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=SECONDARY, spaceBefore=0, spaceAfter=15))

    # Meta Table
    meta_data = [
        [Paragraph("<b>Project Name:</b> AutoSec TARA Assistant (TATA-TARA)", body_style), Paragraph("<b>Standards:</b> ISO/SAE 21434 & UNECE R155/R156", body_style)],
        [Paragraph("<b>Architecture:</b> RAG + Pure Python Deterministic Engine", body_style), Paragraph("<b>Target Audience:</b> Leadership, Engineers & Auditors", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[250, 254])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # SECTION 1: PROBLEM STATEMENT
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. Executive Problem Statement", h1_style))
    story.append(Paragraph(
        "Modern Connected & Autonomous Vehicles (CAVs) incorporate over 100 Electronic Control Units (ECUs), complex vehicle-to-everything (V2X) communication channels, OTA updates, and millions of lines of code. This drastically expands the automotive attack surface.",
        body_style
    ))
    story.append(Paragraph("<b>Critical Industry Challenges:</b>", h2_style))
    story.append(Paragraph("• <b>Mandatory Compliance Pressure:</b> UNECE R155/R156 mandates a certified Cybersecurity Management System (CSMS) and ISO/SAE 21434 threat analysis for vehicle type approval across global markets.", bullet_style))
    story.append(Paragraph("• <b>Manual & Fragmented Workflows:</b> Existing TARA practices rely heavily on static, disjointed Excel spreadsheets, leading to human error and data silos.", bullet_style))
    story.append(Paragraph("• <b>Extreme Latency & Resource Drain:</b> Manual TARA for a single ECU architecture requires 4 to 8 weeks of specialized engineering effort per iteration.", bullet_style))
    story.append(Paragraph("• <b>Subjective & Inconsistent Scoring:</b> Risk levels vary drastically across engineering teams due to qualitative guesswork in attack potential estimation.", bullet_style))
    story.append(Paragraph("• <b>Hallucination Risk of Pure GenAI:</b> Applying off-the-shelf LLMs directly to risk scoring risks hallucinating safety-critical regulatory calculations.", bullet_style))

    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # SECTION 2: PROPOSED SOLUTION
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Proposed Solution: AutoSec TARA Assistant", h1_style))
    story.append(Paragraph(
        "<b>AutoSec TARA Assistant</b> is an enterprise-grade threat analysis and risk assessment platform that bridges generative AI intelligence with strict, zero-hallucination deterministic compliance scoring.",
        body_style
    ))
    story.append(Paragraph("<b>Core Solution Innovations:</b>", h2_style))
    story.append(Paragraph("• <b>Deterministic ISO 21434 Risk Engine:</b> Pure Python mathematical engine calculating Attack Potential across 5 standard parameters (Elapsed Time, Expertise, Knowledge, Window, Equipment) mapped to a 4x4 Impact/Feasibility matrix (Annex G). Zero LLM involvement in risk scoring.", bullet_style))
    story.append(Paragraph("• <b>RAG-Powered Threat Knowledge Base:</b> Integrates ChromaDB vector store and BGE local embeddings (`bge-small-en`) to retrieve relevant threat vectors from UNECE R155, MITRE ATT&CK for ICS/Automotive, and CVE databases.", bullet_style))
    story.append(Paragraph("• <b>Generative Threat Synthesis:</b> Uses Google Gemini 2.5 Flash for context-aware threat scenario descriptions and Cybersecurity Requirement (CSR) generation.", bullet_style))
    story.append(Paragraph("• <b>Attack Tree & Topology Graphs:</b> Visualizes complete attack paths and asset dependencies using Graphviz and PyVis interactive graphs.", bullet_style))
    story.append(Paragraph("• <b>Automated Audit Export:</b> Instant generation of UNECE R155 compliant PDF and CSV artifacts for type approval documentation.", bullet_style))

    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # SECTION 3: EXISTING VS OUR PROJECT IMPLEMENTED
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Existing Practices vs. AutoSec TARA Implementation", h1_style))
    
    comp_data = [
        [Paragraph("Feature / Aspect", table_header_style), Paragraph("Existing Industry Practice", table_header_style), Paragraph("AutoSec TARA Assistant", table_header_style)],
        [Paragraph("<b>Assessment Method</b>", table_cell_style), Paragraph("Manual spreadsheet calculations", table_cell_style), Paragraph("Automated Streamlit/FastAPI workbench", table_cell_style)],
        [Paragraph("<b>Risk Calculation</b>", table_cell_style), Paragraph("Qualitative human guesswork", table_cell_style), Paragraph("Deterministic ISO 21434 Annex G matrix", table_cell_style)],
        [Paragraph("<b>Threat Intelligence</b>", table_cell_style), Paragraph("Static PDFs & tribal engineering knowledge", table_cell_style), Paragraph("Semantic ChromaDB RAG vector search", table_cell_style)],
        [Paragraph("<b>Turnaround Time</b>", table_cell_style), Paragraph("4 to 8 weeks per vehicle revision", table_cell_style), Paragraph("< 1 minute per item definition", table_cell_style)],
        [Paragraph("<b>AI Safety & Accuracy</b>", table_cell_style), Paragraph("No AI or unconstrained LLM prompts", table_cell_style), Paragraph("Hybrid AI (LLM for text, Code for risk score)", table_cell_style)],
        [Paragraph("<b>Visual Attack Paths</b>", table_cell_style), Paragraph("Manually drawn Visio/PowerPoint charts", table_cell_style), Paragraph("Dynamic, auto-generated attack graphs", table_cell_style)],
        [Paragraph("<b>Audit & Export</b>", table_cell_style), Paragraph("Disjointed files requiring manual assembly", table_cell_style), Paragraph("1-click standardized PDF/CSV audit reports", table_cell_style)],
    ]
    comp_table = Table(comp_data, colWidths=[110, 194, 200])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
    ]))
    story.append(comp_table)

    story.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # SECTION 4: PUBLIC & INDUSTRY IMPACT
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. Public & Industry Impact", h1_style))
    story.append(Paragraph("• <b>Accelerated Automotive Development:</b> Enables OEMs (e.g. Tata Motors, JLR) and Tier-1 suppliers (Thales, Bosch) to reduce TARA turnaround time by up to 95%, accelerating vehicle launches.", bullet_style))
    story.append(Paragraph("• <b>Guaranteed Regulatory Homologation:</b> Guarantees alignment with UNECE R155 CSMS audit requirements, preventing costly vehicle recall risks or delays in type approval.", bullet_style))
    story.append(Paragraph("• <b>Public Safety Protection:</b> Identifies safety-critical attack paths (e.g., remote CAN bus injection, OTA firmware tampering, gateway spoofing) before vehicles hit public roads.", bullet_style))
    story.append(Paragraph("• <b>Standardized Cybersecurity Lifecycle:</b> Establishes a single source of truth for threat catalogs across cross-functional engineering teams.", bullet_style))

    story.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # SECTION 5: TECHNOLOGIES USED
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. System Architecture & Technologies Used", h1_style))
    
    tech_data = [
        [Paragraph("Component Layer", table_header_style), Paragraph("Technology Stack", table_header_style), Paragraph("Role & Implementation Details", table_header_style)],
        [Paragraph("<b>Frontend Workbench</b>", table_cell_style), Paragraph("Streamlit, Custom CSS", table_cell_style), Paragraph("Thales dark-themed UI workbench, interactive forms, heatmaps", table_cell_style)],
        [Paragraph("<b>API Layer</b>", table_cell_style), Paragraph("FastAPI, Uvicorn, Pydantic", table_cell_style), Paragraph("RESTful backend microservices for enterprise integration", table_cell_style)],
        [Paragraph("<b>Database & Storage</b>", table_cell_style), Paragraph("SQLite, SQLAlchemy ORM", table_cell_style), Paragraph("Persistence for threat scenarios, item definitions, and audit logs", table_cell_style)],
        [Paragraph("<b>Vector Store & Embeddings</b>", table_cell_style), Paragraph("ChromaDB, HuggingFace BGE", table_cell_style), Paragraph("Local embedding (`bge-small-en`) for semantic document retrieval", table_cell_style)],
        [Paragraph("<b>Generative AI Engine</b>", table_cell_style), Paragraph("Google GenAI SDK (Gemini 2.5)", table_cell_style), Paragraph("Context-aware threat description & requirement synthesis", table_cell_style)],
        [Paragraph("<b>Risk Engine</b>", table_cell_style), Paragraph("Pure Python Math Module", table_cell_style), Paragraph("Deterministic Annex G ISO 21434 scoring matrix", table_cell_style)],
        [Paragraph("<b>Visuals & PDF Export</b>", table_cell_style), Paragraph("Graphviz, PyVis, ReportLab", table_cell_style), Paragraph("Interactive attack graphs & downloadable PDF/CSV audit reports", table_cell_style)]
    ]
    tech_table = Table(tech_data, colWidths=[110, 140, 254])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), SECONDARY),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
    ]))
    story.append(tech_table)

    story.append(Spacer(1, 15))

    # Architecture Flow Diagram ASCII Box
    story.append(Paragraph("<b>End-to-End Architecture & Data Flow Diagram:</b>", h2_style))
    arch_box = [
        [Paragraph("""<font name="Courier" size="7.5" color="#0F172A">
+-----------------------------------------------------------------------------------+
|                            STREAMLIT FRONTEND WORKBENCH                           |
|      (Item Definition Input | Interactive Risk Heatmap | Attack Tree Viewer)      |
+----------------------------------------+------------------------------------------+
                                         | REST API / Python Calls
                                         v
+-----------------------------------------------------------------------------------+
|                               FASTAPI / CORE SERVICES                            |
|                                                                                   |
|  +---------------------------+   +-------------------+   +--------------------+  |
|  |     INGESTION SERVICE     |   |   RAG RETRIEVAL   |   | GEMINI LLM ENGINE  |  |
|  | Parses Architecture & Specs|-->| Reads ChromaDB    |-->| Generates Threat   |  |
|  +---------------------------+   | BGE Vector Store  |   | Scenario & CSR     |  |
|                                  +-------------------+   +---------+----------+  |
|                                                                    |              |
|                                  +---------------------------------+              |
|                                  v                                                |
|  +-----------------------------------------------------------------------------+  |
|  |                 DETERMINISTIC ISO/SAE 21434 RISK ENGINE                     |  |
|  |  Sums (Time+Expertise+Knowledge+Window+Equipment) -> Attack Feasibility       |  |
|  |  Max (Safety, Financial, Operational, Privacy) -> Impact Level              |  |
|  |  Lookup in ISO 21434 Annex G Matrix -> Deterministic Risk Level (1-5)       |  |
|  +-------------------------------------+---------------------------------------+  |
|                                        |                                          |
|                                        v                                          |
|  +-----------------------------------------------------------------------------+  |
|  |                          EXPORT & PERSISTENCE LAYER                         |  |
|  |    SQLite Audit DB  |  Graphviz Attack Trees  |  PDF/CSV Report Generation    |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
</font>""", body_style)]
    ]
    arch_table = Table(arch_box, colWidths=[504])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(arch_table)

    story.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # SECTION 6: STEP-BY-STEP PROCESS FLOW
    # -------------------------------------------------------------------------
    story.append(Paragraph("6. Step-by-Step Execution Process & Output", h1_style))
    
    steps = [
        ("Step 1: Item & Architecture Definition", "User inputs vehicle architecture details (e.g. Telematics Gateway, Central Gateway, ADAS ECU, CAN Bus, Ethernet, OTA boundary). Data is parsed into structured Pydantic item definitions."),
        ("Step 2: Vector Ingestion & Knowledge Lookup", "RAG pipeline embeds automotive threat intelligence (ISO 21434 guidelines, UNECE R155 threat catalog, CVE records) into ChromaDB using `bge-small-en` local embeddings."),
        ("Step 3: Threat Scenario & CSR Generation", "RAG pipeline retrieves top matching historical attack patterns. Gemini 2.5 Flash constructs structured threat scenario descriptions, STRIDE categories, and Cybersecurity Requirements (CSR)."),
        ("Step 4: Deterministic Risk Scoring", "The risk engine computes Attack Potential by evaluating 5 factors: Elapsed Time, Expertise, Knowledge of Item, Window of Opportunity, and Equipment. Mapped against maximum Impact (Safety, Financial, Operational, Privacy) to yield the exact ISO 21434 Risk Level (1–5)."),
        ("Step 5: Attack Tree & Dependency Mapping", "GraphBuilder module dynamically draws attack trees showing the exact path an attacker takes from entry boundaries (e.g., Cellular/V2X) to target ECUs."),
        ("Step 6: Mitigation Control Mapping", "Maps Thales & ISO security controls (e.g., SecOC message authentication, Hardware Security Module (HSM), PKI certificates, firewall rules)."),
        ("Step 7: Automated Compliance Export", "Exports complete audit trail reports into PDF and CSV format, fully certified for UNECE type approval submissions.")
    ]

    for title, desc in steps:
        story.append(Paragraph(f"<b>{title}:</b> {desc}", bullet_style))

    story.append(Spacer(1, 15))

    # -------------------------------------------------------------------------
    # SECTION 7: COMPLETE PRESENTATION SCRIPT & DEMO GUIDE
    # -------------------------------------------------------------------------
    story.append(Paragraph("7. Complete Presentation Script & Demo Guide", h1_style))
    story.append(Paragraph("Use this verbatim script during project presentation & live software demo (Duration: ~10 Minutes).", body_style))
    story.append(Spacer(1, 5))

    slides_script = [
        {
            "num": "Slide 1 / Opening",
            "title": "Title & Executive Introduction (0:00 - 1:15)",
            "visual": "Display Dashboard Home Screen / Title Slide",
            "spoken": '"Good morning esteemed judges and members of the panel. Today, we are proud to introduce AutoSec TARA Assistant — an automated, ISO/SAE 21434 and UNECE R155 compliant Threat Analysis and Risk Assessment workbench designed specifically for the automotive industry."',
            "action": "Open Streamlit Workbench at http://localhost:8501. Point out the clean Thales UI dark theme."
        },
        {
            "num": "Slide 2",
            "title": "The Automotive Cybersecurity Crisis (1:15 - 2:30)",
            "visual": "Show Connected Vehicle Attack Surface Diagram",
            "spoken": '"Modern vehicles are no longer purely mechanical; they are software-defined supercomputers on wheels. With over 100 ECUs, wireless V2X communications, and OTA updates, the attack surface has exploded. Regulations like UNECE R155 make TARA mandatory for vehicle type approval. However, traditional TARA is conducted manually using disconnected Excel spreadsheets — taking up to 8 weeks per vehicle revision, incurring massive costs, and exposing OEMs to subjective human error."',
            "action": "Highlight pain points on screen: 8-week delay, manual spreadsheet errors, and unstandardized risk scores."
        },
        {
            "num": "Slide 3",
            "title": "The Solution — AutoSec TARA Assistant (2:30 - 3:45)",
            "visual": "Show Solution Architecture Overview",
            "spoken": '"AutoSec TARA Assistant solves this challenge by combining the intelligence of Generative AI with a zero-hallucination, deterministic risk engine. Our platform ingests vehicle architecture specs, uses RAG vector search to find matching threat vectors, calculates exact ISO 21434 risk scores mathematically, and generates complete audit reports in less than a minute."',
            "action": "Navigate to the System Architecture tab in the application."
        },
        {
            "num": "Slide 4",
            "title": "Live Demo Step 1: System Definition & RAG Retrieval (3:45 - 5:30)",
            "visual": "Demonstrate Ingesting Telematics ECU & OTA Boundary",
            "spoken": '"Let us walk through a live scenario. Here in our TARA Workbench, we select a target item — for instance, the Telematics Control Unit connected via Cellular and CAN Bus. When we trigger threat analysis, our ChromaDB vector database searches thousands of UNECE R155 threat vectors using local BGE embeddings to find exact historical attack patterns."',
            "action": "Click \'Generate TARA Analysis\' for Telematics ECU. Show retrieved ChromaDB citations live on screen."
        },
        {
            "num": "Slide 5",
            "title": "Live Demo Step 2: Deterministic ISO 21434 Engine (5:30 - 7:00)",
            "visual": "Show Risk Matrix Heatmap & Factor Selectors",
            "spoken": '"Now, notice how risk scoring works. Unlike naive LLM implementations that hallucinate scores, our risk engine is 100% deterministic code. We evaluate Attack Potential across 5 ISO parameters: Elapsed Time, Expertise, Knowledge, Window, and Equipment. The system sums these values to determine Attack Feasibility, evaluates maximum Impact across Safety, Financial, Operational, and Privacy, and looks up the exact ISO 21434 Annex G matrix risk level."',
            "action": "Adjust the Expertise slider from \'Layman\' to \'Expert\' live. Show the risk level automatically update from 2 to 4."
        },
        {
            "num": "Slide 6",
            "title": "Live Demo Step 3: Attack Trees & Compliance Export (7:00 - 8:30)",
            "visual": "Show Dynamic Attack Tree Graph & Download PDF Button",
            "spoken": '"Beyond text tables, our system dynamically generates visual Attack Trees using Graphviz, illustrating how an attacker pivots from external cellular networks into the CAN bus. Finally, with a single click, we generate a complete UNECE R155 audit report in PDF and CSV formats, ready for regulatory homologation."',
            "action": "Click \'Download PDF Audit Report\'. Open the generated PDF file to show clean layout and audit trail."
        },
        {
            "num": "Slide 7",
            "title": "Conclusion & Summary (8:30 - 10:00)",
            "visual": "Summary Slide / Impact Metrics",
            "spoken": '"In summary, AutoSec TARA Assistant reduces TARA assessment duration from 8 weeks to under 60 seconds, eliminates subjective human error, enforces strict ISO 21434 compliance, and guarantees regulatory readiness for connected fleets. Thank you, and we welcome your questions!"',
            "action": "Switch back to executive summary view. Invite panel questions."
        }
    ]

    for item in slides_script:
        story.append(KeepTogether([
            Paragraph(f"<b>[{item['num']}] {item['title']}</b>", h2_style),
            Paragraph(f"<b>Visual Cue:</b> {item['visual']}", bullet_style),
            Paragraph(f"<b>Presenter Script:</b> {item['spoken']}", script_spoken),
            Paragraph(f"<b>Demo Action:</b> {item['action']}", script_action),
            Spacer(1, 4)
        ]))

    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # SECTION 8: EXPECTED QUESTIONS & ANSWERS (Q&A)
    # -------------------------------------------------------------------------
    story.append(Paragraph("8. Expected Questions & Answers (Q&A)", h1_style))
    story.append(Paragraph("Comprehensive guide to answering technical, regulatory, and architectural panel questions during the viva/presentation.", body_style))
    story.append(Spacer(1, 5))

    qna_list = [
        ("Q1: How do you prevent LLMs from hallucinating safety-critical risk scores?",
         "A1: We decouple risk calculation entirely from the LLM. The LLM (Gemini 2.5) is restricted solely to text generation for threat descriptions and CSRs. All risk levels, feasibility ratings, and impact assessments are computed by a pure Python mathematical engine following the exact lookup tables in ISO/SAE 21434 Annex G."),

        ("Q2: Which cybersecurity standards does this platform align with?",
         "A2: It strictly aligns with ISO/SAE 21434 (Road vehicles — Cybersecurity engineering) Annex G risk matrices and UNECE R155/R156 CSMS compliance mandates for vehicle type approval."),

        ("Q3: What embedding model and vector database are used for RAG?",
         "A3: We use ChromaDB as our local persistent vector database paired with HuggingFace's `bge-small-en` (BAAI General Embedding) local model. This ensures fast, offline semantic search over threat catalogs without sending confidential architecture docs to cloud vector providers."),

        ("Q4: How does the system handle multi-step attack paths across ECUs?",
         "A4: Our GraphBuilder service constructs directed acyclic graphs (DAGs) representing trust boundaries, entry points (V2X/Telematics), gateway ECUs, and target actuators. Attack trees display step-by-step traversal paths."),

        ("Q5: What happens if an API key for Gemini is unavailable or offline?",
         "A5: The platform features a graceful fallback mechanism. If Gemini is unavailable, the RAG pipeline populates threat scenarios directly from ChromaDB's indexed UNECE/ISO standard document chunks while the deterministic risk engine continues scoring without disruption."),

        ("Q6: How does this project scale for enterprise Tier-1 suppliers like Thales or Tata Motors?",
         "A6: Built with a FastAPI microservice backend and SQLite/PostgreSQL storage, the platform can be deployed via Docker containers (`docker-compose up`) into enterprise CI/CD pipelines and connected to ALM tools like Jama or Jira."),

        ("Q7: How is Attack Potential computed in ISO 21434?",
         "A7: It sums 5 factors: Elapsed Time, Expertise, Knowledge of Item, Window of Opportunity, and Equipment. Scores <= 9 yield 'High' feasibility, 10-13 yield 'Medium', 14-19 yield 'Low', and >= 20 yield 'Very Low'."),

        ("Q8: How does the system determine the final Impact level?",
         "A8: Impact is evaluated across four distinct dimensions: Safety, Financial, Operational, and Privacy. The engine takes the maximum severity level among all four dimensions as per ISO 21434 recommendations.")
    ]

    for q, a in qna_list:
        story.append(KeepTogether([
            Paragraph(f"<b>{q}</b>", h2_style),
            Paragraph(a, body_style),
            Spacer(1, 4)
        ]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {filename}")

if __name__ == "__main__":
    build_pdf()
