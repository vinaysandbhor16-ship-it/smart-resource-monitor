"""Modern Dark and Light Theme stylesheets for NEXUS."""

DARK_THEME_QSS = """
/* Global Window & Typography */
QMainWindow, QWidget {
    background-color: #0B1020;
    color: #F1F5F9;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

/* Sidebar */
#SidebarWidget {
    background-color: #111827;
    border-right: 1px solid #1E293B;
}

#SidebarTitle {
    color: #38BDF8;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1.5px;
}

#SidebarSubtitle {
    color: #94A3B8;
    font-size: 11px;
    font-weight: 500;
}

/* Navigation Buttons */
QPushButton.NavButton {
    background-color: transparent;
    color: #94A3B8;
    border: none;
    border-radius: 8px;
    text-align: left;
    padding: 10px 16px;
    font-size: 14px;
    font-weight: 600;
}

QPushButton.NavButton:hover {
    background-color: #1F2937;
    color: #F8FAFC;
}

QPushButton.NavButton:checked {
    background-color: #1E293B;
    color: #38BDF8;
    border-left: 3px solid #38BDF8;
}

/* Top Header Bar */
#HeaderWidget {
    background-color: #0F172A;
    border-bottom: 1px solid #1E293B;
    padding: 8px 20px;
}

#HeaderStatusBadge {
    background-color: #064E3B;
    color: #34D399;
    font-size: 11px;
    font-weight: 600;
    border-radius: 12px;
    padding: 4px 10px;
}

#HeaderStatusBadgeStopped {
    background-color: #450A0A;
    color: #F87171;
    font-size: 11px;
    font-weight: 600;
    border-radius: 12px;
    padding: 4px 10px;
}

/* Cards */
QFrame.MetricCard {
    background-color: #151E30;
    border: 1px solid #1E293B;
    border-radius: 10px;
    padding: 16px;
}

QFrame.MetricCard:hover {
    border: 1px solid #334155;
}

QLabel.CardTitle {
    color: #94A3B8;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QLabel.CardValue {
    color: #F8FAFC;
    font-size: 26px;
    font-weight: 700;
}

QLabel.CardSubtext {
    color: #64748B;
    font-size: 11px;
}

/* Standard Buttons */
QPushButton.PrimaryButton {
    background-color: #0284C7;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton.PrimaryButton:hover {
    background-color: #0369A1;
}

QPushButton.PrimaryButton:pressed {
    background-color: #075985;
}

QPushButton.SecondaryButton {
    background-color: #1E293B;
    color: #E2E8F0;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 500;
}

QPushButton.SecondaryButton:hover {
    background-color: #334155;
}

QPushButton.DangerButton {
    background-color: #991B1B;
    color: #FEE2E2;
    border: 1px solid #B91C1C;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 600;
}

QPushButton.DangerButton:hover {
    background-color: #B91C1C;
}

/* Input Fields & Search */
QLineEdit {
    background-color: #0F172A;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
}

QLineEdit:focus {
    border: 1px solid #38BDF8;
}

QComboBox {
    background-color: #0F172A;
    color: #F8FAFC;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 12px;
}

QComboBox::drop-down {
    border: none;
}

/* Modern Tables */
QTableWidget {
    background-color: #0F172A;
    color: #E2E8F0;
    border: 1px solid #1E293B;
    border-radius: 8px;
    gridline-color: #1E293B;
    selection-background-color: #1E293B;
    selection-color: #38BDF8;
}

QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #1E293B;
}

QHeaderView::section {
    background-color: #111827;
    color: #94A3B8;
    font-weight: 600;
    font-size: 12px;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #1E293B;
}

/* Progress Bars */
QProgressBar {
    background-color: #1E293B;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: #FFFFFF;
    font-size: 10px;
    font-weight: bold;
    min-height: 12px;
    max-height: 14px;
}

QProgressBar::chunk {
    background-color: #38BDF8;
    border-radius: 4px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #0B1020;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Tab & Dialogs */
QDialog {
    background-color: #0F172A;
    color: #F8FAFC;
}
"""

LIGHT_THEME_QSS = """
QMainWindow, QWidget {
    background-color: #F8FAFC;
    color: #0F172A;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

#SidebarWidget {
    background-color: #FFFFFF;
    border-right: 1px solid #E2E8F0;
}

#SidebarTitle {
    color: #0284C7;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 1.5px;
}

#SidebarSubtitle {
    color: #64748B;
    font-size: 11px;
    font-weight: 500;
}

QPushButton.NavButton {
    background-color: transparent;
    color: #64748B;
    border: none;
    border-radius: 8px;
    text-align: left;
    padding: 10px 16px;
    font-size: 14px;
    font-weight: 600;
}

QPushButton.NavButton:hover {
    background-color: #F1F5F9;
    color: #0F172A;
}

QPushButton.NavButton:checked {
    background-color: #E0F2FE;
    color: #0284C7;
    border-left: 3px solid #0284C7;
}

#HeaderWidget {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    padding: 8px 20px;
}

#HeaderStatusBadge {
    background-color: #DCFCE7;
    color: #15803D;
    font-size: 11px;
    font-weight: 600;
    border-radius: 12px;
    padding: 4px 10px;
}

#HeaderStatusBadgeStopped {
    background-color: #FEE2E2;
    color: #B91C1C;
    font-size: 11px;
    font-weight: 600;
    border-radius: 12px;
    padding: 4px 10px;
}

QFrame.MetricCard {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 16px;
}

QFrame.MetricCard:hover {
    border: 1px solid #CBD5E1;
}

QLabel.CardTitle {
    color: #64748B;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
}

QLabel.CardValue {
    color: #0F172A;
    font-size: 26px;
    font-weight: 700;
}

QLabel.CardSubtext {
    color: #94A3B8;
    font-size: 11px;
}

QPushButton.PrimaryButton {
    background-color: #0284C7;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
}

QPushButton.PrimaryButton:hover {
    background-color: #0369A1;
}

QPushButton.SecondaryButton {
    background-color: #F1F5F9;
    color: #1E293B;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 500;
}

QPushButton.SecondaryButton:hover {
    background-color: #E2E8F0;
}

QPushButton.DangerButton {
    background-color: #DC2626;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 600;
}

QLineEdit {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 8px 12px;
}

QTableWidget {
    background-color: #FFFFFF;
    color: #0F172A;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    gridline-color: #F1F5F9;
    selection-background-color: #E0F2FE;
    selection-color: #0284C7;
}

QHeaderView::section {
    background-color: #F8FAFC;
    color: #475569;
    font-weight: 600;
    font-size: 12px;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #E2E8F0;
}
"""
