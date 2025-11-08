# Import all tasks here
from app.tasks.nlp_tasks import analyze_document_text
from app.tasks.apa_tasks import validate_apa_coherence
from app.tasks.export_tasks import export_document
from app.tasks.stats_tasks import calculate_document_stats
from app.tasks.audit_tasks import archive_old_audit_logs

